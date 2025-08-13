/**
 * Navigation utilities
 */

/**
 * Simple navigation helper for client-side routing
 */
export const navigateTo = (path: string) => {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
};