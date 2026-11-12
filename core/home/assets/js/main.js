// main.js — Portfolio navigation and scroll behavior

document.addEventListener('DOMContentLoaded', () => {

  const navToggle = document.getElementById('navToggle');
  const navLinksEl = document.getElementById('navLinks');
  document.getElementById('navbar').classList.add('nav-ready');

  function setMenuOpen(open) {
    navLinksEl.classList.toggle('open', open);
    navToggle.setAttribute('aria-expanded', String(open));
  }

  // Keep fragment URLs, back navigation, and native keyboard navigation intact.
  document.querySelectorAll('.nav-links a[href^="#"]').forEach(link => {
    link.addEventListener('click', () => setMenuOpen(false));
  });

  navToggle.addEventListener('click', () => {
    setMenuOpen(!navLinksEl.classList.contains('open'));
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navLinksEl.classList.contains('open')) {
      setMenuOpen(false);
      navToggle.focus();
    }
  });

  // --- Scroll to top button ---
  const scrollBtn = document.querySelector('.scroll-button');
  if (scrollBtn) {
    window.addEventListener('scroll', () => {
      scrollBtn.classList.toggle('visible', window.scrollY > 300);
    }, { passive: true });

    scrollBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // --- Contact form ---
  const contactForm = document.querySelector('[data-contact-form]');
  if (contactForm) {
    const submitButton = contactForm.querySelector('[data-contact-submit]');
    const status = contactForm.querySelector('[data-contact-status]');
    const defaultButtonText = submitButton.textContent;
    const progressDelayMilliseconds = 8000;
    const requestTimeoutMilliseconds = 20000;

    const setStatus = (message, isError = false) => {
      status.textContent = message;
      status.classList.toggle('contact-form__status--error', isError);
    };

    const clearFieldErrors = () => {
      contactForm.querySelectorAll('[data-contact-error]').forEach(error => {
        error.hidden = true;
        error.textContent = '';
      });
      contactForm.querySelectorAll('[aria-invalid]').forEach(field => {
        field.setAttribute('aria-invalid', 'false');
      });
    };

    const showFieldErrors = errors => {
      let firstInvalidField = null;
      Object.entries(errors || {}).forEach(([fieldName, messages]) => {
        const control = contactForm.elements.namedItem(fieldName);
        const field = control?.length && !control.tagName ? control[0] : control;
        const error = contactForm.querySelector(
          `[data-contact-error="${fieldName}"]`,
        );
        if (!field || !error || !Array.isArray(messages) || !messages[0]) {
          return;
        }
        field.setAttribute('aria-invalid', 'true');
        error.textContent = messages[0];
        error.hidden = false;
        firstInvalidField ||= field;
      });
      firstInvalidField?.focus();
    };

    const challenge = contactForm.querySelector('[data-contact-challenge]');
    let challengeWidget;
    const showChallenge = () => {
      if (!challenge) {
        setStatus('Verification is temporarily unavailable. Please try again later.', true);
        return;
      }
      challenge.hidden = false;
      const render = () => {
        if (challengeWidget !== undefined) window.turnstile.reset(challengeWidget);
        else challengeWidget = window.turnstile.render(challenge, {
          sitekey: challenge.dataset.sitekey, action: 'contact',
        });
      };
      if (window.turnstile) render();
      else if (!document.querySelector('[data-turnstile-script]')) {
        const script = document.createElement('script');
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
        script.dataset.turnstileScript = '';
        script.onload = render;
        script.onerror = () => {
          script.remove();
          setStatus('Verification could not load. Please try again.', true);
        };
        document.head.appendChild(script);
      }
    };
    if (challenge && !challenge.hidden) showChallenge();

    contactForm.addEventListener('submit', async event => {
      event.preventDefault();
      if (!contactForm.reportValidity() || submitButton.disabled) {
        return;
      }

      clearFieldErrors();
      setStatus('Sending your message…');
      submitButton.disabled = true;
      submitButton.textContent = 'Sending…';

      let progressTimer;
      let timeoutTimer;
      try {
        const controller = new AbortController();
        progressTimer = window.setTimeout(() => {
          setStatus('Still sending — this may take a few more seconds…');
        }, progressDelayMilliseconds);
        timeoutTimer = window.setTimeout(() => {
          controller.abort();
        }, requestTimeoutMilliseconds);

        const response = await fetch(contactForm.action, {
          method: 'POST',
          headers: { Accept: 'application/json' },
          body: new FormData(contactForm),
          credentials: 'same-origin',
          signal: controller.signal,
        });
        const payload = await response.json().catch(() => ({}));

        if (payload.challenge_required === true) {
          setStatus('Please complete the verification and submit again.', true);
          showChallenge();
          return;
        }
        if ([403, 429].includes(response.status) || (response.ok && payload.ok === false)) {
          setStatus('Your submission could not be accepted. Please try again later.', true);
          return;
        }
        if (
          !response.ok
          || payload.ok !== true
          || typeof payload.submission_id !== 'string'
        ) {
          showFieldErrors(payload.errors);
          setStatus(
            response.status === 400
              ? 'Please check the highlighted fields and try again.'
              : 'The message could not be sent right now. Please try again.',
            true,
          );
          return;
        }

        contactForm.reset();
        if (challengeWidget !== undefined) window.turnstile.reset(challengeWidget);
        contactForm.elements.namedItem('submission_id').value = (
          payload.submission_id
        );
        setStatus('Thanks — your message has been sent.');
        document.dispatchEvent(new Event('contact:submitted'));
      } catch (error) {
        setStatus(
          error?.name === 'AbortError'
            ? 'Delivery is taking longer than expected. Please wait a moment before trying again.'
            : 'The message could not be sent right now. Please try again.',
          true,
        );
      } finally {
        window.clearTimeout(progressTimer);
        window.clearTimeout(timeoutTimer);
        submitButton.disabled = false;
        submitButton.textContent = defaultButtonText;
      }
    });
  }

});
