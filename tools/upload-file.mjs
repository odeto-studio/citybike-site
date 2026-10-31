// Upload one local file to Webflow Assets under "Launch 2026/<folder>" and print its id + hosted URL.
// Run: OP_SERVICE_ACCOUNT_TOKEN=... node tools/upload-file.mjs <path> <folder> [fileName]
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import { wf, SITE } from "./wf.mjs";

const [src, folderName, as] = process.argv.slice(2);
const bytes = readFileSync(src);
const name = as || path.basename(src);

const all = (await wf("GET", `/sites/${SITE}/asset_folders?limit=100`)).assetFolders;
const parent = all.find((f) => !f.parentFolder && f.displayName === "Launch 2026")?.id;
const folder = all.find((f) => f.parentFolder === parent && f.displayName === folderName)?.id;
if (!folder) throw new Error(`no folder Launch 2026/${folderName}`);

const meta = await wf("POST", `/sites/${SITE}/assets`, {
  fileName: name, fileHash: createHash("md5").update(bytes).digest("hex"), parentFolder: folder,
});
const form = new FormData();
for (const [k, v] of Object.entries(meta.uploadDetails)) form.append(k, v);
form.append("file", new Blob([bytes], { type: meta.contentType || meta.uploadDetails["content-type"] }), name);
const s3 = await fetch(meta.uploadUrl, { method: "POST", body: form });
if (s3.status !== 201) throw new Error(`${name}: S3 ${s3.status} ${await s3.text()}`);
console.log(JSON.stringify({ id: meta.id, hostedUrl: meta.hostedUrl }));
