// Select all the elements you want to animate
const faders = document.querySelectorAll('.fade-in');

/* 
  Intersection Observer Options:
  - root: null (uses browser viewport)
  - threshold: 0.1 means the callback fires when 10% of the element is in view
*/
const options = {
  threshold: 0.1
};

const fadeInOnScroll = new IntersectionObserver(function (entries, fadeInOnScroll) {
  entries.forEach(entry => {
    // If the element is not in view, do nothing
    if (!entry.isIntersecting) return;

    // Add the 'show' class to trigger CSS transition
    entry.target.classList.add('show');
    // Once animated in, no need to observe further
    fadeInOnScroll.unobserve(entry.target);
  });
}, options);

// Attach observer to each .fade-in element
faders.forEach(fader => {
  fadeInOnScroll.observe(fader);
});