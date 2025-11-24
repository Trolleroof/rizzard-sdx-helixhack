# Scrape Professors with Firecrawl and Load into HelixDB

## Overview

Build a pipeline to scrape professor profiles from URLs using Firecrawl, extract structured data, generate embeddings, and store them in HelixDB using HelixQL for vector search.

## Implementation Plan

### 1. Add Dependencies

- Add `firecrawl-py` to `backend/requirements.txt`
- Add `helix-py` to `backend/requirements.txt`

### 2. Create Firecrawl Service

**File**: `backend/app/services/firecrawl_service.py`

- Initialize Firecrawl client using `FIRECRAWL_API` from settings
- Create `scrape_url(url: str) -> dict` function that:
  - Calls Firecrawl API to scrape the URL
  - Returns structured data (markdown content, metadata)
  - Handles errors gracefully (network issues, invalid URLs)
- Create `scrape_batch(urls: list[str]) -> list[dict]` for batch processing
- Extract professor information from scraped content (name, department, research summary, etc.)

### 3. Create HelixDB Service with HelixQL

**File**: `backend/app/services/helixdb_service.py`

- Initialize HelixDB client (`helix.Client`)
- **Define HelixQL schema** for Professor nodes:
  ```hql
  N::Professor {
      name: String,
      department: String,
      profile_url: String,
      summary: String,
      keywords: [String]
  }
  ```

- **Create HelixQL queries**:
  ```hql
  QUERY InsertProfessor(name: String, department: String, profile_url: String, summary: String, keywords: [String], vector: [F64]) =>
      professor <- AddV<Professor>(vector, { name: name, department: department, profile_url: profile_url, summary: summary, keywords: keywords })
      RETURN professor
  ```

  ```hql
  QUERY SearchSimilarProfessors(vector: [F64], limit: I64) =>
      professors <- SearchV<Professor>(vector, limit)
      RETURN professors
  ```

- Create Python wrapper functions:
  - `initialize_schema()` - Executes HelixQL schema definition using `db.query()` or schema file
  - `insert_professor(profile_data: dict, embedding: list[float]) -> str `- Calls `InsertProfessor` HelixQL query via `db.query('InsertProfessor', {...})`
  - `batch_insert_professors(professors: list[dict]) -> list[str]` - Batch insert using HelixQL queries
- Handle connection errors and retries

### 4. Create Scraping Orchestrator

**File**: `backend/app/services/scrape_orchestrator.py`

- Orchestrates the full pipeline:

  1. Takes list of professor URLs
  2. Scrapes each URL using Firecrawl service
  3. Extracts and structures professor data (maps to `ProfileInput` schema)
  4. Generates embeddings using existing `embed_texts()` from `embedding.py`
  5. Inserts into HelixDB using HelixDB service (calls HelixQL queries)

- Handles partial failures (continue on error, log failures)
- Returns summary of successful/failed scrapes

### 5. Create API Endpoint (Optional)

**File**: `backend/app/routers/scrape.py`

- POST `/scrape-professors` endpoint
- Accepts list of URLs in request body
- Calls orchestrator service
- Returns scraping results and status

### 6. Create Standalone Script

**File**: `backend/scripts/scrape_professors.py`

- Command-line script for one-time bulk scraping
- Accepts input file (JSON with URLs or simple text file)
- Uses orchestrator service
- Provides progress feedback and summary

### 7. Update Configuration

**File**: `backend/app/config.py`

- Add HelixDB connection settings:
  - `helixdb_local: bool = True` (default)
  - `helixdb_verbose: bool = Field(False, env="HELIXDB_VERBOSE")`

## Data Flow

1. **Input**: List of professor profile URLs
2. **Firecrawl**: Scrapes each URL → returns markdown content
3. **Extraction**: Parse markdown to extract:

   - Name
   - Department
   - Research summary/description
   - Publications (if available)
   - Keywords/topics

4. **Embedding**: Generate vector embedding from research summary using `embed_texts()`
5. **HelixDB via HelixQL**: 

   - Execute HelixQL schema definition (if not already exists)
   - Execute `InsertProfessor` HelixQL query with:
     - Properties (name, department, profile_url, summary, keywords)
     - Vector embedding using `AddV<Professor>(vector, { properties })`

## Files to Create/Modify

- `backend/app/services/firecrawl_service.py` (new)
- `backend/app/services/helixdb_service.py` (new - uses HelixQL for schema and queries)
- `backend/app/services/scrape_orchestrator.py` (new)
- `backend/app/routers/scrape.py` (new)
- `backend/scripts/scrape_professors.py` (new)
- `backend/requirements.txt` (modify - add dependencies)
- `backend/app/config.py` (modify - add HelixDB config)
- `backend/schema.hql` (optional - separate HelixQL schema file for version control)

## Error Handling

- Network timeouts for Firecrawl requests
- Invalid URLs or inaccessible pages
- HelixDB connection failures
- HelixQL query execution errors (schema conflicts, invalid syntax, type mismatches)
- Partial batch failures (continue processing remaining items)
- Logging for debugging and monitoring

## HelixQL Implementation Details

- **Schema Definition**: Must use HelixQL `N::Professor { ... }` syntax
- **Vector Insertion**: Use `AddV<Professor>(vector, { properties })` in HelixQL queries
- **Query Execution**: All database operations go through HelixQL queries via `db.query(query_name, params)`
- **Schema File**: Consider storing HelixQL schema in separate `.hql` file for version control
- **Type Safety**: Ensure Python types map correctly to HelixQL types (String, [String], [F64], I64)

## Testing Considerations

- Test with single URL first
- Test batch processing with small list (5-10 URLs)
- Verify embeddings are generated correctly
- Verify HelixQL queries execute successfully
- Verify data appears in HelixDB via vector search
- Test error handling with invalid URLs
- Test HelixQL schema conflicts (re-running initialization)