import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

USER_AGENT = "polite-scraper-student-project/1.0 (learning assignment; jannatul-f-dev)"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
DELAY_SECONDS = 0.6
PAGE_URL = "https://books.toscrape.com/catalogue/page-{}.html"


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


def get_book_links(page_number):
    url = PAGE_URL.format(page_number)
    html = fetch_page(url, f"catalogue-page-{page_number}.html")
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    return [urljoin(url, a["href"]) for a in soup.select("article.product_pod h3 a")]


def discover_all_links(pages=3):
    all_links = []
    for n in range(1, pages + 1):
        for link in get_book_links(n):
            if link not in all_links:
                all_links.append(link)
    return all_links


if __name__ == "__main__":
    links = discover_all_links()
    print(f"Found {len(links)} unique book links")
    print(links[0])