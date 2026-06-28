(function () {
  var legacyNav = document.querySelector(".example-nav");
  if (legacyNav) {
    window.addEventListener(
      "scroll",
      function () {
        legacyNav.classList.toggle("is-scrolled", window.scrollY > 12);
      },
      { passive: true }
    );
  }

  var proNav = document.querySelector(".ex-pro-nav");
  var proLinks = document.querySelector("[data-nav-links]");
  var proToggle = document.querySelector("[data-nav-toggle]");

  if (proToggle && proLinks) {
    proToggle.addEventListener("click", function () {
      var open = proLinks.classList.toggle("is-open");
      proToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  if (proNav) {
    window.addEventListener(
      "scroll",
      function () {
        proNav.classList.toggle("is-scrolled", window.scrollY > 24);
      },
      { passive: true }
    );
  }

  if (proLinks) {
    var sections = Array.from(proLinks.querySelectorAll('a[href^="#"]')).map(function (link) {
      var id = link.getAttribute("href").slice(1);
      var section = document.getElementById(id);
      return section ? { link: link, section: section } : null;
    }).filter(Boolean);

    if (sections.length && "IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              sections.forEach(function (item) {
                item.link.classList.toggle("is-active", item.section === entry.target);
              });
            }
          });
        },
        { rootMargin: "-40% 0px -55% 0px", threshold: 0.01 }
      );
      sections.forEach(function (item) {
        observer.observe(item.section);
      });
    }
  }
})();
