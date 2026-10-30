// Write the approved legal pages (projects/launch-site/working/legal/<slug>.html) into the Legal Pages CMS items and mark them ready to publish.
// No phone number anywhere on the site (Ian 2026-10-30): the contact blocks list email only.
// Run: OP_SERVICE_ACCOUNT_TOKEN=... node tools/legal-to-cms.mjs [--dry]
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { wf } from "./wf.mjs";

const COLLECTION = "676f05e19f0c2d276a11bccb"; // Legal Pages
const ITEMS = { "privacy-policy": "676f05e19f0c2d276a11bd31", "terms-of-service": "676f05e19f0c2d276a11bd32", "cookie-consent-policy": "676f05e19f0c2d276a11bd33" };
const DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../projects/launch-site/working/legal");
const DRY = process.argv.includes("--dry");

const items = Object.entries(ITEMS).map(([slug, id]) => {
  const html = readFileSync(path.join(DIR, `${slug}.html`), "utf8").trim();
  if (html.includes("{{")) throw new Error(`${slug}: unfilled placeholder`);
  return { id, isDraft: false, fieldData: { content: html } };
});

if (DRY) { for (const i of items) console.log(i.id, i.fieldData.content.length, "chars"); process.exit(0); }
const res = await wf("PATCH", `/collections/${COLLECTION}/items`, { items });
for (const i of res.items) console.log(i.id, i.fieldData.slug, "isDraft", i.isDraft, i.fieldData.content.length, "chars");
