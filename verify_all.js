const fs = require('fs');
const { execSync } = require('child_process');

// Verify all .vue files in src/
const files = execSync('git ls-files frontend/src/ | grep "\\.vue$"', {encoding:'utf8'}).trim().split('\n');
let bad = 0;
for (const f of files) {
    const buf = fs.readFileSync(f);
    const start = buf.slice(0, 10).toString();
    // Check: starts with <template> or BOM+<template> (both valid)
    if (!start.startsWith('<template>') && !buf.slice(0,13).toString().startsWith('\uFEFF<template>')) {
        console.log('BAD: ' + f + ' => ' + buf.slice(0,16).toString('hex'));
        bad++;
    }
}
console.log(bad === 0 ? 'ALL CLEAN' : bad + ' BROKEN');
