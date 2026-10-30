// frontend/src/components/RecommendationCards.jsx
// Responsive display of AI-generated personalized recommendations

import React from 'react';
import {
  Sparkles,
  MapPin,
  Clock,
  DollarSign,
  Lightbulb,
  Check,
  AlertCircle,
  Loader2,
  Compass,
} from 'lucide-react';

const CATEGORY_COLORS = {
  Attractions: { bg: '#eef2ff', text: '#4338ca', border: '#c7d2fe' },
  Activities: { bg: '#ecfdf5', text: '#065f46', border: '#a7f3d0' },
  Dining: { bg: '#fff7ed', text: '#9a3412', border: '#fed7aa' },
  'Cultural Experiences': { bg: '#faf5ff', text: '#6b21a8', border: '#e9d5ff' },
  'Nature and Adventure': { bg: '#f0fdf4', text: '#166534', border: '#bbf7d0' },
};

export function RecommendationCards({
  items = [],
  destination = '',
  isLoading = false,
  error = null,
  onSelectDestination = null,
  isDestinationMode = false,
}) {
  if (isLoading) {
    return (
      <div className="recommendations-loading">
        <Loader2 className="spinner" size={32} />
        <p>Curating personalized AI recommendations for {destination || 'you'}…</p>
        <span className="loading-subtext">Analyzing travel style, budget, interests & dietary needs</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <AlertCircle size={18} />
          <strong>Recommendation Notice</strong>
        </div>
        <p>{error}</p>
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div className="recommendations-empty">
        <Compass size={36} color="#94a3b8" />
        <p>No recommendations loaded yet.</p>
        <span>Click below to generate personalized recommendations based on your preferences.</span>
      </div>
    );
  }

  // If in Destination Suggestion Mode
  if (isDestinationMode) {
    return (
      <div className="recommendations-grid">
        {items.map((dest, idx) => (
          <div key={idx} className="recommendation-card destination-card">
            <div className="card-top">
              <span className="category-badge" style={{ background: '#f0f9ff', color: '#0369a1', borderColor: '#bae6fd' }}>
                📍 Destination Idea
              </span>
              <span className="cost-pill">{dest.estimated_budget_range}</span>
            </div>

            <h3 className="card-title">{dest.destination}</h3>
            <p className="card-desc">{dest.description}</p>

            <div className="match-reason-box">
              <Sparkles size={14} className="match-icon" />
              <span><strong>Why it matches:</strong> {dest.why_it_matches}</span>
            </div>

            {dest.highlight_attractions && dest.highlight_attractions.length > 0 && (
              <div className="highlights-list">
                <span className="highlights-label">Top Highlights:</span>
                <ul>
                  {dest.highlight_attractions.map((h, hIdx) => (
                    <li key={hIdx}>{h}</li>
                  ))}
                </ul>
              </div>
            )}

            {dest.practical_tips && (
              <div className="tips-footer">
                <Lightbulb size={14} className="tip-icon" />
                <span>{dest.practical_tips}</span>
              </div>
            )}

            {onSelectDestination && (
              <button
                type="button"
                className="btn-select-dest"
                onClick={() => onSelectDestination(dest.destination)}
              >
                <Check size={14} /> Select {dest.destination.split(',')[0]}
              </button>
            )}
          </div>
        ))}
      </div>
    );
  }

  // Activity & Dining Recommendations Mode
  return (
    <div className="recommendations-grid">
      {items.map((item, idx) => {
        const theme = CATEGORY_COLORS[item.category] || {
          bg: '#f8fafc',
          text: '#334155',
          border: '#e2e8f0',
        };

        return (
          <div key={idx} className="recommendation-card">
            <div className="card-top">
              <span
                className="category-badge"
                style={{
                  background: theme.bg,
                  color: theme.text,
                  borderColor: theme.border,
                }}
              >
                {item.category}
              </span>
              {item.estimated_cost && (
                <span className="cost-pill">
                  <DollarSign size={12} /> {item.estimated_cost}
                </span>
              )}
            </div>

            <h3 className="card-title">{item.name}</h3>

            {item.location && (
              <div className="card-meta">
                <MapPin size={13} />
                <span>{item.location}</span>
                {item.suggested_duration && (
                  <>
                    <span className="meta-sep">&bull;</span>
                    <Clock size={13} />
                    <span>{item.suggested_duration}</span>
                  </>
                )}
              </div>
            )}

            <p className="card-desc">{item.description}</p>

            {item.reason_for_recommendation && (
              <div className="match-reason-box">
                <Sparkles size={14} className="match-icon" />
                <span><strong>Why it fits:</strong> {item.reason_for_recommendation}</span>
              </div>
            )}

            {item.best_time_to_visit && (
              <div className="best-time">
                <Clock size={13} /> Best time: {item.best_time_to_visit}
              </div>
            )}

            {item.practical_tips && (
              <div className="tips-footer">
                <Lightbulb size={14} className="tip-icon" />
                <span><strong>Tip:</strong> {item.practical_tips}</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default RecommendationCards;

