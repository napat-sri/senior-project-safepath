const berlinGeocodingEntries = [
  { label: 'Alexanderplatz', aliases: ['alexanderplatz', 'alexander platz', 'alexanderplatz berlin'] },
  { label: 'Brandenburg Gate', aliases: ['brandenburg gate', 'brandenburger tor'] },
  { label: 'Potsdamer Platz', aliases: ['potsdamer platz'] },
  { label: 'Berlin Central Station', aliases: ['berlin central station', 'hauptbahnhof', 'berlin hauptbahnhof'] },
  { label: 'Museum Island', aliases: ['museum island', 'museumsinsel'] },
  { label: 'Friedrichstrasse', aliases: ['friedrichstrasse', 'friedrichstraße'] },
  { label: 'Tiergarten', aliases: ['tiergarten'] },
  { label: 'Kreuzberg', aliases: ['kreuzberg'] },
  { label: 'Prenzlauer Berg', aliases: ['prenzlauer berg'] },
  { label: 'Charlottenburg', aliases: ['charlottenburg'] },
  { label: 'Wilmersdorf', aliases: ['wilmersdorf'] },
  { label: 'Neukolln', aliases: ['neukolln', 'neukoelln', 'neukölln'] },
  { label: 'Schöneberg', aliases: ['schoneberg', 'schöneberg'] },
  { label: 'Moabit', aliases: ['moabit'] },
  { label: 'Gorlitzer Park', aliases: ['gorlitzer park', 'görlitzer park'] },
  { label: 'Humboldt Forum', aliases: ['humboldt forum'] },
  { label: 'East Side Gallery', aliases: ['east side gallery'] },
  { label: 'Gendarmenmarkt', aliases: ['gendarmenmarkt'] },
  { label: 'Kurfürstendamm', aliases: ['kurfurstendamm', 'kurfuerstendamm', 'kudamm'] },
  { label: 'Berlin City Center', aliases: ['berlin', 'berlin city center', 'mitte'] }
];

const routeSuggestions = [
  {
    id: 'alexanderplatz-brandenburg-gate',
    name: 'Alexanderplatz to Brandenburg Gate',
    origin: 'Alexanderplatz',
    destination: 'Brandenburg Gate',
    routeType: 'walking',
    safetyScore: 92,
    distance: '4.8 km',
    duration: '21 min',
    summary: 'Bright central streets and steady pedestrian traffic make this the safest all-round option.',
    accentColor: '#10B981',
    coordinates: [
      [52.5219, 13.4132],
      [52.5228, 13.4048],
      [52.5217, 13.3935],
      [52.5195, 13.3848],
      [52.5163, 13.3777]
    ],
    breakdown: [
      { label: 'Accident Risk', score: 88 },
      { label: 'Crime Level', score: 91 },
      { label: 'Street Lighting', score: 96 },
      { label: 'User Reports', score: 93 }
    ]
  },
  {
    id: 'friedrichstrasse-tiergarten',
    name: 'Friedrichstrasse through Tiergarten',
    origin: 'Friedrichstrasse',
    destination: 'Tiergarten',
    routeType: 'cycling',
    safetyScore: 84,
    distance: '6.2 km',
    duration: '24 min',
    summary: 'Wide cycling lanes and calmer side streets keep this route balanced and predictable.',
    accentColor: '#F59E0B',
    coordinates: [
      [52.5176, 13.3887],
      [52.5204, 13.3872],
      [52.5226, 13.3727],
      [52.5169, 13.3595],
      [52.5109, 13.3528]
    ],
    breakdown: [
      { label: 'Accident Risk', score: 79 },
      { label: 'Crime Level', score: 82 },
      { label: 'Street Lighting', score: 88 },
      { label: 'User Reports', score: 87 }
    ]
  },
  {
    id: 'museum-island-west-end',
    name: 'Museum Island to West End',
    origin: 'Museum Island',
    destination: 'Charlottenburg',
    routeType: 'driving',
    safetyScore: 73,
    distance: '7.1 km',
    duration: '28 min',
    summary: 'A practical cross-city route with a few lower-visibility stretches that benefit from extra attention.',
    accentColor: '#EF4444',
    coordinates: [
      [52.5169, 13.4010],
      [52.5178, 13.3908],
      [52.5193, 13.3725],
      [52.5207, 13.3514],
      [52.5217, 13.3372]
    ],
    breakdown: [
      { label: 'Accident Risk', score: 69 },
      { label: 'Crime Level', score: 74 },
      { label: 'Street Lighting', score: 77 },
      { label: 'User Reports', score: 72 }
    ]
  }
];

function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .trim()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ');
}

function matchesEntry(query, entry) {
  const normalizedQuery = normalizeText(query);
  return [entry.label, ...entry.aliases].some((candidate) =>
    normalizedQuery.includes(normalizeText(candidate))
  );
}

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

export function getGeocodingSuggestions(query, limit = 6) {
  const normalizedQuery = normalizeText(query);

  if (!normalizedQuery) {
    return berlinGeocodingEntries.slice(0, limit).map((entry) => entry.label);
  }

  return berlinGeocodingEntries
    .filter((entry) => matchesEntry(normalizedQuery, entry) || normalizeText(entry.label).includes(normalizedQuery))
    .map((entry) => entry.label)
    .slice(0, limit);
}

export function validateBerlinLocation(value) {
  if (!String(value || '').trim()) {
    return 'This field is required.';
  }

  const normalizedValue = normalizeText(value);
  const isBerlinMatch = berlinGeocodingEntries.some((entry) => matchesEntry(normalizedValue, entry));

  if (!isBerlinMatch) {
    return 'This map is intended for Berlin City only.';
  }

  return '';
}

export function getRouteSuggestions() {
  return routeSuggestions;
}

export function getRouteById(routeId) {
  return routeSuggestions.find((route) => route.id === routeId) || routeSuggestions[0];
}
