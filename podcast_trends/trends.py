from collections import Counter
from datetime import datetime

def top_episodes(records, start=None, end=None, limit=10):
    filtered = []
    for r in records:
        if r["episode_date"]:
            date = datetime.strptime(r["episode_date"], "%Y-%m-%d")
            if start and date < start:
                continue
            if end and date > end:
                continue
        filtered.append(r)

    counter = Counter()
    for r in filtered:
        counter[r["episode_id"]] += r["total"]

    return counter.most_common(limit)
