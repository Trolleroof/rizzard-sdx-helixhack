'use client';

import { useState } from 'react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import CardDeck from '../components/CardDeck';
import { Professor } from '../components/ProfessorCard';

export default function Home() {
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [selectedProfessors, setSelectedProfessors] = useState<Professor[]>([]);
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      return;
    }

    setSearchQuery(query);
    setIsSearching(true);
    setShowResults(false);
    setProfessors([]); // Clear previous results

    try {
      console.log('Starting search for:', query);
      
      // Call the backend API to get professor profiles
      const response = await fetch(
        `http://localhost:8000/profiles/search?query=${encodeURIComponent(query)}&limit=20`
      );

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API error:', errorText);
        throw new Error(`Failed to fetch profiles: ${response.status} ${errorText}`);
      }

      const data = await response.json();

      console.log('API Response:', data);
      console.log('Results count:', data.results?.length || 0);

      // Transform the API response to match our Professor interface
      const transformedProfiles: Professor[] = (data.results || []).map((result: any) => {
        const profile = result.profile || {};
        const scores = result.scores || null;
        const matchSummary = result.summary_text || null;

        return {
          profile_id: profile.profile_id || profile.id || '',
          name: profile.name || 'Unknown Professor',
          title: profile.title || '',
          department: profile.department || '',
          summary: profile.summary || '',
          keywords: profile.keywords || [],
          activity_signals: profile.activity_signals || {
            recent_publications: profile.recent_publications || [],
            news_mentions: profile.news_mentions || [],
            hiring: profile.hiring || false,
            last_updated: profile.last_updated || '',
          },
          image_url: profile.image_url,
          scores: scores ? {
            semantic: scores.semantic || 0,
            compatibility: scores.compatibility || 0,
            feasibility: scores.feasibility || 0,
            final_score: scores.final_score || 0,
          } : undefined,
          match_summary: matchSummary,
        };
      });

      console.log('Transformed profiles:', transformedProfiles.length);
      console.log('Setting professors and showResults...');
      
      setProfessors(transformedProfiles);
      setShowResults(transformedProfiles.length > 0);
      
      console.log('State updated. showResults:', transformedProfiles.length > 0, 'professors:', transformedProfiles.length);
    } catch (error) {
      console.error('Error fetching profiles:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setProfessors([]);
      setShowResults(false);
    } finally {
      setIsSearching(false);
      console.log('Search complete. isSearching set to false');
    }
  };

  const handleMatch = (professor: Professor) => {
    setSelectedProfessors((prev) => [...prev, professor]);
  };

  const handleSkip = (professor: Professor) => {
    // Just log for now, could add to a "passed" list if needed
    console.log('Skipped:', professor.name);
  };

  const handleComplete = () => {
    console.log('All professors reviewed!');
  };

  return (
    <div className="flex min-h-screen flex-col" style={{ backgroundColor: '#FFFFFF' }}>
      {/* Header */}
      <header className="border-b-2" style={{ borderColor: '#00356B', backgroundColor: '#FFFFFF' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold" style={{ color: '#00356B' }}>
            Rizzard
          </h1>
          <p className="text-sm mt-1" style={{ color: '#00356B', opacity: 0.7 }}>
            Research Matchmaking Engine
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Search Section */}
          <section className="rounded-lg shadow-lg border-2 p-6" style={{ backgroundColor: '#FFFFFF', borderColor: '#00356B' }}>
            <h2 className="text-2xl font-bold mb-4" style={{ color: '#00356B' }}>
              Find Your Research Match
            </h2>
            <SearchBar onSearch={handleSearch} isLoading={isSearching} />

            {isSearching && (
              <div className="mt-6">
                <LoadingSpinner />
                <p className="text-center mt-4" style={{ color: '#00356B' }}>
                  Searching for researchers matching "{searchQuery}"...
                </p>
              </div>
            )}
          </section>

          {/* Results Section - Swipeable Cards */}
          {!isSearching && showResults && professors.length > 0 && (
            <section className="rounded-lg shadow-lg border-2 p-6" style={{ backgroundColor: '#FFFFFF', borderColor: '#00356B' }}>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold" style={{ color: '#00356B' }}>
                  Your Matches ({professors.length})
                </h2>
                {selectedProfessors.length > 0 && (
                  <div className="px-4 py-2 rounded-full text-sm font-semibold" style={{ backgroundColor: '#FF69A6', color: '#FFFFFF' }}>
                    {selectedProfessors.length} selected
                  </div>
                )}
              </div>

              <CardDeck
                professors={professors}
                onMatch={handleMatch}
                onSkip={handleSkip}
                onComplete={handleComplete}
              />
            </section>
          )}

          {/* No Results Message */}
          {!isSearching && !showResults && searchQuery && professors.length === 0 && (
            <section className="rounded-lg shadow-lg border-2 p-6" style={{ backgroundColor: '#FFFFFF', borderColor: '#00356B' }}>
              <div className="text-center py-12">
                <p className="text-lg" style={{ color: '#00356B' }}>
                  No professors found matching "{searchQuery}"
                </p>
                <p className="text-sm mt-2" style={{ color: '#00356B', opacity: 0.7 }}>
                  Try a different search term
                </p>
              </div>
            </section>
          )}

          {/* Selected Professors Section */}
          {selectedProfessors.length > 0 && (
            <section className="rounded-lg shadow-lg border-2 p-6" style={{ backgroundColor: '#FFFFFF', borderColor: '#00356B' }}>
              <h2 className="text-2xl font-bold mb-4" style={{ color: '#00356B' }}>
                Your Shortlist ({selectedProfessors.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedProfessors.map((professor) => (
                  <div
                    key={professor.profile_id}
                    className="border-2 rounded-lg p-4 hover:shadow-md transition-shadow"
                    style={{ borderColor: '#00356B' }}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold" style={{ color: '#00356B' }}>{professor.name}</h3>
                      {professor.scores && (
                        <span className="px-2 py-1 rounded-full text-xs font-bold" style={{ backgroundColor: '#FFCD00', color: '#00356B' }}>
                          {Math.round(professor.scores.final_score * 100)}%
                        </span>
                      )}
                    </div>
                    {professor.title && (
                      <p className="text-sm mt-1" style={{ color: '#00356B', opacity: 0.8 }}>{professor.title}</p>
                    )}
                    {professor.department && (
                      <p className="text-xs mt-1" style={{ color: '#00356B', opacity: 0.6 }}>{professor.department}</p>
                    )}
                    <div className="mt-3 flex flex-wrap gap-1">
                      {professor.keywords.slice(0, 3).map((keyword, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded text-xs font-medium"
                          style={{ backgroundColor: '#FFCD00', color: '#00356B' }}
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
