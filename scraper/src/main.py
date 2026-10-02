import os
import requests

USER_AGENT = "polite-scraper-student-project/1.0 (learning assignment; jannatul-f-dev)"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")


def fetch_page(url, filename):
    os.makedirs(CACHE_DIR, exist_ok=True)
    filepath = os.path.join(CACHE_DIR, filename)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT: {filename} ({len(html)} bytes)")
        return html

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


if __name__ == "__main__":
    fetch_page("https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")