import { useState, useEffect } from 'react';
import {
  CloudRain, Thermometer, Droplets, Wind, AlertTriangle,
  CheckCircle2, Car, ShieldAlert, RefreshCw, ChevronRight,
} from 'lucide-react';
import { t } from '../lib/translations';
import { fetchDashboard, setWeatherOverride, clearWeatherOverride } from '../lib/api';
import type { Profile, DashboardData } from '../lib/types';
import { useNavigate } from 'react-router-dom';

interface DashboardProps {
  profile: Profile;
  lang: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  normal: 'severity-normal',
  watch: 'severity-watch',
  warning: 'severity-warning',
  critical: 'severity-critical',
};

const RISK_COLORS: Record<string, string> = {
  low: '#10b981',
  moderate: '#f59e0b',
  high: '#ef4444',
  very_high: '#dc2626',
};

const SCENARIOS = [
  { value: '', label: 'Auto' },
  { value: 'normal', label: '☀️ Normal' },
  { value: 'heavy_rain', label: '🌧️ Heavy Rain' },
  { value: 'flood_risk', label: '🌊 Flood Risk' },
  { value: 'cyclone_warning', label: '🌀 Cyclone' },
  { value: 'post_monsoon_clear', label: '🌤️ Post-Monsoon' },
];

/**
 * Dashboard component renders the main dashboard page containing weather details,
 * personalized risk assessment, a quick action checklist, travel safety advice,
 * and current active alerts.
 */
