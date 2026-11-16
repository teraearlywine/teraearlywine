const CONSENT_STORAGE_KEY = 'analytics_consent';
const CONSENT_RESET_KEY = 'analytics_consent_reset';
const CONSENT_CHOICES = new Set(['accepted', 'rejected']);
const analyticsEnabledCallbacks = new Set();

const ALLOWED_VALUES = Object.freeze({
  contact_method: new Set(['email', 'booking']),
  guide: new Set(['teams', 'professionals', 'both']),
  placement: new Set([
    'navigation',
    'hero',
    'services',
    'projects',
    'article',
    'contact',
    'footer',
    'error',
    'signup',
    'writing_stack',
    'featured',
    'archive',
  ]),
  destination_type: new Set([
    'teams',
    'professionals',
    'writing',
    'archive',
    'rss',
    'section',
    'service',
    'github',
    'linkedin',
    'youtube',
    'idea_factory',
    'email',
    'booking',
    'home',
    'resource',
    'exercise',
    'dashboard_example',
    'net_sales_demo',
    'decision_note',
    'diagnostic',
    'ai_workflow_review',
    'migration_cutover',
    'readiness_scorecard',
  ]),
});

const EVENT_PARAMETERS = Object.freeze({
  navigation_click: ['placement', 'destination_type'],
  outbound_click: ['placement', 'destination_type'],
  contact_view: ['placement'],
  contact_click: ['contact_method', 'placement', 'destination_type'],
  contact_submit: [],
  resource_download: ['placement', 'destination_type'],
  newsletter_cta_click: ['placement', 'guide'],
  newsletter_guide_select: ['guide'],
  newsletter_signup: ['guide'],
  newsletter_confirm: ['guide'],
  newsletter_guide_download: ['guide'],
  newsletter_unsubscribe: [],
});

const PRODUCTION_MEASUREMENT_ID = 'G-NF6SVCGZDF';
const PRODUCTION_HOSTS = new Set(['teraearlywine.com', 'www.teraearlywine.com']);
const CAMPAIGN_TUPLES = new Map([
  ['linkedin|social|website_baseline_2026_09|profile', {
    campaign_source: 'linkedin', campaign_medium: 'social',
    campaign_name: 'website_baseline_2026_09', campaign_content: 'profile',
  }],
  ['newsletter|email|website_baseline_2026_09|footer', {
    campaign_source: 'newsletter', campaign_medium: 'email',
    campaign_name: 'website_baseline_2026_09', campaign_content: 'footer',
  }],
  ['newsletter|email|business_of_technology|issue', {
    campaign_source: 'newsletter', campaign_medium: 'email',
    campaign_name: 'business_of_technology', campaign_content: 'issue',
  }],
]);
const REFERRER_ORIGINS = new Map([
  ['google.com', 'https://www.google.com/'],
  ['www.google.com', 'https://www.google.com/'],
  ['bing.com', 'https://www.bing.com/'],
  ['www.bing.com', 'https://www.bing.com/'],
  ['linkedin.com', 'https://www.linkedin.com/'],
  ['www.linkedin.com', 'https://www.linkedin.com/'],
  ['lnkd.in', 'https://www.linkedin.com/'],
]);

function canCollectAnalytics(config, hostname) {
  if (!config || !config.measurementId) return false;
  if (config.measurementId !== PRODUCTION_MEASUREMENT_ID) return true;
  return config.debugMode === false
    && PRODUCTION_HOSTS.has(hostname.toLowerCase());
}

function allowlistedAttribution(locationHref, referrer) {
  const result = { page_referrer: '' };
  try {
    const url = new URL(locationHref);
    const names = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
    const values = names.map((name) => url.searchParams.getAll(name));
    if (values.every((list) => list.length === 1 && !list[0].includes('|'))) {
      const campaign = CAMPAIGN_TUPLES.get(values.map((list) => list[0]).join('|'));
      if (campaign) Object.assign(result, campaign);
    }
  } catch (_) { /* Unknown campaign stays unknown. */ }
  try {
    const url = new URL(referrer);
    if (url.protocol === 'https:' && !url.username && !url.password && !url.port) {
      result.page_referrer = REFERRER_ORIGINS.get(url.hostname) || '';
    }
  } catch (_) { /* Unknown referrer stays blank. */ }
  return result;
}

