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

export function getSafetyTone(score) {
  if (score >= 85) {
    return {
      label: 'Strong',
      color: '#10B981',
      soft: 'rgba(16, 185, 129, 0.14)'
    };
  }

  if (score >= 70) {
    return {
      label: 'Balanced',
      color: '#F59E0B',
      soft: 'rgba(245, 158, 11, 0.14)'
    };
  }

  return {
    label: 'Caution',
    color: '#EF4444',
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
