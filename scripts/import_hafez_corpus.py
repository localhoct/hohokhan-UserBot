from __future__ import annotations

import argparse
import http.cookiejar
import json
import random
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE_URL = "https://divanhafez.com"
DEFAULT_OUTPUT = Path("hohokhan/data/hafez_fortunes.json")
USER_AGENT = "HoHoKhan corpus importer/1.0"


def _request(opener: urllib.request.OpenerDirector, request: urllib.request.Request) -> dict:
    with opener.open(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _new_opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def _draw_interpretation(opener: urllib.request.OpenerDirector) -> tuple[int, str]:
    draw = _request(
        opener,
        urllib.request.Request(
            f"{BASE_URL}/api/fal",
            data=b"",
            method="POST",
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        ),
    )
    number = int(draw["n"])
    query = urllib.parse.urlencode({"token": draw["token"], "id": draw["gid"]})
    tabir = _request(
        opener,
        urllib.request.Request(
            f"{BASE_URL}/api/tabir?{query}",
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        ),
    )
    return number, str(tabir["tabir"]["fa"]).strip()


def _fetch_poem(number: int) -> str:
    for attempt in range(1, 8):
        try:
            request = urllib.request.Request(
                f"{BASE_URL}/fa/g/{number}", headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                page = response.read().decode("utf-8")
            marker = '<script type="application/ld+json">'
            start = page.find(marker)
            if start < 0:
                raise ValueError(f"poem metadata missing for {number}")
            start += len(marker)
            end = page.find("</script>", start)
            payload = json.loads(page[start:end])
            poem = next(item for item in payload["@graph"] if item.get("@type") == "Poem")
            return str(poem["text"]).strip()
        except (OSError, ValueError, KeyError, StopIteration, json.JSONDecodeError):
            if attempt == 7:
                raise
            time.sleep(attempt * 2 + random.random())
    raise RuntimeError("unreachable")


def _load(path: Path) -> dict[int, dict[str, object]]:
    if not path.is_file():
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {int(row["number"]): row for row in rows}


def _save(path: Path, rows: dict[int, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(
            [rows[number] for number in sorted(rows)],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import the licensed Hafez corpus.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    rows = _load(args.output)
    lock = threading.Lock()
    stop = threading.Event()

    def collect() -> None:
        opener = _new_opener()
        failures = 0
        while not stop.is_set():
            try:
                number, interpretation = _draw_interpretation(opener)
                with lock:
                    row = rows.setdefault(number, {"number": number})
                    if not row.get("interpretation"):
                        row["interpretation"] = interpretation
                        _save(args.output, rows)
                        print(f"interpretations: {len(rows)}/495 (added {number})", flush=True)
                    if len(rows) == 495:
                        stop.set()
                failures = 0
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                failures += 1
                time.sleep(min(60, 2**min(failures, 5)) + random.random())

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(collect) for _ in range(max(1, args.workers))]
        for future in futures:
            future.result()

    missing_poems = [number for number in range(1, 496) if not rows[number].get("poem")]
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(_fetch_poem, number): number for number in missing_poems}
        for future, number in futures.items():
            rows[number]["poem"] = future.result()
            _save(args.output, rows)
            completed = sum(bool(row.get("poem")) for row in rows.values())
            print(f"poems: {completed}/495 (added {number})", flush=True)
    _save(args.output, rows)


if __name__ == "__main__":
    main()
