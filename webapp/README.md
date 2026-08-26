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

## Production (gunicorn + nginx)

Run the app with gunicorn, bound to localhost only:

```bash
pip install gunicorn
gunicorn -w 2 -b 127.0.0.1:5000 app:app
```

Then put nginx in front to handle the public port and (optionally) TLS. A minimal site config — save to `/etc/nginx/sites-available/podcasts` and symlink to `sites-enabled/`:

```nginx
server {
    listen 80;
    server_name your-domain-or-ip;

    # stream audio efficiently without passing through Flask
    location /podcasts/audio/ {
        alias /path/to/podcasts/;
        sendfile on;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/podcasts /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

For HTTPS, run `sudo certbot --nginx -d your-domain` (requires [Certbot](https://certbot.eff.org/) and a real domain pointed at your server).

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
