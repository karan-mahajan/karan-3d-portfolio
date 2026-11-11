function wrap(pick) {
  return {
    getItem(key) {
      try { return pick().getItem(key); } catch { return null; }
    },
    setItem(key, value) {
      try { pick().setItem(key, value); } catch { /* storage blocked */ }
    },
    removeItem(key) {
      try { pick().removeItem(key); } catch { /* storage blocked */ }
    },
  };
}

/** localStorage / sessionStorage that never throw when site data is blocked. */
export const safeLocal = wrap(() => window.localStorage);
export const safeSession = wrap(() => window.sessionStorage);
