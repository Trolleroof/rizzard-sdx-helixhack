'use client';

import { useState } from 'react';
import ProfessorCard, { Professor } from './ProfessorCard';

interface CardDeckProps {
  professors: Professor[];
  onMatch: (professor: Professor) => void;
  onSkip: (professor: Professor) => void;
  onComplete?: () => void;
}

export default function CardDeck({ professors, onMatch, onSkip, onComplete }: CardDeckProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState<'left' | 'right' | null>(null);

  const handleSwipe = (swipeDirection: 'left' | 'right') => {
    const currentProfessor = professors[currentIndex];
    setDirection(swipeDirection);

    // Call the appropriate callback
    if (swipeDirection === 'right') {
      onMatch(currentProfessor);
    } else {
      onSkip(currentProfessor);
    }

    // Move to next card after animation
    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setDirection(null);

      // Check if we've gone through all cards
      if (currentIndex + 1 >= professors.length && onComplete) {
        onComplete();
      }
    }, 300);
  };

  const handleButtonSwipe = (swipeDirection: 'left' | 'right') => {
    handleSwipe(swipeDirection);
  };

  if (professors.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <p style={{ color: '#00356B', opacity: 0.6 }}>No professors to show</p>
      </div>
    );
  }

  if (currentIndex >= professors.length) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="text-6xl">🎉</div>
        <h2 className="text-2xl font-bold" style={{ color: '#00356B' }}>All done!</h2>
        <p style={{ color: '#00356B', opacity: 0.8 }}>You've reviewed all professors</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Card Stack Container */}
      <div className="relative w-full h-[600px]">
        {professors
          .slice(currentIndex, currentIndex + 3)
          .map((professor, idx) => {
            const isTop = idx === 0;
            const offset = idx;

            return (
              <div
                key={`${professor.profile_id}-${currentIndex + idx}`}
                className="absolute inset-0 transition-transform duration-200"
                style={{
                  zIndex: 10 - idx,
                  transform: `scale(${1 - offset * 0.05}) translateY(${offset * 10}px)`,
                  opacity: 1 - offset * 0.2,
                  pointerEvents: isTop ? 'auto' : 'none',
                }}
              >
                <ProfessorCard
                  professor={professor}
                  onSwipe={handleSwipe}
                  isTop={isTop}
                />
              </div>
            );
          })}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center gap-6">
        <button
          onClick={() => handleButtonSwipe('left')}
          className="w-16 h-16 rounded-full border-2 hover:opacity-80 transition-opacity shadow-lg flex items-center justify-center text-2xl font-bold"
          style={{ backgroundColor: '#FFFFFF', borderColor: '#00356B', color: '#00356B' }}
          aria-label="Skip"
        >
          ✕
        </button>
        <button
          onClick={() => handleButtonSwipe('right')}
          className="w-16 h-16 rounded-full border-2 hover:opacity-80 transition-opacity shadow-lg flex items-center justify-center text-2xl"
          style={{ backgroundColor: '#FF69A6', borderColor: '#FF69A6', color: '#FFFFFF' }}
          aria-label="Interested"
        >
          ♥
        </button>
      </div>

      {/* Progress Indicator */}
      <div className="flex justify-center items-center gap-2 text-sm font-semibold" style={{ color: '#00356B' }}>
        <span>
          {currentIndex + 1} / {professors.length}
        </span>
      </div>
    </div>
  );
}
