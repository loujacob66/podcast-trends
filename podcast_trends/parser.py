import re
from pathlib import Path
import pandas as pd

def parse_podcast_url(url):
    path = Path(url)
    filename = path.name
    full_path = str(path)

    # Extract episode date
    match_date = re.search(r'(\d{8})', filename)
    if match_date:
        episode_date = pd.to_datetime(match_date.group(1), format='%Y%m%d', errors='coerce')
    else:
        match_path = re.search(r'/(\d{4})/(\d{2})/', full_path)
        if match_path:
            year, month = match_path.groups()
            episode_date = pd.to_datetime(f"{year}-{month}-01", format="%Y-%m-%d", errors='coerce')
        else:
            episode_date = None

    # Extract title
    title = re.sub(r'[_-]?\d{8}.*', '', filename).replace('.mp3', '').replace('_', ' ').strip()

    # Extract code
    match_code = re.search(r'(\d{3})@', filename)
    code = match_code.group(1) if match_code else None

    # Episode ID = title + date (or fallback to title)
    episode_id = f"{title}_{episode_date.strftime('%Y-%m-%d')}" if episode_date else title

    return {
        "title": title,
        "episode_date": episode_date.strftime("%Y-%m-%d") if episode_date else None,
        "code": code,
        "episode_id": episode_id
    }
