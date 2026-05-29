const fs = require("fs");
const path = require("path");

// Deep audit: find routes that return static/fake data
function walk(dir, exclude, exts) {
    const results = [];
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
        if (exclude.includes(e.name)) continue;
        const full = path.join(dir, e.name);
        if (e.isDirectory()) results.push(...walk(full, exclude, exts));
        else if (exts.some(ext => e.name.endsWith(ext))) results.push(full);
    }
    return results;
}

const exclude = ['.git','node_modules','__pycache__','dist','.venv','data','logs','backups','memory','state','archive'];
const allPy = walk('backend', exclude, ['.py']);

// Find routes that might be fake (return static dict without any real logic)
console.log("=== 疑似假路由(只返回静态数据，无DB/API调用) ===");
let fakeCount = 0;
for (const f of allPy) {
    const content = fs.readFileSync(f, 'utf8');
    const lines = content.split('\n');
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('@router.') && (lines[i].includes('get') || lines[i].includes('post'))) {
            // Find the function body
            let body = '';
            let j = i + 1;
            let indent = '';
            while (j < lines.length && !lines[j].includes('@router.') && !lines[j].startsWith('def ') && !lines[j].startsWith('class ')) {
                if (lines[j].includes('return {')) {
                    body += lines[j].trim() + ' ';
                }
                j++;
            }
            // Check if return is static (no function calls, no DB, no await)
            if (body.includes('return {') && !body.includes('await') && !body.includes('state.') && !body.includes('db.') && !body.includes('call_ai') && !body.includes('execute(') && !body.includes('.get(') && !body.includes('memory_store') && !body.includes('registry')) {
                // Check if it has any real logic
                const funcBody = content.substring(content.indexOf('\n', i), content.indexOf('\n\n', i+5) || content.length);
                const hasRealLogic = funcBody.includes('import ') || funcBody.includes('.execute') || funcBody.includes('.query') || funcBody.includes('.search') || funcBody.includes('.get_knowledge');
                if (!hasRealLogic && body.length < 200) {
                    const m = lines[i].match(/@router\.\w+\(["']([^"']+)["']/);
                    console.log(`  ${f.replace(/\\/g,'/')}: ${m?m[1]:'?'} → ${body.substring(0,100)}`);
                    fakeCount++;
                }
            }
        }
    }
}
console.log(`\n疑似假路由: ${fakeCount} 个`);