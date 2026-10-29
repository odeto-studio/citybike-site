// Push rider FAQs into the General FAQs collection from projects/launch-site/pages/faq/cms-items.json.
// Adds Category (Option), Featured (Switch) and Sort Order (Number) if missing, creates missing items (by name),
// and sets Category=Business on the existing sponsor items. Staged only: nothing goes live until a site publish.
// Run: OP_SERVICE_ACCOUNT_TOKEN=... node tools/faq-cms.mjs
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { wf } from "./wf.mjs";

const COL = "676f05e19f0c2d276a11bc29";
const HERE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const spec = JSON.parse(readFileSync(path.resolve(HERE, "../../projects/launch-site/pages/faq/cms-items.json"), "utf8"));
const slugify = (s) => s.toLowerCase().replace(/[’']/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);

let col = await wf("GET", `/collections/${COL}`);
const has = (slug) => col.fields.find((f) => f.slug === slug);
if (!has("category")) await wf("POST", `/collections/${COL}/fields`, { type: "Option", displayName: "Category", isRequired: false, helpText: "Rider FAQ group on /faq (Business = sponsor questions)", metadata: { options: spec.categories.map((name) => ({ name })) } });
if (!has("featured")) await wf("POST", `/collections/${COL}/fields`, { type: "Switch", displayName: "Featured", isRequired: false, helpText: "Shows in the home page FAQ" });
if (!has("sort-order")) await wf("POST", `/collections/${COL}/fields`, { type: "Number", displayName: "Sort Order", isRequired: false, helpText: "Lower shows first", metadata: { format: "integer" } });
col = await wf("GET", `/collections/${COL}`);
const opt = Object.fromEntries(has("category").validations.options.map((o) => [o.name, o.id]));

const items = [];
for (let offset = 0; ; offset += 100) {
  const page = await wf("GET", `/collections/${COL}/items?limit=100&offset=${offset}`);
  items.push(...page.items);
  if (page.items.length < 100) break;
}
const byName = Object.fromEntries(items.map((i) => [i.fieldData.name, i]));

for (const it of spec.items) {
  if (byName[it.q]) { console.log(`exists: ${it.q}`); continue; }
  const r = await wf("POST", `/collections/${COL}/items`, {
    isDraft: !!it.draft, isArchived: false,
    fieldData: { name: it.q, slug: slugify(it.q), answer: it.a, category: opt[it.category], featured: !!it.featured, "sort-order": it.order },
  });
  console.log(`created ${r.id}${it.draft ? " (draft, Ian: " + it.ian + ")" : ""}: ${it.q}`);
}
for (const name of spec.business_items) {
  const i = byName[name];
  if (!i) { console.log(`missing business item: ${name}`); continue; }
  if (i.fieldData.category === opt.Business) continue;
  await wf("PATCH", `/collections/${COL}/items/${i.id}`, { fieldData: { category: opt.Business } });
  console.log(`business: ${name}`);
}
