# AI Nuggets — Web Player

A lightweight Flask web player for the [ai-nuggets](https://github.com/andrewsu/ai-nuggets) podcast pipeline. Drop this `webapp/` directory into your fork and you get a browseable episode list, inline audio player, and transcript viewer.

## Quick Start

```bash
cd webapp/
pip install -r requirements.txt
python app.py        # dev server on http://localhost:5000
```

By default the app looks for podcasts one level up (`../podcasts/`), which is the layout of the ai-nuggets repo. Override with an env var if yours are elsewhere:

```bash
PODCAST_DIR=/path/to/podcasts python app.py
```

## Production (gunicorn)

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Put nginx in front of it to handle TLS and static caching.

## Podcast Directory Layout

The app expects the same layout that the ai-nuggets pipeline produces:

```
podcasts/
└── my-show/
    ├── show.toml          # title, description, host
    ├── feed.xml           # RSS feed (auto-updated by pipeline)
    ├── episodes/          # mp3 files
    │   └── 2024-01-15.mp3
    └── scripts/           # markdown transcripts (optional)
        └── 2024-01-15.md
```

`show.toml` keys used by the player:

| Key | Description |
|---|---|
| `title` | Show display name |
| `description` | One-line description shown on the index |
| `host` | Host name shown on the show page |

Transcripts are optional. If a `scripts/<guid>.md` file exists the "Show Transcript" button appears for that episode.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PODCAST_DIR` | `../podcasts` | Path to the podcasts directory |
