const berlinGeocodingEntries = [
  // { label: 'Alexanderplatz', aliases: ['alexanderplatz', 'alexander platz', 'alexanderplatz berlin'] },
  // { label: 'Brandenburg Gate', aliases: ['brandenburg gate', 'brandenburger tor'] },
  // { label: 'Potsdamer Platz', aliases: ['potsdamer platz'] },
  // { label: 'Berlin Central Station', aliases: ['berlin central station', 'hauptbahnhof', 'berlin hauptbahnhof'] },
  // { label: 'Museum Island', aliases: ['museum island', 'museumsinsel'] },
  // { label: 'Friedrichstrasse', aliases: ['friedrichstrasse', 'friedrichstraße'] },
  // { label: 'Tiergarten', aliases: ['tiergarten'] },
  // { label: 'Kreuzberg', aliases: ['kreuzberg'] },
  // { label: 'Prenzlauer Berg', aliases: ['prenzlauer berg'] },
  // { label: 'Charlottenburg', aliases: ['charlottenburg'] },
  // { label: 'Wilmersdorf', aliases: ['wilmersdorf'] },
  // { label: 'Neukolln', aliases: ['neukolln', 'neukoelln', 'neukölln'] },
  // { label: 'Schöneberg', aliases: ['schoneberg', 'schöneberg'] },
  // { label: 'Moabit', aliases: ['moabit'] },
  // { label: 'Gorlitzer Park', aliases: ['gorlitzer park', 'görlitzer park'] },
  // { label: 'Humboldt Forum', aliases: ['humboldt forum'] },
  // { label: 'East Side Gallery', aliases: ['east side gallery'] },
  // { label: 'Gendarmenmarkt', aliases: ['gendarmenmarkt'] },
  // { label: 'Kurfürstendamm', aliases: ['kurfurstendamm', 'kurfuerstendamm', 'kudamm'] },
  // { label: 'Berlin City Center', aliases: ['berlin', 'berlin city center', 'mitte'] }
];

let routeSuggestions = [];
var safetyScores = {
  safe: process.env.ACCENT_COLOR_SAFE_SCORE || 80,
  fair: process.env.ACCENT_COLOR_FAIR_SCORE || 65,
  danger: process.env.ACCENT_COLOR_DANGER_SCORE || 50
};

var accentColors = {
  safe: process.env.ACCENT_COLOR_SAFE_HEX || "#4CAF50",
  fair: process.env.ACCENT_COLOR_FAIR_HEX || "#FF9800",
  danger: process.env.ACCENT_COLOR_DANGER_HEX || "#F44336"
};
export function getSafetyTone(score) {
  if (score >= safetyScores.safe) {
    return {
      label: 'Strong',
      color: accentColors.safe,
      soft: 'rgba(16, 185, 129, 0.14)'
    };
  }

  if (score >= safetyScores.fair) {
    return {
      label: 'Balanced',
      color: accentColors.fair,
      soft: 'rgba(245, 158, 11, 0.14)'
    };
  }

  return {
    label: 'Caution',
    color: accentColors.danger,
    soft: 'rgba(239, 68, 68, 0.14)'
  };
}

export function validateBerlinLocation(value) {
  if (!String(value || '').trim()) {
    return 'This field is required.';
  }

  return '';
}

export function getRouteSuggestions() {
  return routeSuggestions;
}

export function setRouteSuggestions(suggestions) {
  routeSuggestions.length = 0;
  routeSuggestions.push(...suggestions);
}

export function getRouteById(routeId) {
  return routeSuggestions.find((route) => route.id === routeId) || routeSuggestions[0];
}
