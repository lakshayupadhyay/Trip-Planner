// frontend/src/components/SharedTripView.jsx
// Public read-only view of a shared trip and its itinerary.
// Accessed via ?share=TOKEN URL parameter.
// SECURITY: No edit/delete controls. No user PII displayed.

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin,
  Calendar,
  DollarSign,
  Compass,
  Heart,
  Sunrise,
  Sun,
  Moon,
  Utensils,
  Bus,
  Lightbulb,
  Clock,
  Route,
  ArrowDown,
  Loader2,
  AlertCircle,
  Sparkles,
  Navigation,
} from 'lucide-react';
import tripsAPI from '../services/tripsAPI';
import './SharedTripView.css';

export default function SharedTripView({ shareToken }) {
  const [trip, setTrip] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const loadSharedTrip = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await tripsAPI.getSharedTrip(shareToken);
        if (!cancelled) setTrip(data);
      } catch (err) {
        if (!cancelled) setError(err.message || 'This shared trip link is invalid or has been revoked.');
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    loadSharedTrip();
    return () => { cancelled = true; };
  }, [shareToken]);

  // ── Loading ─────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="stv-center">
        <Loader2 size={36} className="stv-spin" />
        <p style={{ color: '#64748b', marginTop: '0.75rem' }}>Loading shared trip…</p>
      </div>
    );
  }

  // ── Error ───────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="stv-center">
        <AlertCircle size={36} style={{ color: '#ef4444' }} />
        <p style={{ color: '#ef4444', marginTop: '0.75rem', fontWeight: 600 }}>{error}</p>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginTop: '0.25rem' }}>
          This link may have expired or been revoked by the trip owner.
        </p>
      </div>
    );
  }

  if (!trip) return null;

  const timeSlotIcon = (slot) => {
    if (slot === 'morning') return <Sunrise size={14} className="stv-slot-icon stv-slot-morning" />;
    if (slot === 'afternoon') return <Sun size={14} className="stv-slot-icon stv-slot-afternoon" />;
    return <Moon size={14} className="stv-slot-icon stv-slot-evening" />;
  };

  return (
    <div className="stv-wrapper">
      {/* ── Hero Banner ──────────────────────────────────────────────── */}
      <motion.div
        className="stv-hero"
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="stv-hero-badge">Shared Trip Itinerary</div>
        <h1 className="stv-hero-title">
          <MapPin size={22} /> {trip.destination}
        </h1>
        <div className="stv-hero-meta">
          <span><Calendar size={14} /> {trip.start_date} — {trip.end_date}</span>
          <span><DollarSign size={14} /> ${Number(trip.total_budget).toLocaleString()} Budget</span>
          <span><Compass size={14} /> {trip.travel_pace?.charAt(0).toUpperCase() + trip.travel_pace?.slice(1)} Pace</span>
          {trip.primary_vibe && (
            <span><Heart size={14} /> {trip.primary_vibe}</span>
          )}
        </div>
        {trip.secondary_vibes?.length > 0 && (
          <div className="stv-vibes">
            {trip.secondary_vibes.map((v, i) => (
              <span key={i} className="stv-vibe-tag">{v}</span>
            ))}
          </div>
        )}
      </motion.div>

      {/* ── Trip Summary ─────────────────────────────────────────────── */}
      {trip.trip_summary && (
        <motion.div
          className="stv-summary-card"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Sparkles size={16} style={{ color: '#6366f1' }} />
          <p>{trip.trip_summary}</p>
        </motion.div>
      )}

      {/* ── Day-by-Day Itinerary ─────────────────────────────────────── */}
      {trip.days?.length > 0 ? (
        <div className="stv-days">
          {trip.days.map((day, idx) => (
            <motion.div
              key={day.day_number}
              className="stv-day-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * idx }}
            >
              <div className="stv-day-header">
                <span className="stv-day-number">Day {day.day_number}</span>
                <span className="stv-day-theme">{day.theme}</span>
                {day.date && <span className="stv-day-date">{day.date}</span>}
              </div>

              {/* Activities */}
              <div className="stv-activities">
                {/* Morning */}
                {day.morning_activity && (
                  <div className="stv-activity">
                    <div className="stv-act-header">
                      {timeSlotIcon('morning')}
                      <strong>{day.morning_activity.name}</strong>
                      {day.morning_activity.schedule && (
                        <span className="stv-time-badge">
                          <Clock size={11} /> {day.morning_activity.schedule.start_time}
                        </span>
                      )}
                    </div>
                    <p className="stv-act-desc">{day.morning_activity.description}</p>
                    <div className="stv-act-meta">
                      {day.morning_activity.location && <span><MapPin size={11} /> {day.morning_activity.location}</span>}
                      <span><Clock size={11} /> {day.morning_activity.suggested_duration}</span>
                      <span><DollarSign size={11} /> {day.morning_activity.estimated_cost}</span>
                    </div>
                  </div>
                )}

                {/* Lunch */}
                {day.lunch && (
                  <div className="stv-activity stv-dining">
                    <div className="stv-act-header">
                      <Utensils size={14} className="stv-slot-icon stv-slot-dining" />
                      <strong>{day.lunch.name}</strong>
                      <span className="stv-cuisine-tag">{day.lunch.cuisine}</span>
                    </div>
                    <p className="stv-act-desc">{day.lunch.description}</p>
                    <span className="stv-act-cost"><DollarSign size={11} /> {day.lunch.estimated_cost}</span>
                  </div>
                )}

                {/* Afternoon */}
                {day.afternoon_activity && (
                  <div className="stv-activity">
                    <div className="stv-act-header">
                      {timeSlotIcon('afternoon')}
                      <strong>{day.afternoon_activity.name}</strong>
                      {day.afternoon_activity.schedule && (
                        <span className="stv-time-badge">
                          <Clock size={11} /> {day.afternoon_activity.schedule.start_time}
                        </span>
                      )}
                    </div>
                    <p className="stv-act-desc">{day.afternoon_activity.description}</p>
                    <div className="stv-act-meta">
                      {day.afternoon_activity.location && <span><MapPin size={11} /> {day.afternoon_activity.location}</span>}
                      <span><Clock size={11} /> {day.afternoon_activity.suggested_duration}</span>
                      <span><DollarSign size={11} /> {day.afternoon_activity.estimated_cost}</span>
                    </div>
                  </div>
                )}

                {/* Dinner */}
                {day.dinner && (
                  <div className="stv-activity stv-dining">
                    <div className="stv-act-header">
                      <Utensils size={14} className="stv-slot-icon stv-slot-dining" />
                      <strong>{day.dinner.name}</strong>
                      <span className="stv-cuisine-tag">{day.dinner.cuisine}</span>
                    </div>
                    <p className="stv-act-desc">{day.dinner.description}</p>
                    <span className="stv-act-cost"><DollarSign size={11} /> {day.dinner.estimated_cost}</span>
                  </div>
                )}

                {/* Evening */}
                {day.evening_activity && (
                  <div className="stv-activity">
                    <div className="stv-act-header">
                      {timeSlotIcon('evening')}
                      <strong>{day.evening_activity.name}</strong>
                    </div>
                    <p className="stv-act-desc">{day.evening_activity.description}</p>
                  </div>
                )}
              </div>

              {/* Route Summary */}
              {(day.total_travel_distance_km || day.transportation) && (
                <div className="stv-route-summary">
                  {day.transportation && (
                    <span><Bus size={13} /> {day.transportation.mode} — {day.transportation.estimated_time}</span>
                  )}
                  {day.total_travel_distance_km && (
                    <span><Route size={13} /> ~{day.total_travel_distance_km.toFixed(1)} km total</span>
                  )}
                </div>
              )}

              {/* Daily Tip */}
              {day.practical_tips && (
                <div className="stv-daily-tip">
                  <Lightbulb size={13} />
                  <span>{day.practical_tips}</span>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="stv-empty">
          <p>This shared trip does not have a generated itinerary yet.</p>
        </div>
      )}

      {/* ── Packing Tips ─────────────────────────────────────────────── */}
      {trip.packing_and_prep_tips?.length > 0 && (
        <motion.div
          className="stv-packing"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h3>🎒 Packing &amp; Prep Tips</h3>
          <ul>
            {trip.packing_and_prep_tips.map((tip, i) => (
              <li key={i}>{tip}</li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer className="stv-footer">
        Generated with ✈️ Personalized Travel Planner
      </footer>
    </div>
  );
}

