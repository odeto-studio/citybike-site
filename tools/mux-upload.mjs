// Upload a local video to the Drifters City Bike Mux environment and wait until it is playable.
// Public playback, a static MP4 rendition (for non-Safari browsers, no hls.js), results appended to webflow/mux.json.
// Run: OP_SERVICE_ACCOUNT_TOKEN=... node tools/mux-upload.mjs <file> <slug>
// Creds: 1Password Automation "Drifters City Bike - Mux API" (Token ID, Secret Key), env "Drifters City Bike".
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const [file, slug] = process.argv.slice(2);
if (!file || !slug) throw new Error("usage: node tools/mux-upload.mjs <file> <slug>");

const op = (field) => execFileSync("op", ["read", `op://Automation/Drifters City Bike - Mux API/${field}`]).toString().trim();
const auth = "Basic " + Buffer.from(`${op("Token ID")}:${op("Secret Key")}`).toString("base64");
const api = async (method, p, body) => {
  const r = await fetch(`https://api.mux.com${p}`, { method, headers: { Authorization: auth, "Content-Type": "application/json" }, body: body && JSON.stringify(body) });
  const j = await r.json();
  if (!r.ok) throw new Error(`${method} ${p} ${r.status} ${JSON.stringify(j)}`);
  return j.data;
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const up = await api("POST", "/video/v1/uploads", {
  cors_origin: "*",
  new_asset_settings: {
    playback_policies: ["public"],
    video_quality: "plus",
    static_renditions: [{ resolution: "highest" }],
    passthrough: slug,
    meta: { title: slug, external_id: slug },
  },
});
const put = await fetch(up.url, { method: "PUT", body: readFileSync(file), headers: { "Content-Type": "video/mp4" } });
if (!put.ok) throw new Error(`upload PUT ${put.status}`);
console.log(`uploaded ${path.basename(file)} (${Math.round(statSync(file).size / 1024)} KB), upload ${up.id}`);

let assetId;
for (let i = 0; i < 60 && !assetId; i++) { await sleep(3000); assetId = (await api("GET", `/video/v1/uploads/${up.id}`)).asset_id; }
let asset;
for (let i = 0; i < 100; i++) {
  asset = await api("GET", `/video/v1/assets/${assetId}`);
  const mp4 = (asset.static_renditions?.files || []).find((f) => f.status === "ready");
  if (asset.status === "errored") throw new Error(JSON.stringify(asset.errors));
  if (asset.status === "ready" && mp4) break;
  await sleep(5000);
}
const pid = asset.playback_ids.find((p) => p.policy === "public").id;
const mp4 = asset.static_renditions.files.find((f) => f.status === "ready");
const out = {
  slug, asset_id: asset.id, playback_id: pid, duration: asset.duration, aspect_ratio: asset.aspect_ratio,
  hls: `https://stream.mux.com/${pid}.m3u8`,
  mp4: `https://stream.mux.com/${pid}/${mp4.name}`,
  poster: `https://image.mux.com/${pid}/thumbnail.webp?time=0&width=1080`,
  uploaded: new Date().toISOString(),
};
const here = path.dirname(fileURLToPath(import.meta.url));
const log = path.join(here, "..", "webflow", "mux.json");
const all = existsSync(log) ? JSON.parse(readFileSync(log, "utf8")) : {};
all[slug] = out;
writeFileSync(log, JSON.stringify(all, null, 2) + "\n");
console.log(JSON.stringify(out, null, 2));
