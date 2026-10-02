import os
import time
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

USER_AGENT = "polite-scraper-student-project/1.0 (learning assignment; jannatul-f-dev)"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
DELAY_SECONDS = 0.6
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES = 3


def fetch_page(url, filename):
    os.makedirs(CACHE_DIR, exist_ok=True)
    filepath = os.path.join(CACHE_DIR, filename)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT: {filename} ({len(html)} bytes)")
        return html

    time.sleep(DELAY_SECONDS)
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=5)

    if response.status_code != 200:
        print(f"FETCH FAILED: {url} returned status {response.status_code}")
        return None

    response.encoding = "utf-8"
    html = response.text
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
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


if __name__ == "__main__":
    links = discover_all_links()
    records = []
    for url, source_page in links.items():
        slug = url.rstrip("/").split("/")[-2]
        filename = f"book-{slug}.html"
        html = fetch_page(url, filename)
        if html is None:
            continue
        mtime = os.path.getmtime(os.path.join(CACHE_DIR, filename))
        fetched_at = datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        records.append(extract_book(html, url, source_page, fetched_at))

    print(json.dumps(records[0], indent=2))
    print(f"detail_pages={len(records)}")