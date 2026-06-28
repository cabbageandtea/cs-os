(() => {
  "use strict";

  const revealEls = document.querySelectorAll("[data-reveal]");
  if (!revealEls.length) return;

  const show = (el) => el.classList.add("is-visible");

  const inView = (el) => {
    const rect = el.getBoundingClientRect();
    return rect.top < window.innerHeight * 0.92 && rect.bottom > 0;
  };

  revealEls.forEach((el) => {
    if (inView(el)) show(el);
  });

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    revealEls.forEach(show);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          show(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { rootMargin: "0px 0px -5% 0px", threshold: 0.05 }
  );

  revealEls.forEach((el) => {
    if (!el.classList.contains("is-visible")) observer.observe(el);
  });
})();
