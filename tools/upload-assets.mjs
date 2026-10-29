// Upload the build's media from webflow/assets.csv to Webflow Assets, into "Launch 2026/<webflow_folder>".
// Skips rows that already have a webflow_asset_id, blog-mockup-only files, the hero film (Mux), the Windsor font (already on the site),
// and sponsor/Collectives logos (bound from their CMS collections). Uses the WebP twin in projects/launch-site/webp/ when one exists.
// Writes asset ids back to webflow/assets.csv. Run: OP_SERVICE_ACCOUNT_TOKEN=... node tools/upload-assets.mjs [--dry]
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { wf, SITE } from "./wf.mjs";

const HERE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SITE_DIR = path.resolve(HERE, "../../projects/launch-site");
const CSV = path.join(HERE, "webflow/assets.csv");
const DRY = process.argv.includes("--dry");
const SKIP = [/\.mp4$/, /\.ttf$/, /collectives\//, /sponsor-/, /blog-frames-/, /live-blog-before/, /ian-press/, /priority-spec-board/, /related\//];

const lines = readFileSync(CSV, "utf8").trim().split("\n");
const head = lines[0].split(",");
const rows = lines.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [head[i], v])));

let parent;
const folders = {};
async function folder(name) {
  if (!parent) {
    const all = (await wf("GET", `/sites/${SITE}/asset_folders?limit=100`)).assetFolders;
    for (const f of all) folders[`${f.parentFolder || ""}/${f.displayName}`] = f.id;
    parent = folders["/Launch 2026"] || (await wf("POST", `/sites/${SITE}/asset_folders`, { displayName: "Launch 2026" })).id;
  }
  const key = `${parent}/${name}`;
  if (!folders[key]) folders[key] = (await wf("POST", `/sites/${SITE}/asset_folders`, { displayName: name, parentFolder: parent })).id;
  return folders[key];
}

for (const r of rows) {
  if (r.webflow_asset_id || SKIP.some((re) => re.test(r.file))) continue;
  const webp = path.join(SITE_DIR, "webp", path.basename(r.file).replace(/\.png$/, ".webp"));
  const src = existsSync(webp) ? webp : path.join(SITE_DIR, r.file);
  const bytes = readFileSync(src);
  const name = path.basename(src);
  if (DRY) { console.log(`would upload ${name} (${Math.round(bytes.length / 1024)} KB) -> Launch 2026/${r.webflow_folder}`); continue; }
  const meta = await wf("POST", `/sites/${SITE}/assets`, {
    fileName: name, fileHash: createHash("md5").update(bytes).digest("hex"), parentFolder: await folder(r.webflow_folder),
  });
  const form = new FormData();
  for (const [k, v] of Object.entries(meta.uploadDetails)) form.append(k, v);
  form.append("file", new Blob([bytes], { type: meta.contentType || meta.uploadDetails["content-type"] }), name);
  const s3 = await fetch(meta.uploadUrl, { method: "POST", body: form });
  if (s3.status !== 201) throw new Error(`${name}: S3 ${s3.status} ${await s3.text()}`);
  r.webflow_asset_id = meta.id;
  console.log(`${name} -> ${meta.id} ${meta.hostedUrl}`);
  writeFileSync(CSV, [head.join(","), ...rows.map((x) => head.map((h) => x[h] ?? "").join(","))].join("\n") + "\n");
}
