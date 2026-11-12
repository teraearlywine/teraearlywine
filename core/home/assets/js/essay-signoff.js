const video = document.querySelector('[data-essay-signoff] video');
const motion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (video && !motion.matches && 'IntersectionObserver' in window) {
  const signature = video.parentElement;
  const observer = new IntersectionObserver(entries => {
    if (!entries.some(entry => entry.isIntersecting)) return;
    observer.disconnect();
    if (motion.matches) return;
    video.poster = signature.querySelector('img').src;
    video.hidden = false;
    video.src = video.dataset.src;
    video.play().catch(showStill);
  }, { threshold: 0.25 });

  function showStill() {
    observer.disconnect();
    video.hidden = true;
    video.pause();
    motion.removeEventListener('change', onPreferenceChange);
  }

  function onPreferenceChange() {
    if (motion.matches) showStill();
  }

  video.addEventListener('ended', showStill, { once: true });
  video.addEventListener('error', showStill, { once: true });
  motion.addEventListener('change', onPreferenceChange);
  observer.observe(signature);
}
