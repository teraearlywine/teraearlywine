'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const mainSource = fs.readFileSync(
  path.join(__dirname, '..', 'core', 'home', 'assets', 'js', 'main.js'),
  'utf8',
);

class FakeClassList {
  add() {}
  remove() {}
  toggle() {}
}

class FakeElement {
  constructor(textContent = '') {
    this.classList = new FakeClassList();
    this.disabled = false;
    this.listeners = new Map();
    this.textContent = textContent;
  }

  addEventListener(type, callback) {
    this.listeners.set(type, callback);
  }
}

function createHarness(fetchImplementation, challengeConfigured = false) {
  const challenge = challengeConfigured ? { hidden: true, dataset: { sitekey: "test-key" } } : null;
  const widgetCalls = { render: 0, reset: 0 };
  const submitButton = new FakeElement('Send message');
  const status = new FakeElement();
  const submissionId = { value: 'initial-submission-id' };
  const contactForm = new FakeElement();
  contactForm.action = '/contact';
  contactForm.resetCount = 0;
  contactForm.elements = {
    namedItem(name) {
      return name === 'submission_id' ? submissionId : null;
    },
  };
  contactForm.querySelector = (selector) => (
    selector === '[data-contact-submit]' ? submitButton : (selector === '[data-contact-status]' ? status : (selector === '[data-contact-challenge]' ? challenge : null))
  );
  contactForm.querySelectorAll = () => [];
  contactForm.reportValidity = () => true;
  contactForm.reset = () => {
    contactForm.resetCount += 1;
  };

  const navbar = new FakeElement();
  navbar.offsetHeight = 0;
  const navLinks = new FakeElement();
  const navToggle = new FakeElement();
  const documentListeners = new Map();
  const dispatchedEvents = [];
  const document = {
    addEventListener(type, callback) {
      documentListeners.set(type, callback);
    },
    dispatchEvent(event) {
      dispatchedEvents.push(event.type);
    },
    getElementById(id) {
      if (id === 'navbar') return navbar;
      if (id === 'navLinks') return navLinks;
      if (id === 'navToggle') return navToggle;
      return null;
    },
    querySelector(selector) {
      return selector === '[data-contact-form]' ? contactForm : null;
    },
    querySelectorAll() {
      return [];
    },
  };

  class FakeIntersectionObserver {
    observe() {}
    unobserve() {}
  }

  let nextTimerId = 0;
  const timers = new Map();
  const window = {
    turnstile: {
      render(element, options) {
        assert.equal(element, challenge);
        assert.equal(options.action, "contact");
        widgetCalls.render++;
        return "widget-id";
      },
      reset() { widgetCalls.reset++; },
    },
    addEventListener() {},
    clearTimeout(timerId) {
      timers.delete(timerId);
    },
    scrollTo() {},
    scrollY: 0,
    setTimeout(callback, delay) {
      nextTimerId += 1;
      timers.set(nextTimerId, { callback, delay });
      return nextTimerId;
    },
  };
  const context = {
    AbortController,
    Event,
    FormData: class FakeFormData {},
    IntersectionObserver: FakeIntersectionObserver,
    document,
    fetch: fetchImplementation,
    window,
  };
  vm.createContext(context);
  vm.runInContext(mainSource, context, { filename: 'main.js' });
  documentListeners.get('DOMContentLoaded')();

  return {
    async submit() {
      return contactForm.listeners.get('submit')({
        preventDefault() {},
      });
    },
    contactForm,
    challenge,
    widgetCalls,
    dispatchedEvents,
    runTimer(delay) {
      const timer = [...timers.values()].find(item => item.delay === delay);
      assert.ok(timer, `missing ${delay}ms timer`);
      timer.callback();
    },
    status,
    submissionId,
    submitButton,
    timers,
  };
}

async function testSuccessfulSubmissionRestoresTheForm() {
  let resolveFetch;
  const fetchPromise = new Promise(resolve => {
    resolveFetch = resolve;
  });
  const harness = createHarness(() => fetchPromise);
  const submission = harness.submit();

  assert.equal(harness.status.textContent, 'Sending your message…');
  assert.equal(harness.submitButton.disabled, true);
  assert.equal(harness.submitButton.textContent, 'Sending…');

  harness.runTimer(8000);
  assert.equal(
    harness.status.textContent,
    'Still sending — this may take a few more seconds…',
  );

  resolveFetch({
    ok: true,
    async json() {
      return {
        ok: true,
        submission_id: 'next-submission-id',
      };
    },
  });
  await submission;

  assert.equal(harness.status.textContent, 'Thanks — your message has been sent.');
  assert.equal(harness.submitButton.disabled, false);
  assert.equal(harness.submitButton.textContent, 'Send message');
  assert.equal(harness.submissionId.value, 'next-submission-id');
  assert.equal(harness.contactForm.resetCount, 1);
  assert.equal(harness.timers.size, 0);
  assert.deepEqual(harness.dispatchedEvents, ['contact:submitted']);
}

