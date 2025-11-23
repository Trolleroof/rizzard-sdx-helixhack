Below is a clean rewritten architecture that keeps your core backend in Node.js + Express, but clearly separates which AI/ML tasks are handled by a Python microservice (FastAPI or Flask).
 This rewrite is meant for teamwork: you handle JS, your friend handles Python AI logic, without mixing responsibilities.
Everything below is formatted as a proper architecture section, replacing the old one.

🚀 Rizzard — Hybrid Architecture (Node.js Backend + Python AI Microservice)
This architecture preserves your original design but moves all heavy AI work to Python so your teammate can take over the ML/AI tasks.

2. High-Level Architecture Overview
Rizzard consists of five primary layers:

🟦 A. Frontend (User Interface)
Swipeable researcher cards (Tinder-style)
 Match Score with detailed breakdown
 Activity flags (Green/Yellow/Red)
 “Generate Email” & “Project Idea” buttons
 Sends user intent to the backend
Tech: React, TailwindCSS, Axios/Fetch

🟧 B. Backend (Node.js + Express)
This is now a thin orchestration layer, not the AI engine.
Node.js handles:
✔ Routing and API Endpoints
/match


/email


/project


/scrape


✔ Intent Parsing (lightweight JS logic)
Extract keywords from user query.
✔ Department Routing
Map keyword → UCSD department URL(s).
✔ Firecrawl Scraping
Node sends scraping requests to Firecrawl and gets structured JSON.
✔ Profile Aggregation (light processing)
Combine scraped fields into a profile object before sending to Python.
✔ HelixDB Interaction
Insert researchers, embeddings, publications, and edges into HelixDB.
✔ Final Response Assembly
Node combines results from Python → sends structured match results to frontend.

🟩 C. Python AI Microservice (FastAPI or Flask)
This is where your buddy does ALL the AI tasks.
 Node.js offloads AI work by calling Python like a remote service:
POST http://python-service:5000/embed
POST http://python-service:5000/score
POST http://python-service:5000/email
POST http://python-service:5000/project
POST http://python-service:5000/process-profile

Python handles:

🔥 1. Embedding Generation
Use SentenceTransformers (all-MiniLM-L6-v2)


Generate embeddings for:


Researcher profiles


User query


Normalize vectors


Return embeddings to Node.js



🔥 2. Semantic Similarity (Cosine Similarity)
Python computes cosine similarity between embedding vectors:
[
 \text{cosine}(q, r)
 ]
Faster and easier with numpy or sentence_transformers.util.cos_sim.

🔥 3. Compatibility Score
Python handles the deeper ML logic:
Keyword/method overlap


Seniority matching


Department diversity


Graph proximity (optional)


Statistical similarity of research areas


Returns a score 0–1.

🔥 4. Feasibility Score
Python analyzes activity signals:
Recent publications


News patterns


Lab hiring signals


“Busy” or “active” patterns


NLP-based readiness signals


Returns score 0–1.

🔥 5. Match Engine (Final Score Computation)
Python computes:
final_score = 0.6 * semantic + 0.2 * compatibility + 0.2 * feasibility

Returns match score + breakdown to Node.js.

🔥 6. NLP Profile Processing
Python can enhance profile text:
Extract methods, topics, keywords


Summarize research overview


Clean and normalize text


Extract research “love languages”



🔥 7. LLM Generation
Python calls LLM APIs for:
Personalized cold outreach email


Suggested joint project ideas


Python supports:
OpenAI


Claude


Groq


Local models


HuggingFace
 depending on preference.



🟨 D. Database Layer (HelixDB)
Stores:
Researcher nodes


Embedding vectors (inserted via Node)


Publication nodes


Topic nodes


Edges:
WORKS_AT


CO_AUTHORED


PUBLISHED


RELATED_TO


Used for:
Graph filtering


Vector similarity search


Co-author distance checks



🟥 E. Dynamic Scraping Layer (Firecrawl)
Firecrawl scrapes relevant UCSD departments based on intent.
Extracts:
Names


Titles


Departments


Publication info


Lab descriptions


Activity signals


Research summaries


Returns structured JSON → sent to Python for processing → returned to Node.

3. Intent-Based UCSD Scraping (Hybrid Workflow)
Node.js:
Parse intent


Route to departments


Call Firecrawl


Cache results


Send scraped profiles → Python


Python:
Clean & process profile text


Extract methods, keywords, signals


Produce standardized profiles


Send back to Node



4. Data Processing & Embedding Generation (Python)
Python performs:
Text cleaning


NLP keyword extraction


Embedding generation


Mean pooling + normalization


Semantic similarity calculation


Compatibility scoring


Feasibility scoring


Node:
Inserts resulting data into HelixDB



5. Match Engine (Python)
Python computes:
A. Semantic Similarity
Cosine similarity of vectors.
B. Compatibility Score
Keyword/method overlap, dept diversity, seniority matching.
C. Feasibility Score
NLP on recent updates, activity patterns.
Final Score
Sent back to Node → sent to frontend.

6. Backend API (Node.js)
Node just coordinates:
/match
Receives user intent


Scrapes via Firecrawl


Sends profiles to Python


Python returns full scoring


Node enriches with HelixDB graph metadata


Sends match results to frontend


/email, /project
Python handles LLM content generation
 Node returns it.

8. End-To-End System Flow



9. Updated Tech Stack Summary
Frontend
React
 TailwindCSS
 Axios
Backend Orchestrator (Node.js)
Express
 Firecrawl API
 HelixDB client
 Axios (to call Python microservice)
AI Microservice (Python)
FastAPI or Flask
 SentenceTransformers
 NumPy / SciPy
 LLM API of choice
 Regex / spaCy for NLP
 Cosine similarity + scoring modules

✅ Express (Node.js) handles all backend web APIs
These are the APIs your frontend talks to:
✔ Routing
/match


/email


/project


/scrape


✔ Firecrawl scraping
Node calls Firecrawl and gets structured UCSD data.
✔ HelixDB writes/queries
Node inserts researchers, embeddings, edges, etc.
✔ Intent parsing + department routing
Light logic → maps user intent → UCSD departments.
✔ Final response formatting for frontend
Node packages scores, metadata, flags, profiles.

🟩 FastAPI (Python) handles all AI-heavy APIs
These are internal APIs that only the Node backend calls.
✔ Embeddings
POST /embed
 → SentenceTransformers (MiniLM or any model)
✔ Cosine similarity scoring
POST /score
 → Python computes semantic similarity
✔ Profile NLP processing
POST /process-profile
 → extract keywords, methods, signals
✔ Match engine scoring
POST /match-scores
 → return semantic, compatibility, feasibility scores
✔ LLM generation
POST /email
 → cold outreach
 POST /project
 → project idea

💡 Simple way to think about it:
Frontend ↔ Express
(React only ever talks to Node)
Express ↔ FastAPI
(Node talks to Python for AI tasks)
Express ↔ HelixDB
(Node manages the graph & vectors)

🔥 Why this split is perfect
✔ You stay in JavaScript
Your partner stays in Python
 → No one suffers.
✔ Node remains simple
No heavy ML in Express.
✔ Python shines where it’s strongest
NLP, embeddings, scoring, LLM calls.
✔ Clean responsibilities
Frontend calls one backend (Express),
 and Express calls the AI microservice (FastAPI).

