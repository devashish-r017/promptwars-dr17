import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster, toast } from 'sonner';

import Navbar from './components/Navbar';
import ProfilePicker from './components/ProfilePicker';
import Dashboard from './components/Dashboard';
import PrepPlanPage from './components/PrepPlan';
import AlertsCenter from './components/AlertsCenter';
import ChatPanel from './components/ChatPanel';
import { updateProfile, fetchAlerts } from './lib/api';
import type { Profile, Alert } from './lib/types';

/**
 * AppContent component manages user profile state, language settings,
 * alert polling, and routes navigation within the application layout.
 */
function AppContent() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [lang, setLang] = useState('en');
  const location = useLocation();

  // Restore profile from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('stormshield_profile');
    if (saved) {
      try {
        setProfile(JSON.parse(saved));
      } catch {
        localStorage.removeItem('stormshield_profile');
      }
    }
    const savedLang = localStorage.getItem('stormshield_lang');
    if (savedLang) setLang(savedLang);
  }, []);

  const handleSelectProfile = (p: Profile) => {
    setProfile(p);
    setLang(p.preferred_language || 'en');
    localStorage.setItem('stormshield_profile', JSON.stringify(p));
    localStorage.setItem('stormshield_lang', p.preferred_language || 'en');
  };

  const handleSwitchProfile = () => {
    setProfile(null);
    localStorage.removeItem('stormshield_profile');
  };

  const handleLanguageToggle = async () => {
    const newLang = lang === 'en' ? 'hi' : 'en';
    setLang(newLang);
    localStorage.setItem('stormshield_lang', newLang);
    if (profile) {
      try {
        const updated = await updateProfile(profile.id, { preferred_language: newLang });
        setProfile(updated);
        localStorage.setItem('stormshield_profile', JSON.stringify(updated));
      } catch {
        // Ignore — lang is already set locally
      }
    }
  };

  // Poll for new alerts and show toasts (every 30s when profile is active)
  useEffect(() => {
    if (!profile) return;
    let lastAlertId = 0;

    const checkAlerts = async () => {
      try {
        const alerts: Alert[] = await fetchAlerts(profile.city);
        if (alerts.length > 0) {
          const [newest] = alerts;
          if (newest.id > lastAlertId) {
            if (lastAlertId > 0) {
              // New alert arrived
              const toastFn = newest.severity === 'critical' ? toast.error :
                              newest.severity === 'warning' ? toast.warning : toast.info;
              toastFn(newest.title, {
                description: newest.description,
                duration: 8000,
              });
            }
            lastAlertId = newest.id;
          }
        }
      } catch {
        // Silently fail
      }
    };

    checkAlerts();
    const interval = setInterval(checkAlerts, 30000);
    return () => clearInterval(interval);
  }, [profile]);

  // Get current page context for chat
  /**
   * Helper function to determine the current page context string for the AI chat agent.
   */
  const getPageContext = () => {
    if (location.pathname.includes('plan')) return 'preparedness_plan';
    if (location.pathname.includes('alerts')) return 'alerts_center';
    return 'dashboard';
  };

  if (!profile) {
    return <ProfilePicker lang={lang} onSelect={handleSelectProfile} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      <Navbar
        profile={profile}
        lang={lang}
        onLanguageToggle={handleLanguageToggle}
        onSwitchProfile={handleSwitchProfile}
      />

      <main>
        <Routes>
          <Route path="/dashboard" element={<Dashboard profile={profile} lang={lang} />} />
          <Route path="/plan" element={<PrepPlanPage profile={profile} lang={lang} />} />
          <Route path="/alerts" element={<AlertsCenter profile={profile} lang={lang} />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>

      <ChatPanel profile={profile} lang={lang} pageContext={getPageContext()} />
    </div>
  );
}

/**
 * Main application entry component that mounts global routing context and notifications toaster.
 */
export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors closeButton />
      <AppContent />
    </BrowserRouter>
  );
}
