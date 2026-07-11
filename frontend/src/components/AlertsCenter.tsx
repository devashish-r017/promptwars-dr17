import { useState, useEffect, useCallback } from 'react';
import { Bell, Play, Square, AlertTriangle, Info, ShieldAlert } from 'lucide-react';
import { t } from '../lib/translations';
import { fetchAlerts, startDemo, stopDemo } from '../lib/api';
import type { Profile, Alert } from '../lib/types';

interface AlertsCenterProps {
  profile: Profile;
  lang: string;
}

const SEVERITY_ICON: Record<string, React.ReactNode> = {
  info: <Info className="w-5 h-5 text-sky-500" />,
  warning: <AlertTriangle className="w-5 h-5 text-amber-500" />,
  critical: <ShieldAlert className="w-5 h-5 text-red-500" />,
};

const SEVERITY_BG: Record<string, string> = {
  info: 'border-l-sky-500 bg-sky-50',
  warning: 'border-l-amber-500 bg-amber-50',
  critical: 'border-l-red-500 bg-red-50',
};

export default function AlertsCenter({ profile, lang }: AlertsCenterProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [demoRunning, setDemoRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadAlerts = useCallback(async () => {
    try {
      const a = await fetchAlerts(profile.city);
      setAlerts(a);
    } catch {
      // Silently fail on poll
    } finally {
      setLoading(false);
    }
  }, [profile.city]);

  // Initial load + polling every 30s
  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 30000);
    return () => clearInterval(interval);
  }, [loadAlerts]);

  // More frequent polling during demo
  useEffect(() => {
    if (!demoRunning) return;
    const interval = setInterval(loadAlerts, 5000);
    return () => clearInterval(interval);
  }, [demoRunning, loadAlerts]);

  const handleStartDemo = async () => {
    try {
      await startDemo(profile.city);
      setDemoRunning(true);
      // Auto-stop after 3 minutes
      setTimeout(() => setDemoRunning(false), 180000);
    } catch {
      // ignore
    }
  };

  const handleStopDemo = async () => {
    try {
      await stopDemo();
      setDemoRunning(false);
    } catch {
      // ignore
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Bell className="w-6 h-6 text-red-500" />
          {t('alerts.title', lang)}
        </h1>

        {/* Demo controls */}
        <div className="flex items-center gap-2">
          {demoRunning && (
            <span className="flex items-center gap-1.5 text-xs text-red-500 font-medium">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              Demo Active
            </span>
          )}
          {!demoRunning ? (
            <button onClick={handleStartDemo} className="btn btn-primary btn-sm">
              <Play className="w-4 h-4" />
              {t('alerts.demo_start', lang)}
            </button>
          ) : (
            <button onClick={handleStopDemo} className="btn btn-danger btn-sm">
              <Square className="w-4 h-4" />
              {t('alerts.demo_stop', lang)}
            </button>
          )}
        </div>
      </div>

      {/* Alert feed */}
      {loading ? (
        <div className="flex justify-center py-10">
          <div className="spinner" style={{ width: '2rem', height: '2rem' }} />
        </div>
      ) : alerts.length === 0 ? (
        <div className="card card-body text-center py-12">
          <Bell className="w-12 h-12 text-slate-200 mx-auto mb-3" />
          <p className="text-slate-400 text-lg">{t('alerts.no_alerts', lang)}</p>
          <p className="text-slate-300 text-sm mt-1">Start the demo timeline to see alerts in action</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`card border-l-4 overflow-hidden fade-in ${SEVERITY_BG[alert.severity] || SEVERITY_BG.info}`}
            >
              <div className="p-4">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 shrink-0">
                    {SEVERITY_ICON[alert.severity] || SEVERITY_ICON.info}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-slate-800">{alert.title}</h3>
                      <div className="flex items-center gap-2">
                        <span className={`severity-badge text-xs ${
                          alert.severity === 'critical' ? 'severity-critical' :
                          alert.severity === 'warning' ? 'severity-warning' : 'severity-normal'
                        }`}>
                          {alert.severity}
                        </span>
                        <span className="text-xs text-slate-400">
                          {new Date(alert.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-600 mt-1">{alert.description}</p>
                    <div className="text-xs text-slate-400 mt-1">📍 {alert.affected_area}</div>

                    {/* Recommended actions */}
                    {alert.recommended_actions.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-200/50">
                        <div className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5">
                          {t('alerts.actions', lang)}
                        </div>
                        <ul className="space-y-1">
                          {alert.recommended_actions.map((action, i) => (
                            <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                              <span className="text-slate-300 mt-0.5">→</span>
                              {action}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
