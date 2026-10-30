// frontend/src/components/Navbar.jsx
// Modern clean navigation bar matching the 7-page PDF reference

import React, { useState } from 'react';
import {
  Compass,
  MapPin,
  Calendar,
  Sparkles,
  Bookmark,
  History,
  PlusCircle,
  User,
  Menu,
  X,
  Luggage,
} from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  savedTripsCount = 0,
  savedPlacesCount = 0,
  onOpenAuth,
  currentUser = { name: 'Alex Johnson', initials: 'AJ', email: 'alex@example.com' },
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Compass },
    { id: 'explore', label: 'Explore', icon: MapPin },
    { id: 'plan', label: 'Plan Trip', icon: Sparkles, highlight: true },
    { id: 'saved_places', label: 'Saved Places', icon: Bookmark, badge: savedPlacesCount },
    { id: 'history', label: 'Trip History', icon: History, badge: savedTripsCount },
  ];

  const handleSelectTab = (tabId) => {
    setActiveTab(tabId);
    setMobileMenuOpen(false);
  };

  return (
    <nav
      style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        boxShadow: '0 1px 3px rgba(15, 23, 42, 0.05)',
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '0 1.5rem',
          height: '4.25rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Brand Logo */}
        <div
          onClick={() => handleSelectTab('landing')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            cursor: 'pointer',
            userSelect: 'none',
          }}
        >
          <div
            style={{
              width: '2.4rem',
              height: '2.4rem',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              fontSize: '1.2rem',
              boxShadow: '0 4px 10px rgba(37, 99, 235, 0.25)',
            }}
          >
            ✈️
          </div>
          <div>
            <span
              style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                color: '#0f172a',
                letterSpacing: '-0.025em',
              }}
            >
              Travel<span style={{ color: '#2563eb' }}>Planner</span>
            </span>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <div
          style={{
            display: 'none',
            alignItems: 'center',
            gap: '0.4rem',
          }}
          className="desktop-nav"
        >
          <style>{`
            @media (min-width: 820px) {
              .desktop-nav { display: flex !important; }
              .mobile-toggle { display: none !important; }
            }
          `}</style>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleSelectTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  padding: '0.5rem 0.95rem',
                  borderRadius: '9999px',
                  border: 'none',
                  fontSize: '0.9rem',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  backgroundColor: isActive ? '#eff6ff' : 'transparent',
                  color: isActive ? '#1d4ed8' : '#475569',
                  transition: 'all 0.15s ease',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = '#f8fafc';
                    e.currentTarget.style.color = '#0f172a';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#475569';
                  }
                }}
              >
                <Icon size={16} strokeWidth={isActive ? 2.2 : 1.8} />
                <span>{item.label}</span>
                {item.badge > 0 && (
                  <span
                    style={{
                      backgroundColor: isActive ? '#2563eb' : '#e2e8f0',
                      color: isActive ? '#ffffff' : '#475569',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '0.1rem 0.45rem',
                      borderRadius: '9999px',
                      marginLeft: '0.15rem',
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Right Actions: Plan Button & User Avatar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {activeTab !== 'plan' && (
            <button
              onClick={() => handleSelectTab('plan')}
              style={{
                display: 'none',
                alignItems: 'center',
                gap: '0.45rem',
                backgroundColor: '#eff6ff',
                color: '#1d4ed8',
                border: '1px solid #bfdbfe',
                padding: '0.5rem 1rem',
                borderRadius: '9999px',
                fontSize: '0.88rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              className="quick-plan-btn"
            >
              <style>{`
                @media (min-width: 640px) {
                  .quick-plan-btn { display: inline-flex !important; }
                }
              `}</style>
              <PlusCircle size={15} />
              <span>New Trip</span>
            </button>
          )}

          {/* User Profile Pill matching PDF Page 2 */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowUserDropdown(!showUserDropdown)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                padding: '0.35rem 0.65rem 0.35rem 0.4rem',
                borderRadius: '9999px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              title="User Account"
            >
              <div
                style={{
                  width: '2rem',
                  height: '2rem',
                  borderRadius: '9999px',
                  backgroundColor: '#dbeafe',
                  color: '#1e40af',
                  fontWeight: 700,
                  fontSize: '0.82rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {currentUser?.initials || 'LU'}
              </div>
              <span
                style={{
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  color: '#1e293b',
                  display: 'none',
                }}
                className="user-name-label"
              >
                <style>{`
                  @media (min-width: 768px) {
                    .user-name-label { display: inline !important; }
                  }
                `}</style>
                {currentUser?.name || 'Alex'}
              </span>
            </button>

            {/* Dropdown Menu */}
            {showUserDropdown && (
              <div
                style={{
                  position: 'absolute',
                  right: 0,
                  top: '2.8rem',
                  width: '220px',
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
                  border: '1px solid #e2e8f0',
                  padding: '0.5rem',
                  zIndex: 60,
                }}
              >
                <div
                  style={{
                    padding: '0.75rem',
                    borderBottom: '1px solid #f1f5f9',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#0f172a' }}>
                    {currentUser?.name || 'Alex Johnson'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    {currentUser?.email || 'alex@example.com'}
                  </div>
                </div>

                <div style={{ padding: '0.35rem 0' }}>
                  <button
                    onClick={() => {
                      handleSelectTab('overview');
                      setShowUserDropdown(false);
                    }}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.5rem 0.75rem',
                      fontSize: '0.85rem',
                      color: '#334155',
                      border: 'none',
                      background: 'transparent',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      textAlign: 'left',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <Compass size={15} /> Dashboard
                  </button>
                  <button
                    onClick={() => {
                      handleSelectTab('history');
                      setShowUserDropdown(false);
                    }}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.5rem 0.75rem',
                      fontSize: '0.85rem',
                      color: '#334155',
                      border: 'none',
                      background: 'transparent',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      textAlign: 'left',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <Luggage size={15} /> My Trips ({savedTripsCount})
                  </button>
                  <button
                    onClick={() => {
                      setShowUserDropdown(false);
                      if (onOpenAuth) onOpenAuth();
                    }}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.5rem 0.75rem',
                      fontSize: '0.85rem',
                      color: '#2563eb',
                      fontWeight: 600,
                      border: 'none',
                      background: 'transparent',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      borderTop: '1px solid #f1f5f9',
                      marginTop: '0.35rem',
                      paddingTop: '0.6rem',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#eff6ff')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <User size={15} /> Switch / Sign In
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Mobile Menu Hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '2.4rem',
              height: '2.4rem',
              borderRadius: '8px',
              border: '1px solid #e2e8f0',
              backgroundColor: '#ffffff',
              color: '#334155',
              cursor: 'pointer',
            }}
            className="mobile-toggle"
            aria-label="Toggle navigation"
          >
            {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div
          style={{
            borderTop: '1px solid #f1f5f9',
            backgroundColor: '#ffffff',
            padding: '1rem 1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
          }}
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleSelectTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  borderRadius: '10px',
                  border: 'none',
                  fontSize: '0.95rem',
                  fontWeight: isActive ? 600 : 500,
                  backgroundColor: isActive ? '#eff6ff' : '#ffffff',
                  color: isActive ? '#1d4ed8' : '#334155',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <Icon size={18} />
                  <span>{item.label}</span>
                </div>
                {item.badge > 0 && (
                  <span
                    style={{
                      backgroundColor: isActive ? '#2563eb' : '#e2e8f0',
                      color: isActive ? '#ffffff' : '#475569',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '0.15rem 0.5rem',
                      borderRadius: '9999px',
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
}

