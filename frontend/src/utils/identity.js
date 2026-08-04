// Lightweight identity for tracking activity in Langfuse *before* real auth
// exists. Every visitor gets a stable anonymous "guest" id plus a per-visit
// session id. These are sent to the backend (route agent) and the chatbot
// widget so their Langfuse traces can be grouped by visitor and by visit.
//
// When real auth lands, replace getUserId() so it returns the authenticated
// user's id (e.g. "member_<id>") and keep everything else as-is.

import keycloak from '../services/keycloak';

const GUEST_KEY = 'safepath_guest_id';
const SESSION_KEY = 'safepath_session_id';

function makeId(prefix) {
  const rand =
    (typeof crypto !== 'undefined' && crypto.randomUUID)
      ? crypto.randomUUID()
      : (typeof crypto !== 'undefined' && crypto.getRandomValues)
        ? Array.from(crypto.getRandomValues(new Uint32Array(4)), (part) => part.toString(36)).join('')
        : `${Date.now().toString(36)}_${(typeof performance !== 'undefined' ? performance.now().toString(36).replace('.', '') : '0')}`;
  return `${prefix}_${rand}`;
}

// Stable across visits (persists until the user clears browser storage).
// This is the "who" — use it as the Langfuse user_id.
export function getGuestId() {
  if (typeof localStorage === 'undefined') return makeId('guest');
  let id = localStorage.getItem(GUEST_KEY);
  if (!id) {
    id = makeId('guest');
    localStorage.setItem(GUEST_KEY, id);
  }
  return id;
}

// Resets per browser tab/visit. This is the "when" — use it as session_id so
// a single visit's actions group together in Langfuse.
export function getSessionId() {
  if (typeof sessionStorage === 'undefined') return makeId('sess');
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = makeId('sess');
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

// Single place to resolve the current identity. Swap the guest branch for the
// authenticated user id once auth exists.
export function getUserId() {
  // TODO(auth): return `member_${authedUser.id}` when the user is logged in.
  if (keycloak.authenticated && keycloak.tokenParsed) {
    // console.log('Authenticated user id:', keycloak.tokenParsed.sub);
    return `member_${keycloak.tokenParsed.sub}`;
  }
  else {
    return getGuestId();
  }
}


export function getIdentity() {
  return { user_id: getUserId(), session_id: getSessionId() };
}
