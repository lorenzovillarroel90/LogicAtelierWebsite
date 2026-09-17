
(() => {
  document.querySelectorAll('.nav-menu-panel a').forEach((link) => link.addEventListener('click', () => link.closest('details')?.removeAttribute('open')));
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const targets = document.querySelectorAll('.section-heading, .game-card, .value-grid article, .shot-card, .feature-panel, .pro-panel, .policy-section');
  if (!reduce && 'IntersectionObserver' in window) {
    targets.forEach((element) => element.classList.add('reveal'));
    const observer = new IntersectionObserver((entries, instance) => {
      entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); instance.unobserve(entry.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    targets.forEach((element) => observer.observe(element));
  }
})();
