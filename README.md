# CHI 2027 Digital Experience Competition — website

Source for **chidigitalexperience.org**, built per
[spec/CHI_Competition_Website_Spec.md](spec/CHI_Competition_Website_Spec.md).

## Stack

- [Astro](https://astro.build/) — static output, Markdown content collections
- npm (`npm install`, `npm run dev`, `npm run build`)
- Deployed to GitHub Pages via `.github/workflows/deploy.yml` on push to `main`

## Structure

```
public/data/          the programme data feeds — passed through untouched (see spec §4a/§B2)
  chi2025/, chi2026/, sandbox/, chi2027/   one dir per edition
  schema/v1.json       JSON Schema (draft — see the note on the Programme Data page)
  LICENCE               CC BY-NC-SA 4.0 text + attribution line for the data
src/content/faq/       one Markdown file per FAQ entry — see faq-README.md
src/config/forms.ts     Microsoft Forms embed URLs (set once the chairs create the forms)
src/pages/              one route per page in the site map (spec §3)
src/components/         header, footer, bridge accent motif, MS Forms embed component
scripts/publish.py       publishes a new programme JSON into public/data/<edition>/
```

## Editing content

- **FAQ**: add/edit a `.md` file in `src/content/faq/` — no code change needed, just a rebuild/deploy.
- **Dates, judging criteria, page copy**: currently inline in the relevant `src/pages/*.astro` file (small enough for v1 not to warrant a separate data file — see the spec's suggested-approach note).
- **Submission forms**: built and hosted in Microsoft Forms, not on this site. Set the embed URLs in `src/config/forms.ts` once created. Confirm each form is set to "Anyone with the link can respond".
- **Accepted Teams page**: gated behind `IS_LIVE` in `src/pages/accepted-teams/index.astro` until notification (end of January 2027).

## Publishing a programme data update

```sh
scripts/publish.py <edition> <path-to-new-json> -m "what changed"
```

Writes a new revision, updates `latest.json`, and bumps `version.json` under `public/data/<edition>/`. Review with `git diff` before committing.

## Known gaps (see spec §8)

- `public/data/schema/v1.json` is a draft of the top-level shape only, not a complete/validated schema.
- FAQ has two placeholder entries; real content still to be written.
- Data protection requirements, consent/privacy/one-page-summary templates, and compute/LLM credit details are all placeholders pending the chairs.
- Microsoft Forms URLs are unset.
