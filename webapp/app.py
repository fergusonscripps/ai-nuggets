"""Standalone Flask web player for the AI podcast pipeline.

Reads show configs and episode feeds from the podcasts/ directory in the
parent repo (or any path set via PODCAST_DIR env var), and serves a web
player with episode audio and transcripts.

Usage:
    pip install -r requirements.txt
    python app.py                          # dev server on port 5000
    gunicorn -w 2 -b 0.0.0.0:5000 app:app  # production
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import tomllib
from flask import Flask, abort, jsonify, redirect, render_template, send_file, url_for

# ── Config ────────────────────────────────────────────────────────────────────

# Path to the podcasts/ directory — defaults to ../podcasts/ relative to this
# file so it works out of the box when webapp/ sits inside the pipeline repo.
# Override with PODCAST_DIR=/absolute/path if you host them separately.
PODCAST_DIR = os.environ.get(
    'PODCAST_DIR',
    str(Path(__file__).resolve().parent.parent / 'podcasts')
)

app = Flask(__name__)


# ── Show loading ──────────────────────────────────────────────────────────────

def _load_shows():
    """Read all show configs and parse episode lists from feed.xml files."""
    shows = []
    if not os.path.isdir(PODCAST_DIR):
        return shows

    for show_dir in sorted(os.listdir(PODCAST_DIR)):
        show_path = os.path.join(PODCAST_DIR, show_dir)
        toml_path = os.path.join(show_path, 'show.toml')
        feed_path = os.path.join(show_path, 'feed.xml')

        if not os.path.isfile(toml_path):
            continue

        try:
            with open(toml_path, 'rb') as f:
                cfg = tomllib.load(f)
        except Exception:
            continue

        episodes = []
        if os.path.isfile(feed_path):
            try:
                ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
                tree = ET.parse(feed_path)
                for item in tree.findall('.//item'):
                    guid = item.findtext('guid', '').strip()
                    enc  = item.find('enclosure')
                    mp3_filename = os.path.basename(enc.get('url', '')) if enc is not None else None
                    script_file  = os.path.join(show_path, 'scripts', guid + '.md')
                    episodes.append({
                        'title':        item.findtext('title', ''),
                        'description':  item.findtext('description', ''),
                        'pubDate':      item.findtext('pubDate', ''),
                        'guid':         guid,
                        'duration':     item.findtext('itunes:duration', '', ns),
                        'mp3_filename': mp3_filename,
                        'has_script':   os.path.isfile(script_file),
                    })
            except Exception:
                pass

        shows.append({
            'slug':        show_dir,
            'title':       cfg.get('title', show_dir),
            'description': cfg.get('description', ''),
            'host':        cfg.get('host', ''),
            'episodes':    episodes,
        })
    return shows


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('podcasts'))


@app.route('/podcasts')
def podcasts():
    return render_template('podcasts.html', shows=_load_shows())


@app.route('/podcasts/<show_slug>')
def podcast_show(show_slug):
    if '/' in show_slug or '..' in show_slug:
        abort(404)
    show = next((s for s in _load_shows() if s['slug'] == show_slug), None)
    if not show:
        abort(404)
    return render_template('podcast_show.html', show=show)


@app.route('/podcasts/<show_slug>/audio/<filename>')
def serve_audio(show_slug, filename):
    if '/' in show_slug or '..' in show_slug or '/' in filename or '..' in filename:
        abort(400)
    if not filename.endswith('.mp3'):
        abort(400)
    file_path = os.path.join(PODCAST_DIR, show_slug, 'episodes', filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_file(file_path, mimetype='audio/mpeg', as_attachment=False,
                     download_name=filename)


@app.route('/podcasts/<show_slug>/script/<guid>')
def serve_script(show_slug, guid):
    if '/' in show_slug or '..' in show_slug or '/' in guid or '..' in guid:
        abort(400)
    script_path = os.path.join(PODCAST_DIR, show_slug, 'scripts', guid + '.md')
    if not os.path.isfile(script_path):
        return jsonify({'error': 'Script not found'}), 404
    with open(script_path, 'r') as f:
        content = f.read()
    content = re.sub(r'^##\s*Script\s*\n', '', content).strip()
    return jsonify({'content': content})


# ── Startup ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
