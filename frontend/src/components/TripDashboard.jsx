// frontend/src/components/TripDashboard.jsx
// Activity 5.1: Trip Save & Management Dashboard
// Displays saved trips, provides editing, deletion with confirmation,
// filter & search, and direct viewing of saved itineraries.

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin,
  Calendar,
  Users,
  DollarSign,
  Sparkles,
  Edit2,
  Trash2,
  Eye,
  Plus,
  Search,
  RotateCcw,
  AlertCircle,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Compass,
  X,
} from 'lucide-react';
import tripsAPI from '../services/tripsAPI';
import { TRAVEL_VIBES } from './CreateTrip';
import './TripDashboard.css';

const TRAVEL_STYLES = [
  { value: 'cultural', label: 'Cultural' },
  { value: 'adventure', label: 'Adventure' },
  { value: 'relaxation', label: 'Relaxation' },
  { value: 'family', label: 'Family' },
  { value: 'luxury', label: 'Luxury' },
  { value: 'budget', label: 'Budget' },
];

export function TripDashboard({
  onSelectTrip = null,
  onCreateNew = null,
}) {
  const [trips, setTrips] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('all'); // 'all' | 'itinerary' | 'draft'

  // Modals state
  const [editingTrip, setEditingTrip] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateError, setUpdateError] = useState(null);

  const [deletingTrip, setDeletingTrip] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Fetch all trips on mount
  const loadTrips = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await tripsAPI.getAllTrips();
      setTrips(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || 'Failed to load saved trips.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTrips();
  }, []);

  // Filtered trips computation
  const filteredTrips = trips.filter((trip) => {
    const matchesSearch =
      !searchQuery ||
      trip.destination?.toLowerCase().includes(searchQuery.toLowerCase().strip?.() || searchQuery.toLowerCase());

    if (!matchesSearch) return false;
    if (activeFilter === 'itinerary') return Boolean(trip.has_itinerary);
    if (activeFilter === 'draft') return !trip.has_itinerary;
    return true;
  });

  // Calculate nights between dates
  const calculateDuration = (start, end) => {
    if (!start || !end) return 0;
    const diff = Math.round((new Date(end) - new Date(start)) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 1;
  };

  // Format date display
  const formatDateDisplay = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  // Handle Edit Submit
  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    if (!editingTrip) return;

    setIsUpdating(true);
    setUpdateError(null);

    const payload = {
      destination: editingTrip.destination.trim(),
      start_date: editingTrip.start_date,
      end_date: editingTrip.end_date,
      num_travelers: parseInt(editingTrip.num_travelers, 10) || 1,
      budget: parseFloat(editingTrip.budget),
      travel_style: editingTrip.travel_style,
      travel_pace: editingTrip.travel_pace,
      primary_vibe: editingTrip.primary_vibe,
      secondary_vibes: editingTrip.secondary_vibes || [],
      travel_interests: editingTrip.travel_interests || [],
      dietary_preferences: editingTrip.dietary_preferences || [],
      additional_requirements: editingTrip.additional_requirements || null,
    };

    try {
      const updated = await tripsAPI.updateTrip(editingTrip.id, payload);
      setTrips((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
      setEditingTrip(null);
    } catch (err) {
      setUpdateError(err.message || 'Failed to update trip.');
    } finally {
      setIsUpdating(false);
    }
  };

  // Handle Delete Submit
  const handleDeleteSubmit = async () => {
    if (!deletingTrip) return;
    setIsDeleting(true);

    try {
      await tripsAPI.deleteTrip(deletingTrip.id);
      setTrips((prev) => prev.filter((t) => t.id !== deletingTrip.id));
      setDeletingTrip(null);
    } catch (err) {
      alert(`Deletion failed: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="dashboard-container">
      {/* ── Dashboard Header ────────────────────────────────────────────── */}
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h2>My Saved Trips &amp; Itineraries</h2>
          <p>Manage your saved journeys, inspect day-by-day itineraries, or make edits.</p>
        </div>
        <div className="dashboard-actions">
          <button
            type="button"
            className="btn-card-action"
            onClick={loadTrips}
            title="Refresh trips list"
          >
            <RotateCcw size={14} className={isLoading ? 'spinner' : ''} /> Refresh
          </button>
          {onCreateNew && (
            <button
              type="button"
              className="btn-card-primary"
              onClick={onCreateNew}
            >
              <Plus size={16} /> Plan New Trip
            </button>
          )}
        </div>
      </div>

      {/* ── Toolbar: Search & Filters ───────────────────────────────────── */}
      <div className="dashboard-toolbar">
        <div className="search-box">
          <Search size={16} color="#94a3b8" />
          <input
            type="text"
            placeholder="Search by destination (e.g. Kyoto, Paris)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <X
              size={14}
              color="#94a3b8"
              style={{ cursor: 'pointer' }}
              onClick={() => setSearchQuery('')}
            />
          )}
        </div>

        <div className="filter-tabs">
          <button
            type="button"
            className={`filter-tab ${activeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setActiveFilter('all')}
          >
            All Trips ({trips.length})
          </button>
          <button
            type="button"
            className={`filter-tab ${activeFilter === 'itinerary' ? 'active' : ''}`}
            onClick={() => setActiveFilter('itinerary')}
          >
            With Itineraries ({trips.filter((t) => t.has_itinerary).length})
          </button>
          <button
            type="button"
            className={`filter-tab ${activeFilter === 'draft' ? 'active' : ''}`}
            onClick={() => setActiveFilter('draft')}
          >
            Drafts ({trips.filter((t) => !t.has_itinerary).length})
          </button>
        </div>
      </div>

      {/* ── Loading State ───────────────────────────────────────────────── */}
      {isLoading && (
        <div className="dashboard-loading">
          <Loader2 size={36} className="spinner" style={{ color: '#6366f1', margin: '0 auto 1rem auto' }} />
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Loading your saved trips from Supabase…</p>
        </div>
      )}

      {/* ── Error Banner ────────────────────────────────────────────────── */}
      {error && !isLoading && (
        <div className="modal-alert-warning" style={{ background: '#fef2f2', borderColor: '#fecaca', color: '#991b1b' }}>
          <AlertCircle size={18} />
          <div style={{ flex: 1 }}>
            <strong>Unable to load trips:</strong> {error}
          </div>
          <button type="button" className="btn-card-action" onClick={loadTrips}>
            Retry
          </button>
        </div>
      )}

      {/* ── Empty State ─────────────────────────────────────────────────── */}
      {!isLoading && !error && filteredTrips.length === 0 && (
        <div className="dashboard-empty">
          <Compass size={48} color="#94a3b8" />
          <h3>
            {trips.length === 0
              ? 'No Trips Saved Yet'
              : 'No Trips Match Your Search'}
          </h3>
          <p>
            {trips.length === 0
              ? 'Create your personalized journey with AI recommendations, daily schedules, and route optimization.'
              : 'Try clearing your search query or switching your filter tabs.'}
          </p>
          {trips.length === 0 && onCreateNew && (
            <button
              type="button"
              className="btn-card-primary"
              onClick={onCreateNew}
              style={{ padding: '0.6rem 1.25rem', fontSize: '0.9rem' }}
            >
              <Sparkles size={16} /> Plan Your First Trip
            </button>
          )}
        </div>
      )}

      {/* ── Trips Grid ──────────────────────────────────────────────────── */}
      {!isLoading && filteredTrips.length > 0 && (
        <div className="trips-grid">
          {filteredTrips.map((trip) => {
            const nights = calculateDuration(trip.start_date, trip.end_date);

            return (
              <motion.div
                key={trip.id}
                className="trip-card"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                {/* Header */}
                <div className="trip-card-header">
                  <h3 className="trip-destination-title">
                    <MapPin size={18} color="#6366f1" />
                    <span>{trip.destination}</span>
                  </h3>
                  <span className={`status-tag ${trip.has_itinerary ? 'ready' : 'draft'}`}>
                    {trip.has_itinerary ? '✓ Itinerary Ready' : '⏳ Draft'}
                  </span>
                </div>

                {/* Dates & Duration */}
                <div className="trip-meta-row">
                  <Calendar size={14} color="#64748b" />
                  <span>
                    {formatDateDisplay(trip.start_date)} &ndash; {formatDateDisplay(trip.end_date)} ({nights} night{nights !== 1 ? 's' : ''})
                  </span>
                </div>

                {/* Travelers & Budget */}
                <div className="trip-stats-grid">
                  <div className="stat-box">
                    <span className="stat-box-label">Travelers</span>
                    <span className="stat-box-val">
                      <Users size={12} style={{ display: 'inline', marginRight: 4 }} />
                      {trip.num_travelers || 1}
                    </span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-box-label">Total Budget</span>
                    <span className="stat-box-val">${trip.budget?.toLocaleString()} USD</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-box-label">Style</span>
                    <span className="stat-box-val" style={{ textTransform: 'capitalize' }}>
                      {trip.travel_style || 'Cultural'}
                    </span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-box-label">Pace</span>
                    <span className="stat-box-val" style={{ textTransform: 'capitalize' }}>
                      {trip.travel_pace || 'Moderate'}
                    </span>
                  </div>
                </div>

                {/* Vibes */}
                <div className="trip-vibes-row">
                  {trip.primary_vibe && (
                    <span className="vibe-chip primary">
                      <Sparkles size={11} />
                      {trip.primary_vibe}
                    </span>
                  )}
                  {trip.secondary_vibes &&
                    trip.secondary_vibes.map((sv, idx) => (
                      <span key={idx} className="vibe-chip secondary">
                        +{sv}
                      </span>
                    ))}
                </div>

                {/* Footer Actions */}
                <div className="trip-card-footer">
                  <div className="card-action-btns">
                    <button
                      type="button"
                      className="btn-card-action"
                      onClick={() => setEditingTrip({ ...trip })}
                      title="Edit trip parameters"
                    >
                      <Edit2 size={13} /> Edit
                    </button>
                    <button
                      type="button"
                      className="btn-card-action danger"
                      onClick={() => setDeletingTrip(trip)}
                      title="Delete trip"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>

                  {/* Primary card button: View or Continue Planning */}
                  <button
                    type="button"
                    className={`btn-card-primary ${!trip.has_itinerary ? 'secondary-tone' : ''}`}
                    onClick={() => onSelectTrip && onSelectTrip(trip)}
                  >
                    {trip.has_itinerary ? (
                      <>
                        <Eye size={14} /> View Itinerary
                      </>
                    ) : (
                      <>
                        <Sparkles size={14} /> Continue Plan
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* ── Edit Trip Modal ─────────────────────────────────────────────── */}
      <AnimatePresence>
        {editingTrip && (
          <div className="modal-overlay">
            <motion.div
              className="modal-content"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
            >
              <div className="modal-header">
                <h3>Edit Trip Details: {editingTrip.destination}</h3>
                <button
                  type="button"
                  className="btn-close-modal"
                  onClick={() => setEditingTrip(null)}
                >
                  <X size={18} />
                </button>
              </div>

              {editingTrip.has_itinerary && (
                <div className="modal-alert-warning">
                  <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: 1 }} />
                  <div>
                    <strong>Itinerary Notice:</strong> Changing your destination or travel dates
                    may require regenerating your daily itinerary plan.
                  </div>
                </div>
              )}

              {updateError && (
                <div className="modal-alert-warning" style={{ background: '#fef2f2', borderColor: '#fecaca', color: '#991b1b' }}>
                  <AlertCircle size={18} />
                  <div>{updateError}</div>
                </div>
              )}

              <form onSubmit={handleUpdateSubmit}>
                {/* Destination */}
                <div className="form-field">
                  <label htmlFor="edit_destination">Destination *</label>
                  <input
                    id="edit_destination"
                    type="text"
                    className="form-input"
                    value={editingTrip.destination}
                    onChange={(e) =>
                      setEditingTrip((prev) => ({ ...prev, destination: e.target.value }))
                    }
                    required
                  />
                </div>

                {/* Dates */}
                <div className="form-row">
                  <div className="form-field">
                    <label htmlFor="edit_start_date">Start Date *</label>
                    <input
                      id="edit_start_date"
                      type="date"
                      className="form-input"
                      value={editingTrip.start_date}
                      onChange={(e) =>
                        setEditingTrip((prev) => ({ ...prev, start_date: e.target.value }))
                      }
                      required
                    />
                  </div>
                  <div className="form-field">
                    <label htmlFor="edit_end_date">End Date *</label>
                    <input
                      id="edit_end_date"
                      type="date"
                      className="form-input"
                      min={editingTrip.start_date}
                      value={editingTrip.end_date}
                      onChange={(e) =>
                        setEditingTrip((prev) => ({ ...prev, end_date: e.target.value }))
                      }
                      required
                    />
                  </div>
                </div>

                {/* Travelers & Budget */}
                <div className="form-row">
                  <div className="form-field">
                    <label htmlFor="edit_travelers">Number of Travelers *</label>
                    <input
                      id="edit_travelers"
                      type="number"
                      min={1}
                      max={20}
                      className="form-input"
                      value={editingTrip.num_travelers || 1}
                      onChange={(e) =>
                        setEditingTrip((prev) => ({
                          ...prev,
                          num_travelers: parseInt(e.target.value, 10) || 1,
                        }))
                      }
                      required
                    />
                  </div>
                  <div className="form-field">
                    <label htmlFor="edit_budget">Total Budget (USD) *</label>
                    <input
                      id="edit_budget"
                      type="number"
                      min={1}
                      className="form-input"
                      value={editingTrip.budget}
                      onChange={(e) =>
                        setEditingTrip((prev) => ({ ...prev, budget: e.target.value }))
                      }
                      required
                    />
                  </div>
                </div>

                {/* Style & Pace */}
                <div className="form-row">
                  <div className="form-field">
                    <label htmlFor="edit_style">Travel Style</label>
                    <select
                      id="edit_style"
                      className="form-select"
                      value={editingTrip.travel_style || 'cultural'}
                      onChange={(e) =>
                        setEditingTrip((prev) => ({ ...prev, travel_style: e.target.value }))
                      }
                    >
                      {TRAVEL_STYLES.map((st) => (
                        <option key={st.value} value={st.value}>
                          {st.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-field">
                    <label htmlFor="edit_pace">Travel Pace</label>
                    <select
                      id="edit_pace"
                      className="form-select"
                      value={editingTrip.travel_pace || 'moderate'}
                      onChange={(e) =>
                        setEditingTrip((prev) => ({ ...prev, travel_pace: e.target.value }))
                      }
                    >
                      <option value="slow">Slow — Relaxed</option>
                      <option value="moderate">Moderate — Balanced</option>
                      <option value="fast">Fast — High Density</option>
                    </select>
                  </div>
                </div>

                {/* Primary Vibe */}
                <div className="form-field">
                  <label htmlFor="edit_primary_vibe">Primary Travel Vibe</label>
                  <select
                    id="edit_primary_vibe"
                    className="form-select"
                    value={editingTrip.primary_vibe || ''}
                    onChange={(e) =>
                      setEditingTrip((prev) => ({ ...prev, primary_vibe: e.target.value }))
                    }
                  >
                    <option value="">Default (None Selected)</option>
                    {TRAVEL_VIBES.map((v) => (
                      <option key={v.id} value={v.title}>
                        {v.title} — {v.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn-card-action"
                    onClick={() => setEditingTrip(null)}
                    disabled={isUpdating}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-card-primary"
                    disabled={isUpdating}
                  >
                    {isUpdating ? (
                      <>
                        <Loader2 size={14} className="spinner" /> Saving Updates…
                      </>
                    ) : (
                      <>
                        <CheckCircle size={14} /> Save Changes
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ── Delete Confirmation Dialog ──────────────────────────────────── */}
      <AnimatePresence>
        {deletingTrip && (
          <div className="modal-overlay">
            <motion.div
              className="modal-content delete-dialog"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
            >
              <div className="delete-dialog-icon">
                <Trash2 size={24} />
              </div>
              <h4>Delete Trip to {deletingTrip.destination}?</h4>
              <p>
                Are you sure you want to delete this trip from your account?
                {deletingTrip.has_itinerary &&
                  ' All associated day-by-day itineraries and route schedules will be permanently deleted.'}
              </p>
              <div className="delete-dialog-actions">
                <button
                  type="button"
                  className="btn-card-action"
                  onClick={() => setDeletingTrip(null)}
                  disabled={isDeleting}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn-danger"
                  onClick={handleDeleteSubmit}
                  disabled={isDeleting}
                >
                  {isDeleting ? (
                    <>
                      <Loader2 size={14} className="spinner" /> Deleting…
                    </>
                  ) : (
                    'Yes, Delete Trip'
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default TripDashboard;

