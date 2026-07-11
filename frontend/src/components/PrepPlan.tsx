import { useState, useEffect } from 'react';
import { BookOpen, ChevronDown, ChevronUp, RefreshCw, AlertTriangle, Star } from 'lucide-react';
import { t } from '../lib/translations';
import { fetchPlan, regeneratePlan } from '../lib/api';
import type { Profile, PrepPlan, PlanPhase } from '../lib/types';

interface PrepPlanPageProps {
  profile: Profile;
  lang: string;
}

const PHASE_STYLES: Record<string, { bg: string; border: string; badge: string; icon: string }> = {
  before: { bg: 'bg-sky-50', border: 'border-sky-200', badge: 'phase-before', icon: '🔵' },
  during: { bg: 'bg-amber-50', border: 'border-amber-200', badge: 'phase-during', icon: '🟠' },
  after: { bg: 'bg-emerald-50', border: 'border-emerald-200', badge: 'phase-after', icon: '🟢' },
};

const PRIORITY_COLORS: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-slate-100 text-slate-600',
};

/**
 * PrepPlanPage component displays the 3-phase preparedness plan (Before, During, After Monsoon)
 * personalized by the AI for the user's specific context.
 */
export default function PrepPlanPage({ profile, lang }: PrepPlanPageProps) {
  const [plan, setPlan] = useState<PrepPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const loadPlan = async () => {
    setLoading(true);
    setError('');
    try {
      const p = await fetchPlan(profile.id);
      setPlan(p);
      // Auto-expand current phase
      const expandState: Record<string, boolean> = {};
      p.phases.forEach((phase) => {
        expandState[phase.phase] = phase.phase === p.current_phase;
      });
      setExpanded(expandState);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load plan');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadPlan(); }, [profile.id]);

  /**
   * Request a fresh plan generation by invalidating cache on the backend.
   */
  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const p = await regeneratePlan(profile.id);
      setPlan(p);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to regenerate');
    } finally {
      setRegenerating(false);
    }
  };

  const togglePhase = (phase: string) => {
    setExpanded((prev) => ({ ...prev, [phase]: !prev[phase] }));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="spinner" style={{ width: '2rem', height: '2rem' }} />
        <p className="text-slate-500 text-sm">{t('plan.loading', lang)}</p>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <AlertTriangle className="w-8 h-8 text-amber-500" />
        <p className="text-slate-600">{error || t('general.error', lang)}</p>
        <button onClick={loadPlan} className="btn btn-primary btn-sm">
          <RefreshCw className="w-4 h-4" /> {t('general.retry', lang)}
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-sky-500" />
            {t('plan.title', lang)}
          </h1>
          {plan.profile_summary && (
            <p className="text-sm text-slate-500 mt-1">{plan.profile_summary}</p>
          )}
        </div>
        <button
          onClick={handleRegenerate}
          disabled={regenerating}
          className="btn btn-secondary btn-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
          {t('plan.regenerate', lang)}
        </button>
      </div>

      {/* Phase accordions */}
      <div className="space-y-4">
        {plan.phases.map((phase: PlanPhase) => {
          const style = PHASE_STYLES[phase.phase] || PHASE_STYLES.before;
          const isExpanded = expanded[phase.phase] ?? false;
          const isCurrent = phase.phase === plan.current_phase;

          return (
            <div key={phase.phase} className={`card overflow-hidden transition-all ${isCurrent ? 'ring-2 ring-sky-300' : ''}`}>
              {/* Accordion header */}
              <button
                onClick={() => togglePhase(phase.phase)}
                className={`w-full flex items-center justify-between p-4 ${style.bg} transition-colors hover:opacity-90`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{style.icon}</span>
                  <div className="text-left">
                    <div className="font-semibold text-slate-800">{phase.title}</div>
                    <div className="text-xs text-slate-500">{phase.items.length} action items</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {isCurrent && (
                    <span className={`severity-badge ${style.badge} text-xs`}>
                      {t('plan.current_phase', lang)}
                    </span>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-slate-400" />
                  )}
                </div>
              </button>

              {/* Accordion content */}
              {isExpanded && (
                <div className="p-4 space-y-3 fade-in">
                  {phase.items.map((item, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors"
                    >
                      <div className="mt-0.5">
                        <span className={`severity-badge text-xs ${PRIORITY_COLORS[item.priority] || PRIORITY_COLORS.medium}`}>
                          {t(`general.${item.priority}`, lang)}
                        </span>
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-slate-400 uppercase tracking-wide text-xs mb-0.5">
                          {item.category}
                        </div>
                        <div className="text-sm text-slate-800">{item.description}</div>
                        {item.personalized_note && (
                          <div className="flex items-start gap-1 mt-1 text-xs text-sky-600">
                            <Star className="w-3 h-3 mt-0.5 shrink-0" />
                            <span>{item.personalized_note}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
