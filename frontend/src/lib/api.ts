/* Centralized API client — all backend calls go through here. */

import type {
  Profile,
  ProfileCreate,
  WeatherData,
  PrepPlan,
  DashboardData,
  Alert,
  ChatMessage,
} from './types';

const BASE = '/api';

/**
 * Helper to perform HTTP fetch requests and handle JSON/error responses.
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// --- Profiles ---

export function fetchProfiles(): Promise<Profile[]> {
  return request('/profiles');
}

export function createProfile(data: ProfileCreate): Promise<Profile> {
  return request('/profiles', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function getProfile(id: number): Promise<Profile> {
  return request(`/profiles/${id}`);
}

export function updateProfile(id: number, data: Partial<ProfileCreate>): Promise<Profile> {
  return request(`/profiles/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export function deleteProfile(id: number): Promise<void> {
  return request(`/profiles/${id}`, { method: 'DELETE' });
}

// --- Weather ---

export function fetchWeather(city: string): Promise<WeatherData> {
  return request(`/weather/${encodeURIComponent(city)}`);
}

export function setWeatherOverride(scenario: string): Promise<{ status: string }> {
  return request('/weather/override', {
    method: 'POST',
    body: JSON.stringify({ scenario }),
  });
}

export function clearWeatherOverride(): Promise<{ status: string }> {
  return request('/weather/override', { method: 'DELETE' });
}

// --- Dashboard ---

export function fetchDashboard(profileId: number): Promise<DashboardData> {
  return request(`/dashboard/${profileId}`);
}

// --- Plans ---

export function fetchPlan(profileId: number): Promise<PrepPlan> {
  return request(`/plans/${profileId}`);
}

export function regeneratePlan(profileId: number): Promise<PrepPlan> {
  return request(`/plans/${profileId}/regenerate`, { method: 'POST' });
}

// --- Alerts ---

export function fetchAlerts(city: string): Promise<Alert[]> {
  return request(`/alerts?city=${encodeURIComponent(city)}`);
}

export function startDemo(city: string = 'Mumbai'): Promise<{ status: string }> {
  return request(`/alerts/demo/start?city=${encodeURIComponent(city)}`, { method: 'POST' });
}

export function stopDemo(): Promise<{ status: string }> {
  return request('/alerts/demo/stop', { method: 'POST' });
}

// --- Chat ---

/**
 * Send a chat message to the assistant with current profile and history context.
 */
export function sendChatMessage(
  profileId: number,
  message: string,
  pageContext: string,
  history: ChatMessage[],
): Promise<{ reply: string }> {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({
      profile_id: profileId,
      message,
      page_context: pageContext,
      history,
    }),
  });
}
