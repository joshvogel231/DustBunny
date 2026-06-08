/**
 * export-mascot.mjs
 * Generates mascot.png and mascot.jpg in public/mascot/
 * Run: node scripts/export-mascot.mjs
 */

import sharp from "sharp";
import { writeFileSync, mkdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(__dirname, "../public/mascot");
mkdirSync(OUT_DIR, { recursive: true });

// ── Deterministic RNG (matches Mascot.astro exactly) ────────────────────────
function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const TAU = Math.PI * 2;

function furBlob(cx, cy, rxO, ryO, rxI, ryI, spikes, rand) {
  let d = "";
  const ticks = [];
  for (let i = 0; i < spikes; i++) {
    const t = i / spikes;
    const aO = TAU * t + (rand() - 0.5) * 0.08;
    const aI = TAU * (t + 0.5 / spikes) + (rand() - 0.5) * 0.08;
    const fo = 0.82 + rand() * 0.34;
    const fi = 0.9 + rand() * 0.12;
    const ox = cx + Math.cos(aO) * rxO * fo;
    const oy = cy + Math.sin(aO) * ryO * fo;
    const ix = cx + Math.cos(aI) * rxI * fi;
    const iy = cy + Math.sin(aI) * ryI * fi;
    d += i === 0 ? `M${ox.toFixed(1)} ${oy.toFixed(1)}` : `L${ox.toFixed(1)} ${oy.toFixed(1)}`;
    d += `L${ix.toFixed(1)} ${iy.toFixed(1)}`;
    if (i % 3 === 0) {
      const sx = cx + Math.cos(aO) * rxO * (fo - 0.34);
      const sy = cy + Math.sin(aO) * ryO * (fo - 0.34);
      ticks.push(`M${sx.toFixed(1)} ${sy.toFixed(1)}L${ox.toFixed(1)} ${oy.toFixed(1)}`);
    }
  }
  return { d: d + "Z", ticks };
}

const rand = mulberry32(7);
const body = furBlob(130, 152, 102, 92, 82, 74, 32, rand);

const motesDef = [
  { cx: 34,  cy: 100, s: 1    },
  { cx: 234, cy: 66,  s: 0.8  },
  { cx: 228, cy: 216, s: 1.1  },
  { cx: 58,  cy: -6,  s: 0.7  },
  { cx: 46,  cy: 232, s: 0.85 },
];
const motes = motesDef.map((m) => ({
  ...m,
  d: furBlob(m.cx, m.cy, 16 * m.s, 14 * m.s, 11 * m.s, 10 * m.s, 11, rand).d,
}));

// ── Build static SVG (no animations, no CSS classes) ─────────────────────────
const tickPaths = body.ticks
  .map((t) => `<path d="${t}" stroke="#1a1714" stroke-width="2" fill="none" opacity="0.18" stroke-linecap="round"/>`)
  .join("\n  ");

const motePaths = motes
  .map(
    (m) =>
      `<path d="${m.d}" fill="#c9b79c" stroke="#1a1714" stroke-width="3" stroke-linejoin="round" opacity="0.55"/>`
  )
  .join("\n  ");

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -44 260 320" width="520" height="640">
  <defs>
    <pattern id="fuzz" width="8" height="8" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.1" fill="rgba(0,0,0,0.10)"/>
    </pattern>
  </defs>

  <!-- ground shadow -->
  <ellipse cx="130" cy="250" rx="80" ry="13" fill="#1a1714" opacity="0.16"/>

  <!-- ears (behind body) -->
  <path d="M118 96 C 106 56, 96 2, 100 -26 C 103 -42, 120 -40, 124 -10 C 127 30, 128 70, 128 96 Z"
        fill="#c9b79c" stroke="#1a1714" stroke-width="6" stroke-linejoin="round"/>
  <path d="M118 96 C 106 56, 96 2, 100 -26 C 103 -42, 120 -40, 124 -10 C 127 30, 128 70, 128 96 Z"
        fill="url(#fuzz)" stroke="none"/>
  <path d="M119 88 C 110 54, 102 4, 106 -19 C 109 -33, 120 -31, 122 -8 C 124 28, 124 64, 124 88 Z"
        fill="#e0a89f" stroke="none"/>

  <path d="M140 96 C 134 58, 128 4, 136 -22 C 141 -40, 159 -42, 168 -25 C 177 -9, 171 13, 152 13 C 160 44, 158 72, 152 96 Z"
        fill="#c9b79c" stroke="#1a1714" stroke-width="6" stroke-linejoin="round"/>
  <path d="M140 96 C 134 58, 128 4, 136 -22 C 141 -40, 159 -42, 168 -25 C 177 -9, 171 13, 152 13 C 160 44, 158 72, 152 96 Z"
        fill="url(#fuzz)" stroke="none"/>
  <path d="M141 88 C 136 56, 131 6, 138 -16 C 143 -32, 158 -33, 165 -20 C 172 -8, 167 10, 151 11 C 158 40, 155 68, 151 88 Z"
        fill="#e0a89f" stroke="none"/>

  <!-- feet -->
  <ellipse cx="104" cy="244" rx="17" ry="11" fill="#c9b79c" stroke="#1a1714" stroke-width="6"/>
  <ellipse cx="156" cy="244" rx="17" ry="11" fill="#c9b79c" stroke="#1a1714" stroke-width="6"/>

  <!-- body -->
  <path d="${body.d}" fill="#c9b79c" stroke="#1a1714" stroke-width="6" stroke-linejoin="round"/>
  <path d="${body.d}" fill="url(#fuzz)" stroke="none"/>

  <!-- belly highlight -->
  <ellipse cx="128" cy="170" rx="56" ry="46" fill="#e0d3b6" opacity="0.55"/>

  <!-- inner fur ticks -->
  ${tickPaths}

  <!-- eyes -->
  <circle cx="106" cy="150" r="19" fill="#1a1714"/>
  <circle cx="113" cy="143" r="6"  fill="#f4ead2"/>
  <circle cx="101" cy="156" r="2.6" fill="#f4ead2" opacity="0.85"/>

  <circle cx="154" cy="150" r="19" fill="#1a1714"/>
  <circle cx="161" cy="143" r="6"  fill="#f4ead2"/>
  <circle cx="149" cy="156" r="2.6" fill="#f4ead2" opacity="0.85"/>

  <!-- rosy cheeks -->
  <ellipse cx="80"  cy="174" rx="13" ry="9" fill="#e0584c" opacity="0.3"/>
  <ellipse cx="180" cy="174" rx="13" ry="9" fill="#e0584c" opacity="0.3"/>

  <!-- nose + smile -->
  <path d="M124 170 q6 6 12 0 q-6 6 -12 0 Z" fill="#e0584c" stroke="#1a1714" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M114 180 q16 14 32 0" stroke="#1a1714" stroke-width="4" fill="none" stroke-linecap="round"/>

  <!-- floating dust puffs -->
  ${motePaths}
</svg>`;

// Save intermediate SVG for reference
const svgPath = join(OUT_DIR, "mascot.svg");
writeFileSync(svgPath, svg, "utf8");
console.log("✔  mascot.svg written");

// ── Convert to PNG (transparent background, trimmed tight) ──────────────────
const pngPath = join(OUT_DIR, "mascot.png");
await sharp(Buffer.from(svg))
  .resize(1040)
  .trim({ background: "transparent", threshold: 10 })
  .png({ compressionLevel: 9 })
  .toFile(pngPath);
console.log("✔  mascot.png written →", pngPath);

// ── Convert to JPEG (cream background, trimmed tight, 1:1 square) ────────────
const jpgPath = join(OUT_DIR, "mascot.jpg");

// First render + trim on transparent canvas, then composite onto square cream bg
const trimmedPng = await sharp(Buffer.from(svg))
  .resize(1040)
  .trim({ background: "transparent", threshold: 10 })
  .png()
  .toBuffer();

const { width: tw, height: th } = await sharp(trimmedPng).metadata();
const side = Math.max(tw, th);
const pad = 40; // breathing room around the mascot

await sharp({
  create: {
    width:  side + pad * 2,
    height: side + pad * 2,
    channels: 3,
    background: "#f4ead2",
  },
})
  .composite([{
    input: trimmedPng,
    left:  Math.round((side + pad * 2 - tw) / 2),
    top:   Math.round((side + pad * 2 - th) / 2),
  }])
  .jpeg({ quality: 92 })
  .toFile(jpgPath);
console.log("✔  mascot.jpg written →", jpgPath);

// ── 9:16 portrait (1080×1920) — for Runway / Reels / TikTok ─────────────────
const jpg916Path = join(OUT_DIR, "mascot-9x16.jpg");
const W = 1080, H = 1920;

// Scale the trimmed mascot so it fills ~75% of the width, then center it
const mascotW = Math.round(W * 0.75);
const resized = await sharp(trimmedPng)
  .resize(mascotW, undefined, { fit: "inside" })
  .png()
  .toBuffer();

const { width: rw, height: rh } = await sharp(resized).metadata();
const left = Math.round((W - rw) / 2);
const top  = Math.round((H - rh) / 2);

await sharp({
  create: { width: W, height: H, channels: 3, background: "#f4ead2" },
})
  .composite([{ input: resized, left, top }])
  .jpeg({ quality: 92 })
  .toFile(jpg916Path);
console.log("✔  mascot-9x16.jpg written →", jpg916Path);

console.log("\nAll done! Files are in public/mascot/");
