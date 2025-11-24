"""Script to insert mock professor data into HelixDB for testing.

DEPRECATED: This script is deprecated. Use insert_ucsd_professors.py instead
to insert real UCSD professor data from db/schema.hx.
"""

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


# Mock professor data
MOCK_PROFESSORS = [
    {
        "profile_id": "prof_001",
        "name": "Dr. Sarah Chen",
        "title": "Associate Professor",
        "department": "Computer Science",
        "profile_url": "https://example.edu/professors/sarah-chen",
        "summary": "Dr. Chen specializes in machine learning, deep learning, and neural networks. Her research focuses on developing novel algorithms for computer vision and natural language processing. She has published over 50 papers in top-tier conferences and journals.",
        "keywords": ["machine learning", "deep learning", "computer vision", "neural networks", "NLP"],
        "recent_publications": [
            "Attention Mechanisms in Vision Transformers (2024)",
            "Multimodal Learning for Medical Imaging (2023)"
        ],
        "news_mentions": [],
        "hiring": True,
        "last_updated": "2024-11-01",
    },
    {
        "profile_id": "prof_002",
        "name": "Dr. Michael Rodriguez",
        "title": "Professor",
        "department": "Medicine",
        "profile_url": "https://example.edu/professors/michael-rodriguez",
        "summary": "Dr. Rodriguez is a leading researcher in oncology and cancer immunotherapy. His work focuses on developing personalized cancer treatments using CAR-T cell therapy and immune checkpoint inhibitors. He has led multiple clinical trials and received numerous awards for his contributions to cancer research.",
        "keywords": ["oncology", "cancer immunotherapy", "CAR-T therapy", "clinical trials", "personalized medicine"],
        "recent_publications": [
            "CAR-T Cell Therapy for Solid Tumors (2024)",
            "Biomarkers in Cancer Immunotherapy (2023)"
        ],
        "news_mentions": ["Featured in Nature Medicine (2024)"],
        "hiring": False,
        "last_updated": "2024-10-15",
    },
    {
        "profile_id": "prof_003",
        "name": "Dr. Emily Watson",
        "title": "Assistant Professor",
        "department": "Physics",
        "profile_url": "https://example.edu/professors/emily-watson",
        "summary": "Dr. Watson's research explores quantum computing and quantum information theory. She works on developing quantum algorithms for optimization problems and quantum error correction. Her lab collaborates with industry partners on quantum hardware development.",
        "keywords": ["quantum computing", "quantum information", "quantum algorithms", "quantum error correction"],
        "recent_publications": [
            "Quantum Algorithms for Optimization (2024)",
            "Error Correction in Quantum Systems (2023)"
        ],
        "news_mentions": [],
        "hiring": True,
        "last_updated": "2024-11-10",
    },
    {
        "profile_id": "prof_004",
        "name": "Dr. James Park",
        "title": "Professor",
        "department": "Medicine",
        "profile_url": "https://example.edu/professors/james-park",
        "summary": "Dr. Park is an expert in cardiology and cardiovascular medicine. His research focuses on heart failure, cardiac regeneration, and stem cell therapy for cardiac repair. He has developed innovative treatments for patients with advanced heart disease.",
        "keywords": ["cardiology", "heart failure", "cardiac regeneration", "stem cell therapy", "cardiovascular medicine"],
        "recent_publications": [
            "Stem Cell Therapy for Heart Failure (2024)",
            "Cardiac Regeneration Mechanisms (2023)"
        ],
        "news_mentions": ["Awarded Research Excellence Prize (2024)"],
        "hiring": False,
        "last_updated": "2024-09-20",
    },
    {
        "profile_id": "prof_005",
        "name": "Dr. Lisa Anderson",
        "title": "Associate Professor",
        "department": "Computer Science",
        "profile_url": "https://example.edu/professors/lisa-anderson",
        "summary": "Dr. Anderson specializes in cybersecurity, cryptography, and blockchain technology. Her research addresses security vulnerabilities in distributed systems and develops cryptographic protocols for secure communication. She has advised government agencies on cybersecurity policy.",
        "keywords": ["cybersecurity", "cryptography", "blockchain", "distributed systems", "network security"],
        "recent_publications": [
            "Post-Quantum Cryptography (2024)",
            "Blockchain Security Analysis (2023)"
        ],
        "news_mentions": [],
        "hiring": True,
        "last_updated": "2024-10-05",
    },
    {
        "profile_id": "prof_006",
        "name": "Dr. Robert Kim",
        "title": "Professor",
        "department": "Medicine",
        "profile_url": "https://example.edu/professors/robert-kim",
        "summary": "Dr. Kim is a renowned researcher in neurology and neurodegenerative diseases. His work focuses on Alzheimer's disease, Parkinson's disease, and developing therapeutic interventions. He leads a large research team studying brain aging and cognitive decline.",
        "keywords": ["neurology", "Alzheimer's disease", "Parkinson's disease", "neurodegeneration", "brain aging"],
        "recent_publications": [
            "Biomarkers for Early Alzheimer's Detection (2024)",
            "Therapeutic Targets in Parkinson's (2023)"
        ],
        "news_mentions": ["Featured in Science Magazine (2024)"],
        "hiring": True,
        "last_updated": "2024-11-05",
    },
    {
        "profile_id": "prof_007",
        "name": "Dr. Maria Garcia",
        "title": "Assistant Professor",
        "department": "Computer Science",
        "profile_url": "https://example.edu/professors/maria-garcia",
        "summary": "Dr. Garcia's research focuses on human-computer interaction, user experience design, and accessibility. She develops assistive technologies for people with disabilities and studies how AI can improve human-computer interfaces. Her work has been recognized with multiple design awards.",
        "keywords": ["human-computer interaction", "UX design", "accessibility", "assistive technology", "AI interfaces"],
        "recent_publications": [
            "AI-Powered Accessibility Tools (2024)",
            "Voice Interfaces for Visually Impaired Users (2023)"
        ],
        "news_mentions": [],
        "hiring": False,
        "last_updated": "2024-09-15",
    },
    {
        "profile_id": "prof_008",
        "name": "Dr. David Thompson",
        "title": "Professor",
        "department": "Medicine",
        "profile_url": "https://example.edu/professors/david-thompson",
        "summary": "Dr. Thompson is an expert in infectious diseases and epidemiology. His research focuses on emerging pathogens, vaccine development, and public health interventions. He has been involved in global health initiatives and pandemic response planning.",
        "keywords": ["infectious diseases", "epidemiology", "vaccine development", "public health", "pandemic response"],
        "recent_publications": [
            "Novel Vaccine Platforms (2024)",
            "Epidemiological Modeling for Outbreaks (2023)"
        ],
        "news_mentions": [],
        "hiring": True,
        "last_updated": "2024-10-25",
    },
]


