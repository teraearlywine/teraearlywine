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

function createHarness(fetchImplementation) {
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
    selector === '[data-contact-submit]' ? submitButton : status
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
  const document = {
    addEventListener(type, callback) {
      documentListeners.set(type, callback);
    },
    dispatchEvent() {},
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
  assert.equal(harness.timers.size, 0);
}

Promise.resolve()
  .then(testSuccessfulSubmissionRestoresTheForm)
  .then(testTimedOutSubmissionRestoresTheForm)
  .catch(error => {
    console.error(error);
    process.exitCode = 1;
  });
