"""Standalone helper for scraping professor profiles via Firecrawl."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings
from app.services.scrape_orchestrator import ScrapeOrchestrator


def _load_urls(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(path)

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    if path.suffix.lower() == ".json":
        payload = json.loads(text)
        if isinstance(payload, dict):
            urls = payload.get("urls", [])
        elif isinstance(payload, list):
            urls = payload
        else:
            raise ValueError("JSON payload must be a list or contain a 'urls' array")
    else:
        urls = [line.strip() for line in text.splitlines() if line.strip()]

    return [str(url) for url in urls if url]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape professor profile URLs and write them into HelixDB",
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="URLs to scrape if not supplying an input file",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Optional text/JSON file containing URLs (one per line or a JSON list)",
    )
    parser.add_argument(
        "--init-schema",
        action="store_true",
        help="Attempt to apply the Helix schema before scraping",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    urls: List[str] = list(args.urls)
    if args.input:
        urls.extend(_load_urls(args.input))

    urls = [url.strip() for url in urls if url.strip()]
    if not urls:
        raise SystemExit("No URLs supplied. Use arguments or --input file.")

    orchestrator = ScrapeOrchestrator(settings=get_settings())
    summary = orchestrator.run(urls, initialize_schema=args.init_schema)
    payload = summary.to_dict()

    print(
        f"Scraped {payload['success_count']} / {payload['total']} URLs ("
        f"{payload['failure_count']} failed)."
    )

    for result in payload["results"]:
        status = "OK" if result["success"] else "FAIL"
        detail = result.get("helix_id") or result.get("error", "")
        print(f"[{status}] {result['url']} :: {detail}")


if __name__ == "__main__":
    main()

