// Island: data-dcb-app-link. iPhone -> App Store, Android -> Google Play, everything else keeps its href (/download).
(function () {
  var APP_STORE = "https://apps.apple.com/us/app/drifters-city-bike/id6755121198", GOOGLE_PLAY = "#google-play-url-pending"; // App Store confirmed 2026-10-29; Google Play pending from Ian
  var ua = navigator.userAgent || "";
  var t = /iPhone|iPad|iPod/i.test(ua) ? APP_STORE : /Android/i.test(ua) ? GOOGLE_PLAY : null;
  if (t) document.querySelectorAll("[data-dcb-app-link]").forEach(function (a) { a.href = t; });
})();
