// frontend/src/components/ExploreDestinations.jsx
// Explore Destinations & Destination Details Modal matching Pages 5 & 6 of the PDF reference

import React, { useState } from 'react';
import {
  Compass,
  Search,
  MapPin,
  Star,
  Clock,
  DollarSign,
  Sparkles,
  Calendar,
  ArrowRight,
  X,
  CheckCircle2,
  Bookmark,
  Share2,
} from 'lucide-react';

const DESTINATIONS = [
  {
    id: 'manali',
    name: 'Manali, India',
    country: 'India',
    vibe: 'Mountain',
    vibeTag: '🏔️ Mountain & Trekking',
    photo: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=700&q=80',
    rating: 4.9,
    reviews: 324,
    budget: '$65/day',
    bestTime: 'October to June',
    duration: '4-6 Days',
    description:
      'A high-altitude Himalayan resort town in Himachal Pradesh known for its breathtaking valleys, Solang pine forests, and adventure sports.',
    highlights: ['Solang Valley Paragliding', 'Rohtang Pass Snow Vista', 'Old Manali Cafes', 'Hadimba Temple Pine Walk'],
  },
  {
    id: 'kyoto',
    name: 'Kyoto, Japan',
    country: 'Japan',
    vibe: 'Cultural',
    vibeTag: '🏛️ Cultural & Historic',
    photo: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=700&q=80',
    rating: 4.9,
    reviews: 512,
    budget: '$180/day',
    bestTime: 'March–May & Oct–Nov',
    duration: '3-5 Days',
    description:
      'The cultural heart of Japan with thousands of classical Buddhist temples, gardens, imperial palaces, Shinto shrines, and traditional wooden houses.',
    highlights: ['Fushimi Inari Torii Path', 'Arashiyama Bamboo Grove', 'Gion Geisha District', 'Kinkaku-ji Golden Pavilion'],
  },
  {
    id: 'amalfi',
    name: 'Amalfi Coast, Italy',
    country: 'Italy',
    vibe: 'Beach',
    vibeTag: '🏖️ Coastal & Scenic',
    photo: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=700&q=80',
    rating: 4.8,
    reviews: 418,
    budget: '$260/day',
    bestTime: 'May to September',
    duration: '4-7 Days',
    description:
      'A dramatic 50-kilometer stretch of coastline in southern Italy featuring pastel-colored cliffside fishing villages, lemon terraces, and sparkling waters.',
    highlights: ['Positano Cliffside Walk', 'Path of the Gods Hike', 'Ravello Villa Gardens', 'Capri Boat Excursion'],
  },
  {
    id: 'swiss-alps',
    name: 'Swiss Alps, Switzerland',
    country: 'Switzerland',
    vibe: 'Mountain',
    vibeTag: '🏔️ Alpine & Nature',
    photo: 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=700&q=80',
    rating: 4.9,
    reviews: 389,
    budget: '$240/day',
    bestTime: 'December–March or July–Sep',
    duration: '5-8 Days',
    description:
      'Iconic snow-capped peaks, glacier-carved valleys, crystal blue lakes, and panoramic scenic trains connecting world-class alpine villages.',
    highlights: ['Jungfraujoch Top of Europe', 'Matterhorn Viewpoints', 'Interlaken Paragliding', 'Glacier Express Scenic Rail'],
  },
  {
    id: 'bali',
    name: 'Bali, Indonesia',
    country: 'Indonesia',
    vibe: 'Nature',
    vibeTag: '🌲 Nature & Tropical',
    photo: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=700&q=80',
    rating: 4.8,
    reviews: 620,
    budget: '$75/day',
    bestTime: 'April to October',
    duration: '5-10 Days',
    description:
      'An Indonesian paradise known for its forested volcanic mountains, iconic rice paddies, spiritual Hindu temples, and coral reefs.',
    highlights: ['Tegallalang Rice Terraces', 'Uluwatu Cliff Sunset Temple', 'Ubud Art & Yoga Sanctuary', 'Nusa Penida Coastal Day Trip'],
  },
  {
    id: 'paris',
    name: 'Paris, France',
    country: 'France',
    vibe: 'Cultural',
    vibeTag: '🏛️ Art & Gastronomy',
    photo: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=700&q=80',
    rating: 4.7,
    reviews: 730,
    budget: '$210/day',
    bestTime: 'June–August or Sep–Oct',
    duration: '3-6 Days',
    description:
      'France’s capital is a global center for art, fashion, gastronomy, and culture with iconic 19th-century cityscape crisscrossed by wide boulevards and the River Seine.',
    highlights: ['Louvre Museum & Tuileries', 'Eiffel Tower Sunset Picnic', 'Montmartre & Sacré-Cœur', 'Seine River Evening Cruise'],
  },
];

