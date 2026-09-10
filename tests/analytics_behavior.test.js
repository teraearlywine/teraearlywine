'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const analyticsSource = fs.readFileSync(
  path.join(__dirname, '..', 'core', 'home', 'assets', 'js', 'analytics.js'),
  'utf8',
);

class FakeElement {
  constructor(dataset = {}) {
    this.dataset = dataset;
    this.hidden = false;
    this.listeners = new Map();
  }

  addEventListener(type, callback) {
    this.listeners.set(type, callback);
  }

  click() {
    this.listeners.get('click')?.({ target: this });
  }

  closest(selector) {
    if (selector === '[data-analytics-event]' && this.dataset.analyticsEvent) {
      return this;
    }
    return null;
  }

  focus() {
    this.ownerDocument.activeElement = this;
  }
}

function createHarness(initialConsent = null, storageAvailable = true, options = {}) {
  const storage = new Map();
  if (initialConsent) {
    storage.set('analytics_consent', initialConsent);
  }

  const rejectButton = new FakeElement({ consentChoice: 'rejected' });
  const acceptButton = new FakeElement({ consentChoice: 'accepted' });
  const reopenButton = new FakeElement();
  const contactSection = new FakeElement();
  const configElement = {
    textContent: JSON.stringify({
      measurementId: options.measurementId ?? 'G-TEST123',
      debugMode: options.debugMode ?? true,
      pagePath: options.pagePath ?? '/',
    }),
  };
  const banner = new FakeElement();
  banner.hidden = true;
  banner.querySelectorAll = () => [rejectButton, acceptButton];

  const documentListeners = new Map();
  const loadedScripts = [];
  const cookieWrites = [];
  let cookieHeader = '';
  const document = {
    activeElement: null,
    referrer: options.referrer ?? 'https://referrer.example/account?email=private%40example.com#secret',
    head: {
      appendChild(element) {
        loadedScripts.push(element);
      },
    },
    getElementById(id) {
      if (id === 'analyticsConfig') return options.missingConfig ? null : configElement;
      if (id === 'analyticsConsent') return banner;
      return null;
    },
    querySelector(selector) {
      if (selector === '[data-consent-reopen]') return reopenButton;
      if (selector === '[data-analytics-contact-view]') return contactSection;
      return null;
    },
    createElement(tagName) {
      return { tagName, async: false, src: '' };
    },
    addEventListener(type, callback) {
      documentListeners.set(type, callback);
    },
  };
  Object.defineProperty(document, 'cookie', {
    get() {
      return cookieHeader;
    },
    set(value) {
      cookieWrites.push(value);
    },
  });

  for (const element of [
    rejectButton,
    acceptButton,
    reopenButton,
    contactSection,
    banner,
  ]) {
    element.ownerDocument = document;
  }

  class FakeIntersectionObserver {
    constructor(callback, options) {
      this.callback = callback;
      this.options = options;
      this.disconnected = false;
      FakeIntersectionObserver.instance = this;
    }

    observe(element) {
      this.observedElement = element;
    }

    disconnect() {
      this.disconnected = true;
    }

    trigger(intersectionRatio) {
      if (!this.disconnected) {
        this.callback([{
          isIntersecting: intersectionRatio > 0,
          intersectionRatio,
        }]);
      }
    }
  }

  const localStorage = {
    getItem(key) {
      if (!storageAvailable) throw new Error('storage unavailable');
      return storage.get(key) ?? null;
    },
    setItem(key, value) {
      if (!storageAvailable) throw new Error('storage unavailable');
      storage.set(key, value);
    },
    removeItem(key) {
      if (!storageAvailable) throw new Error('storage unavailable');
      storage.delete(key);
    },
  };
  const window = {
    document,
    IntersectionObserver: FakeIntersectionObserver,
    localStorage,
    location: new URL(options.href ?? 'https://www.teraearlywine.com/work?email=person%40example.com#private'),
  };
  const context = {
    Date,
    IntersectionObserver: FakeIntersectionObserver,
    JSON,
    URL,
    document,
    encodeURIComponent,
    window,
  };
  vm.createContext(context);
  vm.runInContext(analyticsSource, context, { filename: 'analytics.js' });

  return {
    context,
    acceptButton,
    banner,
    contactSection,
    cookieWrites,
    document,
    documentListeners,
    loadedScripts,
    observer: FakeIntersectionObserver.instance,
    rejectButton,
    reopenButton,
    setCookieHeader(value) {
      cookieHeader = value;
    },
    storage,
    window,
  };
}

function commands(harness) {
  return (harness.window.dataLayer || []).map((entry) => Array.from(entry));
}

function dispatchTrackedClick(harness, dataset) {
  const target = new FakeElement(dataset);
  target.ownerDocument = harness.document;
  harness.documentListeners.get('click')({ target });
}

