// frontend/src/components/DashboardView.jsx
// Overview Dashboard matching Page 2 of the PDF reference

import React, { useState, useEffect } from 'react';
import {
  Compass,
  MapPin,
  Calendar,
  Sparkles,
  Bookmark,
  PlusCircle,
  ArrowRight,
  TrendingUp,
  Clock,
  Shield,
  Trash2,
  Share2,
  Download,
  Luggage,
  CheckCircle2,
} from 'lucide-react';
import tripsAPI from '../services/tripsAPI';

export default function DashboardView({
  onSelectTrip,
  onPlanNewTrip,
  onExploreDestinations,
  onViewSavedPlaces,
  savedTripsCount = 0,
  savedPlacesCount = 0,
  currentUser = { name: 'Alex Johnson', initials: 'AJ' },
}) {
  const [trips, setTrips] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Default destination photo mapping
  const getDestinationPhoto = (destination = '') => {
    const dest = destination.toLowerCase();
    if (dest.includes('kyoto') || dest.includes('japan')) {
      return 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=700&q=80';
    }
    if (dest.includes('paris') || dest.includes('france')) {
      return 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=700&q=80';
    }
    if (dest.includes('amalfi') || dest.includes('italy') || dest.includes('rome')) {
      return 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=700&q=80';
    }
    if (dest.includes('bali') || dest.includes('indonesia')) {
      return 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=700&q=80';
    }
    if (dest.includes('swiss') || dest.includes('alps') || dest.includes('switzerland')) {
      return 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=700&q=80';
    }
    if (dest.includes('manali') || dest.includes('india') || dest.includes('himalaya')) {
      return 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=700&q=80';
    }
    return 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=700&q=80';
  };

  useEffect(() => {
    let isMounted = true;
    const fetchTrips = async () => {
      setIsLoading(true);
      try {
        const data = await tripsAPI.getAllTrips();
        if (isMounted && Array.isArray(data)) {
          setTrips(data);
        }
      } catch (err) {
        console.error('Failed to load trips for dashboard', err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    fetchTrips();
    return () => {
      isMounted = false;
    };
  }, []);

  const featuredDestinations = [
    {
      name: 'Kyoto, Japan',
      vibe: 'Cultural & Zen',
      photo: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80',
      rating: '4.9 ★',
      budget: '$180/day',
    },
    {
      name: 'Amalfi Coast, Italy',
      vibe: 'Scenic & Romantic',
      photo: 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=600&q=80',
      rating: '4.8 ★',
      budget: '$260/day',
    },
    {
      name: 'Swiss Alps, Switzerland',
      vibe: 'Adventure & Nature',
      photo: 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=600&q=80',
      rating: '4.9 ★',
      budget: '$240/day',
    },
  ];

  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: 'calc(100vh - 4.25rem)', padding: '2rem 1.5rem 4rem' }}>
      <div style={{ maxWidth: '1240px', margin: '0 auto' }}>
        {/* ── Welcome Banner matching PDF reference ───────────────────── */}
        <div
          style={{
            background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
            border: '1px solid #e2e8f0',
            borderRadius: '20px',
            padding: '2rem 2.25rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 20px -2px rgba(15, 23, 42, 0.05)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1.5rem',
          }}
        >
          <div>
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
                marginBottom: '0.75rem',
              }}
            >
              <Sparkles size={14} /> AI Travel Concierge Active
            </div>
            <h1
              style={{
                fontSize: 'clamp(1.75rem, 3vw, 2.25rem)',
                fontWeight: 800,
                color: '#0f172a',
                margin: '0 0 0.5rem',
                letterSpacing: '-0.025em',
              }}
            >
              Welcome back, {currentUser?.name?.split(' ')[0] || 'Traveler'}! 👋
            </h1>
            <p style={{ fontSize: '0.95rem', color: '#64748b', margin: 0, maxWidth: '580px', lineHeight: 1.5 }}>
              Ready to embark on your next journey? Browse your saved itineraries, optimize routes, or build a new
              adventure tailored to your vibe.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              onClick={onPlanNewTrip}
              style={{
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '12px',
                padding: '0.8rem 1.4rem',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                boxShadow: '0 4px 14px rgba(37, 99, 235, 0.3)',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#1d4ed8')}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#2563eb')}
            >
              <PlusCircle size={18} />
              <span>Plan New Trip</span>
            </button>
            <button
              onClick={onExploreDestinations}
              style={{
                backgroundColor: '#ffffff',
                color: '#1e293b',
                border: '1px solid #cbd5e1',
                borderRadius: '12px',
                padding: '0.8rem 1.25rem',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
              }}
            >
              <Compass size={18} color="#2563eb" />
              <span>Explore Places</span>
            </button>
          </div>
        </div>

        {/* ── Metric Summary Cards ────────────────────────────────────── */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1.25rem',
            marginBottom: '2.5rem',
          }}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '16px',
              padding: '1.4rem',
              border: '1px solid #e2e8f0',
              boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
            }}
          >
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '12px',
                backgroundColor: '#eff6ff',
                color: '#2563eb',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Luggage size={22} />
            </div>
            <div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>
                {trips.length || savedTripsCount || 0}
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: 500 }}>Active Itineraries</div>
            </div>
          </div>

          <div
            onClick={onViewSavedPlaces}
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '16px',
              padding: '1.4rem',
              border: '1px solid #e2e8f0',
              boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#93c5fd')}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#e2e8f0')}
          >
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '12px',
                backgroundColor: '#fef3c7',
                color: '#d97706',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Bookmark size={22} />
            </div>
            <div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>
                {savedPlacesCount || 12}
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: 500 }}>Saved Places</div>
            </div>
          </div>

          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '16px',
              padding: '1.4rem',
              border: '1px solid #e2e8f0',
              boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
            }}
          >
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '12px',
                backgroundColor: '#ecfdf5',
                color: '#059669',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <MapPin size={22} />
            </div>
            <div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>8</div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: 500 }}>Destinations Explored</div>
            </div>
          </div>

          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '16px',
              padding: '1.4rem',
              border: '1px solid #e2e8f0',
              boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
            }}
          >
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: '12px',
                backgroundColor: '#f5f3ff',
                color: '#7c3aed',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Sparkles size={22} />
            </div>
            <div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>100%</div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: 500 }}>AI Route Optimized</div>
            </div>
          </div>
        </div>

        {/* ── "Your Itineraries" Section matching PDF reference ────────── */}
        <div style={{ marginBottom: '3rem' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1.25rem',
            }}
          >
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.25rem' }}>
                Your Itineraries
              </h2>
              <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
                Manage, customize, and export your upcoming and past travel plans.
              </p>
            </div>

            {trips.length > 0 && (
              <button
                onClick={onPlanNewTrip}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  color: '#2563eb',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                <span>+ Create New</span>
              </button>
            )}
          </div>

          {isLoading ? (
            <div
              style={{
                padding: '3rem',
                textAlign: 'center',
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                color: '#64748b',
              }}
            >
              <Sparkles size={28} className="spin" color="#2563eb" style={{ margin: '0 auto 1rem' }} />
              <div>Loading your itineraries...</div>
            </div>
          ) : trips.length === 0 ? (
            /* Empty State */
            <div
              style={{
                padding: '3.5rem 2rem',
                textAlign: 'center',
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                border: '1px dashed #cbd5e1',
              }}
            >
              <div
                style={{
                  width: '4rem',
                  height: '4rem',
                  borderRadius: '50%',
                  backgroundColor: '#eff6ff',
                  color: '#2563eb',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '1rem',
                  fontSize: '1.75rem',
                }}
              >
                ✈️
              </div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.5rem' }}>
                No travel itineraries yet
              </h3>
              <p style={{ fontSize: '0.9rem', color: '#64748b', maxWidth: '440px', margin: '0 auto 1.5rem' }}>
                Create your very first personalized itinerary with our 3-step AI builder. Choose your destination, vibe,
                and budget!
              </p>
              <button
                onClick={onPlanNewTrip}
                style={{
                  backgroundColor: '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '0.75rem 1.5rem',
                  fontSize: '0.92rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Start Planning Now
              </button>
            </div>
          ) : (
            /* Trips Grid matching PDF cards */
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: '1.5rem',
              }}
            >
              {trips.map((trip) => {
                const photoUrl = getDestinationPhoto(trip.destination);
                return (
                  <div
                    key={trip.id}
                    style={{
                      backgroundColor: '#ffffff',
                      borderRadius: '16px',
                      border: '1px solid #e2e8f0',
                      overflow: 'hidden',
                      boxShadow: '0 4px 15px -2px rgba(15, 23, 42, 0.05)',
                      transition: 'all 0.25s ease',
                      display: 'flex',
                      flexDirection: 'column',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-3px)';
                      e.currentTarget.style.boxShadow = '0 12px 25px -4px rgba(37, 99, 235, 0.12)';
                      e.currentTarget.style.borderColor = '#bfdbfe';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 4px 15px -2px rgba(15, 23, 42, 0.05)';
                      e.currentTarget.style.borderColor = '#e2e8f0';
                    }}
                  >
                    {/* Card Cover Image */}
                    <div style={{ position: 'relative', height: '175px', overflow: 'hidden' }}>
                      <img
                        src={photoUrl}
                        alt={trip.destination}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                      <div
                        style={{
                          position: 'absolute',
                          top: '0.75rem',
                          right: '0.75rem',
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          backdropFilter: 'blur(4px)',
                          color: '#1d4ed8',
                          padding: '0.25rem 0.65rem',
                          borderRadius: '9999px',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                        }}
                      >
                        {trip.status || 'Active Plan'}
                      </div>
                      <div
                        style={{
                          position: 'absolute',
                          bottom: '0.75rem',
                          left: '0.75rem',
                          backgroundColor: 'rgba(15, 23, 42, 0.75)',
                          backdropFilter: 'blur(4px)',
                          color: '#ffffff',
                          padding: '0.25rem 0.65rem',
                          borderRadius: '6px',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.3rem',
                        }}
                      >
                        <Sparkles size={12} /> {trip.primary_vibe || 'Cultural'} Vibe
                      </div>
                    </div>

                    {/* Card Content */}
                    <div style={{ padding: '1.25rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                        <h3
                          style={{
                            fontSize: '1.15rem',
                            fontWeight: 700,
                            color: '#0f172a',
                            margin: 0,
                          }}
                        >
                          {trip.title || trip.destination}
                        </h3>
                        {trip.budget && (
                          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#16a34a' }}>
                            ${trip.budget}
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#64748b', fontSize: '0.82rem', marginBottom: '0.85rem' }}>
                        <Calendar size={14} />
                        <span>
                          {trip.start_date || 'Upcoming'} &bull; {trip.num_travelers || 1} Traveler
                          {trip.num_travelers > 1 ? 's' : ''}
                        </span>
                      </div>

                      <div style={{ marginTop: 'auto', paddingTop: '0.75rem', borderTop: '1px solid #f1f5f9' }}>
                        <button
                          onClick={() => onSelectTrip(trip)}
                          style={{
                            width: '100%',
                            backgroundColor: '#eff6ff',
                            color: '#1d4ed8',
                            border: '1px solid #bfdbfe',
                            borderRadius: '10px',
                            padding: '0.65rem 1rem',
                            fontSize: '0.88rem',
                            fontWeight: 600,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.45rem',
                            transition: 'all 0.15s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#2563eb';
                            e.currentTarget.style.color = '#ffffff';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#eff6ff';
                            e.currentTarget.style.color = '#1d4ed8';
                          }}
                        >
                          <span>View Full Itinerary</span>
                          <ArrowRight size={15} />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ── Trending Destinations Section ───────────────────────────── */}
        <div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1.25rem',
            }}
          >
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.25rem' }}>
                Trending Destinations
              </h2>
              <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
                Curated global hotspots ready for instant AI itinerary generation.
              </p>
            </div>
            <button
              onClick={onExploreDestinations}
              style={{
                fontSize: '0.88rem',
                fontWeight: 600,
                color: '#2563eb',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem',
              }}
            >
              <span>Explore All</span>
              <ArrowRight size={15} />
            </button>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {featuredDestinations.map((dest, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '16px',
                  border: '1px solid #e2e8f0',
                  overflow: 'hidden',
                  boxShadow: '0 4px 12px rgba(15, 23, 42, 0.04)',
                }}
              >
                <div style={{ position: 'relative', height: '160px' }}>
                  <img src={dest.photo} alt={dest.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  <div
                    style={{
                      position: 'absolute',
                      top: '0.65rem',
                      right: '0.65rem',
                      backgroundColor: 'rgba(15, 23, 42, 0.75)',
                      color: '#ffffff',
                      borderRadius: '9999px',
                      padding: '0.2rem 0.55rem',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                    }}
                  >
                    {dest.rating}
                  </div>
                </div>

                <div style={{ padding: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4 style={{ margin: '0 0 0.25rem', fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>
                      {dest.name}
                    </h4>
                    <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#2563eb' }}>{dest.budget}</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.75rem' }}>{dest.vibe}</div>
                  <button
                    onClick={() => {
                      // Trigger plan trip with prefilled destination
                      onPlanNewTrip(dest.name);
                    }}
                    style={{
                      width: '100%',
                      backgroundColor: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      padding: '0.55rem',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      color: '#1e293b',
                      cursor: 'pointer',
                    }}
                  >
                    Plan Itinerary &rarr;
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

