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

function createHarness(initialConsent = null, storageAvailable = true) {
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
      measurementId: 'G-TEST123',
      debugMode: true,
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
    referrer: 'https://referrer.example/account?email=private%40example.com#secret',
    head: {
      appendChild(element) {
        loadedScripts.push(element);
      },
    },
    getElementById(id) {
      if (id === 'analyticsConfig') return configElement;
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
    location: {
      href: 'https://www.teraearlywine.com/work?email=person%40example.com#private',
      hostname: 'www.teraearlywine.com',
      origin: 'https://www.teraearlywine.com',
      pathname: '/work',
    },
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
assert.equal(configCommand[2].page_location, 'https://www.teraearlywine.com/work');
assert.equal(configCommand[2].page_path, '/work');
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