async function testTimedOutSubmissionRestoresTheForm() {
  const harness = createHarness((url, options) => new Promise((resolve, reject) => {
    options.signal.addEventListener('abort', () => {
      reject(new DOMException('Aborted', 'AbortError'));
    });
  }));
  const submission = harness.submit();

  harness.runTimer(20000);
  await submission;

  assert.equal(
    harness.status.textContent,
    'Delivery is taking longer than expected. Please wait a moment before trying again.',
  );
  assert.equal(harness.submitButton.disabled, false);
  assert.equal(harness.submitButton.textContent, 'Send message');
  assert.equal(harness.contactForm.resetCount, 0);
  assert.deepEqual(harness.dispatchedEvents, []);
  assert.equal(harness.timers.size, 0);
}

async function testInvalidFormDoesNotRequestOrEmitSuccess() {
  let calls = 0;
  const harness = createHarness(() => { calls += 1; });
  harness.contactForm.reportValidity = () => false;
  await harness.submit();
  assert.equal(calls, 0);
  assert.deepEqual(harness.dispatchedEvents, []);
}

async function testRejectedResponsesNeverEmitSuccess() {
  const responses = [
    { ok: false, status: 400, payload: { ok: false, errors: {} } },
    { ok: false, status: 502, payload: { ok: false } },
    { ok: false, status: 503, payload: { ok: false } },
    { ok: false, status: 403, payload: { ok: false } },
    { ok: false, status: 429, payload: { ok: false } },
    { ok: true, status: 200, payload: { ok: false } },
    { ok: true, status: 200, payload: { ok: true } },
    { ok: true, status: 200, invalidJson: true },
  ];
  for (const response of responses) {
    const harness = createHarness(async () => ({
      ...response,
      async json() {
        if (response.invalidJson) throw new SyntaxError('Invalid JSON');
        return response.payload;
      },
    }));
    await harness.submit();
    assert.deepEqual(harness.dispatchedEvents, []);
    assert.equal(harness.contactForm.resetCount, 0);
    assert.equal(harness.submissionId.value, 'initial-submission-id');
    assert.equal(harness.submitButton.disabled, false);
  }
}

async function testConcurrentSubmitDeliversAndEmitsOnce() {
  let resolveFetch;
  let calls = 0;
  const harness = createHarness(() => {
    calls += 1;
    return new Promise(resolve => { resolveFetch = resolve; });
  });
  const first = harness.submit();
  await harness.submit();
  assert.equal(calls, 1);
  assert.deepEqual(harness.dispatchedEvents, []);
  resolveFetch({
    ok: true,
    async json() { return { ok: true, submission_id: 'next-submission-id' }; },
  });
  await first;
  assert.deepEqual(harness.dispatchedEvents, ['contact:submitted']);
}

async function testChallengeRendersAndAllowsExplicitRetry() {
  let attempts = 0;
  const harness = createHarness(async () => {
    attempts++;
    return attempts === 1
      ? { ok: false, status: 403, async json() { return { ok: false, challenge_required: true }; } }
      : { ok: true, status: 200, async json() { return { ok: true, submission_id: 'new-id' }; } };
  }, true);
  await harness.submit();
  assert.equal(harness.challenge.hidden, false);
  assert.equal(harness.widgetCalls.render, 1);
  assert.equal(harness.contactForm.resetCount, 0);
  assert.deepEqual(harness.dispatchedEvents, []);
  assert.equal(harness.submitButton.disabled, false);
  await harness.submit();
  assert.equal(harness.widgetCalls.reset, 1);
  assert.deepEqual(harness.dispatchedEvents, ['contact:submitted']);
}

async function testMissingChallengeConfigurationFailsClearly() {
  const harness = createHarness(async () => ({ ok: false, status: 403, async json() { return { ok: false, challenge_required: true }; } }));
  await harness.submit();
  assert.match(harness.status.textContent, /Verification is temporarily unavailable/);
  assert.deepEqual(harness.dispatchedEvents, []);
}

Promise.resolve()
  .then(testSuccessfulSubmissionRestoresTheForm)
  .then(testTimedOutSubmissionRestoresTheForm)
  .then(testInvalidFormDoesNotRequestOrEmitSuccess)
  .then(testRejectedResponsesNeverEmitSuccess)
  .then(testConcurrentSubmitDeliversAndEmitsOnce)
  .then(testChallengeRendersAndAllowsExplicitRetry)
  .then(testMissingChallengeConfigurationFailsClearly)
  .catch(error => {
    console.error(error);
    process.exitCode = 1;
  });
