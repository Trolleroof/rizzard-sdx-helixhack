Rizzard
1. Overview
Rizzard is now reimagined as the dating app for research collaboration AI-powered "Research Matchmaking Engine" that predicts strong intellectual chemistry, identifies long-term compatibility, senses real-time signals of interest (publications, grants, talks), and even checks if a collaboration is practically possible.
Think of it as Tinder + Hinge + OkCupid for Academia, powered by Firecrawl, HelixDB, embeddings, and LLMs.

2. Core Purpose
Help researchers find their ideal research match — someone with aligned interests, complementary skills, active energy, and the right timing.
Instead of dating profiles, we use:
Research Interests


Lab Strengths


Publication Patterns


Co-author Networks


Dynamic Research Energy (new paper = green flag)



3. Key System Pillars
A. Collaboration Prediction Engine ("Who You're Most Compatible With")
Predicts collaboration chemistry using:
Topic similarity


Shared methods


Co-author proximity


Recency of publications


Momentum indicators


Output: A “Collaboration Match Score,” similar to Hinge’s Most Compatible pick.

B. Compatibility Modeling ("Intellectual Love Languages")
Assesses deeper alignment:
Similar research passions


Complementary strengths (modeling vs. experiments)


Departmental diversity


Seniority match


Shared academic vibes


Output: A Compatibility Score (0–10), similar to OkCupid’s Match Percentage.

C. Dynamic Research Signal Tracking ("Green Flags & Red Flags")
Firecrawl continuously extracts signals to show who’s:
Publishing new work (🟢 Green Flag: Active!)


Getting grants (🟢 Energy high!)


Posting job openings (🟢 Capacity available!)


Not publishing recently (🟡 Might be busy)


Overloaded with projects (🔴 Not the right time)


These signals form a real-time Research Activity Feed, like seeing someone’s recent posts or stories.

D. Collaboration Feasibility Layer ("Are They Emotionally Available?")
Assesses whether a collaboration would actually work.
Looks for:
Lab availability


Active grant cycles


Currently open positions


Recent burnout signals (no papers, no news)


Departmental bureaucracy


Output: A Feasibility Score.
This is the equivalent of determining whether someone is actually ready to date.

E. Firecrawl Ingestion Pipeline ("Profile Creation")
Firecrawl becomes the engine that builds each researcher’s dating-style profile.
It gathers data from:
Faculty pages


Lab websites


CV PDFs


Publication lists


News/updates


Seminar postings


This creates a rich researcher "bio" including:
Research passions


Methods they love working with


Their academic history


Collaboration patterns


Recent activity (like a dynamic status)



4. User Experience
A researcher (like a user creating a dating profile) enters:
Their project idea (their “intent”)


What kind of collaborator they’re looking for


Filters (different department, seniority, etc.)


The system returns:
Best Matches (like Tinder/Hinge suggestions)


Compatibility breakdown (like OkCupid match analysis)


Feasibility (like: "Are they available?")


Dynamic signals (green flags!)


Users can:
"Swipe right" to shortlist


Auto-generate a personalized, charming cold email


Auto-generate a joint project pitch (your first date idea)



5. Sample Output
Your Top Match: Dr. Alice Chen
Match Score: 89%


Compatibility: 8.7/10 (Strong intellectual chemistry)


Feasibility: Medium (She’s busy but has openings)


Green Flags: New ML-stress-analysis paper 2 weeks ago


Shared Interests: Materials modeling + ML applications


Icebreaker: "Ask about her seminar next month!"


Buttons:
Send Intro Message (Email)


Suggest First-Date Project Idea



6. High-Level Architecture (Dating-App Inspired)
Firecrawl: Profile Builder


Scrapes and assembles researcher bios


Processing Pipeline: Profile Enhancer


Cleans text


Generates embeddings


Identifies passions, strengths, quirks


HelixDB: The Match Graph


Stores researcher nodes


Captures collaboration history (past relationships)


Manages similarity vectors (compatibility metrics)


Matchmaking Engine


Prediction model → "Who should you talk to?"


Compatibility → "Why you're a good match"


Feasibility → "Are they available?"


Frontend


Swipe-style shortlist


Visual profiles


Outreach generation



7. Hackathon MVP Scope
Must-Haves
Scrape 5–10 researcher profiles


Build Tinder-style profile cards


Generate embeddings for "interests"


Create Match Score (similarity + filters)


Basic co-author graph distance filter


Email generator (first message)


Stretch Goals
Compatibility breakdown visuals


Green flag / red flag indicators


Joint project idea generator



8. Rizzard Tech Stack (Short Version)
🎨 Frontend
Purpose: Tinder-style swipe UI for research profiles.
Next.js


TailwindCSS for fast styling


Tinder-card–style stack (e.g., react-tinder-card)




⚙️ Backend
Purpose: All intelligence — scraping, embeddings, scoring, graph search, LLM outputs.
Core Backend Framework
FastAPI (Python)


Simple, fast, async


Auto-generated docs


Data Ingestion
Firecrawl API


Scrape faculty pages


Extract publications, CVs, lab pages


Build researcher profiles (JSON/Markdown)


AI / ML Layer
SentenceTransformers (all-MiniLM-L6-v2)


Embeddings for project idea + researcher profiles


Cosine similarity


Hand-engineered scoring:


Semantic similarity


Compatibility score


Feasibility score


OpenAI GPT models


Cold email generator


Joint project idea generator


Database Layer
HelixDB (graph + vector DB)


Nodes: Researchers, Publications, Topics, Labs


Edges: CO_AUTHORED, WORKS_AT, RELATED_TO


Vector search + graph filtering for matchmaking

