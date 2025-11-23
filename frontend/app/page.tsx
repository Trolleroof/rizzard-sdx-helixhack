'use client';

import { useState } from 'react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Home() {
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setIsSearching(true);
    
    // Simulate search - replace with actual API call later
    setTimeout(() => {
      setIsSearching(false);
    }, 2000);
  };

  return (
    <div className="flex min-h-screen flex-col bg-white">
      {/* Header */}
      <header className="border-b border-zinc-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-zinc-900">
            Rizzard
          </h1>
          <p className="text-sm text-zinc-600 mt-1">
            Research Matchmaking Engine
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Search Section */}
          <section className="bg-white rounded-lg shadow-sm border border-zinc-200 p-6">
            <h2 className="text-xl font-semibold text-zinc-900 mb-4">
              Find Your Research Match
            </h2>
            <SearchBar onSearch={handleSearch} isLoading={isSearching} />
            
            {isSearching && (
              <div className="mt-6">
                <LoadingSpinner />
                <p className="text-center text-zinc-600 mt-4">
                  Searching for researchers matching "{searchQuery}"...
                </p>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
