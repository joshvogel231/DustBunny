# The Dust Bunny

> Don't get left in the [digital] dust.

The personal brand website for **Josh Vogel** — a service-based small-business
web developer building affordable, custom-coded sites with SEO + AI SEO baked
in. Live at [the-dustbunny.com](https://the-dustbunny.com).

This repo *is* the site. It's also the proof of competence for prospects — so
performance, SEO, and polish matter more than usual.

---

## Stack

- **[Astro 5](https://astro.build)** — static-first, near-zero client JS
- **[Tailwind CSS v4](https://tailwindcss.com)** (CSS-first `@theme` in
  `src/styles/global.css`)
- **Vanilla SVG** for the mascot (procedurally generated spiky fur in
  `src/components/Mascot.astro`)
- Inline scripts for all interactivity (no JS framework, no client hydration)
- Deployed to **[Netlify](https://netlify.com)** with native form handling

## Local development

```bash
npm install
npm run dev
```

Dev server runs on `http://localhost:4321`.

> **Heads up:** Astro's dev HMR occasionally locks up after rapid edits and
> starts returning 500s. The fix is always the same — stop and start the dev
> server.

## Build

```bash
npm run build
```

Outputs a fully static site to `dist/`. No server runtime required.
Drop it on any static host (Netlify, Vercel, S3, etc.).

## Project structure

```
dust-bunny/
├── public/
│   ├── work/             # 4 client site screenshots (JPG, baked into build)
│   ├── josh/             # 4 founder photos (Tampa → Army → today)
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── Mascot.astro          # Procedural spiky fur SVG
│   │   ├── Nav.astro             # Header w/ desktop + mobile menus
│   │   └── GeauxTigers.astro     # Reusable Mardi Gras confetti easter egg
│   ├── layouts/
│   │   └── Layout.astro          # HTML shell + global inline scripts
│   ├── pages/
│   │   ├── index.astro           # Homepage
│   │   ├── about.astro           # Real story + 4-phase polaroid timeline
│   │   └── faq.astro             # 17 FAQs covering fit / pricing / scope
│   └── styles/
│       └── global.css            # Tailwind + design system + components
└── README.md
```

## Pages

| Path | What's there |
|---|---|
| `/` | Hero, stats, services, recent work (4 cards), process, "Meet our Head Dust Bunny" teaser, contact form |
| `/about` | The "Yeah… none of that was true." punchline + 4-phase polaroid timeline + real bio |
| `/faq` | 17 questions on fit, pricing, timeline, scope, ownership, maintenance |

## Design system

Defined entirely in `src/styles/global.css` via Tailwind v4's `@theme`:

- **Palette:** cream `#f4ead2`, comic red `#e23b2e`, mustard `#f2b93b`,
  teal `#2a9d9b`, ink `#1a1714`, dust `#c9b79c`
- **Fonts:** Anton (impact headlines), Bungee (display/logo), Space Grotesk (body)
- **Visual language:** vintage comic / Americana — Ben-Day halftone dots, bold
  ink outlines, hard drop-shadows, starbursts, comic-stamp stickers

Reusable component classes: `.ink`, `.ink-2`, `.panel`, `.sticker`,
`.burst`, `.halftone-{red|teal|mustard|ink}`, `.shadow-comic{,-sm,-lg}`.

## Interactive features

All animations respect `prefers-reduced-motion`.

- Mobile hamburger menu w/ animated drop sheet
- Scroll cameos — corner peek-a-boo bunny + behind-contact-panel reveal
- Work card flip on hover + 7s alternate-direction screenshot pan
- Stats count-up animation triggered at mid-viewport
- Hover dust-bunny bursts on every CTA (auto-injected by Layout script)
- Geaux Tigers Mardi Gras confetti on hover
- Process dropdown ("How it actually goes down")
- Typewriter effect on hero badge
- Dust-puff scatter on header nav links

## Forms

The contact form uses Netlify's built-in form handling
(`data-netlify="true"`). Submissions appear in Netlify dashboard →
**Forms** after first deploy. No third-party form service needed.

Fields: name, business name, email, current site (optional), message.

## Deployment

1. Push to GitHub
2. Netlify → **Add new site** → **Import an existing project** → pick repo
3. Build command: `npm run build` · Publish directory: `dist`
4. Node version: 20
5. Domain: point GoDaddy nameservers to Netlify's `dnsN.p0X.nsone.net`

After the first push, every commit to `main` triggers an auto-deploy.

## Screenshots

Client portfolio screenshots in `public/work/` were captured via local headless
Chrome at 1280×2400, then resized + JPEG-compressed via `sips`. To refresh:

```bash
# Example — replace URL/filename
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars --window-size=1280,2400 \
  --screenshot=raw.png "https://example.com"
sips -s format jpeg -s formatOptions 80 --resampleWidth 800 \
  raw.png --out public/work/example.jpg
rm raw.png
```

---

© Josh Vogel. The Dust Bunny.
