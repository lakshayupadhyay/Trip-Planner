// frontend/src/components/SavedPlaces.jsx
// Saved Places Manager matching Pages 6 & 7 of the PDF reference

import React, { useState } from 'react';
import {
  Bookmark,
  MapPin,
  Star,
  Clock,
  Plus,
  Trash2,
  ExternalLink,
  Sparkles,
  ArrowRight,
  Filter,
} from 'lucide-react';

const INITIAL_SAVED_PLACES = [
  {
    id: 1,
    name: 'Fushimi Inari Shrine',
    destination: 'Kyoto, Japan',
    category: 'Attraction',
    photo: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80',
    rating: 4.9,
    duration: '2.5 hrs',
    note: 'Hike all the way up through the 10,000 torii gates early morning.',
  },
  {
    id: 2,
    name: 'Positano Cliffside Viewpoint',
    destination: 'Amalfi Coast, Italy',
    category: 'Scenic View',
    photo: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=600&q=80',
    rating: 4.8,
    duration: '1 hr',
    note: 'Spectacular sunset angle overlooking Spiaggia Grande beach.',
  },
  {
    id: 3,
    name: 'Solang Valley Pine Forest',
    destination: 'Manali, India',
    category: 'Attraction',
    photo: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80',
    rating: 4.9,
    duration: '3 hrs',
    note: 'Paragliding & zorbing hub surrounded by Himalayan snow peaks.',
  },
  {
    id: 4,
    name: 'Le Comptoir du Relais',
    destination: 'Paris, France',
    category: 'Dining',
    photo: 'https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=600&q=80',
    rating: 4.7,
    duration: '1.5 hrs',
    note: 'Legendary Saint-Germain bistro for classic beef bourguignon.',
  },
  {
    id: 5,
    name: 'Tegallalang Rice Terraces',
    destination: 'Bali, Indonesia',
    category: 'Scenic View',
    photo: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=600&q=80',
    rating: 4.8,
    duration: '2 hrs',
    note: 'Lush green stepped hillsides with jungle swing photo spots.',
  },
  {
    id: 6,
    name: 'Jungfraujoch Sphinx Observatory',
    destination: 'Swiss Alps, Switzerland',
    category: 'Attraction',
    photo: 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=600&q=80',
    rating: 4.9,
    duration: '4 hrs',
    note: 'Europe’s highest railway station with views over Aletsch Glacier.',
  },
];

const CATEGORIES = ['All', 'Attraction', 'Dining', 'Scenic View', 'Hotel'];

