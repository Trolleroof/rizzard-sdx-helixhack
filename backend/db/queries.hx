// Helix schema + queries for professor profiles

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

QUERY InsertProfessor(profile_id: String, name: String, title: String, department: String, profile_url: String, summary: String, keywords: [String], recent_publications: [String], news_mentions: [String], hiring: Boolean, last_updated: String, rerank_strategy: String, vector: [F64]) =>
    professor <- AddV<Professor>(vector, { profile_id: profile_id, name: name, title: title, department: department, profile_url: profile_url, summary: summary, keywords: keywords, recent_publications: recent_publications, news_mentions: news_mentions, hiring: hiring, last_updated: last_updated, rerank_strategy: rerank_strategy })
    RETURN professor

QUERY SearchSimilarProfessors(vector: [F64], limit: I64) =>
    professors <- SearchV<Professor>(vector, limit)
    RETURN professors

QUERY GetProfessorByUrl(url: String) =>
    professor <- V<Professor>::WHERE(_::{profile_url}::EQ(url))
    RETURN professor
