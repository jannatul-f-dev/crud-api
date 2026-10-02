import os
import re
import time
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydantic import BaseModel, field_validator

USER_AGENT = "polite-scraper-student-project/1.0 (learning assignment; jannatul-f-dev)"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
DELAY_SECONDS = 0.6
RETRY_WAIT_SECONDS = 2
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 3

# TEST ONLY: put a made-up URL here to prove one bad page does not kill the run.
EXTRA_TEST_URLS = []

STATS = {"pages_fetched": 0, "cache_hits": 0, "failed_pages": 0}


class Book(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str | None = None
    description: str | None = None
    source_page: str
    fetched_at: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("title is empty")
        return v

    @field_validator("product_url", "source_page")
    @classmethod
    def must_be_https(cls, v):
        if not v.startswith("https://"):
            raise ValueError("URL must start with https://")
        return v

    @field_validator("price_gbp")
    @classmethod
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v


def fetch_page(url, filename):
    os.makedirs(CACHE_DIR, exist_ok=True)
    filepath = os.path.join(CACHE_DIR, filename)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        STATS["cache_hits"] += 1
        print(f"CACHE HIT: {filename} ({len(html)} bytes)")
        return html

    headers = {"User-Agent": USER_AGENT}
    response = None
    for attempt in (1, 2):
        time.sleep(DELAY_SECONDS if attempt == 1 else RETRY_WAIT_SECONDS)
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except requests.RequestException as e:
            print(f"ATTEMPT {attempt} ERROR: {url} ({type(e).__name__})")
            continue
        if response.status_code == 200:
            break
        if response.status_code >= 500:
            print(f"ATTEMPT {attempt} SERVER ERROR {response.status_code}: {url}")
            continue
        print(f"FETCH FAILED: {url} returned status {response.status_code}")
        STATS["failed_pages"] += 1
        return None
    else:
        print(f"FETCH FAILED: {url} after 2 attempts")
        STATS["failed_pages"] += 1
        return None

    response.encoding = "utf-8"
    html = response.text
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    STATS["pages_fetched"] += 1
    print(f"FETCH: {filename} ({len(html)} bytes)")
    return html


def parse_catalogue_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    links = [urljoin(page_url, a["href"]) for a in soup.select("article.product_pod h3 a")]
    next_a = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_a["href"]) if next_a else None
    return links, next_url


def discover_all_links():
    found = {}
    discovered = 0
    pages = 0
    page_url = START_URL
    while page_url and pages < MAX_PAGES:
        pages += 1
        html = fetch_page(page_url, f"catalogue-page-{pages}.html")
        if html is None:
            break
        links, next_url = parse_catalogue_page(html, page_url)
        discovered += len(links)
        for link in links:
            if link not in found:
                found[link] = page_url
        page_url = next_url
    print(f"catalogue_pages={pages}, discovered={discovered}, unique_urls={len(found)}")
    return found


def extract_book(html, product_url, source_page, fetched_at):
    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("article.product_page")

    title = product.select_one("h1").get_text(strip=True)
    price_text = product.select_one("p.price_color").get_text(strip=True)
    availability_text = " ".join(product.select_one("p.availability").get_text().split())

    rating_el = product.select_one("p.star-rating")
    rating_text = rating_el["class"][1] if rating_el else None

    description = None
    header = product.select_one("#product_description")
    if header:
        p = header.find_next_sibling("p")
        if p:
            description = p.get_text(strip=True)

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def normalize(raw):
    data = dict(raw)
    match = re.search(r"\d+(?:\.\d+)?", raw["price_text"])
    if not match:
        raise ValueError("no number found in price_text")
    data["price_gbp"] = float(match.group())
    return data


def save_json(filename, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    started = datetime.now(timezone.utc)
    t0 = time.time()

    links = discover_all_links()
    for test_url in EXTRA_TEST_URLS:
        links[test_url] = START_URL

    records = []
    for url, source_page in links.items():
        slug = url.rstrip("/").split("/")[-2]
        filename = f"book-{slug}.html"
        html = fetch_page(url, filename)
        if html is None:
            continue
        try:
            mtime = os.path.getmtime(os.path.join(CACHE_DIR, filename))
            fetched_at = datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            records.append(extract_book(html, url, source_page, fetched_at))
        except Exception as e:
            print(f"PARSE FAILED: {url} ({e})")
            STATS["failed_pages"] += 1
    print(f"detail_pages={len(records)}")

    valid = {}
    errors = []
    for raw in records:
        try:
            book = Book(**normalize(raw))
            valid[book.product_url] = book.model_dump()
        except ValueError as e:
            errors.append({"product_url": raw.get("product_url"), "reason": str(e)})

    save_json("books.json", list(valid.values()))
    save_json("errors.json", errors)

    report = {
        "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds": round(time.time() - t0, 2),
        "pages_fetched": STATS["pages_fetched"],
        "cache_hits": STATS["cache_hits"],
        "valid_records": len(valid),
        "invalid_records": len(errors),
        "failed_pages": STATS["failed_pages"],
    }
    save_json("run-report.json", report)
    print(f"valid={len(valid)}, invalid={len(errors)}")
    print(json.dumps(report, indent=2))
