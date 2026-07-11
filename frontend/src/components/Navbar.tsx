import { NavLink } from 'react-router-dom';
import { Shield, Globe } from 'lucide-react';
import { t } from '../lib/translations';
import type { Profile } from '../lib/types';

interface NavbarProps {
  profile: Profile | null;
  lang: string;
  onLanguageToggle: () => void;
  onSwitchProfile: () => void;
}

/**
 * Navbar component renders the main sticky navigation bar with
 * navigation links, language switcher, and profile indicator.
 */
export default function Navbar({ profile, lang, onLanguageToggle, onSwitchProfile }: NavbarProps) {
  return (
    <nav className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-400 to-blue-600 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold text-slate-800">{t('app.name', lang)}</span>
              <span className="hidden sm:inline text-xs text-slate-400 ml-2">⛈️</span>
            </div>
          </div>

          {/* Navigation links */}
          {profile && (
            <div className="hidden sm:flex items-center gap-1">
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-sky-50 text-sky-700'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                  }`
                }
              >
                {t('nav.dashboard', lang)}
              </NavLink>
              <NavLink
                to="/plan"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-sky-50 text-sky-700'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                  }`
                }
              >
                {t('nav.plan', lang)}
              </NavLink>
              <NavLink
                to="/alerts"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-sky-50 text-sky-700'
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-50'
                  }`
                }
              >
                {t('nav.alerts', lang)}
              </NavLink>
            </div>
          )}

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* Language toggle */}
            <button
              onClick={onLanguageToggle}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors border border-slate-200"
              title="Switch language"
            >
              <Globe className="w-4 h-4" />
              <span>{lang === 'en' ? 'हिं' : 'EN'}</span>
            </button>

            {/* Profile indicator */}
            {profile && (
              <button
                onClick={onSwitchProfile}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-slate-600 hover:bg-slate-50 transition-colors border border-slate-200"
              >
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-sky-400 to-indigo-500 flex items-center justify-center text-white text-xs font-bold">
                  {profile.name.charAt(0).toUpperCase()}
                </div>
                <span className="hidden sm:inline max-w-[120px] truncate">{profile.name}</span>
              </button>
            )}
          </div>
        </div>

        {/* Mobile nav */}
        {profile && (
          <div className="sm:hidden flex gap-1 pb-2 overflow-x-auto">
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive ? 'bg-sky-50 text-sky-700' : 'text-slate-500 hover:bg-slate-50'
                }`
              }
            >
              {t('nav.dashboard', lang)}
            </NavLink>
            <NavLink
              to="/plan"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive ? 'bg-sky-50 text-sky-700' : 'text-slate-500 hover:bg-slate-50'
                }`
              }
            >
              {t('nav.plan', lang)}
            </NavLink>
            <NavLink
              to="/alerts"
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive ? 'bg-sky-50 text-sky-700' : 'text-slate-500 hover:bg-slate-50'
                }`
              }
            >
              {t('nav.alerts', lang)}
            </NavLink>
          </div>
        )}
      </div>
    </nav>
  );
}
