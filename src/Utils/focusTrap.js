const FOCUSABLE =
  'button, [href], input, textarea, select, [tabindex]:not([tabindex="-1"])';

/**
 * Move focus into a dialog and keep Tab cycling inside it.
 * @returns {() => void} release — stops trapping and restores the prior focus.
 */
export function trapFocus(container) {
  const previous = document.activeElement;
  const onKey = (e) => {
    if (e.key !== 'Tab') return;
    const items = [...container.querySelectorAll(FOCUSABLE)].filter(
      (el) => !el.disabled && el.getClientRects().length > 0,
    );
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    const active = document.activeElement;
    if (!container.contains(active)) {
      e.preventDefault();
      first.focus();
    } else if (e.shiftKey && active === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  };
  document.addEventListener('keydown', onKey, true);
  container.setAttribute('tabindex', '-1');
  container.focus({ preventScroll: true });
  return () => {
    document.removeEventListener('keydown', onKey, true);
    if (previous && previous !== document.body) {
      previous.focus?.({ preventScroll: true });
    } else {
      document.activeElement?.blur?.();
    }
  };
}
