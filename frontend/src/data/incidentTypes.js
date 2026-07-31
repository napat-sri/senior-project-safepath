const INCIDENT_TYPE_COLORS = {
  'Harassment': 'red-darken-1',
  'Theft': 'amber-darken-2',
  'Unsafe area': 'purple-darken-1',
  'Suspicious activity': 'blue-darken-1',
  'Transport issue': 'teal-lighten-1',
  'Other': 'blue-grey',
};
export const incidentTypeColor = (type) => INCIDENT_TYPE_COLORS[type] || 'grey';