function dispatchContactSubmitted(harness, detail = undefined) {
  harness.documentListeners.get('contact:submitted')?.({ detail });
}

const harness = createHarness();
assert.equal(harness.banner.hidden, false);
assert.equal(harness.loadedScripts.length, 0);
assert.equal(harness.window.gtag, undefined);

dispatchTrackedClick(harness, {
  analyticsEvent: 'outbound_click',
  placement: 'hero',
  destinationType: 'github',
});
assert.deepEqual(commands(harness), []);
dispatchContactSubmitted(harness, {
  email: 'private-before-consent@example.com',
  message: 'do not retain this message',
});
assert.deepEqual(commands(harness), []);

harness.rejectButton.click();
assert.equal(harness.storage.get('analytics_consent'), 'rejected');
assert.equal(harness.loadedScripts.length, 0);
assert.equal(harness.window.gtag, undefined);
assert.equal(harness.document.activeElement, null);

harness.reopenButton.click();
assert.equal(harness.storage.has('analytics_consent'), false);
assert.equal(harness.banner.hidden, false);
assert.equal(harness.document.activeElement, harness.rejectButton);

harness.observer.trigger(0.75);
assert.deepEqual(commands(harness), []);
assert.equal(harness.observer.disconnected, false);

harness.acceptButton.click();
assert.equal(harness.storage.get('analytics_consent'), 'accepted');
assert.equal(harness.loadedScripts.length, 1);
assert.equal(
  harness.loadedScripts[0].src,
  'https://www.googletagmanager.com/gtag/js?id=G-TEST123',
);
assert.equal(harness.document.activeElement, harness.reopenButton);

const configCommand = commands(harness).find(([name]) => name === 'config');
assert.ok(configCommand);
assert.equal(configCommand[2].cookie_domain, 'none');
assert.equal(configCommand[2].page_referrer, '');
assert.equal(configCommand[2].page_location, 'https://www.teraearlywine.com/');
assert.equal(configCommand[2].page_path, '/');
assert.equal(JSON.stringify(configCommand).includes('person%40example.com'), false);
assert.equal(JSON.stringify(configCommand).includes('#private'), false);
assert.equal(JSON.stringify(configCommand).includes('referrer.example'), false);
assert.equal(JSON.stringify(configCommand).includes('private%40example.com'), false);
assert.equal(JSON.stringify(configCommand).includes('#secret'), false);

let eventCommands = commands(harness).filter(([name]) => name === 'event');
assert.deepEqual(
  JSON.parse(JSON.stringify(
    eventCommands.map(([name, eventName, parameters]) => ({
      name,
      eventName,
      parameters,
    })),
  )),
  [{
    name: 'event',
    eventName: 'contact_view',
    parameters: {
      placement: 'contact',
      page_referrer: '',
    },
  }],
);
assert.equal(harness.observer.disconnected, true);

const beforeSubmitCount = eventCommands.length;
dispatchContactSubmitted(harness, {
  email: 'private-after-consent@example.com',
  validationError: 'private validation details',
  url: 'https://example.com/private?email=private-after-consent@example.com',
});
eventCommands = commands(harness).filter(([name]) => name === 'event');
assert.equal(eventCommands.length, beforeSubmitCount + 1);
assert.deepEqual(
  JSON.parse(JSON.stringify(eventCommands.at(-1))),
  [
    'event',
    'contact_submit',
    { page_referrer: '' },
  ],
);
assert.equal(
  JSON.stringify(eventCommands.at(-1)).includes('private-after-consent'),
  false,
);
assert.equal(
  JSON.stringify(eventCommands.at(-1)).includes('validation'),
  false,
);

dispatchTrackedClick(harness, {
  analyticsEvent: 'contact_click',
  contactMethod: 'booking',
  destinationType: 'booking',
  href: 'https://calendar.example/book?email=person@example.com',
  placement: 'contact',
});
eventCommands = commands(harness).filter(([name]) => name === 'event');
assert.deepEqual(
  JSON.parse(JSON.stringify(eventCommands.at(-1)[2])),
  {
    contact_method: 'booking',
    placement: 'contact',
    destination_type: 'booking',
    page_referrer: '',
  },
);
assert.equal(JSON.stringify(eventCommands).includes('calendar.example'), false);
assert.equal(JSON.stringify(eventCommands).includes('person@example.com'), false);
assert.equal(JSON.stringify(eventCommands).includes('referrer.example'), false);
assert.equal(JSON.stringify(eventCommands).includes('private%40example.com'), false);

const eventCount = eventCommands.length;
dispatchTrackedClick(harness, {
  analyticsEvent: 'outbound_click',
  destinationType: 'https://example.com/private',
  placement: 'hero',
});
assert.equal(
  commands(harness).filter(([name]) => name === 'event').length,
  eventCount,
);

