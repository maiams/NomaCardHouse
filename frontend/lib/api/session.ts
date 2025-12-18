/**
 * Session ID management for cart operations
 * Generates and persists UUID in localStorage + cookie
 */

const SESSION_KEY = 'noma_session_id';
const COOKIE_NAME = 'noma_session_id';
const COOKIE_MAX_AGE = 60 * 60 * 24 * 30; // 30 days

/**
 * Generate a UUID v4
 */
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Set cookie (client-side)
 */
function setCookie(name: string, value: string, maxAge: number): void {
  if (typeof document === 'undefined') return;

  document.cookie = `${name}=${value}; max-age=${maxAge}; path=/; SameSite=Lax`;
}

/**
 * Get cookie (client-side)
 */
function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;

  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);

  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }

  return null;
}

/**
 * Get or create session ID
 * Priority: localStorage > cookie > generate new
 */
export function getSessionId(): string {
  // Check if running in browser
  if (typeof window === 'undefined') {
    // Server-side: return a placeholder (won't be used for cart operations)
    return '';
  }

  // Try localStorage first
  let sessionId = localStorage.getItem(SESSION_KEY);

  if (sessionId) {
    // Sync to cookie if missing
    if (!getCookie(COOKIE_NAME)) {
      setCookie(COOKIE_NAME, sessionId, COOKIE_MAX_AGE);
    }
    return sessionId;
  }

  // Try cookie
  sessionId = getCookie(COOKIE_NAME);

  if (sessionId) {
    // Sync to localStorage
    localStorage.setItem(SESSION_KEY, sessionId);
    return sessionId;
  }

  // Generate new session ID
  sessionId = generateUUID();

  // Persist in both localStorage and cookie
  localStorage.setItem(SESSION_KEY, sessionId);
  setCookie(COOKIE_NAME, sessionId, COOKIE_MAX_AGE);

  return sessionId;
}

/**
 * Clear session ID (for logout or cart reset)
 */
export function clearSessionId(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(SESSION_KEY);
  setCookie(COOKIE_NAME, '', -1); // Delete cookie
}

/**
 * Refresh session expiry (extend cookie)
 */
export function refreshSession(): void {
  const sessionId = getSessionId();
  if (sessionId) {
    setCookie(COOKIE_NAME, sessionId, COOKIE_MAX_AGE);
  }
}
