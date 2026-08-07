#!/usr/bin/env node
// Scout's logic checks for v0.4.0 — extracts the real slideLine() from src/2048.html
// and runs merge/animation-position assertions against it.
"use strict";
const fs = require("fs");
const path = require("path");

const html = fs.readFileSync(path.join(__dirname, "..", "..", "src", "2048.html"), "utf8");

// Extract slideLine function (pure, no DOM deps)
const m = html.match(/function slideLine\(line\) \{[\s\S]*?\n  \}/);
if (!m) { console.error("FAIL: slideLine not found"); process.exit(1); }
const slideLineSrc = m[0].replace("function slideLine", "function slideLine");
const SIZE = 4;
const slideLine = new Function("SIZE", slideLineSrc + "; return slideLine;")(SIZE);

let pass = 0, fail = 0;
function assert(name, cond) {
  if (cond) { pass++; console.log("  PASS " + name); }
  else { fail++; console.log("  FAIL " + name); }
}

console.log("v0.4.0 logic checks — slideLine (SIZE=4)");

// 1. Simple merge: [2,2,0,0] -> [4,0,0,0], gained 4, merged at index 0
let r = slideLine([2,2,0,0]);
assert("merge [2,2,0,0] -> [4,0,0,0]", r.line.join(",") === "4,0,0,0");
assert("merge gains 4", r.gained === 4);
assert("merge moved", r.moved === true);
assert("merge position marked [0]", r.mergedIdx.join(",") === "0");

// 2. No merge, just slide: [0,2,0,4] -> [2,4,0,0]
r = slideLine([0,2,0,4]);
assert("slide [0,2,0,4] -> [2,4,0,0]", r.line.join(",") === "2,4,0,0");
assert("slide gains 0", r.gained === 0);
assert("slide moved", r.moved === true);
assert("slide marks no merges", r.mergedIdx.length === 0);

// 3. No-op: [2,4,8,16] stays, moved=false
r = slideLine([2,4,8,16]);
assert("no-op [2,4,8,16] unchanged", r.line.join(",") === "2,4,8,16");
assert("no-op moved=false", r.moved === false);
assert("no-op no merges", r.mergedIdx.length === 0);

// 4. Double merge: [2,2,2,2] -> [4,4,0,0], two merges
r = slideLine([2,2,2,2]);
assert("double merge [2,2,2,2] -> [4,4,0,0]", r.line.join(",") === "4,4,0,0");
assert("double merge gains 8", r.gained === 8);
assert("double merge marks [0,1]", r.mergedIdx.join(",") === "0,1");

// 5. Chain rule (no triple merge): [2,2,4,0] -> [4,4,0,0]
r = slideLine([2,2,4,0]);
assert("chain [2,2,4,0] -> [4,4,0,0]", r.line.join(",") === "4,4,0,0");
assert("chain marks only [0]", r.mergedIdx.join(",") === "0");

// 6. Merge at end: [0,0,4,4] -> [8,0,0,0]
r = slideLine([0,0,4,4]);
assert("end merge [0,0,4,4] -> [8,0,0,0]", r.line.join(",") === "8,0,0,0");
assert("end merge marks [0]", r.mergedIdx.join(",") === "0");

// 7. Non-adjacent equal values do NOT merge: [2,0,2,0] -> [4,0,0,0] (they slide together and merge)
r = slideLine([2,0,2,0]);
assert("gap merge [2,0,2,0] -> [4,0,0,0]", r.line.join(",") === "4,0,0,0");
assert("gap merge marks [0]", r.mergedIdx.join(",") === "0");

// 8. [4,2,2,0] -> [4,4,0,0], merge at index 1
r = slideLine([4,2,2,0]);
assert("tail merge [4,2,2,0] -> [4,4,0,0]", r.line.join(",") === "4,4,0,0");
assert("tail merge marks [1]", r.mergedIdx.join(",") === "1");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
