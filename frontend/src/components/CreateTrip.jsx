// frontend/src/components/CreateTrip.jsx
// Redesigned Multi-step Trip Creation matching Page 3 of the PDF reference

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin,
  Calendar,
  Sparkles,
  Users,
  DollarSign,
  Heart,
  Compass,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Clock,
  Coffee,
  Mountain,
  UtensilsCrossed,
  Landmark,
  Gem,
  Trees,
} from 'lucide-react';
import tripsAPI from '../services/tripsAPI';

export const TRAVEL_STYLES = [
  { id: 'cultural', label: 'Cultural', emoji: '🏛️', desc: 'Museums, historic heritage, and local customs' },
  { id: 'relaxed', label: 'Relaxed', emoji: '🏖️', desc: 'Unhurried mornings, serene cafes, and gentle strolls' },
  { id: 'adventure', label: 'Adventure', emoji: '🧗', desc: 'Hiking, outdoor exploration, and thrill-seeking' },
  { id: 'romantic', label: 'Romantic', emoji: '🌹', desc: 'Sunset viewpoints, intimate dining, and scenic walks' },
  { id: 'foodie', label: 'Food & Culinary', emoji: '🍜', desc: 'Street food markets, local delicacies, and tastings' },
  { id: 'nature', label: 'Nature & Wildlife', emoji: '🌲', desc: 'National parks, botanical gardens, and scenic vistas' },
  { id: 'luxury', label: 'Luxury', emoji: '💎', desc: 'Boutique stays, fine dining, and elevated comfort' },
  { id: 'budget', label: 'Budget Friendly', emoji: '🎒', desc: 'Free sights, local transit, and high-value spots' },
];

export const TRAVEL_INTERESTS = [
  'History & Heritage',
  'Local Food & Dining',
  'Scenic Photography',
  'Museums & Art',
  'Hiking & Outdoors',
  'Shopping & Markets',
  'Beaches & Coastal',
  'Nightlife & Lounges',
  'Architecture',
  'Wellness & Spas',
];

export const DIETARY_OPTIONS = [
  'None / All Food',
  'Vegetarian',
  'Vegan',
  'Halal',
  'Kosher',
  'Gluten-Free',
];

