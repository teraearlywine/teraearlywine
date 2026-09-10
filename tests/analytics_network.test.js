'use strict';

// Opt-in check of the live Google library, with ALL collection blocked locally.
// GA4_NETWORK_TEST=1 node --test tests/analytics_network.test.js
// Requires Playwright and its Chromium browser, or GA4_BROWSER_CHANNEL=chrome.
// The production stream must keep automatic Site search OFF: it reads raw q
// independently of page_location. This test intentionally detects config drift.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '../core/home/assets/js/analytics.js'), 'utf8');
const html = `<!doctype html><title>Analytics boundary test</title>
<script id="analyticsConfig" type="application/json">{"measurementId":"G-NF6SVCGZDF","debugMode":false,"pagePath":"/"}</script>
<div id="analyticsConsent"><button data-consent-choice="accepted">Accept</button>
<button data-consent-choice="rejected">Reject</button></div><button data-consent-reopen>Privacy</button>
<form action="/contact" method="post" data-contact-form>
<input name="email" type="email"><textarea name="message"></textarea><button type="submit">Send</button></form>`;

test('live Google tag honors consent and bounded attribution in serialized requests', {
  skip: process.env.GA4_NETWORK_TEST !== '1',
  timeout: 90000,
}, async () => {
  const { chromium } = require('playwright');
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.GA4_BROWSER_CHANNEL ? {channel: process.env.GA4_BROWSER_CHANNEL} : {}),
  });
  try {
    for (const variant of ['unknown', 'linkedin', 'newsletter', 'unknown_path']) {
      const isUnknown = variant.startsWith('unknown');
      const pagePath = variant === 'unknown_path' ? '/404' : '/';
      const context = await browser.newContext({serviceWorkers: 'block'});
      try {
        const requests = [];
        let scripts = 0;
        await context.route('**/*', async (route) => {
          const request = route.request();
          const url = new URL(request.url());
          if (url.hostname === 'www.teraearlywine.com') {
            return route.fulfill({contentType: 'text/html', body: html.replace('"pagePath":"/"', `"pagePath":"${pagePath}"`)});
          }
          // Only the library itself may reach Google. Never send a collect hit.
          if (url.hostname === 'www.googletagmanager.com' && url.pathname === '/gtag/js') {
            scripts += 1;
            return route.continue();
          }
          requests.push({url: request.url(), body: request.postData() || ''});
          return route.abort();
        });
        const page = await context.newPage();
        const campaign = variant === 'linkedin'
          ? 'utm_source=linkedin&utm_medium=social&utm_campaign=website_baseline_2026_09&utm_content=profile'
          : variant === 'newsletter'
            ? 'utm_source=newsletter&utm_medium=email&utm_campaign=website_baseline_2026_09&utm_content=footer'
            : 'utm_source=PRIVATE_SOURCE&utm_medium=PRIVATE_MEDIUM&utm_campaign=PRIVATE_NAME&utm_content=PRIVATE_CONTENT';
        await page.goto(`https://www.teraearlywine.com/${variant === 'unknown_path' ? 'customer/PRIVATE_ID' : ''}?${campaign}&utm_id=PRIVATE_ID&utm_term=PRIVATE_TERM&gclid=PRIVATE_GCLID&utm_source_platform=PRIVATE_PLATFORM&utm_creative_format=PRIVATE_CREATIVE&utm_marketing_tactic=PRIVATE_TACTIC&q=PRIVATE_SEARCH&search=PRIVATE_QUERY#PRIVATE_HASH`, {
          referer: isUnknown ? 'https://unknown.example/PRIVATE_REF' : 'https://www.google.com/search?q=PRIVATE_REF',
        });
        await page.addScriptTag({content: source});
        await page.waitForTimeout(300);
        assert.equal(scripts, 0);
        assert.equal(requests.length, 0);
        await page.click('[data-consent-choice="rejected"]');
        await page.waitForTimeout(300);
        assert.equal(scripts, 0);
        assert.equal(requests.length, 0);
        await page.click('[data-consent-reopen]');
        await page.click('[data-consent-choice="accepted"]');
        const pageView = await waitForEvent(requests, 'page_view');
        assert.equal(scripts, 1);
        assert.equal(pageView.get('dl'), 'https://www.teraearlywine.com' + pagePath);
        assert.equal(pageView.get('dr') || '', isUnknown ? '' : 'https://www.google.com/');
        assert.equal(pageView.get('cs'), isUnknown ? '' : variant);
        assert.equal(pageView.get('cm'), isUnknown ? '' : variant === 'linkedin' ? 'social' : 'email');
        assert.equal(pageView.get('cn'), isUnknown ? '' : 'website_baseline_2026_09');
        assert.equal(pageView.get('cc'), isUnknown ? '' : variant === 'linkedin' ? 'profile' : 'footer');
        assert.equal(pageView.get('ci'), '');
        assert.equal(pageView.get('ck'), '');
        await page.evaluate(() => document.querySelector('form').addEventListener('submit', (event) => event.preventDefault()));
        await page.fill('input[name="email"]', 'PRIVATE_EMAIL@example.com');
        await page.fill('textarea', 'PRIVATE_MESSAGE');
        await page.click('button[type="submit"]');
        await page.evaluate(() => document.dispatchEvent(new Event('contact:submitted')));
        const submitted = await waitForEvent(requests, 'contact_submit');
        assert.equal(submitted.get('dr') || '', pageView.get('dr') || '');
        assert.equal(JSON.stringify(requests).includes('PRIVATE_'), false, JSON.stringify(requests));
        assert.equal(JSON.stringify(requests).includes('unknown.example'), false);
        // Let queued automatic hits flush before measuring revocation.
        await page.waitForTimeout(1000);
        await page.click('[data-consent-reopen]');
        const beforeRevokedEvent = requests.length;
        await page.evaluate(() => document.dispatchEvent(new Event('contact:submitted')));
        await page.waitForTimeout(1500);
        assert.equal(requests.length, beforeRevokedEvent);
        assert.equal(JSON.stringify(requests).includes('PRIVATE_'), false);
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
});

async function waitForEvent(requests, eventName) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    for (const request of requests) {
      const url = new URL(request.url);
      for (const line of request.body.split('\n')) {
        const fields = new URLSearchParams(`${url.search.slice(1)}&${line}`);
        if (fields.get('en') === eventName) return fields;
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`No intercepted ${eventName} request from the live Google library`);
}
