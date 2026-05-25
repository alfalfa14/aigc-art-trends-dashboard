# AI-Generated Art Style Trends Dashboard

A data dashboard built for DIGS 20004 Final Project. It visualizes how AI-generated art styles have shifted across regions and time periods from 2022 to 2024.

## Files

- `app_aigc.py` — Dash dashboard
- `ai_generated_art_trends_2024.csv` — dataset from Kaggle
- `requirements.txt` — Python dependencies
- `assets/` — CSS styling adapted from the Week 7 course template
- `writeup.pdf` — project writeup and statement on collaboration

## Data Source

Kaggle: [AI-Generated Art Trends Dataset](https://www.kaggle.com/datasets/waqi786/ai-generated-art-trends)

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 app_aigc.py
```

Then open: http://127.0.0.1:8050/

## Dashboard Features

- **Style trend** — line chart showing each art style's share per year; checklist to select/deselect styles
- **Region × Style** — heatmap showing artwork count for each region and style combination
- **World map** — bubble map showing artwork volume and average popularity score by region
- Time range slider filters all three charts by quarter