// main.js — Portfolio navigation and scroll behavior

document.addEventListener('DOMContentLoaded', () => {

  // --- Navbar scroll effect ---
  const navbar = document.getElementById('navbar');
  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // --- Smooth scroll for nav links ---
  document.querySelectorAll('.nav-links a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        const offset = navbar.offsetHeight;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      }
      // Close mobile menu if open
      document.getElementById('navLinks').classList.remove('open');
      document.getElementById('navToggle').classList.remove('open');
      document.getElementById('navToggle').setAttribute('aria-expanded', 'false');
    });
  });

  // --- Active nav link highlighting ---
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a');

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach(link => {
          link.classList.toggle('active', link.getAttribute('aria-current') === 'page' || link.getAttribute('href') === '#' + id);
        });
      }
    });
  }, { rootMargin: '-40% 0px -60% 0px' });

  sections.forEach(section => sectionObserver.observe(section));

  // --- Mobile menu toggle ---
  const navToggle = document.getElementById('navToggle');
  const navLinksEl = document.getElementById('navLinks');

  navToggle.addEventListener('click', () => {
    navToggle.classList.toggle('open');
    navLinksEl.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(navLinksEl.classList.contains('open')));
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navLinksEl.classList.contains('open')) {
      navLinksEl.classList.remove('open');
      navToggle.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.focus();
    }
  });

  // --- Fade-up scroll animations ---
  const fadeElements = document.querySelectorAll('.fade-up');
  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        fadeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  fadeElements.forEach(el => fadeObserver.observe(el));

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
