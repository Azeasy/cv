# cv

LaTeX CV for Azizzhan Supiyev — built automatically via GitHub Actions and published to GitHub Pages.

---

## Live links

| Asset | URL |
|---|---|
| English CV (latest) | https://azeasy.github.io/cv/cv.pdf |
| Russian CV (latest) | https://azeasy.github.io/cv/ru/cv.pdf |
| Index page | https://azeasy.github.io/cv/ |
| Latest release (EN) | https://github.com/Azeasy/cv/releases/latest/download/cv.pdf |
| Latest release (RU) | https://github.com/Azeasy/cv/releases/latest/download/cv_ru.pdf |

Adding a new language (e.g. Italian) automatically adds:
- `https://azeasy.github.io/cv/it/cv.pdf`
- `https://github.com/Azeasy/cv/releases/latest/download/cv_it.pdf`

---

## Repo structure

```
latex/
  main.tex              # EN source (canonical)
  main_ru.tex           # RU source (manually maintained)
  main_it.tex           # IT source (example — add any main_<lang>.tex)
  main.generated.ru.tex # RU preview from translate script (gitignored)
translations/
  ru.json               # RU translation memory (committed, manually editable)
  it.json               # IT translation memory (created on first --lang IT run)
scripts/
  bootstrap_tm.py       # Seed TM from an existing manually-translated .tex
  translate_segments.py # Generate preview + update TM via DeepL or OpenAI
  translate/            # Internal package (paths, extractor, backends, …)
.github/workflows/
  build-deploy.yml      # Build all languages + deploy to Pages on push to main
  release.yml           # Build all languages + publish GitHub Release on tag v*
  translate.yml         # Manual translation preview (workflow_dispatch + lang input)
```

PDFs are never committed. They are built by CI and either deployed to Pages or uploaded as release assets.

---

## Adding a new language

1. Create `latex/main_<lang>.tex` (translate manually or use the bootstrap workflow).
2. Commit and push to `main`.
3. The build workflow auto-detects the new file and adds `/<lang>/cv.pdf` to Pages.

**That's it.** No workflow changes needed.

---

## Build locally

### Prerequisites

```bash
# macOS — install BasicTeX then latexmk via tlmgr
brew install --cask basictex
# Add to ~/.zshrc: export PATH="/Library/TeX/texbin:$PATH"
sudo tlmgr update --self
sudo tlmgr install latexmk

# Ubuntu / Debian
sudo apt-get install texlive-latex-base texlive-latex-extra \
    texlive-fonts-recommended texlive-fonts-extra \
    texlive-lang-cyrillic texlive-lang-european latexmk
```

### Compile

```bash
# English CV → build/main.pdf
latexmk -pdf -interaction=nonstopmode -output-directory=build latex/main.tex

# Russian CV → build/main_ru.pdf
latexmk -pdf -interaction=nonstopmode -output-directory=build latex/main_ru.tex

# Any other language
latexmk -pdf -interaction=nonstopmode -output-directory=build latex/main_it.tex

# Clean auxiliary files
latexmk -C -output-directory=build latex/main.tex
```

---

## Publish the latest CV (Pages)

Push any commit to `main`:

```bash
git add latex/main.tex   # or any main_<lang>.tex
git commit -m "update cv"
git push origin main
```

The `build-deploy` workflow runs automatically and deploys to GitHub Pages within ~2 minutes.

> **One-time setup:** Go to **Settings → Pages → Source** and set it to **GitHub Actions**.

---

## Publish a versioned release

Create and push a version tag:

```bash
git tag v2026.03.04
git push origin v2026.03.04
```

The `release` workflow builds all detected language PDFs and creates (or updates) a GitHub Release marked as latest, uploading `cv.pdf`, `cv_ru.pdf`, `cv_it.pdf`, etc. as downloadable assets.

Tag format convention: `v<YYYY>.<MM>.<DD>` (e.g. `v2026.03.04`).

---

## Translation memory

### How it works

1. `scripts/translate_segments.py` reads `latex/main.tex` and extracts translatable segments:
   - `\section{...}` titles
   - `\resumeSubheading` argument lines (company, dates, role, location)
   - content inside `\resumeItem{...}`
   - the first summary paragraph
2. Each segment is **normalised** (lowercased, whitespace collapsed, punctuation stripped) and hashed via `sha1[:12]` to produce a stable ID.
3. The ID is looked up in `translations/<lang>.json` (the *translation memory*).
   - If found → the stored translation is reused, no API call.
   - If missing → DeepL (or OpenAI) is called, the result is stored in the TM.
4. A preview file `latex/main.generated.<lang>.tex` is written with all segments replaced.
5. `latex/main_<lang>.tex` is **never touched**.

Minor punctuation changes do not invalidate existing TM entries.

### TM file structure

```
translations/
  ru.json    ← Russian
  it.json    ← Italian (created on first --lang IT run)
  de.json    ← German  (created on first --lang DE run)
```

Each file:
```json
{
  "a13c92f4b21c": {
    "en": "Built REST APIs, ETL pipelines…",
    "ru": "Разрабатывал REST API, ETL‑конвейеры…",
    "source": "manual",
    "updated_at": "2026-03-04"
  }
}
```

### Run locally

```bash
# Load your API key
source <(grep -v '^#' .env | sed 's/^/export /')

# Russian (default)
python scripts/translate_segments.py

# Italian
python scripts/translate_segments.py --lang IT

# German via OpenAI
python scripts/translate_segments.py --lang DE --backend openai

# Re-translate everything (overwrite TM entries)
python scripts/translate_segments.py --lang RU --force
```

### Bootstrap TM from an existing translated file

If you already have a manually translated `main_<lang>.tex`, seed the TM from it first to avoid unnecessary API calls:

```bash
python scripts/bootstrap_tm.py           # Russian (default)
python scripts/bootstrap_tm.py --lang it # Italian
```

### Run via GitHub Actions

1. Add `DEEPL_API_KEY` as a repository secret (**Settings → Secrets and variables → Actions → New repository secret**).
2. Go to **Actions → Generate Translation Preview → Run workflow**.
3. Select the target language (e.g. `IT`).
4. Download the `translation-preview-IT` artifact (`latex/main.generated.it.tex` + `translations/it.json`).
5. Review the generated file. Copy improvements into `latex/main_it.tex` manually.

The workflow **never commits or pushes** anything automatically.

### Manually improving translations

Edit `translations/<lang>.json` directly — change the target-language string and optionally set `"source": "manual"`. The script will never overwrite an existing key unless you run with `--force`.

Commit the updated file so improvements persist.

---

## GitHub Actions setup checklist

- [ ] **Settings → Pages → Source** set to **GitHub Actions**
- [ ] `DEEPL_API_KEY` added as a repository secret (only needed for the translate workflow)
