const fs = require("fs");
const path = require("path");
const base = "D:\\下载\\源码\\mall-project\\backend\\routers";
const files = fs.readdirSync(base).filter(f => f.endsWith(".py") && f !== "__init__.py").sort();
const results = [];
for (const file of files) {
  const content = fs.readFileSync(path.join(base, file), "utf8");
  const re = /@router\.(get|post|put|delete|patch)\s*\(\s*["']([^"']+)["']/g;
  let m; const routes = [];
  while ((m = re.exec(content)) !== null) routes.push(m[1].toUpperCase() + " " + m[2]);
  if (routes.length) results.push({ file, count: routes.length, routes });
}
let total = 0;
for (const r of results) total += r.count;
console.log("Files: " + files.length + ", With routes: " + results.length + ", Total routes: " + total);
for (const r of results) {
  console.log("\n--- " + r.file + " (" + r.count + ") ---");
  r.routes.forEach(rt => console.log("  " + rt));
}
