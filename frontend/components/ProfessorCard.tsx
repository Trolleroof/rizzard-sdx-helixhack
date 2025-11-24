'use client';

import { motion, useMotionValue, useTransform } from 'framer-motion';
import { useState } from 'react';

export interface Professor {
  profile_id: string;
  name: string;
  title?: string;
  department?: string;
  summary: string;
  keywords: string[];
  image_url?: string;
  activity_signals?: {
    recent_publications?: string[];
    news_mentions?: string[];
    hiring?: boolean;
    last_updated?: string;
  };
  scores?: {
    semantic: number;
    compatibility: number;
    feasibility: number;
    final_score: number;
  };
  match_summary?: string;
}

interface ProfessorCardProps {
  professor: Professor;
  onSwipe: (direction: 'left' | 'right') => void;
  isTop: boolean;
}

export default function ProfessorCard({ professor, onSwipe, isTop }: ProfessorCardProps) {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-25, 25]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

  const [exitX, setExitX] = useState(0);

  const handleDragEnd = (_: any, info: any) => {
    if (Math.abs(info.offset.x) > 100) {
      setExitX(info.offset.x > 0 ? 500 : -500);
      onSwipe(info.offset.x > 0 ? 'right' : 'left');
    }
  };

  return (
    <motion.div
      className="absolute w-full h-full"
      style={{
        x,
        rotate,
        opacity,
        cursor: isTop ? 'grab' : 'default',
      }}
      drag={isTop ? 'x' : false}
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      animate={exitX !== 0 ? { x: exitX } : {}}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      whileTap={isTop ? { cursor: 'grabbing' } : {}}
    >
      <div className="w-full h-full rounded-2xl shadow-xl border-2 overflow-hidden" style={{ backgroundColor: '#FFFFFF', borderColor: '#00356B' }}>
        {/* Professor Image */}
        <div className="h-64 relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #00356B 0%, #FF69A6 100%)' }}>
          {professor.image_url ? (
            <img
              src={professor.image_url}
              alt={professor.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-6xl font-bold" style={{ color: '#FFFFFF' }}>
              {professor.name.charAt(0).toUpperCase()}
            </div>
          )}

          {/* Match Score Badge */}
          {professor.scores && (
            <div className="absolute top-4 left-4 px-4 py-2 rounded-full text-lg font-bold shadow-lg" style={{ backgroundColor: '#FFCD00', color: '#00356B' }}>
              {Math.round(professor.scores.final_score * 100)}% Match
            </div>
          )}

          {/* Activity Badge */}
          {professor.activity_signals?.hiring && (
            <div className="absolute top-4 right-4 px-3 py-1 rounded-full text-sm font-semibold" style={{ backgroundColor: '#FF69A6', color: '#FFFFFF' }}>
              Hiring
            </div>
          )}
        </div>

        {/* Professor Info */}
        <div className="p-6 space-y-4">
          <div>
            <h2 className="text-2xl font-bold" style={{ color: '#00356B' }}>{professor.name}</h2>
            {professor.title && (
              <p className="text-lg mt-1" style={{ color: '#00356B', opacity: 0.8 }}>{professor.title}</p>
            )}
            {professor.department && (
              <p className="text-sm mt-1" style={{ color: '#00356B', opacity: 0.6 }}>{professor.department}</p>
            )}
          </div>

          {/* Claude-Generated Match Summary */}
          {professor.match_summary && (
            <div className="p-3 rounded-lg" style={{ backgroundColor: '#FFCD0020', borderLeft: '3px solid #FFCD00' }}>
              <p className="text-sm font-medium leading-relaxed" style={{ color: '#00356B' }}>
                {professor.match_summary}
              </p>
            </div>
          )}

          {/* Research Summary */}
          {!professor.match_summary && (
            <div>
              <p className="text-sm leading-relaxed line-clamp-3" style={{ color: '#00356B', opacity: 0.9 }}>
                {professor.summary}
              </p>
            </div>
          )}

          {/* Score Breakdown */}
          {professor.scores && (
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center p-2 rounded" style={{ backgroundColor: '#00356B10' }}>
                <div className="text-xs font-semibold" style={{ color: '#00356B', opacity: 0.7 }}>Semantic</div>
                <div className="text-lg font-bold" style={{ color: '#00356B' }}>{Math.round(professor.scores.semantic * 100)}%</div>
              </div>
              <div className="text-center p-2 rounded" style={{ backgroundColor: '#00356B10' }}>
                <div className="text-xs font-semibold" style={{ color: '#00356B', opacity: 0.7 }}>Compatibility</div>
                <div className="text-lg font-bold" style={{ color: '#00356B' }}>{Math.round(professor.scores.compatibility * 100)}%</div>
              </div>
              <div className="text-center p-2 rounded" style={{ backgroundColor: '#00356B10' }}>
                <div className="text-xs font-semibold" style={{ color: '#00356B', opacity: 0.7 }}>Feasibility</div>
                <div className="text-lg font-bold" style={{ color: '#00356B' }}>{Math.round(professor.scores.feasibility * 100)}%</div>
              </div>
            </div>
          )}

          {/* Keywords/Research Areas */}
          {professor.keywords && professor.keywords.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {professor.keywords.slice(0, 5).map((keyword, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-full text-xs font-medium"
                  style={{ backgroundColor: '#FFCD00', color: '#00356B' }}
                >
                  {keyword}
                </span>
              ))}
            </div>
          )}

          {/* Recent Publications */}
          {professor.activity_signals?.recent_publications &&
           professor.activity_signals.recent_publications.length > 0 && (
            <div className="pt-2 border-t" style={{ borderColor: '#00356B', opacity: 0.2 }}>
              <p className="text-xs font-semibold mb-1" style={{ color: '#00356B', opacity: 0.7 }}>Recent Work</p>
              <p className="text-xs line-clamp-2" style={{ color: '#00356B', opacity: 0.8 }}>
                {professor.activity_signals.recent_publications[0]}
              </p>
            </div>
          )}
        </div>

        {/* Swipe Instructions (only on top card) */}
        {isTop && (
          <div className="absolute bottom-0 left-0 right-0 p-4" style={{ background: 'linear-gradient(to top, rgba(0, 53, 107, 0.8), transparent)' }}>
            <div className="flex justify-between items-center text-sm font-semibold" style={{ color: '#FFFFFF' }}>
              <div className="flex items-center gap-2">
                <span className="text-2xl">←</span>
                <span>Skip</span>
              </div>
              <div className="flex items-center gap-2">
                <span>Interested</span>
                <span className="text-2xl">→</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