const VIBE_FILTERS = [
  { id: 'all', label: 'All Destinations' },
  { id: 'beach', label: '🏖️ Beach' },
  { id: 'mountain', label: '🏔️ Mountain' },
  { id: 'cultural', label: '🏛️ Cultural' },
  { id: 'nature', label: '🌲 Nature' },
];

export default function ExploreDestinations({ onStartPlanningDestination }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVibe, setSelectedVibe] = useState('all');
  const [activeModalDest, setActiveModalDest] = useState(null);

  const filteredDestinations = DESTINATIONS.filter((d) => {
    const matchesSearch =
      d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesVibe =
      selectedVibe === 'all' || d.vibe.toLowerCase() === selectedVibe.toLowerCase();
    return matchesSearch && matchesVibe;
  });

  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: 'calc(100vh - 4.25rem)', padding: '2.5rem 1.5rem 5rem' }}>
      <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: '#eff6ff',
              color: '#1d4ed8',
              borderRadius: '9999px',
              padding: '0.25rem 0.75rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              marginBottom: '0.5rem',
            }}
          >
            <Compass size={14} /> Global Destination Directory
          </div>
          <h1
            style={{
              fontSize: '2.25rem',
              fontWeight: 800,
              color: '#0f172a',
              margin: '0 0 0.5rem',
              letterSpacing: '-0.025em',
            }}
          >
            Explore Destinations
          </h1>
          <p style={{ fontSize: '0.95rem', color: '#64748b', maxWidth: '580px', margin: '0 auto' }}>
            Browse trending vacation spots, review daily budgets, and click any destination to immediately generate an AI itinerary.
          </p>
        </div>

        {/* Search & Vibe Filters Bar matching PDF */}
        <div
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            border: '1px solid #e2e8f0',
            padding: '1.25rem',
            marginBottom: '2rem',
            boxShadow: '0 2px 10px rgba(15, 23, 42, 0.04)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          {/* Search Input */}
          <div style={{ position: 'relative' }}>
            <Search
              size={18}
              color="#94a3b8"
              style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }}
            />
            <input
              type="text"
              placeholder="Search destinations by name, region, or attraction..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '0.85rem 1rem 0.85rem 2.8rem',
                borderRadius: '10px',
                border: '1px solid #cbd5e1',
                fontSize: '0.95rem',
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Vibe Pills Filter */}
          <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
            {VIBE_FILTERS.map((f) => {
              const isSelected = selectedVibe === f.id;
              return (
                <button
                  key={f.id}
                  onClick={() => setSelectedVibe(f.id)}
                  style={{
                    backgroundColor: isSelected ? '#eff6ff' : '#f8fafc',
                    color: isSelected ? '#1d4ed8' : '#475569',
                    border: isSelected ? '1px solid #3b82f6' : '1px solid #e2e8f0',
                    borderRadius: '9999px',
                    padding: '0.45rem 1rem',
                    fontSize: '0.85rem',
                    fontWeight: isSelected ? 700 : 500,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {f.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Destination Cards Grid matching PDF Page 5 & 6 ───────────── */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.75rem',
          }}
        >
          {filteredDestinations.map((dest) => (
            <div
              key={dest.id}
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '18px',
                border: '1px solid #e2e8f0',
                overflow: 'hidden',
                boxShadow: '0 4px 15px -2px rgba(15, 23, 42, 0.05)',
                transition: 'all 0.25s ease',
                display: 'flex',
                flexDirection: 'column',
              }}
              className="card-hover"
            >
              {/* Photo & Badges */}
              <div style={{ position: 'relative', height: '190px' }}>
                <img
                  src={dest.photo}
                  alt={dest.name}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                <div
                  style={{
                    position: 'absolute',
                    top: '0.75rem',
                    right: '0.75rem',
                    backgroundColor: 'rgba(15, 23, 42, 0.75)',
                    backdropFilter: 'blur(4px)',
                    color: '#ffffff',
                    padding: '0.25rem 0.65rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                  }}
                >
                  <Star size={13} fill="#f59e0b" color="#f59e0b" />
                  <span>{dest.rating}</span>
                </div>

                <div
                  style={{
                    position: 'absolute',
                    bottom: '0.75rem',
                    left: '0.75rem',
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    padding: '0.25rem 0.65rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: '#1d4ed8',
                  }}
                >
                  {dest.vibeTag}
                </div>
              </div>

              {/* Body */}
              <div style={{ padding: '1.35rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                    {dest.name}
                  </h3>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#16a34a' }}>
                    {dest.budget}
                  </span>
                </div>

                <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: 1.5, margin: '0 0 1rem', flex: 1 }}>
                  {dest.description}
                </p>

                <div style={{ display: 'flex', gap: '0.65rem' }}>
                  <button
                    onClick={() => setActiveModalDest(dest)}
                    style={{
                      flex: 1,
                      backgroundColor: '#f8fafc',
                      border: '1px solid #cbd5e1',
                      borderRadius: '10px',
                      padding: '0.65rem',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      color: '#334155',
                      cursor: 'pointer',
                    }}
                  >
                    View Details
                  </button>

                  <button
                    onClick={() => {
                      if (onStartPlanningDestination) {
                        onStartPlanningDestination(dest.name);
                      }
                    }}
                    style={{
                      flex: 1.2,
                      backgroundColor: '#2563eb',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '10px',
                      padding: '0.65rem',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.35rem',
                    }}
                  >
                    <span>Plan Trip</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── DESTINATION DETAILS & NAVIGATION PLAN MODAL matching PDF Page 6 */}
      {activeModalDest && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            backdropFilter: 'blur(5px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '1rem',
          }}
          onClick={() => setActiveModalDest(null)}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '24px',
              maxWidth: '680px',
              width: '100%',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              overflow: 'hidden',
              position: 'relative',
              maxHeight: '90vh',
              overflowY: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              onClick={() => setActiveModalDest(null)}
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                border: 'none',
                borderRadius: '50%',
                width: '2rem',
                height: '2rem',
                color: '#ffffff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 10,
              }}
            >
              <X size={16} />
            </button>

            {/* Hero Image */}
            <div style={{ position: 'relative', height: '260px' }}>
              <img
                src={activeModalDest.photo}
                alt={activeModalDest.name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(to top, rgba(15, 23, 42, 0.85) 0%, transparent 60%)',
                }}
              />
              <div style={{ position: 'absolute', bottom: '1.25rem', left: '1.5rem', right: '1.5rem', color: '#ffffff' }}>
                <span
                  style={{
                    backgroundColor: '#2563eb',
                    padding: '0.25rem 0.65rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    display: 'inline-block',
                    marginBottom: '0.4rem',
                  }}
                >
                  {activeModalDest.vibeTag}
                </span>
                <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: '0 0 0.25rem' }}>
                  {activeModalDest.name}
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.85rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Star size={14} fill="#f59e0b" color="#f59e0b" /> {activeModalDest.rating} ({activeModalDest.reviews} traveler reviews)
                  </span>
                </div>
              </div>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.75rem' }}>
              <p style={{ fontSize: '0.95rem', color: '#334155', lineHeight: 1.6, margin: '0 0 1.5rem' }}>
                {activeModalDest.description}
              </p>

              {/* Key Logistics Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '1rem',
                  backgroundColor: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '14px',
                  padding: '1rem',
                  marginBottom: '1.5rem',
                  textAlign: 'center',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>BEST TIME</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a', marginTop: '0.2rem' }}>
                    {activeModalDest.bestTime}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>AVG BUDGET</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#16a34a', marginTop: '0.2rem' }}>
                    {activeModalDest.budget}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>DURATION</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a', marginTop: '0.2rem' }}>
                    {activeModalDest.duration}
                  </div>
                </div>
              </div>

              {/* Highlights */}
              <div style={{ marginBottom: '1.75rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.75rem' }}>
                  Must-See Attractions &amp; Highlights
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.65rem' }}>
                  {activeModalDest.highlights.map((h, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.45rem',
                        fontSize: '0.88rem',
                        color: '#334155',
                      }}
                    >
                      <CheckCircle2 size={16} color="#2563eb" />
                      <span>{h}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* CTA Button */}
              <button
                onClick={() => {
                  const destName = activeModalDest.name;
                  setActiveModalDest(null);
                  if (onStartPlanningDestination) {
                    onStartPlanningDestination(destName);
                  }
                }}
                style={{
                  width: '100%',
                  backgroundColor: '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '12px',
                  padding: '0.9rem',
                  fontSize: '1rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  boxShadow: '0 6px 18px rgba(37, 99, 235, 0.3)',
                }}
              >
                <Sparkles size={18} />
                <span>Start Planning This Trip</span>
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

