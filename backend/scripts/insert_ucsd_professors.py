"""Script to insert real UCSD professor data into HelixDB."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import config module directly without triggering app.__init__
import importlib.util
config_path = BACKEND_DIR / "app" / "config.py"
spec = importlib.util.spec_from_file_location("config", config_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
get_settings = config_module.get_settings

# Import services
from app.services.embedding import embed_texts
from app.services.helixdb_service import HelixDBService

# Import professor data
from data.professors import UCSD_PROFESSORS


def main() -> None:
    """Insert UCSD professor data into HelixDB."""
    professors = UCSD_PROFESSORS
    
    print(f"✓ Found {len(professors)} UCSD professors in data file")
    
    if not professors:
        print("❌ No professors found in data file. Exiting.")
        sys.exit(1)
    
    print("\nInitializing HelixDB service...")
    settings = get_settings()
    helix_service = HelixDBService(settings=settings)
    
    print("Initializing schema...")
    try:
        schema_initialized = helix_service.initialize_schema()
        if schema_initialized:
            print("✓ Schema initialized successfully")
        else:
            print("⚠ Schema initialization returned False (may already be initialized)")
    except Exception as exc:
        print(f"⚠ Schema initialization warning: {exc}")
        print("Continuing anyway...")
    
    print(f"\nGenerating embeddings for {len(professors)} professors...")
    summaries = [prof.get("summary", "") or prof.get("name", "") for prof in professors]
    embeddings, model_name = embed_texts(summaries, settings=settings)
    print(f"✓ Generated embeddings using model: {model_name}")
    
    print(f"\nInserting {len(professors)} UCSD professors into HelixDB...")
    success_count = 0
    error_count = 0
    
    for idx, professor in enumerate(professors):
        try:
            embedding = embeddings[idx] if idx < len(embeddings) else []
            if not embedding:
                print(f"⚠ Warning: No embedding for {professor.get('name', 'Unknown')}, skipping...")
                error_count += 1
                continue
            
            # Build payload
            payload = {
                "profile_id": professor.get("profile_id", ""),
                "name": professor.get("name", ""),
                "title": professor.get("title", ""),
                "department": professor.get("department", ""),
                "profile_url": professor.get("profile_url", ""),
                "summary": professor.get("summary", ""),
                "keywords": professor.get("keywords", []),
                "recent_publications": professor.get("recent_publications", []),
                "news_mentions": professor.get("news_mentions", []),
                "hiring": professor.get("hiring", False),
                "last_updated": professor.get("last_updated", ""),
                "rerank_strategy": professor.get("rerank_strategy", "hybrid"),
                "vector": embedding,
            }
            
            # Insert directly using the query
            print(f"Inserting {professor.get('name', 'Unknown')}...")
            result = helix_service.client.query("InsertProfessor", payload)
            
            # Extract vertex ID from result
            if isinstance(result, dict):
                helix_id = str(result.get("id") or result.get("vertex_id") or result.get("_id") or "unknown")
            else:
                helix_id = str(result)
            
            print(f"✓ Inserted: {professor.get('name', 'Unknown')} (ID: {helix_id[:20]}...)")
            success_count += 1
        except Exception as exc:
            print(f"✗ Error inserting {professor.get('name', 'Unknown')}: {exc}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successfully inserted: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(professors)}")
    print(f"{'='*60}")
    print("\n✓ UCSD professor data insertion complete!")
    print("You can now search for professors using the search endpoint.")


if __name__ == "__main__":
    main()

