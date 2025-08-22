#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Liblib API sampler for Transportation (汽车交通)

Outputs:
- 3 list page JSONs from img/group/search
- Up to 10 detail JSONs from img/group/get/{slug} and img/author/{slug}

Usage examples:
  python src/scraping/liblib_api_sampler.py --pages 3 --max-details 10 \
    --out-dir data/raw/liblib/samples

Optionally provide a captured request payload (JSON file) for img/group/search:
  python src/scraping/liblib_api_sampler.py --payload-file payloads/list_payload.json
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set

import requests


LIBLIB_API_BASE = "https://api2.liblib.art"

# Conservative headers to mimic a browser without credentials
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.liblib.art/",
    "Origin": "https://www.liblib.art",
    "Content-Type": "application/json",
}


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    
    # Add cookie if provided via environment variable
    cookie = os.environ.get('LIBLIB_COOKIE')
    if cookie:
        session.headers.update({'Cookie': cookie})
        print(f"Added cookie to session: {cookie[:50]}...")
    
    return session


def safe_post(
    session: requests.Session,
    url: str,
    json_payload: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    max_retries: int = 3,
    backoff_base_seconds: float = 1.0,
) -> Optional[Dict[str, Any]]:
    for attempt in range(max_retries):
        try:
            resp = session.post(url, json=json_payload, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            # Backoff on non-200 (e.g., 429)
            time.sleep(backoff_base_seconds * (2 ** attempt))
        except Exception:
            # Backoff then retry
            time.sleep(backoff_base_seconds * (2 ** attempt))
    return None


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_json(obj: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def default_list_payload(page: int = 1, page_size: int = 24) -> Dict[str, Any]:
    """
    Reasonable default payload for /api/www/model/list. Real payloads may differ.
    Prefer providing --payload-file captured from network if available.
    """
    return {
        "categories": ["汽车交通"],
        "page": page,
        "pageSize": page_size,
        "sortType": "recommend",  # newest|hot|recommend
        "modelType": "",
        "nsfw": False
    }


def extract_slugs_from_list(list_json: Dict[str, Any]) -> List[str]:
    data_root = list_json or {}
    data_obj = data_root.get("data") if isinstance(data_root, dict) else None
    items: List[Dict[str, Any]] = []
    if isinstance(data_obj, dict):
        # Prefer data.data (array) when present; fallback to data.list
        if isinstance(data_obj.get("data"), list):
            items = data_obj.get("data") or []
        elif isinstance(data_obj.get("list"), list):
            items = data_obj.get("list") or []

    slugs: List[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        # Use uuid first; fallback to any available identifier
        slug = (
            item.get("uuid")
            or item.get("groupSlug")
            or item.get("slug")
            or item.get("id")
        )
        if slug is None:
            continue
        # Coerce to string to avoid numeric IDs
        slugs.append(str(slug))
    return slugs


def fetch_list_pages(
    session: requests.Session,
    pages: int,
    out_dir: str,
    payload_file: Optional[str] = None,
    delay_seconds: float = 0.8,
) -> List[str]:
    """
    Returns a de-duplicated list of slugs from fetched pages.
    """
    ensure_dir(out_dir)
    all_slugs: List[str] = []

    for page in range(1, pages + 1):
        if payload_file:
            with open(payload_file, "r", encoding="utf-8") as f:
                base_payload = json.load(f)
            if isinstance(base_payload, dict):
                base_payload = {**base_payload, "page": page}
        else:
            base_payload = default_list_payload(page=page)

        url = f"{LIBLIB_API_BASE}/api/www/model/list"
        resp_json = safe_post(session, url, base_payload)
        if resp_json is None:
            print(f"WARN: list page {page} request failed")
            continue

        out_path = os.path.join(out_dir, f"list_page_{page}.json")
        print(f"DEBUG: Attempting to save to {out_path}")
        print(f"DEBUG: resp_json type: {type(resp_json)}")
        print(f"DEBUG: resp_json keys: {list(resp_json.keys()) if isinstance(resp_json, dict) else 'Not a dict'}")
        save_json(resp_json, out_path)
        print(f"DEBUG: File saved successfully")
        # Debug output: code/message and list size
        try:
            code = resp_json.get("code")
            message = resp_json.get("message") or resp_json.get("msg")
            data_obj = resp_json.get("data") if isinstance(resp_json, dict) else None
            list_len = 0
            if isinstance(data_obj, dict):
                if isinstance(data_obj.get("data"), list):
                    list_len = len(data_obj.get("data"))
                elif isinstance(data_obj.get("list"), list):
                    list_len = len(data_obj.get("list"))
            print(f"List page {page}: code={code}, message={message}, items={list_len}")
        except Exception:
            pass

        slugs = extract_slugs_from_list(resp_json)
        all_slugs.extend(slugs)
        print(f"Saved list page {page} with {len(slugs)} slugs → {out_path}")

        time.sleep(delay_seconds)

    # De-duplicate while preserving order
    seen: Set[str] = set()
    deduped: List[str] = []
    for s in all_slugs:
        if s in seen:
            continue
        seen.add(s)
        deduped.append(s)
    return deduped


def fetch_details(
    session: requests.Session,
    slugs: Iterable[str],
    max_details: int,
    out_dir: str,
    delay_seconds: float = 0.8,
) -> None:
    ensure_dir(out_dir)
    count = 0
    for slug in slugs:
        if count >= max_details:
            break

        now_ts = int(time.time() * 1000)
        detail_url = f"{LIBLIB_API_BASE}/api/www/img/group/get/{slug}?timestamp={now_ts}"
        detail_json = safe_post(session, detail_url, {"timestamp": now_ts})

        # Try to resolve author by userUuid from detail response, if present
        author_json = None
        author_user_uuid: Optional[str] = None
        try:
            if isinstance(detail_json, dict):
                data_obj = detail_json.get("data")
                if isinstance(data_obj, dict):
                    author_user_uuid = data_obj.get("userUuid") or data_obj.get("authorUuid")
        except Exception:
            author_user_uuid = None

        if author_user_uuid:
            author_url = f"{LIBLIB_API_BASE}/api/www/img/author/{author_user_uuid}?timestamp={now_ts}"
            author_json = safe_post(session, author_url, None)

        if detail_json is None and author_json is None:
            print(f"WARN: skip slug {slug}, both detail and author failed")
            continue

        detail_path = os.path.join(out_dir, f"detail_{slug}.json")
        author_path = os.path.join(out_dir, f"author_{author_user_uuid or slug}.json")
        if detail_json is not None:
            save_json(detail_json, detail_path)
        if author_json is not None:
            save_json(author_json, author_path)
        print(f"Saved detail for {slug} → {detail_path} | {author_path}")

        count += 1
        time.sleep(delay_seconds)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Liblib API sampler (Transportation)")
    parser.add_argument(
        "--out-dir",
        default=os.path.join("data", "raw", "liblib", "samples"),
        help="Directory to write JSON samples",
    )
    parser.add_argument("--pages", type=int, default=3, help="Number of list pages to sample")
    parser.add_argument("--max-details", type=int, default=10, help="Max number of details to fetch")
    parser.add_argument(
        "--payload-file",
        type=str,
        default=None,
        help="Path to JSON payload file for img/group/search",
    )
    parser.add_argument("--delay", type=float, default=0.8, help="Delay seconds between requests")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout seconds")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    session = create_session()

    # Ensure output subfolders exist
    list_dir = os.path.join(args.out_dir, "lists")
    detail_dir = os.path.join(args.out_dir, "details")
    ensure_dir(list_dir)
    ensure_dir(detail_dir)

    print(
        f"Starting sampler: pages={args.pages}, max_details={args.max_details}, out_dir={args.out_dir}"
    )
    slugs = fetch_list_pages(
        session=session,
        pages=args.pages,
        out_dir=list_dir,
        payload_file=args.payload_file,
        delay_seconds=args.delay,
    )

    if not slugs:
        print("No slugs extracted from list pages; nothing to fetch.")
        return 1

    fetch_details(
        session=session,
        slugs=slugs,
        max_details=args.max_details,
        out_dir=detail_dir,
        delay_seconds=args.delay,
    )

    print("Sampler completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