harness.setCookieHeader(
  '_ga=abc; _ga_TEST123=def; _gid=ghi; _gat_TEST123=jkl; preference=keep',
);
harness.reopenButton.click();
assert.equal(harness.window['ga-disable-G-TEST123'], true);
const cookieDomains = [
  null,
  'www.teraearlywine.com',
  '.www.teraearlywine.com',
  'teraearlywine.com',
  '.teraearlywine.com',
];
const expectedCookieWrites = [];
for (const name of ['_ga', '_ga_TEST123', '_gid', '_gat_TEST123']) {
  for (const domain of cookieDomains) {
    expectedCookieWrites.push(
      `${name}=; Max-Age=0; path=/; `
      + (domain ? `domain=${domain}; ` : '')
      + 'SameSite=Lax',
    );
  }
}
assert.deepEqual(harness.cookieWrites, expectedCookieWrites);
assert.equal(
  harness.cookieWrites.some((write) => write.startsWith('preference=')),
  false,
);
dispatchTrackedClick(harness, {
  analyticsEvent: 'outbound_click',
  destinationType: 'github',
  placement: 'hero',
});
assert.equal(
  commands(harness).filter(([name]) => name === 'event').length,
  eventCount,
);
harness.rejectButton.click();
assert.equal(commands(harness).filter(([name]) => name === 'event').length, eventCount);
assert.equal(harness.document.activeElement, harness.reopenButton);

const returningVisitor = createHarness('accepted');
assert.equal(returningVisitor.loadedScripts.length, 1);
assert.equal(returningVisitor.banner.hidden, true);

const returningRejector = createHarness('rejected');
assert.equal(returningRejector.loadedScripts.length, 0);
assert.equal(returningRejector.window.gtag, undefined);

const privateContext = createHarness(null, false);
privateContext.acceptButton.click();
assert.equal(privateContext.document.activeElement, null);
dispatchTrackedClick(privateContext, {
  analyticsEvent: 'outbound_click',
  destinationType: 'github',
  placement: 'hero',
});
assert.equal(privateContext.loadedScripts.length, 1);
assert.equal(
  commands(privateContext).filter(([name]) => name === 'event').length,
  1,
);

const serviceVisitor = createHarness('accepted');
dispatchTrackedClick(serviceVisitor, {
  analyticsEvent: 'navigation_click',
  destinationType: 'service',
  placement: 'services',
});
const serviceEvents = commands(serviceVisitor).filter(([name]) => name === 'event');
assert.equal(serviceEvents.length, 1);
assert.equal(serviceEvents[0][1], 'navigation_click');
assert.equal(serviceEvents[0][2].destination_type, 'service');
assert.equal(serviceEvents[0][2].placement, 'services');

// Production routing must fail closed before a tag, config, or custom event exists.
for (const host of ['localhost', '127.0.0.1', 'preview.example', 'teraearlywine.com.attacker.example', 'preview.teraearlywine.com']) {
  const blocked = createHarness('accepted', true, {measurementId: 'G-NF6SVCGZDF', debugMode: false, href: `https://${host}/`});
  dispatchContactSubmitted(blocked);
  assert.equal(blocked.loadedScripts.length, 0, host);
  assert.equal(blocked.window.gtag, undefined, host);
  assert.deepEqual(commands(blocked), [], host);
}
for (const host of ['teraearlywine.com', 'www.teraearlywine.com']) {
  const allowed = createHarness('accepted', true, {measurementId: 'G-NF6SVCGZDF', debugMode: false, href: `https://${host}/`});
  allowed.acceptButton.click();
  assert.equal(allowed.loadedScripts.length, 1);
  const debugBlocked = createHarness('accepted', true, {measurementId: 'G-NF6SVCGZDF', debugMode: true, href: `https://${host}/`});
  assert.equal(debugBlocked.loadedScripts.length, 0);
}
assert.equal(createHarness('accepted', true, {missingConfig: true}).loadedScripts.length, 0);
assert.equal(createHarness('accepted', true, {href: 'http://localhost/', measurementId: 'G-TEST'}).loadedScripts.length, 1);

