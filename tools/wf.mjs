// Tiny Webflow Data API v2 client for drifterscitybike.com. Token: 1Password Automation "Drifters - Webflow City Bike API".
// Usage as a module: import { wf, SITE } from "./wf.mjs"; await wf("GET", `/sites/${SITE}/asset_folders`).
// CLI: node tools/wf.mjs GET /sites/676f05e19f0c2d276a11bbcd/asset_folders
import { execFileSync } from "node:child_process";

export const SITE = "676f05e19f0c2d276a11bbcd";
const token = execFileSync("op", ["read", "op://Automation/Drifters - Webflow City Bike API/credential"]).toString().trim();

export async function wf(method, path, body) {
  const r = await fetch(`https://api.webflow.com/v2${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", accept: "application/json" },
    body: body && JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`${method} ${path} ${r.status} ${text}`);
  return text ? JSON.parse(text) : null;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [m, p, b] = process.argv.slice(2);
  console.log(JSON.stringify(await wf(m, p, b && JSON.parse(b)), null, 2));
}
