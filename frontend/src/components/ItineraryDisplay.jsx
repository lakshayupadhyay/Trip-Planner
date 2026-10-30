// frontend/src/components/ItineraryDisplay.jsx
// Redesigned Day-wise Itinerary Display matching Pages 4 & 5 of the PDF reference

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sunrise,
  Sun,
  Moon,
  Utensils,
  Bus,
  DollarSign,
  Compass,
  Sparkles,
  Clock,
  MapPin,
  Calendar,
  AlertCircle,
  Loader2,
  RotateCcw,
  CheckCircle,
  Share2,
  Download,
  FileText,
  FileSpreadsheet,
  MessageSquare,
  Send,
  Zap,
  Bed,
  Footprints,
  Car,
  ChevronRight,
  Shield,
  X,
} from 'lucide-react';
import tripsAPI from '../services/tripsAPI';
import ShareExportPanel from './ShareExportPanel';

export default function ItineraryDisplay({
  itinerary: initialItinerary,
  trip = null,
  isLoading = false,
  error = null,
  onGenerate = null,
  destination: propDestination = '',
  onBackToTrips = null,
}) {
  const [itinerary, setItinerary] = useState(initialItinerary);
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [isReoptimizing, setIsReoptimizing] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showChatDrawer, setShowChatDrawer] = useState(false);

  // Conversational Refinement State
  const [refinePrompt, setRefinePrompt] = useState('');
  const [isRefining, setIsRefining] = useState(false);
  const [refineError, setRefineError] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: '👋 Need any adjustments? Ask me to tweak Day ' + (selectedDayIndex + 1) + ' or the entire trip (e.g. "Add a scenic sunset spot", "Make dinner vegetarian", "Optimize transit").',
    },
  ]);

  // Keep state in sync with parent prop
  React.useEffect(() => {
    setItinerary(initialItinerary);
  }, [initialItinerary]);

  const destinationName =
    itinerary?.destination || trip?.destination || propDestination || 'Destination';

  // Destination cover photo
  const getDestinationPhoto = (dest) => {
    const d = (dest || '').toLowerCase();
    if (d.includes('kyoto') || d.includes('japan')) {
      return 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=700&q=80';
    }
    if (d.includes('paris') || d.includes('france')) {
      return 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=700&q=80';
    }
    if (d.includes('amalfi') || d.includes('italy') || d.includes('rome')) {
      return 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=700&q=80';
    }
    if (d.includes('swiss') || d.includes('alps')) {
      return 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=700&q=80';
    }
    if (d.includes('bali') || d.includes('indonesia')) {
      return 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=700&q=80';
    }
    return 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=700&q=80';
  };

  // ── 1. LOADING STATE ────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div
        style={{
          minHeight: '60vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '3rem',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            width: '4.5rem',
            height: '4.5rem',
            borderRadius: '50%',
            backgroundColor: '#eff6ff',
            color: '#2563eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1.5rem',
            boxShadow: '0 8px 24px rgba(37, 99, 235, 0.2)',
          }}
        >
          <Sparkles size={32} className="spin" />
        </div>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.5rem' }}>
          Crafting Your Day-by-Day Itinerary…
        </h2>
        <p style={{ fontSize: '0.95rem', color: '#64748b', maxWidth: '480px', margin: '0 0 1rem', lineHeight: 1.5 }}>
          Our AI concierge is structuring morning, afternoon, and evening activities, transit sequencing, and cuisine for{' '}
          <strong>{destinationName}</strong>.
        </p>
        <span
          style={{
            backgroundColor: '#f1f5f9',
            color: '#475569',
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.8rem',
            fontWeight: 600,
          }}
        >
          ⚡ Optimizing routes &amp; conflict-free time slots
        </span>
      </div>
    );
  }

  // ── 2. ERROR STATE ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1.5rem' }}>
        <div
          style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '16px',
            padding: '2rem',
            textAlign: 'center',
          }}
        >
          <AlertCircle size={36} color="#dc2626" style={{ margin: '0 auto 0.75rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#991b1b', margin: '0 0 0.5rem' }}>
            Itinerary Generation Issue
          </h3>
          <p style={{ fontSize: '0.92rem', color: '#b91c1c', margin: '0 0 1.25rem' }}>{error}</p>
          {onGenerate && (
            <button
              onClick={onGenerate}
              style={{
                backgroundColor: '#dc2626',
                color: '#ffffff',
                border: 'none',
                borderRadius: '10px',
                padding: '0.65rem 1.25rem',
                fontSize: '0.9rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Try Generating Again
            </button>
          )}
        </div>
      </div>
    );
  }

  // ── 3. EMPTY STATE ──────────────────────────────────────────────────────────
  if (!itinerary || !itinerary.days || itinerary.days.length === 0) {
    return (
      <div style={{ maxWidth: '640px', margin: '4rem auto', padding: '0 1.5rem', textAlign: 'center' }}>
        <div
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '20px',
            border: '1px dashed #cbd5e1',
            padding: '3rem 2rem',
          }}
        >
          <Compass size={40} color="#3b82f6" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.5rem' }}>
            No Itinerary Generated Yet
          </h3>
          <p style={{ fontSize: '0.92rem', color: '#64748b', maxWidth: '420px', margin: '0 auto 1.5rem' }}>
            Generate a full day-by-day plan with morning exploration, afternoon journeys, evening dining, and transit
            guidance for {destinationName}.
          </p>
          {onGenerate && (
            <button
              onClick={onGenerate}
              style={{
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '10px',
                padding: '0.75rem 1.5rem',
                fontSize: '0.92rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.45rem',
              }}
            >
              <Sparkles size={16} />
              <span>Generate Itinerary Now</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  const days = itinerary.days;
  const currentDay = days[selectedDayIndex] || days[0];

  // Route Optimization handler
  const handleOptimizeCurrentDay = async () => {
    setIsReoptimizing(true);
    try {
      const pace = trip?.travel_pace || 'moderate';
      const optimized = await tripsAPI.optimizeDay(destinationName, currentDay, pace);
      const updatedDays = [...days];
      updatedDays[selectedDayIndex] = optimized;
      setItinerary((prev) => ({ ...prev, days: updatedDays }));
    } catch (err) {
      console.error('Failed to optimize day:', err);
    } finally {
      setIsReoptimizing(false);
    }
  };

  // Conversational Refinement handler
  const handleSendRefinement = async (e) => {
    e.preventDefault();
    if (!refinePrompt.trim() || isRefining) return;

    const userText = refinePrompt.trim();
    setRefinePrompt('');
    setRefineError(null);

    // Append user message
    setChatMessages((prev) => [
      ...prev,
      { id: Date.now(), sender: 'user', text: userText },
    ]);

    setIsRefining(true);
    try {
      const result = await tripsAPI.refineDay(
        destinationName,
        currentDay,
        userText,
        selectedDayIndex + 1
      );

      const updatedDays = [...days];
      updatedDays[selectedDayIndex] = result;
      setItinerary((prev) => ({ ...prev, days: updatedDays }));

      setChatMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'assistant',
          text: `✨ Updated Day ${selectedDayIndex + 1} with your requests! Check the schedule to view the changes.`,
        },
      ]);
    } catch (err) {
      setRefineError(err.message || 'Failed to refine schedule.');
      setChatMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'assistant',
          text: `⚠️ Error updating day: ${err.message}`,
        },
      ]);
    } finally {
      setIsRefining(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: 'calc(100vh - 4.25rem)', padding: '2rem 1.5rem 5rem' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        {/* Top Back / Action Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1.5rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          {onBackToTrips && (
            <button
              onClick={onBackToTrips}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '0.45rem 0.85rem',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: '#475569',
                cursor: 'pointer',
              }}
            >
              &larr; Back to Trips
            </button>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginLeft: 'auto' }}>
            <button
              onClick={() => setShowChatDrawer(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '10px',
                padding: '0.55rem 1rem',
                fontSize: '0.88rem',
                fontWeight: 600,
                color: '#1e293b',
                cursor: 'pointer',
              }}
            >
              <MessageSquare size={16} color="#2563eb" />
              <span>AI Refine &amp; Chat</span>
            </button>

            <button
              onClick={() => setShowShareModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '10px',
                padding: '0.55rem 1.15rem',
                fontSize: '0.88rem',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(37, 99, 235, 0.25)',
              }}
            >
              <Share2 size={16} />
              <span>Share &amp; Export</span>
            </button>
          </div>
        </div>

        {/* ── SPLIT LAYOUT matching Pages 4 & 5 of PDF reference ───────── */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '1.75rem',
            alignItems: 'start',
          }}
        >
          {/* ── LEFT SIDEBAR: TRIP METADATA PILL ──────────────────────── */}
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '20px',
              border: '1px solid #e2e8f0',
              overflow: 'hidden',
              boxShadow: '0 4px 20px -2px rgba(15, 23, 42, 0.05)',
              position: 'sticky',
              top: '5.5rem',
            }}
          >
            {/* Header Image */}
            <div style={{ position: 'relative', height: '180px' }}>
              <img
                src={getDestinationPhoto(destinationName)}
                alt={destinationName}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(to top, rgba(15, 23, 42, 0.85) 0%, transparent 60%)',
                }}
              />
              <div style={{ position: 'absolute', bottom: '1rem', left: '1.25rem', right: '1.25rem', color: '#ffffff' }}>
                <span
                  style={{
                    backgroundColor: '#2563eb',
                    color: '#ffffff',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.55rem',
                    borderRadius: '9999px',
                    textTransform: 'uppercase',
                    display: 'inline-block',
                    marginBottom: '0.35rem',
                  }}
                >
                  Itinerary Overview
                </span>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800, margin: 0, letterSpacing: '-0.02em' }}>
                  {destinationName}
                </h2>
              </div>
            </div>

            {/* Metadata Body */}
            <div style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                  <span style={{ color: '#64748b' }}>Duration:</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{days.length} Days Planned</span>
                </div>
                {trip?.start_date && (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                    <span style={{ color: '#64748b' }}>Dates:</span>
                    <span style={{ fontWeight: 600, color: '#0f172a' }}>
                      {trip.start_date} &rarr; {trip.end_date || 'Ongoing'}
                    </span>
                  </div>
                )}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                  <span style={{ color: '#64748b' }}>Travelers:</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{trip?.num_travelers || 1} Person(s)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.88rem' }}>
                  <span style={{ color: '#64748b' }}>Travel Pace:</span>
                  <span
                    style={{
                      backgroundColor: '#eff6ff',
                      color: '#1d4ed8',
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      padding: '0.2rem 0.55rem',
                      borderRadius: '9999px',
                      textTransform: 'capitalize',
                    }}
                  >
                    {trip?.travel_pace || 'Moderate'}
                  </span>
                </div>
              </div>

              {/* Vibe Tags */}
              <div style={{ marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '0.45rem' }}>
                  Travel Vibes
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  <span
                    style={{
                      backgroundColor: '#dbeafe',
                      color: '#1e40af',
                      borderRadius: '9999px',
                      padding: '0.25rem 0.65rem',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                    }}
                  >
                    ✨ {trip?.primary_vibe || 'Cultural'}
                  </span>
                  {(trip?.secondary_vibes || []).map((v) => (
                    <span
                      key={v}
                      style={{
                        backgroundColor: '#f1f5f9',
                        color: '#475569',
                        borderRadius: '9999px',
                        padding: '0.25rem 0.6rem',
                        fontSize: '0.75rem',
                      }}
                    >
                      {v}
                    </span>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9' }}>
                <button
                  onClick={() => setShowShareModal(true)}
                  style={{
                    width: '100%',
                    backgroundColor: '#eff6ff',
                    color: '#1d4ed8',
                    border: '1px solid #bfdbfe',
                    borderRadius: '10px',
                    padding: '0.65rem',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem',
                  }}
                >
                  <Download size={15} />
                  <span>Export PDF / JSON</span>
                </button>
              </div>
            </div>
          </div>

          {/* ── RIGHT MAIN CONTENT: DAY CARDS & SCHEDULE ─────────────── */}
          <div style={{ flex: 1, minWidth: '320px' }}>
            {/* Day Selector Navigation Pills */}
            <div
              style={{
                display: 'flex',
                gap: '0.5rem',
                overflowX: 'auto',
                paddingBottom: '0.75rem',
                marginBottom: '1.25rem',
              }}
            >
              {days.map((d, index) => {
                const isSelected = selectedDayIndex === index;
                return (
                  <button
                    key={index}
                    onClick={() => setSelectedDayIndex(index)}
                    style={{
                      backgroundColor: isSelected ? '#2563eb' : '#ffffff',
                      color: isSelected ? '#ffffff' : '#475569',
                      border: isSelected ? 'none' : '1px solid #e2e8f0',
                      borderRadius: '12px',
                      padding: '0.65rem 1.25rem',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      boxShadow: isSelected ? '0 4px 12px rgba(37, 99, 235, 0.25)' : 'none',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <span>Day {d.day || index + 1}</span>
                  </button>
                );
              })}
            </div>

            {/* Day Overview Banner Badge matching PDF */}
            <div
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                padding: '1.25rem 1.5rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '1rem',
                boxShadow: '0 2px 10px rgba(15, 23, 42, 0.04)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div
                  style={{
                    width: '2.5rem',
                    height: '2.5rem',
                    borderRadius: '10px',
                    backgroundColor: '#eff6ff',
                    color: '#2563eb',
                    fontWeight: 800,
                    fontSize: '1.1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {String(currentDay.day || selectedDayIndex + 1).padStart(2, '0')}
                </div>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.15rem' }}>
                    {currentDay.theme || `Day ${currentDay.day || selectedDayIndex + 1} Exploration`}
                  </h3>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    {currentDay.date || 'Optimized Sequential Schedule'}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {currentDay.estimated_cost && (
                  <span
                    style={{
                      backgroundColor: '#ecfdf5',
                      color: '#059669',
                      border: '1px solid #a7f3d0',
                      padding: '0.35rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.8rem',
                      fontWeight: 700,
                    }}
                  >
                    Est. Cap: ${currentDay.estimated_cost}
                  </span>
                )}
                <button
                  onClick={handleOptimizeCurrentDay}
                  disabled={isReoptimizing}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    borderRadius: '8px',
                    padding: '0.45rem 0.85rem',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    color: '#1e293b',
                    cursor: 'pointer',
                  }}
                >
                  <Zap size={14} color="#f59e0b" />
                  <span>{isReoptimizing ? 'Optimizing...' : 'Optimize Route'}</span>
                </button>
              </div>
            </div>

            {/* Activity Cards: Morning, Afternoon, Evening, Cuisine, Stay, Transit */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* 1. MORNING EXPLORATION */}
              {currentDay.morning && (
                <div
                  style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '16px',
                    border: '1px solid #e2e8f0',
                    borderLeft: '5px solid #3b82f6',
                    padding: '1.25rem 1.5rem',
                    boxShadow: '0 2px 8px rgba(15, 23, 42, 0.03)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '1.25rem' }}>🌅</span>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#3b82f6', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Morning Exploration
                      </span>
                    </div>
                    {currentDay.morning.time && (
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748b' }}>
                        {currentDay.morning.time}
                      </span>
                    )}
                  </div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.4rem' }}>
                    {currentDay.morning.activity || currentDay.morning.title}
                  </h4>
                  <p style={{ fontSize: '0.88rem', color: '#475569', lineHeight: 1.5, margin: '0 0 0.5rem' }}>
                    {currentDay.morning.description}
                  </p>
                  {currentDay.morning.cost && (
                    <div style={{ fontSize: '0.8rem', color: '#16a34a', fontWeight: 600 }}>
                      Est. Cost: ${currentDay.morning.cost}
                    </div>
                  )}
                </div>
              )}

              {/* 2. AFTERNOON JOURNEY */}
              {currentDay.afternoon && (
                <div
                  style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '16px',
                    border: '1px solid #e2e8f0',
                    borderLeft: '5px solid #0ea5e9',
                    padding: '1.25rem 1.5rem',
                    boxShadow: '0 2px 8px rgba(15, 23, 42, 0.03)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '1.25rem' }}>☀️</span>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#0ea5e9', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Afternoon Journey
                      </span>
                    </div>
                    {currentDay.afternoon.time && (
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748b' }}>
                        {currentDay.afternoon.time}
                      </span>
                    )}
                  </div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.4rem' }}>
                    {currentDay.afternoon.activity || currentDay.afternoon.title}
                  </h4>
                  <p style={{ fontSize: '0.88rem', color: '#475569', lineHeight: 1.5, margin: '0 0 0.5rem' }}>
                    {currentDay.afternoon.description}
                  </p>
                  {currentDay.afternoon.cost && (
                    <div style={{ fontSize: '0.8rem', color: '#16a34a', fontWeight: 600 }}>
                      Est. Cost: ${currentDay.afternoon.cost}
                    </div>
                  )}
                </div>
              )}

              {/* 3. EVENING CHARM */}
              {currentDay.evening && (
                <div
                  style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '16px',
                    border: '1px solid #e2e8f0',
                    borderLeft: '5px solid #8b5cf6',
                    padding: '1.25rem 1.5rem',
                    boxShadow: '0 2px 8px rgba(15, 23, 42, 0.03)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '1.25rem' }}>🌙</span>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#8b5cf6', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Evening Charm
                      </span>
                    </div>
                    {currentDay.evening.time && (
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748b' }}>
                        {currentDay.evening.time}
                      </span>
                    )}
                  </div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.4rem' }}>
                    {currentDay.evening.activity || currentDay.evening.title}
                  </h4>
                  <p style={{ fontSize: '0.88rem', color: '#475569', lineHeight: 1.5, margin: '0 0 0.5rem' }}>
                    {currentDay.evening.description}
                  </p>
                  {currentDay.evening.cost && (
                    <div style={{ fontSize: '0.8rem', color: '#16a34a', fontWeight: 600 }}>
                      Est. Cost: ${currentDay.evening.cost}
                    </div>
                  )}
                </div>
              )}

              {/* 4. CUISINE & DINING */}
              {currentDay.meals && (
                <div
                  style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '16px',
                    border: '1px solid #e2e8f0',
                    borderLeft: '5px solid #f59e0b',
                    padding: '1.25rem 1.5rem',
                    boxShadow: '0 2px 8px rgba(15, 23, 42, 0.03)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.65rem' }}>
                    <span style={{ fontSize: '1.25rem' }}>🍽️</span>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Cuisine &amp; Dining Recommendation
                    </span>
                  </div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.4rem' }}>
                    {typeof currentDay.meals === 'string'
                      ? currentDay.meals
                      : currentDay.meals.dinner || currentDay.meals.lunch || 'Local Specialties'}
                  </h4>
                  {typeof currentDay.meals === 'object' && currentDay.meals.notes && (
                    <p style={{ fontSize: '0.88rem', color: '#475569', margin: 0 }}>
                      {currentDay.meals.notes}
                    </p>
                  )}
                </div>
              )}

              {/* 5. TRANSIT & LOGISTICS */}
              {currentDay.transit && (
                <div
                  style={{
                    backgroundColor: '#f8fafc',
                    borderRadius: '16px',
                    border: '1px solid #e2e8f0',
                    padding: '1rem 1.5rem',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                  }}
                >
                  <Bus size={20} color="#2563eb" style={{ marginTop: '0.2rem' }} />
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#1e293b', marginBottom: '0.2rem' }}>
                      Transit Logistics &amp; Travel Tips
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#475569' }}>
                      {typeof currentDay.transit === 'string'
                        ? currentDay.transit
                        : currentDay.transit.details || 'Subway / Metro / Local Taxi'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── CONVERSATIONAL REFINEMENT DRAWER ─────────────────────────── */}
      {showChatDrawer && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.5)',
            backdropFilter: 'blur(4px)',
            zIndex: 90,
            display: 'flex',
            justifyContent: 'flex-end',
          }}
          onClick={() => setShowChatDrawer(false)}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              width: '100%',
              maxWidth: '460px',
              height: '100%',
              boxShadow: '-10px 0 30px rgba(0, 0, 0, 0.15)',
              display: 'flex',
              flexDirection: 'column',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div
              style={{
                padding: '1.25rem 1.5rem',
                borderBottom: '1px solid #e2e8f0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={18} color="#2563eb" />
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>
                  AI Itinerary Refinement
                </h3>
              </div>
              <button
                onClick={() => setShowChatDrawer(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Chat Messages */}
            <div style={{ flex: 1, padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {chatMessages.map((m) => (
                <div
                  key={m.id}
                  style={{
                    alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                    backgroundColor: m.sender === 'user' ? '#2563eb' : '#f1f5f9',
                    color: m.sender === 'user' ? '#ffffff' : '#1e293b',
                    borderRadius: '14px',
                    padding: '0.75rem 1rem',
                    fontSize: '0.9rem',
                    lineHeight: 1.5,
                  }}
                >
                  {m.text}
                </div>
              ))}
              {isRefining && (
                <div
                  style={{
                    alignSelf: 'flex-start',
                    backgroundColor: '#f1f5f9',
                    color: '#64748b',
                    borderRadius: '14px',
                    padding: '0.75rem 1rem',
                    fontSize: '0.85rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                  }}
                >
                  <Loader2 size={16} className="spin" />
                  <span>Personalizing Day {selectedDayIndex + 1}...</span>
                </div>
              )}
            </div>

            {/* Input Form */}
            <form
              onSubmit={handleSendRefinement}
              style={{
                padding: '1rem 1.5rem',
                borderTop: '1px solid #e2e8f0',
                display: 'flex',
                gap: '0.5rem',
              }}
            >
              <input
                type="text"
                placeholder="Ask to adjust timings, vibe, or activities..."
                value={refinePrompt}
                onChange={(e) => setRefinePrompt(e.target.value)}
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  borderRadius: '10px',
                  border: '1px solid #cbd5e1',
                  fontSize: '0.9rem',
                  outline: 'none',
                }}
              />
              <button
                type="submit"
                disabled={isRefining || !refinePrompt.trim()}
                style={{
                  backgroundColor: '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '0.75rem 1rem',
                  cursor: isRefining ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Send size={16} />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* ── SHARE & EXPORT MODAL ─────────────────────────────────────── */}
      {showShareModal && (
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
          onClick={() => setShowShareModal(false)}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              borderRadius: '20px',
              maxWidth: '600px',
              width: '100%',
              boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
              position: 'relative',
              overflow: 'hidden',
              maxHeight: '90vh',
              display: 'flex',
              flexDirection: 'column',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                padding: '1.25rem 1.5rem',
                borderBottom: '1px solid #e2e8f0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Share2 size={18} color="#2563eb" />
                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>
                  Share &amp; Export Itinerary
                </h3>
              </div>
              <button
                onClick={() => setShowShareModal(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ padding: '1.5rem', overflowY: 'auto' }}>
              <ShareExportPanel
                tripId={trip?.id || itinerary?.trip_id}
                tripTitle={trip?.title || `${destinationName} Itinerary`}
                destination={destinationName}
                itinerary={itinerary}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
