const CONSENT_STORAGE_KEY = 'analytics_consent';
const CONSENT_CHOICES = new Set(['accepted', 'rejected']);
const analyticsEnabledCallbacks = new Set();

const ALLOWED_VALUES = Object.freeze({
  contact_method: new Set(['email', 'booking']),
  placement: new Set([
    'navigation',
    'hero',
    'services',
    'projects',
    'contact',
    'footer',
    'error',
  ]),
  destination_type: new Set([
    'section',
    'service',
    'github',
    'linkedin',
    'youtube',
    'idea_factory',
    'email',
    'booking',
    'home',
  ]),
});

const EVENT_PARAMETERS = Object.freeze({
  navigation_click: ['placement', 'destination_type'],
  outbound_click: ['placement', 'destination_type'],
  contact_view: ['placement'],
  contact_click: ['contact_method', 'placement', 'destination_type'],
  contact_submit: [],
});

function readAnalyticsConfig() {
  const configElement = document.getElementById('analyticsConfig');
  if (!configElement) {
    return null;
  }

  try {
    const config = JSON.parse(configElement.textContent);
    if (typeof config.measurementId !== 'string' || !config.measurementId) {
      return null;
    }
    return {
      measurementId: config.measurementId,
      debugMode: config.debugMode === true,
    };
  } catch (error) {
    return null;
  }
}

const analyticsConfig = readAnalyticsConfig();
let analyticsEnabled = false;
let googleAnalyticsInitialized = false;
let sessionConsentChoice = null;

function readConsentChoice() {
  try {
    const choice = window.localStorage.getItem(CONSENT_STORAGE_KEY);
    if (CONSENT_CHOICES.has(choice)) {
      return choice;
    }
  } catch (error) {
    // Fall back to the choice made for the current page.
  }
  return sessionConsentChoice;
}

function storeConsentChoice(choice) {
  sessionConsentChoice = choice;
  try {
    window.localStorage.setItem(CONSENT_STORAGE_KEY, choice);
  } catch (error) {
    // Consent still applies for this page when persistent storage is unavailable.
  }
}

function clearConsentChoice() {
  sessionConsentChoice = null;
  try {
    window.localStorage.removeItem(CONSENT_STORAGE_KEY);
  } catch (error) {
    // Denied consent still applies for this page when storage is unavailable.
  }
}

function sanitizedPageLocation() {
  try {
    const pageUrl = new URL(window.location.href);
    return {
      page_location: `${pageUrl.origin}${pageUrl.pathname}`,
      page_path: pageUrl.pathname,
    };
  } catch (error) {
    return {
      page_location: window.location.origin + window.location.pathname,
      page_path: window.location.pathname,
    };
  }
}

function notifyAnalyticsEnabled() {
  analyticsEnabledCallbacks.forEach((callback) => callback());
}

function initializeGoogleAnalytics() {
  if (!analyticsConfig) {
    return;
  }

  analyticsEnabled = true;
  window[`ga-disable-${analyticsConfig.measurementId}`] = false;

  if (googleAnalyticsInitialized) {
    notifyAnalyticsEnabled();
    return;
  }

  googleAnalyticsInitialized = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    window.dataLayer.push(arguments);
  };

  window.gtag('js', new Date());
  window.gtag('set', 'ads_data_redaction', true);
  window.gtag('config', analyticsConfig.measurementId, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    cookie_domain: 'none',
    debug_mode: analyticsConfig.debugMode,
    page_referrer: '',
    ...sanitizedPageLocation(),
  });

  const googleTag = document.createElement('script');
  googleTag.async = true;
  googleTag.src = (
    'https://www.googletagmanager.com/gtag/js?id='
    + encodeURIComponent(analyticsConfig.measurementId)
  );
  document.head.appendChild(googleTag);
  notifyAnalyticsEnabled();
}

function disableGoogleAnalytics() {
  analyticsEnabled = false;
  if (analyticsConfig && googleAnalyticsInitialized) {
    window[`ga-disable-${analyticsConfig.measurementId}`] = true;
    clearGoogleAnalyticsCookies();
  }
}

