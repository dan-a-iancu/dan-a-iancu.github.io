# dan-a-iancu.github.io

Source for [dan-a-iancu.github.io](https://dan-a-iancu.github.io/), the personal
academic website of Dan A. Iancu, Professor of Operations, Information, and
Technology at the Stanford Graduate School of Business.

## Stack

A static site built with [Hugo](https://gohugo.io/) and the
[HugoBlox](https://hugoblox.com/) `blox-tailwind` theme, deployed to GitHub Pages
by `.github/workflows/deploy.yml` on every push to `main`.

Hugo is pinned to **0.152.1 extended**. The pin matters: newer releases cannot
build this theme.

## Running it locally

Requires Hugo 0.152.1 extended, Go (Hugo resolves the theme as a Go module) and
Node with pnpm (the theme compiles Tailwind at build time).

```bash
pnpm install
./scripts/dev-server.sh
```

Then open <http://localhost:1313/>.

## Layout

| Path | Contents |
|---|---|
| `content/` | Pages, and one bundle per publication |
| `assets/css/custom.css` | Site-specific styling and layout overrides |
| `layouts/` | Template overrides: custom blocks, views and shortcodes |
| `data/paper-topics.yaml` | Research-topic assignments, one line per paper |
| `scripts/` | Content generators and a static validator |
| `config/_default/` | Hugo configuration |

## Publications are generated

`content/publications/*/index.md` is written by `scripts/gen_publications.py`.
Editing those files directly works until the next regeneration, which then
silently overwrites the change. To edit a paper — title, venue, summary, authors,
awards, links — change its entry in that script and rerun:

```bash
python3 scripts/gen_publications.py && sh scripts/promote_publications.sh
```

The generator writes to `build/pub-staging/` first and never touches `content/` on
its own, so the output can be inspected before promotion.

## Before committing

```bash
python3 scripts/validate.py
```

Checks for broken local links, future dates (which silently hide a page from
production builds), invalid publication types, deprecated front-matter fields and
oversized assets.

## Note on teaching evaluations

`/teaching/evaluations/` publishes quantitative summaries of course evaluations.
The underlying institutional reports are deliberately not in this repository:
they contain verbatim student comments, including feedback designated for the
instructor only.

## License

The site content is © Dan A. Iancu. The underlying theme and starter template are
licensed separately — see `LICENSE.md`.
