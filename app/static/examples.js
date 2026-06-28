(function () {
  var nav = document.querySelector(".example-nav");
  if (nav) {
    window.addEventListener(
      "scroll",
      function () {
        nav.classList.toggle("is-scrolled", window.scrollY > 12);
      },
      { passive: true }
    );
  }
})();