export default function CreateTrip({
  prefillDestination = '',
  onItineraryReady,
  onCancel,
}) {
  const [step, setStep] = useState(1); // 1: Details, 2: Preferences, 3: Logistics
  const [formData, setFormData] = useState({
    destination: prefillDestination || '',
    start_date: '',
    end_date: '',
    num_travelers: 2,
    travel_pace: 'moderate',
    primary_vibe: 'cultural',
    secondary_vibes: [],
    travel_interests: ['History & Heritage', 'Local Food & Dining'],
    budget: '1500',
    currency: 'USD',
    budget_tier: 'moderate',
    dietary_preferences: [],
    additional_requirements: '',
  });

  const [validationError, setValidationError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // Sync prefillDestination
  useEffect(() => {
    if (prefillDestination) {
      setFormData((prev) => ({ ...prev, destination: prefillDestination }));
    }
  }, [prefillDestination]);

  // Calculate duration
  const tripDurationDays =
    formData.start_date && formData.end_date
      ? Math.max(
          1,
          Math.round(
            (new Date(formData.end_date) - new Date(formData.start_date)) / (1000 * 60 * 60 * 24)
          )
        )
      : null;

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setValidationError(null);
  };

  const toggleInterest = (interest) => {
    setFormData((prev) => {
      const current = prev.travel_interests;
      const next = current.includes(interest)
        ? current.filter((i) => i !== interest)
        : [...current, interest];
      return { ...prev, travel_interests: next };
    });
  };

  const toggleDietary = (diet) => {
    if (diet === 'None / All Food') {
      setFormData((prev) => ({ ...prev, dietary_preferences: [] }));
      return;
    }
    setFormData((prev) => {
      const current = prev.dietary_preferences;
      const next = current.includes(diet)
        ? current.filter((d) => d !== diet)
        : [...current, diet];
      return { ...prev, dietary_preferences: next };
    });
  };

  const validateCurrentStep = () => {
    if (step === 1) {
      if (!formData.destination || formData.destination.trim().length < 2) {
        return 'Please enter a destination city or region.';
      }
      if (!formData.start_date) return 'Please select a starting date.';
      if (!formData.end_date) return 'Please select an end date.';
      if (new Date(formData.end_date) <= new Date(formData.start_date)) {
        return 'End date must be after the start date.';
      }
    }
    if (step === 2) {
      if (!formData.primary_vibe) return 'Please pick a travel vibe.';
      if (formData.travel_interests.length === 0) {
        return 'Please choose at least one travel interest.';
      }
    }
    if (step === 3) {
      if (!formData.budget || parseFloat(formData.budget) <= 0) {
        return 'Please enter a budget estimate.';
      }
    }
    return null;
  };

  const handleNext = () => {
    const errorMsg = validateCurrentStep();
    if (errorMsg) {
      setValidationError(errorMsg);
      return;
    }
    setValidationError(null);
    setStep((s) => Math.min(3, s + 1));
  };

  const handleBack = () => {
    setValidationError(null);
    setStep((s) => Math.max(1, s - 1));
  };

  const handleGenerate = async () => {
    const errorMsg = validateCurrentStep();
    if (errorMsg) {
      setValidationError(errorMsg);
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // 1. Create Trip in Supabase backend
      const tripPayload = {
        destination: formData.destination.trim(),
        start_date: formData.start_date,
        end_date: formData.end_date,
        num_travelers: parseInt(formData.num_travelers, 10) || 1,
        budget: parseFloat(formData.budget) || 1000,
        travel_style: formData.primary_vibe,
        travel_interests: formData.travel_interests,
        dietary_preferences: formData.dietary_preferences,
        travel_pace: formData.travel_pace,
        primary_vibe: formData.primary_vibe,
        secondary_vibes: formData.secondary_vibes,
        additional_requirements: formData.additional_requirements || null,
      };

      const createdTrip = await tripsAPI.createTrip(tripPayload);

      // 2. Generate daily AI itinerary
      const itinPayload = {
        ...tripPayload,
        trip_id: createdTrip.id,
      };

      const generatedItin = await tripsAPI.generateItinerary(itinPayload);

      // Pass result to parent to view
      if (onItineraryReady) {
        onItineraryReady(createdTrip, generatedItin);
      }
    } catch (err) {
      console.error('Generation error:', err);
      setSubmitError(err.message || 'Failed to generate itinerary. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        backgroundColor: '#f8fafc',
        minHeight: 'calc(100vh - 4.25rem)',
        padding: '2.5rem 1.5rem 4rem',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <div style={{ width: '100%', maxWidth: '720px' }}>
        {/* Top Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
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
            <Sparkles size={14} /> Step-by-Step AI Generator
          </div>
          <h1
            style={{
              fontSize: '2rem',
              fontWeight: 800,
              color: '#0f172a',
              margin: '0 0 0.4rem',
              letterSpacing: '-0.025em',
            }}
          >
            Design Your Trip
          </h1>
          <p style={{ fontSize: '0.92rem', color: '#64748b', margin: 0 }}>
            Answer 3 quick steps to generate a conflict-free, paced, and optimized travel plan.
          </p>
        </div>

        {/* Step Indicator Bar matching PDF Page 3 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '2rem',
          }}
        >
          {[
            { num: 1, label: 'Details' },
            { num: 2, label: 'Preferences' },
            { num: 3, label: 'Logistics' },
          ].map((s, idx) => {
            const isCompleted = step > s.num;
            const isCurrent = step === s.num;
            return (
              <React.Fragment key={s.num}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    cursor: s.num < step ? 'pointer' : 'default',
                  }}
                  onClick={() => {
                    if (s.num < step) setStep(s.num);
                  }}
                >
                  <div
                    style={{
                      width: '2.2rem',
                      height: '2.2rem',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      backgroundColor: isCurrent ? '#2563eb' : isCompleted ? '#dcfce7' : '#f1f5f9',
                      color: isCurrent ? '#ffffff' : isCompleted ? '#16a34a' : '#64748b',
                      border: isCurrent ? '2px solid #2563eb' : 'none',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    {isCompleted ? <CheckCircle2 size={16} /> : s.num}
                  </div>
                  <span
                    style={{
                      fontSize: '0.88rem',
                      fontWeight: isCurrent ? 700 : 500,
                      color: isCurrent ? '#0f172a' : '#64748b',
                    }}
                  >
                    {s.num}. {s.label}
                  </span>
                </div>

                {idx < 2 && (
                  <div
                    style={{
                      width: '40px',
                      height: '2px',
                      backgroundColor: step > s.num ? '#2563eb' : '#e2e8f0',
                      transition: 'all 0.2s ease',
                    }}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Validation or Error Message */}
        {validationError && (
          <div
            style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              color: '#b91c1c',
              borderRadius: '12px',
              padding: '0.75rem 1rem',
              fontSize: '0.88rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginBottom: '1.25rem',
            }}
          >
            <AlertCircle size={16} />
            <span>{validationError}</span>
          </div>
        )}

        {submitError && (
          <div
            style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              color: '#b91c1c',
              borderRadius: '12px',
              padding: '0.75rem 1rem',
              fontSize: '0.88rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginBottom: '1.25rem',
            }}
          >
            <AlertCircle size={16} />
            <span>{submitError}</span>
          </div>
        )}

        {/* Centered White Card Form matching PDF reference */}
        <div
          style={{
            backgroundColor: '#ffffff',
            borderRadius: '20px',
            border: '1px solid #e2e8f0',
            boxShadow: '0 10px 25px -5px rgba(15, 23, 42, 0.05), 0 8px 10px -6px rgba(15, 23, 42, 0.03)',
            padding: '2.25rem',
            overflow: 'hidden',
          }}
        >
          {/* ── STEP 1: ESSENTIAL DETAILS ─────────────────────────────── */}
          {step === 1 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <div style={{ marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.35rem' }}>
                  Essential Details
                </h2>
                <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
                  Where are you heading and what are your travel dates?
                </p>
              </div>

              {/* Destination Input */}
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                  Destination *
                </label>
                <div style={{ position: 'relative' }}>
                  <MapPin
                    size={18}
                    color="#2563eb"
                    style={{ position: 'absolute', left: '0.9rem', top: '50%', transform: 'translateY(-50%)' }}
                  />
                  <input
                    type="text"
                    required
                    placeholder="e.g. Kyoto, Japan or Amalfi Coast, Italy"
                    value={formData.destination}
                    onChange={(e) => handleChange('destination', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.85rem 0.9rem 0.85rem 2.6rem',
                      borderRadius: '12px',
                      border: '1px solid #cbd5e1',
                      fontSize: '0.95rem',
                      outline: 'none',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Popular:</span>
                  {['Kyoto, Japan', 'Paris, France', 'Amalfi Coast, Italy', 'Bali, Indonesia'].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => handleChange('destination', p)}
                      style={{
                        background: '#f1f5f9',
                        border: 'none',
                        borderRadius: '9999px',
                        padding: '0.15rem 0.55rem',
                        fontSize: '0.75rem',
                        color: '#334155',
                        cursor: 'pointer',
                      }}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              {/* Dates */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '1rem',
                  marginBottom: '1.5rem',
                }}
              >
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                    Start Date *
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.start_date}
                    onChange={(e) => handleChange('start_date', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.85rem',
                      borderRadius: '12px',
                      border: '1px solid #cbd5e1',
                      fontSize: '0.92rem',
                      outline: 'none',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                    End Date *
                  </label>
                  <input
                    type="date"
                    required
                    min={formData.start_date || undefined}
                    value={formData.end_date}
                    onChange={(e) => handleChange('end_date', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.85rem',
                      borderRadius: '12px',
                      border: '1px solid #cbd5e1',
                      fontSize: '0.92rem',
                      outline: 'none',
                      boxSizing: 'border-box',
                    }}
                  />
                </div>
              </div>

              {/* Duration Preview */}
              {tripDurationDays && (
                <div
                  style={{
                    backgroundColor: '#eff6ff',
                    border: '1px solid #bfdbfe',
                    borderRadius: '10px',
                    padding: '0.65rem 1rem',
                    fontSize: '0.85rem',
                    color: '#1e40af',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                    marginBottom: '1.5rem',
                  }}
                >
                  <Clock size={16} />
                  <span>
                    Estimated trip duration: <strong>{tripDurationDays} day{tripDurationDays > 1 ? 's' : ''}</strong>
                  </span>
                </div>
              )}
            </motion.div>
          )}

          {/* ── STEP 2: VIBE & INTERESTS ──────────────────────────────── */}
          {step === 2 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <div style={{ marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.35rem' }}>
                  Vibe &amp; Interests
                </h2>
                <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
                  Tell us what kind of atmosphere you enjoy to personalize places &amp; timing.
                </p>
              </div>

              {/* Primary Travel Vibe */}
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.6rem' }}>
                  Primary Vibe *
                </label>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                    gap: '0.65rem',
                  }}
                >
                  {TRAVEL_STYLES.map((style) => {
                    const isSelected = formData.primary_vibe === style.id;
                    return (
                      <div
                        key={style.id}
                        onClick={() => handleChange('primary_vibe', style.id)}
                        style={{
                          backgroundColor: isSelected ? '#eff6ff' : '#ffffff',
                          border: isSelected ? '2px solid #2563eb' : '1px solid #e2e8f0',
                          borderRadius: '12px',
                          padding: '0.75rem',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '0.2rem',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <span style={{ fontSize: '1.2rem' }}>{style.emoji}</span>
                          <span style={{ fontWeight: isSelected ? 700 : 600, fontSize: '0.88rem', color: isSelected ? '#1d4ed8' : '#0f172a' }}>
                            {style.label}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Travel Pace */}
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.6rem' }}>
                  Travel Pace
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.65rem' }}>
                  {[
                    { id: 'slow', label: 'Relaxed', desc: '1-2 activities/day' },
                    { id: 'moderate', label: 'Moderate', desc: 'Balanced rhythm' },
                    { id: 'fast', label: 'Fast-Paced', desc: 'Pack every hour' },
                  ].map((p) => {
                    const isSelected = formData.travel_pace === p.id;
                    return (
                      <div
                        key={p.id}
                        onClick={() => handleChange('travel_pace', p.id)}
                        style={{
                          backgroundColor: isSelected ? '#eff6ff' : '#ffffff',
                          border: isSelected ? '2px solid #2563eb' : '1px solid #e2e8f0',
                          borderRadius: '12px',
                          padding: '0.75rem',
                          textAlign: 'center',
                          cursor: 'pointer',
                        }}
                      >
                        <div style={{ fontWeight: 700, fontSize: '0.88rem', color: isSelected ? '#1d4ed8' : '#0f172a' }}>
                          {p.label}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: '#64748b' }}>{p.desc}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Interests Multi-Select Pills */}
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.6rem' }}>
                  Travel Interests * (Select all that apply)
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {TRAVEL_INTERESTS.map((interest) => {
                    const isSelected = formData.travel_interests.includes(interest);
                    return (
                      <button
                        key={interest}
                        type="button"
                        onClick={() => toggleInterest(interest)}
                        style={{
                          backgroundColor: isSelected ? '#dbeafe' : '#f1f5f9',
                          color: isSelected ? '#1d4ed8' : '#334155',
                          border: isSelected ? '1px solid #3b82f6' : '1px solid transparent',
                          borderRadius: '9999px',
                          padding: '0.4rem 0.85rem',
                          fontSize: '0.82rem',
                          fontWeight: isSelected ? 600 : 500,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {isSelected ? '✓ ' : '+ '}
                        {interest}
                      </button>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          )}

          {/* ── STEP 3: FINAL LOGISTICS ───────────────────────────────── */}
          {step === 3 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <div style={{ marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.35rem' }}>
                  Final Logistics
                </h2>
                <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
                  Specify group size, budget, and any dietary or special accommodations.
                </p>
              </div>

              {/* Travelers & Budget Row */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '1rem',
                  marginBottom: '1.5rem',
                }}
              >
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                    Group Size *
                  </label>
                  <select
                    value={formData.num_travelers}
                    onChange={(e) => handleChange('num_travelers', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.85rem',
                      borderRadius: '12px',
                      border: '1px solid #cbd5e1',
                      fontSize: '0.92rem',
                      outline: 'none',
                      backgroundColor: '#ffffff',
                    }}
                  >
                    <option value={1}>Solo Explorer (1 person)</option>
                    <option value={2}>Couple / 2 Travelers</option>
                    <option value={3}>Small Group (3 travelers)</option>
                    <option value={4}>Family / Group of 4</option>
                    <option value={5}>Group of 5+</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                    Estimated Budget (USD) *
                  </label>
                  <div style={{ position: 'relative' }}>
                    <DollarSign
                      size={18}
                      color="#16a34a"
                      style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }}
                    />
                    <input
                      type="number"
                      required
                      min={50}
                      placeholder="1500"
                      value={formData.budget}
                      onChange={(e) => handleChange('budget', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.85rem 0.85rem 0.85rem 2.4rem',
                        borderRadius: '12px',
                        border: '1px solid #cbd5e1',
                        fontSize: '0.92rem',
                        outline: 'none',
                        boxSizing: 'border-box',
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Dietary Preferences */}
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.5rem' }}>
                  Dietary Preferences
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem' }}>
                  {DIETARY_OPTIONS.map((diet) => {
                    const isSelected =
                      diet === 'None / All Food'
                        ? formData.dietary_preferences.length === 0
                        : formData.dietary_preferences.includes(diet);
                    return (
                      <button
                        key={diet}
                        type="button"
                        onClick={() => toggleDietary(diet)}
                        style={{
                          backgroundColor: isSelected ? '#dcfce7' : '#f8fafc',
                          color: isSelected ? '#15803d' : '#334155',
                          border: isSelected ? '1px solid #86efac' : '1px solid #e2e8f0',
                          borderRadius: '9999px',
                          padding: '0.35rem 0.75rem',
                          fontSize: '0.8rem',
                          fontWeight: isSelected ? 600 : 500,
                          cursor: 'pointer',
                        }}
                      >
                        {diet}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Special Requirements */}
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                  Special Notes / Accessibility (Optional)
                </label>
                <textarea
                  rows={2}
                  placeholder="e.g. Prefer walking tours, need wheelchair access, celebrating an anniversary..."
                  value={formData.additional_requirements}
                  onChange={(e) => handleChange('additional_requirements', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '12px',
                    border: '1px solid #cbd5e1',
                    fontSize: '0.88rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
            </motion.div>
          )}

          {submitError && (
            <div
              style={{
                backgroundColor: '#fef2f2',
                border: '1px solid #fecaca',
                color: '#b91c1c',
                borderRadius: '10px',
                padding: '0.75rem 1rem',
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginTop: '1.5rem',
              }}
            >
              <AlertCircle size={16} />
              <span>{submitError}</span>
            </div>
          )}

          {isSubmitting && (
            <div
              style={{
                backgroundColor: '#eff6ff',
                border: '1px solid #bfdbfe',
                color: '#1d4ed8',
                borderRadius: '10px',
                padding: '0.65rem 1rem',
                fontSize: '0.82rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginTop: '1.25rem',
              }}
            >
              <Loader2 size={15} className="spin" />
              <span>AI is crafting your personalized itinerary and optimizing routes (approx 5-10s)...</span>
            </div>
          )}

          {/* Action Buttons Row */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: '1.5rem',
              paddingTop: '1.25rem',
              borderTop: '1px solid #f1f5f9',
            }}
          >
            {step > 1 ? (
              <button
                type="button"
                onClick={handleBack}
                disabled={isSubmitting}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  backgroundColor: '#ffffff',
                  color: '#475569',
                  border: '1px solid #cbd5e1',
                  borderRadius: '10px',
                  padding: '0.75rem 1.25rem',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <ArrowLeft size={16} />
                <span>Previous</span>
              </button>
            ) : (
              <div />
            )}

            {step < 3 ? (
              <button
                type="button"
                onClick={handleNext}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  backgroundColor: '#2563eb',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '0.75rem 1.5rem',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(37, 99, 235, 0.25)',
                }}
              >
                <span>Next Step</span>
                <ArrowRight size={16} />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleGenerate}
                disabled={isSubmitting}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '0.85rem 1.85rem',
                  fontSize: '0.98rem',
                  fontWeight: 700,
                  cursor: isSubmitting ? 'not-allowed' : 'pointer',
                  boxShadow: '0 6px 20px rgba(37, 99, 235, 0.35)',
                }}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 size={18} className="spin" />
                    <span>Generating Itinerary...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    <span>Generate Itinerary</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