const helperContext = createHarness().context;
const attribution = (href, referrer = '') => JSON.parse(JSON.stringify(vm.runInContext(`allowlistedAttribution(${JSON.stringify(href)}, ${JSON.stringify(referrer)})`, helperContext)));
const tagged = 'https://www.teraearlywine.com/?utm_source=linkedin&utm_medium=social&utm_campaign=website_baseline_2026_09&utm_content=profile';
assert.equal(attribution(tagged).campaign_source, 'linkedin');
assert.equal(attribution(tagged.replace('linkedin', 'newsletter').replace('social', 'email').replace('profile', 'footer')).campaign_source, 'newsletter');
for (const href of [tagged + '&utm_source=private%40example.com', tagged.replace('linkedin', 'private%40example.com'), tagged.replace('&utm_content=profile', ''), tagged.replace('linkedin', 'linkedin%7C'), 'not a url']) {
  assert.equal(attribution(href).campaign_source, undefined);
}
for (const referrer of ['https://www.google.com/search?q=private#secret', 'https://google.com/']) {
  assert.equal(attribution(tagged, referrer).page_referrer, 'https://www.google.com/');
}
for (const referrer of ['https://www.google.com.attacker.example/', 'http://www.google.com/', 'https://user:password@www.google.com/', 'https://www.google.com:8443/', 'https://teraearlywine.com/', 'invalid']) {
  assert.equal(attribution(tagged, referrer).page_referrer, '');
}
const attributed = createHarness(null, true, {href: tagged + '&utm_term=private%40example.com#secret', referrer: 'https://www.linkedin.com/private?secret=yes'});
assert.deepEqual(commands(attributed), []);
attributed.rejectButton.click();
assert.equal(attributed.loadedScripts.length, 0);
attributed.acceptButton.click();
const attributedConfig = commands(attributed).find(([name]) => name === 'config')[2];
assert.equal(attributedConfig.campaign_source, 'linkedin');
assert.equal(attributedConfig.campaign_term, '');
assert.equal(attributedConfig.campaign_id, '');
assert.equal(attributedConfig.page_location, 'https://www.teraearlywine.com/');
dispatchContactSubmitted(attributed);
const attributedEvent = commands(attributed).filter(([name]) => name === 'event').at(-1)[2];
assert.equal(attributedEvent.page_referrer, 'https://www.linkedin.com/');
assert.equal(attributedEvent.campaign_source, undefined);
assert.equal(JSON.stringify(commands(attributed)).includes('private'), false);
attributed.reopenButton.click();
const revokedCount = commands(attributed).length;
dispatchContactSubmitted(attributed);
assert.equal(commands(attributed).length, revokedCount);

assert.equal(vm.runInContext("canCollectAnalytics(null, 'www.teraearlywine.com')", helperContext), false);
assert.equal(vm.runInContext("canCollectAnalytics({measurementId: 'G-NF6SVCGZDF'}, 'www.teraearlywine.com')", helperContext), false);
const unknownCampaign = createHarness('accepted', true, {href: tagged.replace('linkedin', 'private%40example.com')});
const unknownConfig = commands(unknownCampaign).find(([name]) => name === 'config')[2];
for (const field of ['campaign_source', 'campaign_medium', 'campaign_name', 'campaign_content', 'campaign_id', 'campaign_term']) {
  assert.equal(unknownConfig[field], '');
}
assert.equal(JSON.stringify(commands(unknownCampaign)).includes('private'), false);
for (const [referrer, origin] of [
  ['https://www.bing.com/search?q=private', 'https://www.bing.com/'],
  ['https://bing.com/', 'https://www.bing.com/'],
  ['https://lnkd.in/private', 'https://www.linkedin.com/'],
  ['https://linkedin.com/private', 'https://www.linkedin.com/'],
]) {
  assert.equal(attribution(tagged, referrer).page_referrer, origin);
}

for (const href of ['https://www.teraearlywine.com/person@example.com', 'https://www.teraearlywine.com/customer/PRIVATE_ID?email=PRIVATE_EMAIL#PRIVATE_FRAGMENT']) {
  const unknownPage = createHarness('accepted', true, {href, pagePath: '/404'});
  const config = commands(unknownPage).find(([name]) => name === 'config')[2];
  assert.equal(config.page_location, 'https://www.teraearlywine.com/404');
  assert.equal(config.page_path, '/404');
  dispatchContactSubmitted(unknownPage);
  assert.equal(JSON.stringify(commands(unknownPage)).includes('PRIVATE_'), false);
  assert.equal(JSON.stringify(commands(unknownPage)).includes('person@example.com'), false);
}

// A false debug_mode parameter is not equivalent to omitting it in GA4.
const productionDebugCheck = createHarness('accepted', true, {measurementId: 'G-NF6SVCGZDF', debugMode: false});
const productionTagConfig = commands(productionDebugCheck).find(([name]) => name === 'config')[2];
assert.equal(Object.hasOwn(productionTagConfig, 'debug_mode'), false);
const testDebugCheck = createHarness('accepted', true, {measurementId: 'G-TEST123', debugMode: true, href: 'http://localhost/'});
assert.equal(commands(testDebugCheck).find(([name]) => name === 'config')[2].debug_mode, true);
const testNonDebugCheck = createHarness('accepted', true, {measurementId: 'G-TEST123', debugMode: false, href: 'http://localhost/'});
assert.equal(Object.hasOwn(commands(testNonDebugCheck).find(([name]) => name === 'config')[2], 'debug_mode'), false);