def main() -> None:
    """Insert mock professor data into HelixDB."""
    print("Initializing HelixDB service...")
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

    print(f"\nGenerating embeddings for {len(MOCK_PROFESSORS)} professors...")
    summaries = [prof["summary"] for prof in MOCK_PROFESSORS]
    embeddings, model_name = embed_texts(summaries, settings=settings)
    print(f"✓ Generated embeddings using model: {model_name}")

    print(f"\nInserting {len(MOCK_PROFESSORS)} professors into HelixDB...")
    success_count = 0
    error_count = 0

    for idx, professor in enumerate(MOCK_PROFESSORS):
        try:
            embedding = embeddings[idx] if idx < len(embeddings) else []
            if not embedding:
                print(f"⚠ Warning: No embedding for {professor['name']}, skipping...")
                error_count += 1
                continue

            # Extract activity signals
            activity_signals = {
                "recent_publications": professor["recent_publications"],
                "news_mentions": professor["news_mentions"],
                "hiring": professor["hiring"],
                "last_updated": professor["last_updated"],
            }

            # Build payload directly to bypass the "already exists" check
            payload = {
                "profile_id": professor["profile_id"],
                "name": professor["name"],
                "title": professor["title"],
                "department": professor["department"],
                "profile_url": professor["profile_url"],
                "summary": professor["summary"],
                "keywords": professor["keywords"],
                "recent_publications": professor["recent_publications"],
                "news_mentions": professor["news_mentions"],
                "hiring": professor["hiring"],
                "last_updated": professor["last_updated"],
                "rerank_strategy": "hybrid",
                "vector": embedding,
            }

            # Insert directly using the query (bypassing the "already exists" check)
            print(f"Inserting {professor['name']}...")
            result = helix_service.client.query("InsertProfessor", payload)
            
            # Extract vertex ID from result
            if isinstance(result, dict):
                helix_id = str(result.get("id") or result.get("vertex_id") or result.get("_id") or "unknown")
            else:
                helix_id = str(result)
            
            print(f"✓ Inserted: {professor['name']} (ID: {helix_id})")
            success_count += 1
        except Exception as exc:
            print(f"✗ Error inserting {professor['name']}: {exc}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successfully inserted/updated: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(MOCK_PROFESSORS)}")
    print(f"{'='*60}")
    print("\n✓ Mock data insertion complete!")
    print("You can now test the search functionality.")


if __name__ == "__main__":
    main()

