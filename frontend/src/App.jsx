// frontend/src/App.jsx
// Complete application shell matching the 7-page PDF reference
// Seamlessly connects all 9 screens with real backend APIs and Supabase persistence

import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import AuthModal from './components/AuthModal';
import DashboardView from './components/DashboardView';
import CreateTrip from './components/CreateTrip';
import ItineraryDisplay from './components/ItineraryDisplay';
import ExploreDestinations from './components/ExploreDestinations';
import SavedPlaces from './components/SavedPlaces';
import TripHistory from './components/TripHistory';
import SharedTripView from './components/SharedTripView';
import tripsAPI from './services/tripsAPI';

function App() {
  // Navigation active tab:
  // 'landing' | 'overview' | 'explore' | 'plan' | 'view_itinerary' | 'saved_places' | 'history' | 'shared'
  const [activeTab, setActiveTab] = useState('landing');
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState({
    name: 'Alex Johnson',
    initials: 'AJ',
    email: 'alex.johnson@travelplanner.io',
  });

  // Share token state
  const [shareToken, setShareToken] = useState(null);

  // Active viewed trip state
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [savedItinerary, setSavedItinerary] = useState(null);
  const [isLoadingItinerary, setIsLoadingItinerary] = useState(false);
  const [itineraryError, setItineraryError] = useState(null);

  // Pre-fill destination for CreateTrip
  const [prefillDestination, setPrefillDestination] = useState('');

  // Trip and saved places counts
  const [savedTripsCount, setSavedTripsCount] = useState(0);
  const [savedPlacesCount, setSavedPlacesCount] = useState(6);

  // ── Detect ?share=TOKEN on initial load ──────────────────────────────────
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('share');
    if (token) {
      setShareToken(token);
      setActiveTab('shared');
    }
  }, []);

  // Fetch count of saved trips for badge display
  const refreshTripCount = async () => {
    try {
      const data = await tripsAPI.getAllTrips();
      if (Array.isArray(data)) {
        setSavedTripsCount(data.length);
      }
    } catch {
      // Quiet fail for badge
    }
  };

  useEffect(() => {
    refreshTripCount();
  }, [activeTab]);

  // Handle selecting a trip to view its day-wise itinerary
  const handleSelectTrip = async (trip) => {
    setSelectedTrip(trip);
    setActiveTab('view_itinerary');
    setIsLoadingItinerary(true);
    setItineraryError(null);
    setSavedItinerary(null);

    try {
      const itin = await tripsAPI.getSavedItinerary(trip.id);
      setSavedItinerary(itin);
    } catch (err) {
      // If no pre-saved itinerary exists, we allow on-demand generation in ItineraryDisplay
      setItineraryError(null);
      setSavedItinerary(null);
    } finally {
      setIsLoadingItinerary(false);
    }
  };

  // Generate itinerary for selected trip on demand
  const handleGenerateForSelectedTrip = async () => {
    if (!selectedTrip) return;
    setIsLoadingItinerary(true);
    setItineraryError(null);

    const payload = {
      destination: selectedTrip.destination,
      start_date: selectedTrip.start_date,
      end_date: selectedTrip.end_date,
      num_travelers: selectedTrip.num_travelers || 1,
      budget: selectedTrip.budget,
      travel_style: (selectedTrip.travel_style || 'cultural').toLowerCase(),
      travel_interests: selectedTrip.travel_interests || ['History & Heritage'],
      dietary_preferences: selectedTrip.dietary_preferences || [],
      travel_pace: selectedTrip.travel_pace || 'moderate',
      primary_vibe: selectedTrip.primary_vibe || 'cultural',
      secondary_vibes: selectedTrip.secondary_vibes || [],
      additional_requirements: selectedTrip.additional_requirements || null,
      trip_id: selectedTrip.id,
    };

    try {
      const result = await tripsAPI.generateItinerary(payload);
      setSavedItinerary(result);
      refreshTripCount();
    } catch (err) {
      setItineraryError(err.message || 'Failed to generate daily itinerary.');
    } finally {
      setIsLoadingItinerary(false);
    }
  };

  // Handle when multi-step creator successfully finishes
  const handleItineraryReady = (createdTrip, generatedItinerary) => {
    setSelectedTrip(createdTrip);
    setSavedItinerary(generatedItinerary);
    setActiveTab('view_itinerary');
    refreshTripCount();
  };

  // Handle starting planner with a specific destination prefilled
  const handleStartPlanDestination = (destinationName) => {
    setPrefillDestination(destinationName);
    setActiveTab('plan');
  };

  // ── Public Shared Trip View (bypass normal app chrome) ────────────────────
  if (activeTab === 'shared' && shareToken) {
    return <SharedTripView shareToken={shareToken} />;
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8fafc' }}>
      {/* ── Top Navigation Bar ───────────────────────────────────────── */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        savedTripsCount={savedTripsCount}
        savedPlacesCount={savedPlacesCount}
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthOpen(true)}
      />

      {/* ── Main View Router ─────────────────────────────────────────── */}
      <main style={{ flex: 1 }}>
        {/* 1. Landing Page (Pages 1 & 2) */}
        {activeTab === 'landing' && (
          <LandingPage
            onStartPlanning={() => setActiveTab('plan')}
            onExplore={() => setActiveTab('explore')}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}

        {/* 2. Overview Dashboard (Page 2) */}
        {activeTab === 'overview' && (
          <DashboardView
            onSelectTrip={handleSelectTrip}
            onPlanNewTrip={() => {
              setPrefillDestination('');
              setActiveTab('plan');
            }}
            onExploreDestinations={() => setActiveTab('explore')}
            onViewSavedPlaces={() => setActiveTab('saved_places')}
            savedTripsCount={savedTripsCount}
            savedPlacesCount={savedPlacesCount}
            currentUser={currentUser}
          />
        )}

        {/* 3. Multi-Step Trip Planner (Page 3) */}
        {activeTab === 'plan' && (
          <CreateTrip
            prefillDestination={prefillDestination}
            onItineraryReady={handleItineraryReady}
            onCancel={() => setActiveTab('overview')}
          />
        )}

        {/* 4. Generated Day-wise Itinerary (Pages 4 & 5) */}
        {activeTab === 'view_itinerary' && (
          <ItineraryDisplay
            trip={selectedTrip}
            itinerary={savedItinerary}
            isLoading={isLoadingItinerary}
            error={itineraryError}
            onGenerate={handleGenerateForSelectedTrip}
            destination={selectedTrip?.destination || ''}
            onBackToTrips={() => setActiveTab('overview')}
          />
        )}

        {/* 5. Explore Destinations & Details Modal (Pages 5 & 6) */}
        {activeTab === 'explore' && (
          <ExploreDestinations onStartPlanningDestination={handleStartPlanDestination} />
        )}

        {/* 6. Saved Places (Pages 6 & 7) */}
        {activeTab === 'saved_places' && (
          <SavedPlaces onPlanDestination={handleStartPlanDestination} />
        )}

        {/* 7. Trip History & Timeline (Page 7) */}
        {activeTab === 'history' && (
          <TripHistory
            onSelectTrip={handleSelectTrip}
            onPlanNewTrip={() => {
              setPrefillDestination('');
              setActiveTab('plan');
            }}
          />
        )}
      </main>

      {/* ── Authentication Dialog (Page 2) ───────────────────────────── */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onLoginSuccess={(user) => {
          setCurrentUser(user);
          setIsAuthOpen(false);
        }}
      />
    </div>
  );
}

export default App;