function clearGoogleAnalyticsCookies() {
  if (typeof document.cookie !== 'string' || !document.cookie) {
    return;
  }

  const hostname = window.location.hostname.toLowerCase();
  const cookieDomains = new Set();
  if (hostname) {
    cookieDomains.add(hostname);
    cookieDomains.add(`.${hostname}`);
  }
  if (
    hostname === 'teraearlywine.com'
    || hostname.endsWith('.teraearlywine.com')
  ) {
    cookieDomains.add('teraearlywine.com');
    cookieDomains.add('.teraearlywine.com');
  }

  const analyticsCookieNames = document.cookie
    .split(';')
    .map((cookie) => cookie.split('=', 1)[0].trim())
    .filter((name) => /^_ga(?:_|$)|^_gid$|^_gat(?:_|$)/.test(name));

  for (const name of analyticsCookieNames) {
    document.cookie = `${name}=; Max-Age=0; path=/; SameSite=Lax`;
    for (const domain of cookieDomains) {
      document.cookie = (
        `${name}=; Max-Age=0; path=/; `
        + `domain=${domain}; SameSite=Lax`
      );
    }
  }
}

function sanitizeEventParameters(eventName, parameters) {
  const expectedParameters = EVENT_PARAMETERS[eventName];
  if (!expectedParameters) {
    return null;
  }

  const sanitized = {};
  for (const parameterName of expectedParameters) {
    const value = parameters[parameterName];
    if (
      typeof value !== 'string'
      || !ALLOWED_VALUES[parameterName].has(value)
    ) {
      return null;
    }
    sanitized[parameterName] = value;
  }

  return sanitized;
}

function trackEvent(eventName, parameters = {}) {
  const sanitized = sanitizeEventParameters(eventName, parameters);
  if (
    !analyticsEnabled
    || readConsentChoice() !== 'accepted'
    || !sanitized
    || typeof window.gtag !== 'function'
  ) {
    return false;
  }

  window.gtag('event', eventName, {
    ...sanitized,
    page_referrer: '',
  });
  return true;
}

function initializeConsentControls() {
  const banner = document.getElementById('analyticsConsent');
  if (!banner) {
    return;
  }

  const choiceButtons = banner.querySelectorAll('[data-consent-choice]');
  const reopenButton = document.querySelector('[data-consent-reopen]');
  let returnFocusToReopenButton = false;
  const showBanner = () => {
    banner.hidden = false;
  };
  const hideBanner = () => {
    banner.hidden = true;
  };

  if (readConsentChoice()) {
    hideBanner();
  } else {
    showBanner();
  }

  choiceButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const choice = button.dataset.consentChoice;
      if (!CONSENT_CHOICES.has(choice)) {
        return;
      }

      storeConsentChoice(choice);
      if (choice === 'accepted') {
        initializeGoogleAnalytics();
      } else {
        disableGoogleAnalytics();
      }
      hideBanner();
      if (returnFocusToReopenButton) {
        reopenButton?.focus();
        returnFocusToReopenButton = false;
      }
    });
  });

  reopenButton?.addEventListener('click', () => {
    returnFocusToReopenButton = true;
    clearConsentChoice();
    disableGoogleAnalytics();
    showBanner();
    choiceButtons[0]?.focus();
  });

  if (readConsentChoice() === 'accepted') {
    initializeGoogleAnalytics();
  }
}

function initializeTaggedClickTracking() {
  document.addEventListener('click', (event) => {
    if (!event.target || typeof event.target.closest !== 'function') {
      return;
    }

    const link = event.target.closest('[data-analytics-event]');
    if (!link) {
      return;
    }

    trackEvent(link.dataset.analyticsEvent, {
      contact_method: link.dataset.contactMethod,
      placement: link.dataset.placement,
      destination_type: link.dataset.destinationType,
    });
  });
}

function initializeContactViewTracking() {
  const contactSection = document.querySelector('[data-analytics-contact-view]');
  if (!contactSection || !('IntersectionObserver' in window)) {
    return;
  }

  let isHalfVisible = false;
  let hasTrackedContactView = false;
  const trackVisibleContact = () => {
    if (
      hasTrackedContactView
      || !isHalfVisible
      || !trackEvent('contact_view', { placement: 'contact' })
    ) {
      return;
    }

    hasTrackedContactView = true;
    observer.disconnect();
    analyticsEnabledCallbacks.delete(trackVisibleContact);
  };

  const observer = new IntersectionObserver((entries) => {
    isHalfVisible = entries.some(
      (entry) => entry.isIntersecting && entry.intersectionRatio >= 0.5,
    );
    trackVisibleContact();
  }, { threshold: 0.5 });

  analyticsEnabledCallbacks.add(trackVisibleContact);
  observer.observe(contactSection);
}

function initializeContactSubmitTracking() {
  document.addEventListener('contact:submitted', () => {
    trackEvent('contact_submit');
  });
}

initializeConsentControls();
initializeTaggedClickTracking();
initializeContactViewTracking();
initializeContactSubmitTracking();