function readAnalyticsConfig() {
  // Bearer links may also reach a generic 404 handler. Never load Google on them.
  if (/^\/newsletter\/(?:confirm|unsubscribe)(?:\/|$)/i.test(window.location.pathname)) return null;
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
      pagePath: typeof config.pagePath === 'string' ? config.pagePath : '/404',
    };
  } catch (error) {
    return null;
  }
}

const analyticsConfig = readAnalyticsConfig();
let analyticsEnabled = false;
let googleAnalyticsInitialized = false;
let googleTagLoaded = false;
let sessionConsentChoice = null;
let analyticsPageReferrer = '';

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
    sessionConsentChoice = null;
    if (choice === 'rejected') window.localStorage.setItem(CONSENT_RESET_KEY, String(Date.now()));
  } catch (error) {
    // Consent still applies for this page when persistent storage is unavailable.
  }
}

function clearConsentChoice() {
  sessionConsentChoice = null;
  try {
    window.localStorage.removeItem(CONSENT_STORAGE_KEY);
    window.localStorage.setItem(CONSENT_RESET_KEY, String(Date.now()));
  } catch (error) {
    // Denied consent still applies for this page when storage is unavailable.
  }
}

function sanitizedPageLocation() {
  // Flask supplies only a known route/content path or a fixed error path.
  // Never fall back to the browser pathname, including on unknown URLs.
  const pagePath = analyticsConfig?.pagePath || '/404';
  return {
    page_location: window.location.origin + pagePath,
    page_path: pagePath,
  };
}

function notifyAnalyticsEnabled() {
  analyticsEnabledCallbacks.forEach((callback) => callback());
}

function initializeGoogleAnalytics() {
  if (!canCollectAnalytics(analyticsConfig, window.location.hostname)) return;

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

  const attribution = allowlistedAttribution(window.location.href, document.referrer);
  analyticsPageReferrer = attribution.page_referrer;

  window.gtag('js', new Date());
  window.gtag('set', 'ads_data_redaction', true);
  window.gtag('config', analyticsConfig.measurementId, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    cookie_domain: 'none',
    // GA4 requires omission to disable debug mode; false is not sufficient.
    // The production host guard already rejects debugMode=true.
    ...(analyticsConfig.debugMode ? { debug_mode: true } : {}),
    // Explicit overrides prevent automatic UTM fallback, including unapproved
    // term/id values alongside an otherwise approved campaign tuple.
    campaign_source: '',
    campaign_medium: '',
    campaign_name: '',
    campaign_content: '',
    campaign_term: '',
    campaign_id: '',
    ...attribution,
    ...sanitizedPageLocation(),
  });

  const googleTag = document.createElement('script');
  googleTag.async = true;
  googleTag.referrerPolicy = 'no-referrer';
  googleTag.src = (
    'https://www.googletagmanager.com/gtag/js?id='
    + encodeURIComponent(analyticsConfig.measurementId)
  );
  googleTag.onload = () => {
    googleTagLoaded = true;
    flushNewsletterEvents();
  };
  document.head.appendChild(googleTag);
  notifyAnalyticsEnabled();
}

