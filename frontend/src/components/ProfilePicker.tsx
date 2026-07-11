import { useState, useEffect } from 'react';
import { Shield, Plus, MapPin, Users, Home } from 'lucide-react';
import { t } from '../lib/translations';
import { fetchProfiles, createProfile } from '../lib/api';
import type { Profile, ProfileCreate } from '../lib/types';

const CITIES = [
  'Mumbai', 'Delhi', 'Chennai', 'Kolkata', 'Bengaluru',
  'Hyderabad', 'Pune', 'Jaipur', 'Ahmedabad', 'Lucknow',
];

const DWELLING_TYPES = [
  { value: 'ground_floor', icon: '🏠' },
  { value: 'high_rise', icon: '🏢' },
  { value: 'basement', icon: '🏗️' },
  { value: 'independent_house', icon: '🏡' },
  { value: 'kaccha_house', icon: '🛖' },
];

interface ProfilePickerProps {
  lang: string;
  onSelect: (profile: Profile) => void;
}

export default function ProfilePicker({ lang, onSelect }: ProfilePickerProps) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState<ProfileCreate>({
    name: '',
    city: 'Mumbai',
    family_size: 4,
    has_elderly: false,
    has_children: false,
    has_pets: false,
    dwelling_type: 'independent_house',
    health_conditions: null,
    has_vehicle: false,
    near_water_body: false,
    preferred_language: lang,
  });

  useEffect(() => {
    fetchProfiles()
      .then((p) => { setProfiles(p); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const profile = await createProfile({ ...form, preferred_language: lang });
      onSelect(profile);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8 fade-in">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-sky-400 to-blue-600 flex items-center justify-center shadow-lg">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800">{t('app.name', lang)}</h1>
          <p className="text-slate-500 mt-1">{t('app.tagline', lang)}</p>
        </div>

        {!showForm ? (
          <div className="fade-in">
            {/* Existing profiles */}
            {profiles.length > 0 && (
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-slate-700 mb-3">{t('profile.title', lang)}</h2>
                <div className="grid gap-3">
                  {profiles.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => onSelect(p)}
                      className="card card-body flex items-center gap-4 text-left hover:border-sky-300 transition-all cursor-pointer"
                    >
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500 flex items-center justify-center text-white text-xl font-bold shrink-0">
                        {p.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-slate-800 truncate">{p.name}</div>
                        <div className="flex items-center gap-3 text-sm text-slate-500 mt-0.5">
                          <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{p.city}</span>
                          <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" />{p.family_size}</span>
                          <span className="flex items-center gap-1"><Home className="w-3.5 h-3.5" />{t(`dwelling.${p.dwelling_type}`, lang)}</span>
                        </div>
                      </div>
                      <div className="text-sky-500 text-sm font-medium">Select →</div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Create new profile button */}
            <button
              onClick={() => setShowForm(true)}
              className="btn btn-primary w-full py-3 text-base"
            >
              <Plus className="w-5 h-5" />
              {t('profile.create', lang)}
            </button>
          </div>
        ) : (
          /* Profile creation form */
          <form onSubmit={handleSubmit} className="card card-body fade-in">
            <h2 className="text-xl font-semibold text-slate-800 mb-6">{t('profile.create', lang)}</h2>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>
            )}

            {/* Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('profile.name', lang)}</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-sky-400 focus:ring-2 focus:ring-sky-100 outline-none transition-all text-sm"
                placeholder="e.g., Rahul's Family"
                required
              />
            </div>

            {/* City */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('profile.city', lang)}</label>
              <select
                value={form.city}
                onChange={(e) => setForm({ ...form, city: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-sky-400 focus:ring-2 focus:ring-sky-100 outline-none transition-all text-sm bg-white"
              >
                {CITIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Family size */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('profile.family_size', lang)}</label>
              <input
                type="number"
                min={1}
                max={50}
                value={form.family_size}
                onChange={(e) => setForm({ ...form, family_size: parseInt(e.target.value) || 1 })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-sky-400 focus:ring-2 focus:ring-sky-100 outline-none transition-all text-sm"
              />
            </div>

            {/* Dwelling type */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-2">{t('profile.dwelling', lang)}</label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {DWELLING_TYPES.map((d) => (
                  <button
                    key={d.value}
                    type="button"
                    onClick={() => setForm({ ...form, dwelling_type: d.value })}
                    className={`px-3 py-2.5 rounded-lg border text-sm font-medium transition-all flex items-center gap-2 ${
                      form.dwelling_type === d.value
                        ? 'border-sky-400 bg-sky-50 text-sky-700'
                        : 'border-slate-200 text-slate-600 hover:border-slate-300'
                    }`}
                  >
                    <span>{d.icon}</span>
                    <span>{t(`dwelling.${d.value}`, lang)}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Advanced options */}
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-sky-600 hover:text-sky-700 font-medium mb-4"
            >
              {showAdvanced ? '▾' : '▸'} {t('profile.advanced', lang)}
            </button>

            {showAdvanced && (
              <div className="space-y-3 mb-4 p-4 rounded-lg bg-slate-50 fade-in">
                {/* Toggle switches */}
                {[
                  { key: 'has_elderly', label: t('profile.elderly', lang) },
                  { key: 'has_children', label: t('profile.children', lang) },
                  { key: 'has_pets', label: t('profile.pets', lang) },
                  { key: 'has_vehicle', label: t('profile.vehicle', lang) },
                  { key: 'near_water_body', label: t('profile.water_body', lang) },
                ].map(({ key, label }) => (
                  <label key={key} className="flex items-center justify-between cursor-pointer">
                    <span className="text-sm text-slate-700">{label}</span>
                    <div
                      onClick={() => setForm({ ...form, [key]: !form[key as keyof ProfileCreate] })}
                      className={`w-10 h-6 rounded-full transition-colors relative cursor-pointer ${
                        form[key as keyof ProfileCreate] ? 'bg-sky-500' : 'bg-slate-300'
                      }`}
                    >
                      <div
                        className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                          form[key as keyof ProfileCreate] ? 'translate-x-5' : 'translate-x-1'
                        }`}
                      />
                    </div>
                  </label>
                ))}

                {/* Health conditions */}
                <div>
                  <label className="block text-sm text-slate-700 mb-1">{t('profile.health', lang)}</label>
                  <input
                    type="text"
                    value={form.health_conditions || ''}
                    onChange={(e) => setForm({ ...form, health_conditions: e.target.value || null })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-sky-400 focus:ring-2 focus:ring-sky-100 outline-none transition-all text-sm"
                    placeholder="e.g., asthma, mobility issues"
                  />
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="btn btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving || !form.name.trim()}
                className="btn btn-primary flex-1 disabled:opacity-50"
              >
                {saving ? t('profile.saving', lang) : t('profile.save', lang)}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
