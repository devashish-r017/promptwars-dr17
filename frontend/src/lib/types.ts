/* Types matching backend Pydantic schemas */

export interface ProfileCreate {
  name: string;
  city: string;
  family_size: number;
  has_elderly: boolean;
  has_children: boolean;
  has_pets: boolean;
  dwelling_type: string;
  health_conditions: string | null;
  has_vehicle: boolean;
  near_water_body: boolean;
  preferred_language: string;
}

export interface Profile extends ProfileCreate {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface WeatherData {
  city: string;
  temperature_c: number;
  humidity_percent: number;
  rainfall_mm: number;
  wind_speed_kmh: number;
  condition: string;
  flood_risk: string;
  severity: string;
  monsoon_phase: string;
  source: string;
}

export interface PlanItem {
  category: string;
  description: string;
  priority: string;
  personalized_note: string | null;
}

export interface PlanPhase {
  phase: string;
  title: string;
  items: PlanItem[];
}

export interface PrepPlan {
  phases: PlanPhase[];
  current_phase: string;
  profile_summary: string;
}

export interface RiskScore {
  score: number;
  level: string;
  explanation: string;
}

export interface ChecklistItem {
  item: string;
  category: string;
  is_personalized: boolean;
  reason: string | null;
}

export interface TravelStatus {
  safety_rating: string;
  summary: string;
  tips: string[];
}

export interface SafetyTip {
  category: string;
  icon: string;
  tip: string;
}

export interface Alert {
  id: number;
  severity: string;
  title: string;
  description: string;
  affected_area: string;
  recommended_actions: string[];
  is_active: boolean;
  created_at: string;
  expires_at: string | null;
}

export interface DashboardData {
  weather: WeatherData;
  risk_score: RiskScore;
  checklist: { items: ChecklistItem[] };
  travel: TravelStatus;
  safety: { tips: SafetyTip[] };
  recent_alerts: Alert[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