function disableGoogleAnalytics() {
  analyticsEnabled = false;
  clearNewsletterEvents();
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

function trackEvent(eventName, parameters = {}, sourcePath, referrer = analyticsPageReferrer) {
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
    page_referrer: referrer,
    ...(sourcePath ? {page_location: window.location.origin + sourcePath, page_path: sourcePath} : {}),
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
  } else {
    clearNewsletterEvents();
  }
  window.addEventListener('storage', event => {
    if (event.key !== null && event.key !== CONSENT_STORAGE_KEY) return;
    sessionConsentChoice = null;
    if (event.newValue !== 'accepted') {
      disableGoogleAnalytics();
      if (event.newValue === 'rejected') hideBanner();
      else showBanner();
    } else if (readConsentChoice() === 'accepted') {
      initializeGoogleAnalytics();
      hideBanner();
    }
  });
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

    const parameters = {
      contact_method: link.dataset.contactMethod,
      placement: link.dataset.placement,
      destination_type: link.dataset.destinationType,
      guide: link.dataset.guide,
    };
    const name = link.dataset.analyticsEvent;
    if (name === 'newsletter_guide_download') {
      recordNewsletterEvent(name, parameters);
      return;
    }
    const destinationHash = link.hash || '';
    if (['navigation_click', 'newsletter_cta_click'].includes(name)
        && analyticsEnabled && readConsentChoice() === 'accepted'
        && event.button === 0 && !event.defaultPrevented && !event.ctrlKey && !event.metaKey
        && !event.shiftKey && !event.altKey && !link.target && link.origin === window.location.origin
        && isPublicNavigationPage(analyticsConfig.pagePath) && isPublicNavigationPage(link.pathname)
        && NAVIGATION_HASHES.has(destinationHash)
        && !(link.pathname === analyticsConfig.pagePath && destinationHash)) {
      // GA can batch a click past the lifetime of this document. Deliver it on
      // the next page, preserving the source and leaving native navigation alone.
      try {
        const sanitized = sanitizeEventParameters(name, parameters);
        if (sanitized) {
          window.sessionStorage.setItem(NAVIGATION_CLICK_KEY, JSON.stringify({
            name, parameters: sanitized, from: analyticsConfig.pagePath,
            to: link.pathname, hash: destinationHash, at: Date.now(),
          }));
          return;
        }
      } catch (_) { /* When tab storage is blocked, try ordinary click tracking. */ }
    }
    trackEvent(name, parameters);
  });
}

const NAVIGATION_CLICK_KEY = 'tracked_navigation';
const NAVIGATION_HASHES = new Set([
  '', '#archive', '#blog-offer-heading', '#contact', '#exercise', '#experience',
  '#projects', '#readiness-heading', '#sample', '#services',
]);

function isPublicNavigationPage(path) {
  return ['/', '/blog/', '/for-teams/', '/for-professionals/', '/newsletter/'].includes(path)
    || /^\/blog\/[a-z0-9-]+\/$/.test(path) || /^\/services\/[a-z0-9-]+$/.test(path);
}

function finishTrackedNavigation() {
  try {
    const saved = window.sessionStorage.getItem(NAVIGATION_CLICK_KEY);
    if (!saved) return;
    window.sessionStorage.removeItem(NAVIGATION_CLICK_KEY);
    const click = JSON.parse(saved);
    const age = Date.now() - click.at;
    if (readConsentChoice() === 'accepted' && age >= 0 && age < 60_000
        && ['navigation_click', 'newsletter_cta_click'].includes(click.name)
        && isPublicNavigationPage(click.from) && isPublicNavigationPage(click.to)
        && click.to === analyticsConfig?.pagePath && NAVIGATION_HASHES.has(click.hash)
        && click.hash === window.location.hash) {
      trackEvent(click.name, click.parameters, click.from);
    }
  } catch (_) { /* Browser storage and previously stored data can be unavailable. */ }
}

// The server renders each transition once. A slow Google tag can outlive a
// receipt page, so retain consenting actions briefly in this tab until it loads.
const NEWSLETTER_QUEUE_KEY = 'pending_newsletter_events';
const NEWSLETTER_EVENT_PATHS = new Map([
  ['newsletter_signup', '/newsletter/check-email/'],
  ['newsletter_confirm', '/newsletter/guides/'],
  ['newsletter_guide_download', '/newsletter/guides/'],
  ['newsletter_unsubscribe', '/newsletter/unsubscribed/'],
]);
const NEWSLETTER_QUEUE_LIMIT = 32;
let memoryNewsletterEvents = [];

