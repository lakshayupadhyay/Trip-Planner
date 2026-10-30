// tripsAPI.js — Centralized API service for trips endpoints
// Uses Vite's import.meta.env for environment variable access

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Format error response from FastAPI (including 422 Unprocessable Entity)
 * into a human-readable string for the frontend UI.
 */
async function parseErrorMessage(response) {
  let errorMessage = `HTTP error! status: ${response.status}`;
  try {
    const errorData = await response.json();
    if (Array.isArray(errorData.detail)) {
      // Format 422 Pydantic validation errors: [{loc: [...], msg: "..."}]
      errorMessage = errorData.detail
        .map((err) => {
          const field = err.loc && err.loc.length > 1 ? err.loc[err.loc.length - 1] : 'Field';
          return `${field}: ${err.msg}`;
        })
        .join('; ');
    } else if (typeof errorData.detail === 'string') {
      errorMessage = errorData.detail;
    } else if (errorData.message) {
      errorMessage = errorData.message;
    }
  } catch {
    // If response body is not JSON, retain default status message
  }
  return errorMessage;
}

const tripsAPI = {
  /**
   * Create a new trip
   * POST /api/v1/trips/
   * @param {Object} tripData - Trip details including destination, dates, budget, preferences
   * @returns {Promise<Object>} Created trip object
   */
  createTrip: async (tripData) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tripData),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Get all trips (optionally filtered by user ID)
   * GET /api/v1/trips/
   * @param {string} [userId] - Optional user ID
   * @returns {Promise<Array>} Array of trip objects
   */
  getAllTrips: async (userId) => {
    const url = userId
      ? `${API_BASE_URL}/api/v1/trips/?user_id=${encodeURIComponent(userId)}`
      : `${API_BASE_URL}/api/v1/trips/`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Get all trips for a specific user
   * GET /api/v1/trips/{userId}
   * @param {string} userId - The user's ID
   * @returns {Promise<Array>} Array of trip objects
   */
  getTripsByUser: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Get a specific trip by trip ID
   * GET /api/v1/trips/{tripId}
   * @param {string} tripId - The trip's ID
   * @param {string} [userId] - Optional user ID
   * @returns {Promise<Object>} Trip object
   */
  getTripById: async (tripId, userId) => {
    const url = userId
      ? `${API_BASE_URL}/api/v1/trips/${tripId}/${userId}`
      : `${API_BASE_URL}/api/v1/trips/${tripId}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Update an existing trip and its preferences
   * PUT /api/v1/trips/{tripId}
   * @param {string} tripId - The trip's ID
   * @param {Object} updateData - Updated fields
   * @returns {Promise<Object>} Refreshed trip object
   */
  updateTrip: async (tripId, updateData) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Permanently delete a trip and all its associated daily itineraries
   * DELETE /api/v1/trips/{tripId}
   * @param {string} tripId - The trip's ID
   * @returns {Promise<Object>} { success, message, deleted_trip_id }
   */
  deleteTrip: async (tripId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Retrieve saved itinerary for a trip without triggering AI generation
   * GET /api/v1/trips/{tripId}/itinerary
   * @param {string} tripId - The trip's ID
   * @returns {Promise<Object>} ItineraryResponse
   */
  getSavedItinerary: async (tripId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}/itinerary`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Preview generated AI prompt for travel preferences
   * POST /api/v1/itinerary/prompt-preview
   * @param {Object} preferences - Travel preferences object
   * @returns {Promise<Object>} { destination, duration_days, prompt }
   */
  previewPrompt: async (preferences) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/itinerary/prompt-preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Get AI-powered destination recommendations
   * POST /api/v1/recommendations/destinations
   * @param {Object} preferences - Travel preferences object
   * @returns {Promise<Object>} { recommendations: [...], notes }
   */
  getDestinationRecommendations: async (preferences) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/destinations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Get AI-powered attraction, activity, and dining recommendations for a destination
   * POST /api/v1/recommendations/activities
   * @param {Object} preferences - Destination and travel preferences object
   * @returns {Promise<Object>} { destination, recommendations: [...], notes }
   */
  getActivityRecommendations: async (preferences) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/activities`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Generate complete day-by-day itinerary
   * POST /api/v1/itinerary/generate
   * @param {Object} preferences - Trip preferences payload
   * @returns {Promise<Object>} ItineraryResponse
   */
  generateItinerary: async (preferences) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/itinerary/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Optimize routes, transit legs, and schedules for an entire itinerary
   * POST /api/v1/itinerary/optimize-route
   * @param {Object} itinerary - Full ItineraryResponse object
   * @param {string} travelPace - 'relaxed', 'moderate', or 'fast'
   * @param {string} preferredMode - 'walking', 'transit', or 'driving'
   * @returns {Promise<Object>} Optimized ItineraryResponse
   */
  optimizeRoute: async (itinerary, travelPace = null, preferredMode = null) => {
    const payload = {
      itinerary,
      travel_pace: travelPace,
      preferred_mode: preferredMode,
    };
    const response = await fetch(`${API_BASE_URL}/api/v1/itinerary/optimize-route`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Optimize route, transit legs, and schedule for a single day
   * POST /api/v1/itinerary/optimize-day
   * @param {string} destination - Destination city name
   * @param {Object} day - Single DayItinerary object
   * @param {string} travelPace - 'relaxed', 'moderate', or 'fast'
   * @param {string} preferredMode - 'walking', 'transit', or 'driving'
   * @returns {Promise<Object>} Optimized DayItinerary
   */
  optimizeDay: async (destination, day, travelPace = 'moderate', preferredMode = null) => {
    const payload = {
      destination,
      day,
      travel_pace: travelPace,
      preferred_mode: preferredMode,
    };
    const response = await fetch(`${API_BASE_URL}/api/v1/itinerary/optimize-day`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Conversational itinerary refinement
   * POST /api/v1/itinerary/refine
   * @param {Object} refineData - { itinerary, instruction, target_day_number?, provider? }
   * @returns {Promise<Object>} RefineResponse { itinerary, explanation, affected_day_numbers, scope }
   */
  refineItinerary: async (refineData) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/itinerary/refine`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(refineData),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Refine a single day with natural language instructions
   * POST /api/v1/itinerary/refine-day
   * @param {Object} dayRefineData - { destination, day, instruction, travel_pace?, primary_vibe?, ... }
   * @returns {Promise<Object>} DayItinerary
   */
  refineDay: async (dayRefineData) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/itinerary/refine-day`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dayRefineData),
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  // ── Activity 5.2: Share & Export ──────────────────────────────────────────

  /**
   * Generate or retrieve a secure shareable link for a trip
   * POST /api/v1/trips/{tripId}/share
   * @param {string} tripId - The trip's ID
   * @returns {Promise<Object>} { trip_id, share_token, share_url, is_active }
   */
  shareTrip: async (tripId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}/share`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Revoke public sharing for a trip
   * DELETE /api/v1/trips/{tripId}/share
   * @param {string} tripId - The trip's ID
   * @returns {Promise<Object>} { trip_id, success, message }
   */
  revokeShare: async (tripId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}/share`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Retrieve public read-only shared trip via token
   * GET /api/v1/shared/{shareToken}
   * @param {string} shareToken - Secure share token
   * @returns {Promise<Object>} SharedTripPublicResponse (no user PII)
   */
  getSharedTrip: async (shareToken) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/shared/${shareToken}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },

  /**
   * Export trip itinerary as PDF (triggers browser download)
   * GET /api/v1/trips/{tripId}/export/pdf
   * @param {string} tripId - The trip's ID
   */
  exportPDF: async (tripId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}/export/pdf`, {
      method: 'GET',
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    // Trigger browser download from blob
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const disposition = response.headers.get('content-disposition') || '';
    const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
    const filename = filenameMatch ? filenameMatch[1] : `itinerary-${tripId.slice(0, 8)}.pdf`;

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  /**
   * Export trip itinerary as JSON (triggers browser download)
   * GET /api/v1/trips/{tripId}/export/json
   * @param {string} tripId - The trip's ID
   */
  exportJSON: async (tripId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}/export/json`, {
      method: 'GET',
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    const data = await response.json();
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const filename = `itinerary-${tripId.slice(0, 8)}.json`;

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  /**
   * Generate clipboard-ready text summary of trip
   * POST /api/v1/trips/{tripId}/summary
   * @param {string} tripId - The trip's ID
   * @returns {Promise<Object>} { summary_text, daily_highlights, ... }
   */
  getTripSummary: async (tripId) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/trips/${tripId}/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const msg = await parseErrorMessage(response);
      throw new Error(msg);
    }

    return response.json();
  },
};

export default tripsAPI;