export default function SavedPlaces({ onPlanDestination }) {
  const [places, setPlaces] = useState(INITIAL_SAVED_PLACES);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [newPlaceName, setNewPlaceName] = useState('');
  const [newPlaceCity, setNewPlaceCity] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  const filteredPlaces = places.filter((p) => {
    if (selectedCategory === 'All') return true;
    return p.category.toLowerCase() === selectedCategory.toLowerCase();
  });

  const handleRemove = (id) => {
    setPlaces((prev) => prev.filter((p) => p.id !== id));
  };

  const handleAddPlace = (e) => {
    e.preventDefault();
    if (!newPlaceName.trim()) return;

    const newPlace = {
      id: Date.now(),
      name: newPlaceName.trim(),
      destination: newPlaceCity.trim() || 'Global Spot',
      category: 'Attraction',
      photo: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80',
      rating: 4.8,
      duration: '1-2 hrs',
      note: 'Added to your travel wishlist.',
    };

    setPlaces([newPlace, ...places]);
    setNewPlaceName('');
    setNewPlaceCity('');
    setShowAddForm(false);
  };

  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: 'calc(100vh - 4.25rem)', padding: '2.5rem 1.5rem 5rem' }}>
      <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '2rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                backgroundColor: '#fef3c7',
                color: '#d97706',
                borderRadius: '9999px',
                padding: '0.25rem 0.75rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                marginBottom: '0.5rem',
              }}
            >
              <Bookmark size={14} /> {places.length} Places Bookmarked
            </div>
            <h1
              style={{
                fontSize: '2.25rem',
                fontWeight: 800,
                color: '#0f172a',
                margin: '0 0 0.4rem',
                letterSpacing: '-0.025em',
              }}
            >
              Saved Places
            </h1>
            <p style={{ fontSize: '0.95rem', color: '#64748b', margin: 0 }}>
              Your personal travel bookmarks. Seamlessly incorporate these into your next trip itinerary.
            </p>
          </div>

          <button
            onClick={() => setShowAddForm(!showAddForm)}
            style={{
              backgroundColor: '#2563eb',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              padding: '0.75rem 1.25rem',
              fontSize: '0.92rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.25)',
            }}
          >
            <Plus size={16} />
            <span>Add Saved Place</span>
          </button>
        </div>

        {/* Add Form */}
        {showAddForm && (
          <form
            onSubmit={handleAddPlace}
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #bfdbfe',
              borderRadius: '16px',
              padding: '1.5rem',
              marginBottom: '2rem',
              display: 'flex',
              gap: '1rem',
              flexWrap: 'wrap',
              alignItems: 'flex-end',
            }}
          >
            <div style={{ flex: 1, minWidth: '220px' }}>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                Place Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Louvre Museum"
                value={newPlaceName}
                onChange={(e) => setNewPlaceName(e.target.value)}
                style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', border: '1px solid #cbd5e1', outline: 'none' }}
              />
            </div>
            <div style={{ flex: 1, minWidth: '200px' }}>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                City / Destination
              </label>
              <input
                type="text"
                placeholder="e.g. Paris, France"
                value={newPlaceCity}
                onChange={(e) => setNewPlaceCity(e.target.value)}
                style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', border: '1px solid #cbd5e1', outline: 'none' }}
              />
            </div>
            <button
              type="submit"
              style={{
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.65rem 1.25rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Save Place
            </button>
          </form>
        )}

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
          {CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  backgroundColor: isSelected ? '#eff6ff' : '#ffffff',
                  color: isSelected ? '#1d4ed8' : '#475569',
                  border: isSelected ? '1px solid #3b82f6' : '1px solid #e2e8f0',
                  borderRadius: '9999px',
                  padding: '0.45rem 1rem',
                  fontSize: '0.85rem',
                  fontWeight: isSelected ? 700 : 500,
                  cursor: 'pointer',
                }}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* Places Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '1.5rem',
          }}
        >
          {filteredPlaces.map((place) => (
            <div
              key={place.id}
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                overflow: 'hidden',
                boxShadow: '0 4px 12px rgba(15, 23, 42, 0.04)',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <div style={{ position: 'relative', height: '160px' }}>
                <img src={place.photo} alt={place.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                <button
                  onClick={() => handleRemove(place.id)}
                  style={{
                    position: 'absolute',
                    top: '0.65rem',
                    right: '0.65rem',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '2rem',
                    height: '2rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ef4444',
                    cursor: 'pointer',
                  }}
                  title="Remove bookmark"
                >
                  <Trash2 size={14} />
                </button>
                <div
                  style={{
                    position: 'absolute',
                    bottom: '0.65rem',
                    left: '0.65rem',
                    backgroundColor: 'rgba(15, 23, 42, 0.75)',
                    color: '#ffffff',
                    padding: '0.2rem 0.55rem',
                    borderRadius: '6px',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                  }}
                >
                  {place.category}
                </div>
              </div>

              <div style={{ padding: '1.25rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                    {place.name}
                  </h3>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                    <Star size={13} fill="#f59e0b" /> {place.rating}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#64748b', fontSize: '0.82rem', marginBottom: '0.65rem' }}>
                  <MapPin size={13} />
                  <span>{place.destination}</span>
                </div>

                {place.note && (
                  <p style={{ fontSize: '0.82rem', color: '#475569', fontStyle: 'italic', margin: '0 0 1rem', flex: 1 }}>
                    &ldquo;{place.note}&rdquo;
                  </p>
                )}

                <button
                  onClick={() => {
                    if (onPlanDestination) {
                      onPlanDestination(place.destination);
                    }
                  }}
                  style={{
                    marginTop: 'auto',
                    backgroundColor: '#eff6ff',
                    color: '#1d4ed8',
                    border: '1px solid #bfdbfe',
                    borderRadius: '8px',
                    padding: '0.55rem',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem',
                  }}
                >
                  <Sparkles size={14} />
                  <span>Plan into Itinerary</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