function consentReset() {
  try {
    return window.localStorage.getItem(CONSENT_RESET_KEY) || '';
  } catch (_) {
    return '';
  }
}

function storedNewsletterEvents() {
  try {
    const data = JSON.parse(window.sessionStorage.getItem(NEWSLETTER_QUEUE_KEY) || 'null');
    // A tab on a private link has no analytics script to observe another tab
    // withdrawing consent. A later opt-in must not revive that earlier batch.
    if (data && data.reset === consentReset() && Array.isArray(data.events)) {
      return data.events.slice(-NEWSLETTER_QUEUE_LIMIT);
    }
  } catch (_) { /* Tab storage can be blocked. */ }
  return [];
}

function clearNewsletterEvents() {
  memoryNewsletterEvents = [];
  try { window.sessionStorage.removeItem(NEWSLETTER_QUEUE_KEY); } catch (_) { /* unavailable */ }
}

function flushNewsletterEvents() {
  if (!googleTagLoaded || !analyticsEnabled || readConsentChoice() !== 'accepted') return;
  const events = storedNewsletterEvents();
  // Claim the stored batch before dispatch. Reloads cannot replay it.
  try { window.sessionStorage.removeItem(NEWSLETTER_QUEUE_KEY); } catch (_) { events.length = 0; }
  events.push(...memoryNewsletterEvents);
  memoryNewsletterEvents = [];
  for (const event of events) {
    const path = NEWSLETTER_EVENT_PATHS.get(event?.name);
    const age = Date.now() - event?.at;
    if (path && Number.isFinite(event.at) && age >= 0 && age < 60_000) {
      trackEvent(event.name, {guide: event.guide}, path, '');
    }
  }
}

function recordNewsletterEvent(name, parameters) {
  const path = NEWSLETTER_EVENT_PATHS.get(name);
  const sanitized = sanitizeEventParameters(name, parameters);
  if (!path || path !== analyticsConfig?.pagePath || !sanitized
      || !analyticsEnabled || readConsentChoice() !== 'accepted') return false;
  if (googleTagLoaded) return trackEvent(name, sanitized, path, '');
  const event = {name, ...sanitized, at: Date.now()};
  try {
    const events = [...storedNewsletterEvents(), event].slice(-NEWSLETTER_QUEUE_LIMIT);
    window.sessionStorage.setItem(NEWSLETTER_QUEUE_KEY, JSON.stringify({reset: consentReset(), events}));
  } catch (_) {
    memoryNewsletterEvents = [...memoryNewsletterEvents, event].slice(-NEWSLETTER_QUEUE_LIMIT);
  }
  return true;
}

function initializeNewsletterTracking() {
  const choices = document.querySelector('[data-newsletter-guides]');
  choices?.addEventListener('change', event => {
    if (event.target.name === 'guide' && event.target.checked) {
      trackEvent('newsletter_guide_select', {guide: event.target.value});
    }
  });

  const receipt = document.querySelector('[data-newsletter-receipt]');
  if (!receipt) return;
  const name = receipt.dataset.newsletterReceipt;
  if (!['newsletter_signup', 'newsletter_confirm', 'newsletter_unsubscribe'].includes(name)) return;
  const sendReceipt = () => {
    if (recordNewsletterEvent(name, {guide: receipt.dataset.guide})) {
      analyticsEnabledCallbacks.delete(sendReceipt);
    }
  };
  analyticsEnabledCallbacks.add(sendReceipt);
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

initializeNewsletterTracking();
initializeConsentControls();
finishTrackedNavigation();
initializeTaggedClickTracking();
initializeContactViewTracking();
initializeContactSubmitTracking();
