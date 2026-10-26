# HaggLab design system (v2)

The previous design (v1) is archived in `../design-archive/v1-gemini/`.

## Direction
A small engineering company, not a portfolio. White canvas, near-black ink, one green accent.
Dark sections (process, Fiverr, final call to action, footer) give the page rhythm.
Product previews (HTML/CSS interface mocks with demo data) replace abstract illustrations.

## Tokens (`static/css/tokens.css`)
| Token | Value | Use |
|---|---|---|
| `--bg` | #FFFFFF | Page canvas |
| `--panel` | #F4F5F2 | Alternate sections, quiet fills |
| `--ink-bg` | #0C1517 | Dark sections and footer |
| `--ink` | #0E1A1C | Text (17.6:1) |
| `--muted` | #4E5A5C | Secondary text (7.2:1) |
| `--accent` | #0E7568 | Links, primary buttons (5.5:1) |
| `--accent-on-ink` | #6AD6C3 | Accent on dark sections |
| Status | Concept slate, Prototype amber, Live demo green, Delivered teal | Always with a text label |

Fonts (self-hosted, variable): **Instrument Sans** for everything, **JetBrains Mono** for labels, numbers and specs.
Radius 8px (cards 12px). Shadows only on product previews. Motion 150 to 220ms, state changes only.

## Components
| Component | File | Notes |
|---|---|---|
| Status badge | `components/badge.html` | Text comes from the status field only |
| Product preview | `components/preview.html` | One mock per project slug; footer says "Concept illustration" for concepts |
| Project card | `components/project_card.html` | Hub, solution pages, related projects |
| Results | `components/result_block.html` | Measured block hidden when empty; expected always labelled |
| FAQ | `components/faq_list.html` | Native `<details>`, no JavaScript |
| Brief checklist | `components/brief.html` | Copy button for Fiverr chat |
| Final CTA | `components/final_cta.html` | Fiverr visitors get "Message us on Fiverr" |
| Icons | `components/icon.html` | Inline SVG by name |

## Content from Site Settings (admin)
Blocks stay hidden until the value is set: `reply_time`, `support_window`, `code_ownership_terms`,
`revisions_per_tier`, `nda_policy`, `deletion_contact`, `fiverr_profile_url`,
`fiverr_<project>_gig`, `github_url`, `link_heros_ai`, `link_epicoutlet`, `link_zenos`, `link_zeno`.

## Style guide
`/styleguide/` shows the type, buttons, badges and all ten previews (noindex).

## Navigation (v2.1)
Services mega menu (5 services with icon and one line, plus a "Not sure which one?" panel), Projects, Company menu
(About, How we work, Security and data, FAQ), then Hire on Fiverr and Start a project. Menus open on hover with a
short delay, on click, and with the keyboard (Arrow Down, Escape). The header hides while scrolling down and returns on
the first scroll up. On mobile, Services and Company are accordions. Service names live in `apps/content/services.py`.

## Motion (v2.1)
All motion plays once and is switched off for `prefers-reduced-motion`.
- Reveal: sections fade up 16px when they enter the screen; siblings are staggered 70ms (max 6 steps).
- Product previews: lines appear in order, bars grow, forecast lines draw, the urgency pill pops. Once, never looping.
- Hover: cards lift 3 to 4px with a soft shadow; arrows nudge; service cards show an accent top bar.
- Menus, mobile panel and FAQ answers open and close in 200 to 260ms.
`static/js/early.js` adds the `js` class before first paint so nothing flashes. If `site.js` fails, everything is shown after 2.5 seconds.

## Brand: HaggLab (renamed from Tenet, 2026-10-22)
- Mark: an H whose right stem drops into an L foot (H + L for HaggLab). The H uses `--ink`; the L foot uses `--accent`.
  On dark surfaces the H uses `--on-ink` and the foot `--accent-on-ink`.
- Inline mark: `templates/components/mark.html` (32-unit grid). Files: `static/img/brand-hagglab/hagglab-mark.svg`,
  `hagglab-mark-light.svg`; favicon `static/img/v2/favicon.svg`; share image `static/img/v2/og-default.png`.
- The name comes from the `STUDIO_NAME` setting (default `HaggLab`).
