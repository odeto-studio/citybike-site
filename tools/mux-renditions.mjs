// Add 480p + 720p static MP4 renditions to Mux assets (mux-video.js asks for these on non-Safari browsers) and record them in webflow/mux.json.
// Run: OP_SERVICE_ACCOUNT_TOKEN=... node tools/mux-renditions.mjs <slug> [<slug> ...]
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const slugs = process.argv.slice(2);
const op = (field) => execFileSync("op", ["read", `op://Automation/Drifters City Bike - Mux API/${field}`]).toString().trim();
const auth = "Basic " + Buffer.from(`${op("Token ID")}:${op("Secret Key")}`).toString("base64");
const api = async (method, p, body) => {
  const r = await fetch(`https://api.mux.com${p}`, { method, headers: { Authorization: auth, "Content-Type": "application/json" }, body: body && JSON.stringify(body) });
  const j = r.status === 204 ? {} : await r.json();
  if (!r.ok) throw new Error(`${method} ${p} ${r.status} ${JSON.stringify(j)}`);
  return j.data;
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const file = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "webflow", "mux.json");
const mux = JSON.parse(readFileSync(file, "utf8"));
for (const slug of slugs) {
  const rec = mux[slug];
  // Mux refuses sized renditions while "highest" exists (mux-upload.mjs requests "highest"): drop it first
  const have = (await api("GET", `/video/v1/assets/${rec.asset_id}`)).static_renditions?.files || [];
  for (const f of have.filter((f) => f.resolution === "highest")) await api("DELETE", `/video/v1/assets/${rec.asset_id}/static-renditions/${f.id}`);
  await sleep(3000);
  for (const resolution of ["480p", "720p"]) await api("POST", `/video/v1/assets/${rec.asset_id}/static-renditions`, { resolution });
  for (let i = 0; i < 100; i++) {
    const files = (await api("GET", `/video/v1/assets/${rec.asset_id}`)).static_renditions?.files || [];
    const ready = ["480p", "720p"].every((r) => files.some((f) => f.resolution === r && f.status === "ready"));
    if (ready) break;
    await sleep(5000);
  }
  rec.mp4 = `https://stream.mux.com/${rec.playback_id}/720p.mp4`;
  rec.mp4_small = `https://stream.mux.com/${rec.playback_id}/480p.mp4`;
  delete rec.mp4_highest;
  console.log(slug, "480p + 720p ready");
}
writeFileSync(file, JSON.stringify(mux, null, 2) + "\n");
