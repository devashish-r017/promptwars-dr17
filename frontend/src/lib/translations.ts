/* Static UI translations — English + Hindi */

type TranslationKey = string;

const translations: Record<string, Record<TranslationKey, string>> = {
  en: {
    // App
    'app.name': 'StormShield',
    'app.tagline': 'Intelligent monsoon preparedness for families',

    // Nav
    'nav.dashboard': 'Dashboard',
    'nav.plan': 'Preparedness Plan',
    'nav.alerts': 'Alerts',
    'nav.profile': 'Profile',
    'nav.switch_profile': 'Switch Profile',

    // Profile
    'profile.title': 'Choose Your Profile',
    'profile.create': 'Create New Profile',
    'profile.name': 'Profile Name',
    'profile.city': 'City',
    'profile.family_size': 'Family Size',
    'profile.dwelling': 'Dwelling Type',
    'profile.elderly': 'Elderly Members (65+)',
    'profile.children': 'Children (under 12)',
    'profile.pets': 'Pets',
    'profile.health': 'Health Conditions',
    'profile.vehicle': 'Owns Vehicle',
    'profile.water_body': 'Near Water Body',
    'profile.advanced': 'Advanced Options',
    'profile.save': 'Save Profile',
    'profile.saving': 'Saving...',

    // Dwelling types
    'dwelling.ground_floor': 'Ground Floor',
    'dwelling.high_rise': 'High Rise',
    'dwelling.basement': 'Basement',
    'dwelling.independent_house': 'Independent House',
    'dwelling.kaccha_house': 'Kaccha House',

    // Dashboard
    'dashboard.title': 'Dashboard',
    'dashboard.weather': 'Current Weather',
    'dashboard.risk': 'Your Risk Score',
    'dashboard.checklist': 'Quick Checklist',
    'dashboard.travel': 'Travel Status',
    'dashboard.safety': 'Safety Tips',
    'dashboard.alerts': 'Recent Alerts',
    'dashboard.loading': 'Loading your dashboard...',

    // Severity
    'severity.normal': 'Normal',
    'severity.watch': 'Watch',
    'severity.warning': 'Warning',
    'severity.critical': 'Critical',

    // Flood risk
    'flood.low': 'Low',
    'flood.moderate': 'Moderate',
    'flood.high': 'High',
    'flood.very_high': 'Very High',

    // Monsoon phase
    'phase.pre_monsoon': 'Pre-Monsoon',
    'phase.active_monsoon': 'Active Monsoon',
    'phase.post_monsoon': 'Post-Monsoon',

    // Plan
    'plan.title': 'Preparedness Plan',
    'plan.before': 'Before Monsoon — Preparation',
    'plan.during': 'During Monsoon — Active Safety',
    'plan.after': 'After Monsoon — Recovery',
    'plan.regenerate': 'Regenerate Plan',
    'plan.current_phase': 'Current Phase',
    'plan.loading': 'Generating your personalized plan...',

    // Alerts
    'alerts.title': 'Alerts Center',
    'alerts.no_alerts': 'No active alerts',
    'alerts.demo_start': 'Start Demo Timeline',
    'alerts.demo_stop': 'Stop Demo',
    'alerts.actions': 'Recommended Actions',

    // Chat
    'chat.title': 'StormShield Assistant',
    'chat.placeholder': 'Ask about monsoon preparedness...',
    'chat.send': 'Send',
    'chat.thinking': 'Thinking...',

    // Weather Override
    'override.title': 'Weather Scenario',
    'override.apply': 'Apply',
    'override.reset': 'Reset',

    // General
    'general.loading': 'Loading...',
    'general.error': 'Something went wrong',
    'general.retry': 'Retry',
    'general.view_all': 'View All',
    'general.high': 'High',
    'general.medium': 'Medium',
    'general.low': 'Low',
  },

  hi: {
    // App
    'app.name': 'StormShield',
    'app.tagline': 'परिवारों के लिए बुद्धिमान मानसून तैयारी',

    // Nav
    'nav.dashboard': 'डैशबोर्ड',
    'nav.plan': 'तैयारी योजना',
    'nav.alerts': 'अलर्ट',
    'nav.profile': 'प्रोफ़ाइल',
    'nav.switch_profile': 'प्रोफ़ाइल बदलें',

    // Profile
    'profile.title': 'अपनी प्रोफ़ाइल चुनें',
    'profile.create': 'नई प्रोफ़ाइल बनाएं',
    'profile.name': 'प्रोफ़ाइल का नाम',
    'profile.city': 'शहर',
    'profile.family_size': 'परिवार का आकार',
    'profile.dwelling': 'आवास का प्रकार',
    'profile.elderly': 'बुज़ुर्ग सदस्य (65+)',
    'profile.children': 'बच्चे (12 से कम)',
    'profile.pets': 'पालतू जानवर',
    'profile.health': 'स्वास्थ्य स्थितियां',
    'profile.vehicle': 'वाहन है',
    'profile.water_body': 'जलस्रोत के पास',
    'profile.advanced': 'उन्नत विकल्प',
    'profile.save': 'प्रोफ़ाइल सेव करें',
    'profile.saving': 'सेव हो रहा है...',

    // Dwelling types
    'dwelling.ground_floor': 'भूतल',
    'dwelling.high_rise': 'ऊंची इमारत',
    'dwelling.basement': 'बेसमेंट',
    'dwelling.independent_house': 'स्वतंत्र मकान',
    'dwelling.kaccha_house': 'कच्चा मकान',

    // Dashboard
    'dashboard.title': 'डैशबोर्ड',
    'dashboard.weather': 'मौसम की स्थिति',
    'dashboard.risk': 'आपका जोखिम स्कोर',
    'dashboard.checklist': 'त्वरित चेकलिस्ट',
    'dashboard.travel': 'यात्रा स्थिति',
    'dashboard.safety': 'सुरक्षा सुझाव',
    'dashboard.alerts': 'हाल के अलर्ट',
    'dashboard.loading': 'आपका डैशबोर्ड लोड हो रहा है...',

    // Severity
    'severity.normal': 'सामान्य',
    'severity.watch': 'निगरानी',
    'severity.warning': 'चेतावनी',
    'severity.critical': 'गंभीर',

    // Flood risk
    'flood.low': 'कम',
    'flood.moderate': 'मध्यम',
    'flood.high': 'उच्च',
    'flood.very_high': 'बहुत उच्च',

    // Monsoon phase
    'phase.pre_monsoon': 'मानसून-पूर्व',
    'phase.active_monsoon': 'सक्रिय मानसून',
    'phase.post_monsoon': 'मानसून-उपरांत',

    // Plan
    'plan.title': 'तैयारी योजना',
    'plan.before': 'मानसून से पहले — तैयारी',
    'plan.during': 'मानसून के दौरान — सक्रिय सुरक्षा',
    'plan.after': 'मानसून के बाद — पुनर्प्राप्ति',
    'plan.regenerate': 'योजना पुनः बनाएं',
    'plan.current_phase': 'वर्तमान चरण',
    'plan.loading': 'आपकी व्यक्तिगत योजना बनाई जा रही है...',

    // Alerts
    'alerts.title': 'अलर्ट केंद्र',
    'alerts.no_alerts': 'कोई सक्रिय अलर्ट नहीं',
    'alerts.demo_start': 'डेमो टाइमलाइन शुरू करें',
    'alerts.demo_stop': 'डेमो रोकें',
    'alerts.actions': 'अनुशंसित कार्रवाई',

    // Chat
    'chat.title': 'StormShield सहायक',
    'chat.placeholder': 'मानसून तैयारी के बारे में पूछें...',
    'chat.send': 'भेजें',
    'chat.thinking': 'सोच रहा हूं...',

    // Weather Override
    'override.title': 'मौसम परिदृश्य',
    'override.apply': 'लागू करें',
    'override.reset': 'रीसेट',

    // General
    'general.loading': 'लोड हो रहा है...',
    'general.error': 'कुछ गलत हो गया',
    'general.retry': 'पुनः प्रयास',
    'general.view_all': 'सभी देखें',
    'general.high': 'उच्च',
    'general.medium': 'मध्यम',
    'general.low': 'निम्न',
  },
};

export function t(key: string, lang: string = 'en'): string {
  return translations[lang]?.[key] || translations['en']?.[key] || key;
}

export default translations;
