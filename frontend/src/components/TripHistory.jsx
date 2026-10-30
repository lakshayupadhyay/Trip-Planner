// frontend/src/components/TripHistory.jsx
// Trip Activity & History Timeline matching Page 7 of the PDF reference

import React, { useState, useEffect } from 'react';
import {
  History,
  Calendar,
  MapPin,
  Clock,
  Trash2,
  Share2,
  Download,
  ArrowRight,
  Sparkles,
  Luggage,
  CheckCircle2,
  AlertCircle,
  PlusCircle,
} from 'lucide-react';
import tripsAPI from '../services/tripsAPI';

export default function TripHistory({
  onSelectTrip,
  onPlanNewTrip,
  onOpenShareModal,
}) {
  const [trips, setTrips] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const getDestinationPhoto = (dest) => {
    const d = (dest || '').toLowerCase();
    if (d.includes('kyoto') || d.includes('japan')) {
      return 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80';
    }
    if (d.includes('paris') || d.includes('france')) {
      return 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=600&q=80';
    }
    if (d.includes('amalfi') || d.includes('italy')) {
      return 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=600&q=80';
    }
    if (d.includes('swiss') || d.includes('alps')) {
      return 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=600&q=80';
    }
    if (d.includes('bali') || d.includes('indonesia')) {
      return 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=600&q=80';
    }
    if (d.includes('manali') || d.includes('india')) {
      return 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80';
    }
    return 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80';
  };

  const loadTrips = async () => {
    setIsLoading(true);
    try {
      const data = await tripsAPI.getAllTrips();
      if (Array.isArray(data)) {
        setTrips(data);
      }
    } catch (err) {
      console.error('Failed to load trips history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTrips();
  }, []);

  const handleDeleteTrip = async (tripId) => {
    try {
      await tripsAPI.deleteTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
      setDeleteConfirmId(null);
    } catch (err) {
      alert('Failed to delete trip: ' + err.message);
    }
  };

  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: 'calc(100vh - 4.25rem)', padding: '2.5rem 1.5rem 5rem' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
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
                backgroundColor: '#eff6ff',
                color: '#1d4ed8',
                borderRadius: '9999px',
                padding: '0.25rem 0.75rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                marginBottom: '0.5rem',
              }}
            >
              <History size={14} /> Comprehensive Trip Ledger
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
              Trip Activity &amp; History
            </h1>
            <p style={{ fontSize: '0.95rem', color: '#64748b', margin: 0 }}>
              Review past itineraries, check optimization statuses, and export PDF itineraries for your travel binder.
            </p>
          </div>

          <button
            onClick={onPlanNewTrip}
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
            <PlusCircle size={16} />
            <span>Create New Trip</span>
          </button>
        </div>

        {/* Trips Timeline / Table List */}
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
            <div>Loading trip history...</div>
          </div>
        ) : trips.length === 0 ? (
          <div
            style={{
              padding: '3.5rem 2rem',
              textAlign: 'center',
              backgroundColor: '#ffffff',
              borderRadius: '16px',
              border: '1px dashed #cbd5e1',
            }}
          >
            <Luggage size={36} color="#94a3b8" style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.5rem' }}>
              No trips recorded yet
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#64748b', maxWidth: '420px', margin: '0 auto 1.5rem' }}>
              When you design or generate travel plans, your full trip timeline and export history will appear here.
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
              Plan Your First Trip
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {trips.map((trip) => {
              const photoUrl = getDestinationPhoto(trip.destination);
              return (
                <div
                  key={trip.id}
                  style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '16px',
                    border: '1px solid #e2e8f0',
                    padding: '1.25rem 1.5rem',
                    boxShadow: '0 2px 8px rgba(15, 23, 42, 0.03)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '1.25rem',
                    transition: 'all 0.2s ease',
                  }}
                  className="card-hover"
                >
                  {/* Left: Thumbnail & Details */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', minWidth: '260px' }}>
                    <img
                      src={photoUrl}
                      alt={trip.destination}
                      style={{
                        width: '72px',
                        height: '72px',
                        borderRadius: '12px',
                        objectFit: 'cover',
                      }}
                    />
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                          {trip.title || trip.destination}
                        </h3>
                        <span
                          style={{
                            backgroundColor: '#dcfce7',
                            color: '#15803d',
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            padding: '0.15rem 0.5rem',
                            borderRadius: '9999px',
                            textTransform: 'uppercase',
                          }}
                        >
                          {trip.status || 'Active'}
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.82rem', color: '#64748b' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <Calendar size={13} /> {trip.start_date || 'Upcoming'}
                        </span>
                        <span>&bull;</span>
                        <span>{trip.num_travelers || 1} Traveler(s)</span>
                        {trip.budget && (
                          <>
                            <span>&bull;</span>
                            <span style={{ fontWeight: 600, color: '#16a34a' }}>${trip.budget}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right: Action Buttons */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                    <button
                      onClick={() => onSelectTrip(trip)}
                      style={{
                        backgroundColor: '#eff6ff',
                        color: '#1d4ed8',
                        border: '1px solid #bfdbfe',
                        borderRadius: '10px',
                        padding: '0.55rem 1rem',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                      }}
                    >
                      <span>View Itinerary</span>
                      <ArrowRight size={14} />
                    </button>

                    {deleteConfirmId === trip.id ? (
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        <button
                          onClick={() => handleDeleteTrip(trip.id)}
                          style={{
                            backgroundColor: '#ef4444',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '0.55rem 0.85rem',
                            fontSize: '0.8rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                          }}
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setDeleteConfirmId(null)}
                          style={{
                            backgroundColor: '#f1f5f9',
                            color: '#475569',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '0.55rem 0.85rem',
                            fontSize: '0.8rem',
                            cursor: 'pointer',
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setDeleteConfirmId(trip.id)}
                        style={{
                          backgroundColor: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '10px',
                          padding: '0.55rem',
                          color: '#94a3b8',
                          cursor: 'pointer',
                        }}
                        title="Delete Trip"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

