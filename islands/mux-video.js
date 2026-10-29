// Island: data-dcb-mux="<playback id>" on a muted <video> (Webflow custom element). Safari plays Mux HLS natively;
// other browsers get a static MP4: 480p on phones, tablets and Save-Data, 720p on large screens. No hls.js.
// Reduced motion: no autoplay, the poster stays. JS off: no src, the poster stays. Playback ids: webflow/mux.json.
(function () {
  var vids = document.querySelectorAll("video[data-dcb-mux]");
  if (!vids.length) return;
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var conn = navigator.connection || {};
  var small = window.innerWidth < 992 || conn.saveData;
  vids.forEach(function (v) {
    var id = v.getAttribute("data-dcb-mux");
    if (!id) return;
    if (!v.getAttribute("poster")) v.poster = "https://image.mux.com/" + id + "/thumbnail.webp?time=0&width=720";
    if (still) return;
    v.muted = true;
    v.playsInline = true;
    v.src = v.canPlayType("application/vnd.apple.mpegurl")
      ? "https://stream.mux.com/" + id + ".m3u8"
      : "https://stream.mux.com/" + id + "/" + (small ? "480p" : "720p") + ".mp4";
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  });
})();
