'use client';

import { useState } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export default function SearchBar({ onSearch, isLoading = false }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your research interests or project idea..."
          className="flex-1 px-4 py-3 rounded-lg border-2 focus:outline-none focus:ring-2 transition-all"
          style={{
            borderColor: '#00356B',
            backgroundColor: '#FFFFFF',
            color: '#00356B',
          }}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="px-6 py-3 rounded-lg font-semibold transition-all focus:outline-none focus:ring-2 disabled:cursor-not-allowed"
          style={{
            backgroundColor: isLoading || !query.trim() ? '#00356B50' : '#00356B',
            color: '#FFFFFF',
          }}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  );
}