export default function Dashboard({ profile, lang }: DashboardProps) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [scenario, setScenario] = useState('');
  const navigate = useNavigate();

  const loadDashboard = async () => {
    setLoading(true);
    setError('');
    try {
      const d = await fetchDashboard(profile.id);
      setData(d);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDashboard(); }, [profile.id]);

  /**
   * Changes the simulated weather scenario override and reloads dashboard data.
   */
  const handleScenario = async (val: string) => {
    setScenario(val);
    if (val) {
      await setWeatherOverride(val);
    } else {
      await clearWeatherOverride();
    }
    loadDashboard();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="spinner" style={{ width: '2rem', height: '2rem' }} />
        <p className="text-slate-500 text-sm">{t('dashboard.loading', lang)}</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <AlertTriangle className="w-8 h-8 text-amber-500" />
        <p className="text-slate-600">{error || t('general.error', lang)}</p>
        <button onClick={loadDashboard} className="btn btn-primary btn-sm">
          <RefreshCw className="w-4 h-4" /> {t('general.retry', lang)}
        </button>
      </div>
    );
  }

  const { weather, risk_score, checklist, travel, safety, recent_alerts } = data;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Weather scenario override */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800">{t('dashboard.title', lang)}</h1>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">{t('override.title', lang)}:</span>
          <select
            value={scenario}
            onChange={(e) => handleScenario(e.target.value)}
            className="text-xs px-2 py-1 rounded-lg border border-slate-200 bg-white outline-none"
          >
            {SCENARIOS.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

        {/* Weather card — spans 2 cols on lg */}
        <div className="card card-body lg:col-span-2 fade-in">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <CloudRain className="w-5 h-5 text-sky-500" />
              {t('dashboard.weather', lang)}
            </h2>
            <span className={`severity-badge ${SEVERITY_COLORS[weather.severity]}`}>
              {t(`severity.${weather.severity}`, lang)}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center">
                <Thermometer className="w-5 h-5 text-orange-500" />
              </div>
              <div>
                <div className="text-xl font-bold text-slate-800">{weather.temperature_c}°C</div>
                <div className="text-xs text-slate-400">Temperature</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                <Droplets className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <div className="text-xl font-bold text-slate-800">{weather.rainfall_mm}mm</div>
                <div className="text-xs text-slate-400">Rainfall</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-50 flex items-center justify-center">
                <Droplets className="w-5 h-5 text-cyan-500" />
              </div>
              <div>
                <div className="text-xl font-bold text-slate-800">{weather.humidity_percent}%</div>
                <div className="text-xs text-slate-400">Humidity</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center">
                <Wind className="w-5 h-5 text-slate-500" />
              </div>
              <div>
                <div className="text-xl font-bold text-slate-800">{weather.wind_speed_kmh} km/h</div>
                <div className="text-xs text-slate-400">Wind</div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 mt-4 pt-4 border-t border-slate-100">
            <span className="text-sm text-slate-500">{weather.condition}</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
              {t(`phase.${weather.monsoon_phase}`, lang)}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
              Flood: {t(`flood.${weather.flood_risk}`, lang)}
            </span>
            <span className="text-xs text-slate-300 ml-auto">Source: {weather.source}</span>
          </div>
        </div>

        {/* Risk score */}
        <div className="card card-body fade-in">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">{t('dashboard.risk', lang)}</h2>
          <div className="flex items-center justify-center mb-3">
            <div className="relative w-28 h-28">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e2e8f0" strokeWidth="8" />
                <circle
                  cx="50" cy="50" r="40" fill="none"
                  stroke={RISK_COLORS[risk_score.level] || '#f59e0b'}
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${risk_score.score * 2.51} 251`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold" style={{ color: RISK_COLORS[risk_score.level] }}>
                  {risk_score.score}
                </span>
              </div>
            </div>
          </div>
          <p className="text-sm text-slate-500 text-center">{risk_score.explanation}</p>
        </div>

        {/* Quick checklist */}
        <div className="card card-body fade-in">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              {t('dashboard.checklist', lang)}
            </h2>
          </div>
          <ul className="space-y-2">
            {checklist.items.slice(0, 6).map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <input type="checkbox" className="mt-0.5 rounded border-slate-300 text-sky-500 focus:ring-sky-200" />
                <div>
                  <span className="text-slate-700">{item.item}</span>
                  {item.is_personalized && (
                    <span className="ml-1 text-xs text-sky-500">★</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Travel status */}
        <div className="card card-body fade-in">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Car className="w-5 h-5 text-indigo-500" />
              {t('dashboard.travel', lang)}
            </h2>
            <span className={`severity-badge ${
              travel.safety_rating === 'safe' ? 'severity-normal' :
              travel.safety_rating === 'caution' ? 'severity-watch' : 'severity-critical'
            }`}>
              {travel.safety_rating === 'safe' ? '✅' : travel.safety_rating === 'caution' ? '⚠️' : '❌'} {travel.safety_rating}
            </span>
          </div>
          <p className="text-sm text-slate-600 mb-3">{travel.summary}</p>
          <ul className="space-y-1.5">
            {travel.tips.map((tip, i) => (
              <li key={i} className="text-sm text-slate-500 flex items-start gap-2">
                <span className="text-slate-300 mt-0.5">•</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>

        {/* Safety tips */}
        <div className="card card-body fade-in">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2 mb-3">
            <ShieldAlert className="w-5 h-5 text-amber-500" />
            {t('dashboard.safety', lang)}
          </h2>
          <div className="space-y-3">
            {safety.tips.map((tip, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="text-lg">{tip.icon}</span>
                <div>
                  <div className="text-xs font-medium text-slate-400 uppercase tracking-wide">{tip.category}</div>
                  <div className="text-sm text-slate-700">{tip.tip}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent alerts */}
        <div className="card card-body lg:col-span-3 fade-in">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              {t('dashboard.alerts', lang)}
            </h2>
            <button
              onClick={() => navigate('/alerts')}
              className="text-sm text-sky-600 hover:text-sky-700 flex items-center gap-1"
            >
              {t('general.view_all', lang)} <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {recent_alerts.length === 0 ? (
            <p className="text-sm text-slate-400 py-4 text-center">{t('alerts.no_alerts', lang)}</p>
          ) : (
            <div className="space-y-2">
              {recent_alerts.slice(0, 3).map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border-l-4 ${
                    alert.severity === 'critical' ? 'border-l-red-500 bg-red-50' :
                    alert.severity === 'warning' ? 'border-l-amber-500 bg-amber-50' :
                    'border-l-sky-500 bg-sky-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm text-slate-800">{alert.title}</span>
                    <span className="text-xs text-slate-400">
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">{alert.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
