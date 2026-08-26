# AI Nuggets — + Web Player

> **This is a fork of [andrewsu/ai-nuggets](https://github.com/andrewsu/ai-nuggets).** The only addition is `webapp/` — a lightweight Flask web player that lets you browse and listen to your local podcast output in a browser. Everything else (pipeline, TTS, cron setup) is unchanged from the original.

See [webapp/README.md](webapp/README.md) for setup instructions.

---

After cloning, run `git config core.hooksPath .githooks` once to activate the
pre-commit feed-XML validator.

- **Adding a new show to this deployment?** See [ADDING_A_SHOW.md](ADDING_A_SHOW.md).
- **Running your own ai-nuggets** (your own Cloudflare account, cron, API
  keys)? See [SETUP.md](SETUP.md).
- **Want a local web player?** See [webapp/README.md](webapp/README.md) — a lightweight Flask app that serves a browseable episode list with audio player and transcript viewer from your local `podcasts/` directory.

## Repo layout

```
ai-nuggets/
├── gen_tts.py                          # shared TTS pipeline (Mistral / ElevenLabs)
├── lib/show.py                         # per-show config loader (reads show.toml)
├── scripts/
│   ├── new_show.py                     # scaffold a new podcast
│   ├── run_all_shows.sh                # daily cron entry point
│   ├── publish_episode.sh              # upload an mp3 to R2
│   └── update_feed_for_worker.py       # rewrite feed.xml enclosures for the Worker
├── worker/                             # Cloudflare Worker (analytics + redirect)
├── webapp/                             # optional local web player (Flask)
└── podcasts/<slug>/
    ├── show.toml                       # voice config, paths, RSS metadata
    ├── PROMPT.md                       # audience profile + daily recipe for the AI
    ├── feed.xml                        # this show's RSS feed
    ├── episodes/                       # mp3s
    ├── scripts/                        # daily transcripts (.md or .txt)
    └── logs/                           # run logs
```

## Adding a new show

```bash
python3 scripts/new_show.py my-new-show \
  --title "My New Show" \
  --description "What this show is about" \
  --owner "Owner Name <email>"
```

The daily runner (`scripts/run_all_shows.sh`) auto-discovers any
`podcasts/*/PROMPT.md` — no cron edit needed. After scaffolding you
still need to customize the PROMPT/show.toml, allow the slug on the
Worker, and smoke-test before letting cron take over. See
[ADDING_A_SHOW.md](ADDING_A_SHOW.md) for the full checklist.
