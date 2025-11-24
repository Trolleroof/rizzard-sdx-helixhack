// Helix schema for professor profiles

V::Professor {
    profile_id: String,
    name: String,
    title: String,
    department: String,
    profile_url: String,
    summary: String,
    keywords: [String],
    recent_publications: [String],
    news_mentions: [String],
    hiring: Boolean,
    last_updated: String,
    rerank_strategy: String
}

// Note: Actual UCSD professor data is inserted via scripts/insert_ucsd_professors.py
// The script parses the data from this file's previous version and inserts it into HelixDB
