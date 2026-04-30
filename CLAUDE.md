# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Flask web application that tracks personal learning/reading progress throughout the year. It fetches data from Trello via API and renders cumulative progress charts (books, papers, audiobooks, courses, textbooks, tutorials) comparing actual completion against yearly targets.

## Commands

**Install dependencies:**
```bash
pipenv install
```

**Run development server:**
```bash
python app.py
```
Runs Flask debug server on `localhost:5000`.

**Run production server:**
```bash
source keys.sh && gunicorn -w 2 --bind 0.0.0.0:8000 app:app
```
`keys.sh` must export `TRELLO_API_KEY` and `TRELLO_TOKEN` environment variables.

## Architecture

**`app.py`** — The entire backend. Each year has its own route (`/2021`, `/2024`, `/2025`, `/2026`, `/`) with hardcoded Trello list IDs and yearly targets per category. Three core functions:
- `get_cards(list_id)` — fetches cards from a Trello list via REST API
- `create_data(list_id)` — extracts `dateLastActivity`, buckets by day-of-year, returns cumulative sum
- `get_d(d)` — builds Chart.js dataset objects pairing actual progress with a linear target line

**`templates/index.html`** — Jinja2 template that loops over the datasets passed from the route and renders a Chart.js canvas per category.

**`static/scripts.js`** — Chart.js initialization; calculates day-of-year offsets for the x-axis.

**`gunicorn_config.py`** — Gunicorn settings (2 workers, bind `0.0.0.0:8000`).

## Adding a New Year

1. Add a new route in `app.py` (copy an existing year's route).
2. Update the Trello list IDs for each category (find them via the Trello API or `test.py`).
3. Set yearly targets per category in the route's `targets` dict.
4. Update the default route `/` to point to the new year.
