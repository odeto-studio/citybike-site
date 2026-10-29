// Island: data-dcb-app-link. iPhone -> App Store, Android -> Google Play, everything else keeps its href (/download).
(function () {
  var APP_STORE = "#app-store-url-pending", GOOGLE_PLAY = "#google-play-url-pending"; // Ian sends these
  var ua = navigator.userAgent || "";
  var t = /iPhone|iPad|iPod/i.test(ua) ? APP_STORE : /Android/i.test(ua) ? GOOGLE_PLAY : null;
  if (t) document.querySelectorAll("[data-dcb-app-link]").forEach(function (a) { a.href = t; });
})();
