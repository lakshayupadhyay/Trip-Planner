// frontend/src/components/LandingPage.jsx
// Beautiful Landing Page matching Pages 1 & 2 of PDF reference

import React from 'react';
import {
  Sparkles,
  ArrowRight,
  Compass,
  MapPin,
  Calendar,
  Clock,
  ShieldCheck,
  TrendingUp,
  DollarSign,
  Heart,
  Star,
  CheckCircle2,
  Share2,
} from 'lucide-react';

export default function LandingPage({ onStartPlanning, onExplore, onOpenAuth }) {
  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered Planning',
      description:
        'Intelligent suggestions tailored to your unique vibe, style, and budget. Never start from a blank page again.',
      accent: '#3b82f6',
      badge: 'Smart Engine',
    },
    {
      icon: Compass,
      title: 'Smart Route Optimization',
      description:
        'Save hours with geography & transit-aware sequencing. Zero zigzagging across cities with seamless itineraries.',
      accent: '#0ea5e9',
      badge: 'Efficient Transit',
    },
    {
      icon: DollarSign,
      title: 'Budget-Conscious',
      description:
        'Real-time cost estimates for activities, stays, and dining. Stay in control whether backpacking or luxury traveling.',
      accent: '#10b981',
      badge: 'Cost Control',
    },
    {
      icon: Clock,
      title: 'Paced Time Management',
      description:
        'Harmonious morning, afternoon, and evening blocks with realistic transit buffers so you never feel rushed.',
      accent: '#8b5cf6',
      badge: 'Stress-Free',
    },
  ];

  const partners = [
    { name: 'Airbnb', logo: '🏠 Airbnb' },
    { name: 'Expedia', logo: '✈️ Expedia' },
    { name: 'TripAdvisor', logo: '🦉 TripAdvisor' },
    { name: 'Booking.com', logo: '🏨 Booking.com' },
    { name: 'Lonely Planet', logo: '🌍 Lonely Planet' },
  ];

  const testimonials = [
    {
      quote:
        'Saved me over 15 hours of manual research for our 7-day trip to Kyoto. The route sequencing was flawless and the local ramen recommendations were out of this world.',
      author: 'Elena Rostova',
      role: 'Solo Explorer • 12 Countries',
      avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80',
      rating: 5,
    },
    {
      quote:
        'Traveling with two kids is stressful. TravelPlanner’s pacing and downtime buffers made our Italian family trip the smoothest vacation we’ve ever had.',
      author: 'Marcus & Chloe Vance',
      role: 'Family Travelers • London, UK',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&q=80',
      rating: 5,
    },
    {
      quote:
        'Being able to export to PDF and share a live link with our group chat eliminated all the back-and-forth arguments. Absolute 10/10 travel SaaS.',
      author: 'David Chen',
      role: 'Adventure Group Lead',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=120&q=80',
      rating: 5,
    },
  ];

  return (
    <div style={{ backgroundColor: '#ffffff', minHeight: '100vh', overflowX: 'hidden' }}>
      {/* ── 1. HERO SECTION ────────────────────────────────────────────── */}
      <section
        style={{
          background: 'linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%)',
          padding: '4rem 1.5rem 5rem',
          position: 'relative',
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          {/* Top Badge */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: '#eff6ff',
              border: '1px solid #bfdbfe',
              color: '#1d4ed8',
              borderRadius: '9999px',
              padding: '0.35rem 1rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              marginBottom: '1.5rem',
              boxShadow: '0 2px 6px rgba(37, 99, 235, 0.08)',
            }}
          >
            <Sparkles size={16} />
            <span>AI-Powered Travel Planning for 2026</span>
          </div>

          {/* Headline */}
          <h1
            style={{
              fontSize: 'clamp(2.4rem, 5vw, 3.8rem)',
              fontWeight: 800,
              color: '#0f172a',
              lineHeight: 1.15,
              letterSpacing: '-0.03em',
              maxWidth: '850px',
              margin: '0 0 1.25rem',
            }}
          >
            Plan your next adventure <br />
            <span
              style={{
                background: 'linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              in seconds.
            </span>
          </h1>

          {/* Subtitle */}
          <p
            style={{
              fontSize: 'clamp(1rem, 2vw, 1.2rem)',
              color: '#475569',
              lineHeight: 1.6,
              maxWidth: '680px',
              margin: '0 0 2.5rem',
            }}
          >
            Experience bespoke itineraries tailored to your unique travel style, interests, and budget powered by
            cutting-edge AI.
          </p>

          {/* Hero CTAs */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              flexWrap: 'wrap',
              justifyContent: 'center',
              marginBottom: '3.5rem',
            }}
          >
            <button
              onClick={onStartPlanning}
              style={{
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '12px',
                padding: '0.9rem 1.85rem',
                fontSize: '1.05rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.6rem',
                boxShadow: '0 10px 25px -4px rgba(37, 99, 235, 0.35)',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#1d4ed8';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#2563eb';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <Sparkles size={18} />
              <span>Start Planning for Free</span>
              <ArrowRight size={18} />
            </button>

            <button
              onClick={onExplore}
              style={{
                backgroundColor: '#ffffff',
                color: '#1e293b',
                border: '1px solid #cbd5e1',
                borderRadius: '12px',
                padding: '0.9rem 1.6rem',
                fontSize: '1.05rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f8fafc';
                e.currentTarget.style.borderColor = '#94a3b8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#ffffff';
                e.currentTarget.style.borderColor = '#cbd5e1';
              }}
            >
              <Compass size={18} color="#2563eb" />
              <span>Explore Destinations</span>
            </button>
          </div>

          {/* Interactive Preview Mock Card matching PDF reference */}
          <div
            style={{
              width: '100%',
              maxWidth: '920px',
              backgroundColor: '#ffffff',
              borderRadius: '20px',
              boxShadow: '0 20px 40px -15px rgba(15, 23, 42, 0.12), 0 0 0 1px rgba(226, 232, 240, 0.8)',
              overflow: 'hidden',
              textAlign: 'left',
              position: 'relative',
            }}
          >
            {/* Window bar */}
            <div
              style={{
                backgroundColor: '#f8fafc',
                borderBottom: '1px solid #e2e8f0',
                padding: '0.75rem 1.25rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#f59e0b' }} />
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#10b981' }} />
                <span style={{ fontSize: '0.8rem', color: '#64748b', marginLeft: '0.5rem', fontWeight: 500 }}>
                  Personalized Itinerary Preview &bull; Kyoto, Japan
                </span>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <span
                  style={{
                    backgroundColor: '#dcfce7',
                    color: '#15803d',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.55rem',
                    borderRadius: '9999px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                  }}
                >
                  <CheckCircle2 size={12} /> 100% Route Optimized
                </span>
              </div>
            </div>

            {/* Preview Card Body */}
            <div
              style={{
                padding: '1.75rem',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.5rem',
                alignItems: 'center',
              }}
            >
              {/* Trip Highlight Image & Badges */}
              <div style={{ position: 'relative', borderRadius: '14px', overflow: 'hidden' }}>
                <img
                  src="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=700&q=80"
                  alt="Kyoto Japan"
                  style={{ width: '100%', height: '220px', objectFit: 'cover', display: 'block' }}
                />
                <div
                  style={{
                    position: 'absolute',
                    top: '0.75rem',
                    left: '0.75rem',
                    backgroundColor: 'rgba(15, 23, 42, 0.75)',
                    backdropFilter: 'blur(4px)',
                    color: '#ffffff',
                    padding: '0.35rem 0.75rem',
                    borderRadius: '9999px',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                  }}
                >
                  ⛩️ Cultural & Foodie
                </div>
                <div
                  style={{
                    position: 'absolute',
                    bottom: '0.75rem',
                    left: '0.75rem',
                    right: '0.75rem',
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(6px)',
                    padding: '0.65rem 0.9rem',
                    borderRadius: '10px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#0f172a' }}>Kyoto Autumn Getaway</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>3 Days &bull; 2 Travelers</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#2563eb' }}>$1,200 Est</div>
                    <div style={{ fontSize: '0.75rem', color: '#16a34a' }}>★ 4.9 Rating</div>
                  </div>
                </div>
              </div>

              {/* Day Breakdown Preview */}
              <div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '1rem',
                  }}
                >
                  <span
                    style={{
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      color: '#2563eb',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    Day 1 Sequence &bull; Paced
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Daily Cap: $180</span>
                </div>

                {/* Timeline items */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      backgroundColor: '#f8fafc',
                      padding: '0.65rem 0.85rem',
                      borderRadius: '10px',
                      borderLeft: '3px solid #3b82f6',
                    }}
                  >
                    <span style={{ fontSize: '1.1rem' }}>🌅</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem', color: '#1e293b' }}>
                        Fushimi Inari Shrine Hike
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>08:30 AM &bull; Free Entry &bull; 2 hrs</div>
                    </div>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      backgroundColor: '#f8fafc',
                      padding: '0.65rem 0.85rem',
                      borderRadius: '10px',
                      borderLeft: '3px solid #0ea5e9',
                    }}
                  >
                    <span style={{ fontSize: '1.1rem' }}>☀️</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem', color: '#1e293b' }}>
                        Arashiyama Bamboo Grove & Tenryu-ji
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>01:15 PM &bull; $15 Entry &bull; 2.5 hrs</div>
                    </div>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      backgroundColor: '#f8fafc',
                      padding: '0.65rem 0.85rem',
                      borderRadius: '10px',
                      borderLeft: '3px solid #8b5cf6',
                    }}
                  >
                    <span style={{ fontSize: '1.1rem' }}>🌙</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem', color: '#1e293b' }}>
                        Gion Historic District & Kaiseki Dinner
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>06:30 PM &bull; $65 Dinner &bull; Evening Charm</div>
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.75rem' }}>
                  <button
                    onClick={onStartPlanning}
                    style={{
                      flex: 1,
                      backgroundColor: '#eff6ff',
                      color: '#1d4ed8',
                      border: '1px solid #bfdbfe',
                      padding: '0.65rem',
                      borderRadius: '8px',
                      fontWeight: 600,
                      fontSize: '0.85rem',
                      cursor: 'pointer',
                      textAlign: 'center',
                    }}
                  >
                    Customize This Itinerary &rarr;
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. PARTNERS / SOCIAL PROOF ─────────────────────────────────── */}
      <section
        style={{
          borderTop: '1px solid #f1f5f9',
          borderBottom: '1px solid #f1f5f9',
          padding: '2.5rem 1.5rem',
          backgroundColor: '#fafbfc',
        }}
      >
        <div style={{ maxWidth: '1100px', margin: '0 auto', textAlign: 'center' }}>
          <p
            style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              color: '#94a3b8',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              margin: '0 0 1.5rem',
            }}
          >
            Seamlessly integrating inspiration from leading travel platforms
          </p>
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '2.5rem',
            }}
          >
            {partners.map((partner) => (
              <span
                key={partner.name}
                style={{
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  color: '#64748b',
                  letterSpacing: '-0.02em',
                  opacity: 0.85,
                }}
              >
                {partner.logo}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── 3. FEATURES ("Built for the modern traveler") ──────────────── */}
      <section style={{ padding: '5rem 1.5rem', backgroundColor: '#ffffff' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
            <span
              style={{
                fontSize: '0.82rem',
                fontWeight: 700,
                color: '#2563eb',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
              }}
            >
              Why Choose TravelPlanner
            </span>
            <h2
              style={{
                fontSize: 'clamp(2rem, 3.5vw, 2.75rem)',
                fontWeight: 800,
                color: '#0f172a',
                margin: '0.5rem 0 1rem',
                letterSpacing: '-0.025em',
              }}
            >
              Built for the modern traveler
            </h2>
            <p style={{ fontSize: '1.05rem', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>
              Everything you need to turn vague vacation ideas into meticulously timed, customized travel plans.
            </p>
          </div>

          {/* 4 Feature Cards */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: '1.75rem',
            }}
          >
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div
                  key={idx}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '16px',
                    padding: '2rem',
                    transition: 'all 0.25s ease',
                    boxShadow: '0 4px 15px -2px rgba(15, 23, 42, 0.04)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 16px 30px -5px rgba(37, 99, 235, 0.12)';
                    e.currentTarget.style.borderColor = '#bfdbfe';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 4px 15px -2px rgba(15, 23, 42, 0.04)';
                    e.currentTarget.style.borderColor = '#e2e8f0';
                  }}
                >
                  <div>
                    <div
                      style={{
                        width: '3rem',
                        height: '3rem',
                        borderRadius: '12px',
                        backgroundColor: '#eff6ff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginBottom: '1.25rem',
                        color: feature.accent,
                      }}
                    >
                      <Icon size={24} />
                    </div>
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        backgroundColor: '#f1f5f9',
                        color: '#475569',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '9999px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                      }}
                    >
                      {feature.badge}
                    </span>
                    <h3
                      style={{
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        color: '#0f172a',
                        margin: '0.75rem 0 0.5rem',
                      }}
                    >
                      {feature.title}
                    </h3>
                    <p style={{ fontSize: '0.92rem', color: '#64748b', lineHeight: 1.6, margin: 0 }}>
                      {feature.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── 4. TESTIMONIALS CAROUSEL ───────────────────────────────────── */}
      <section style={{ padding: '4.5rem 1.5rem', backgroundColor: '#f8fafc', borderTop: '1px solid #e2e8f0' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <span
              style={{
                fontSize: '0.82rem',
                fontWeight: 700,
                color: '#2563eb',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
              }}
            >
              Traveler Experiences
            </span>
            <h2
              style={{
                fontSize: 'clamp(1.8rem, 3vw, 2.4rem)',
                fontWeight: 800,
                color: '#0f172a',
                margin: '0.5rem 0 0',
              }}
            >
              Loved by travelers worldwide
            </h2>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {testimonials.map((t, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '16px',
                  padding: '1.75rem',
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 4px 12px rgba(15, 23, 42, 0.04)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', gap: '0.2rem', marginBottom: '1rem', color: '#f59e0b' }}>
                    {[...Array(t.rating)].map((_, i) => (
                      <Star key={i} size={16} fill="#f59e0b" />
                    ))}
                  </div>
                  <p style={{ fontSize: '0.95rem', color: '#334155', lineHeight: 1.6, fontStyle: 'italic', margin: 0 }}>
                    &ldquo;{t.quote}&rdquo;
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '1.5rem' }}>
                  <img
                    src={t.avatar}
                    alt={t.author}
                    style={{ width: '42px', height: '42px', borderRadius: '50%', objectFit: 'cover' }}
                  />
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a' }}>{t.author}</div>
                    <div style={{ fontSize: '0.78rem', color: '#64748b' }}>{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 5. DARK NAVY CTA CARD matching PDF reference ───────────────── */}
      <section style={{ padding: '4.5rem 1.5rem 5.5rem', backgroundColor: '#ffffff' }}>
        <div
          style={{
            maxWidth: '1100px',
            margin: '0 auto',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #2563eb 100%)',
            borderRadius: '24px',
            padding: '4rem 2rem',
            textAlign: 'center',
            color: '#ffffff',
            boxShadow: '0 25px 50px -12px rgba(15, 23, 42, 0.25)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Subtle background glow */}
          <div
            style={{
              position: 'absolute',
              top: '-30%',
              right: '-10%',
              width: '400px',
              height: '400px',
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(56, 189, 248, 0.2) 0%, transparent 70%)',
              pointerEvents: 'none',
            }}
          />

          <span
            style={{
              fontSize: '0.85rem',
              fontWeight: 700,
              backgroundColor: 'rgba(255, 255, 255, 0.12)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '9999px',
              padding: '0.35rem 1rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              marginBottom: '1.25rem',
            }}
          >
            <Sparkles size={14} /> Ready for your next journey?
          </span>

          <h2
            style={{
              fontSize: 'clamp(2.2rem, 4vw, 3.2rem)',
              fontWeight: 800,
              margin: '0 0 1rem',
              letterSpacing: '-0.025em',
            }}
          >
            Your next story starts here.
          </h2>

          <p
            style={{
              fontSize: 'clamp(1rem, 1.8vw, 1.15rem)',
              color: '#cbd5e1',
              maxWidth: '620px',
              margin: '0 auto 2.5rem',
              lineHeight: 1.6,
            }}
          >
            Join thousands of travelers planning stress-free, personalized trips in minutes. AI itinerary generation,
            cost estimation, and real-time route optimization.
          </p>

          <button
            onClick={onStartPlanning}
            style={{
              backgroundColor: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              borderRadius: '12px',
              padding: '1rem 2.25rem',
              fontSize: '1.05rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.6rem',
              boxShadow: '0 10px 25px rgba(56, 189, 248, 0.35)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#7dd3fc';
              e.currentTarget.style.transform = 'scale(1.03)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#38bdf8';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            <Sparkles size={18} />
            <span>Create My Itinerary</span>
            <ArrowRight size={18} />
          </button>
        </div>
      </section>

      {/* ── 6. FOOTER ──────────────────────────────────────────────────── */}
      <footer
        style={{
          borderTop: '1px solid #e2e8f0',
          padding: '2.5rem 1.5rem',
          backgroundColor: '#f8fafc',
          textAlign: 'center',
          color: '#64748b',
          fontSize: '0.88rem',
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.25rem' }}>✈️</span>
            <strong style={{ color: '#0f172a' }}>TravelPlanner</strong>
            <span>&bull; Personalized Travel Itinerary Planner</span>
          </div>
          <p style={{ margin: 0 }}>
            Powered by Gemini, Groq & Supabase. Clean modern travel SaaS architecture.
          </p>
        </div>
      </footer>
    </div>
  );
}

