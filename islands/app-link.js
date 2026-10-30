// Island: data-dcb-app-link. iPhone -> App Store, Android -> Google Play, everything else keeps its href (/download).
(function () {
  var APP_STORE = "https://apps.apple.com/us/app/drifters-city-bike/id6755121198", GOOGLE_PLAY = "#google-play-url-pending"; // App Store confirmed 2026-10-29; Google Play pending from Ian
  var ua = navigator.userAgent || "";
  var pending = GOOGLE_PLAY.charAt(0) === "#"; // Android keeps /download until Ian has the Play listing
  var t = /iPhone|iPad|iPod/i.test(ua) ? APP_STORE : /Android/i.test(ua) && !pending ? GOOGLE_PLAY : null;
  if (t) document.querySelectorAll("[data-dcb-app-link]").forEach(function (a) { a.href = t; });
  if (!pending) return;
  // Google Play badges: "Coming soon" overlay on hover and keyboard focus (CSS, .badge.is-soon); a tap shows it for a moment instead of jumping to #
  document.querySelectorAll('a[href="' + GOOGLE_PLAY + '"]').forEach(function (a) {
    a.classList.add("is-soon");
    a.setAttribute("aria-label", "Google Play: coming soon");
    a.setAttribute("aria-disabled", "true");
    a.addEventListener("click", function (e) {
      e.preventDefault();
      a.classList.add("is-open");
      clearTimeout(a.dcbSoon);
      a.dcbSoon = setTimeout(function () { a.classList.remove("is-open"); }, 2400);
    });
  });
})();
