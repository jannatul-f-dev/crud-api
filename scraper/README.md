# The polite scraper (A9)

A small, polite web scraper that collects book data from [Books to Scrape](https://books.toscrape.com), a public practice sandbox built for learning scraping.

## Target classification

- **Site:** books.toscrape.com
- **Why:** It is explicitly a public sandbox created for people to practise web scraping on. That is permission to scrape it, and this project touches no other site.
- **Scope:** Only the first 3 catalogue pages (60 books total).
- **Data collected:** Book title, price, availability, rating, description, and product URL — all publicly shown on the page, nothing behind a login.
- **robots.txt result:** Requested `https://books.toscrape.com/robots.txt` — it returns a 404 Not Found. No robots file exists for this site. A missing file is not permission by itself, but combined with the site's own stated purpose as a scraping sandbox, scraping it is appropriate here.

I will not reuse this code on another site without checking its rules and terms first.

## Lane and install

Python 3.10 or newer.

```
pip install requests beautifulsoup4 pydantic
```

## Run it

One command, from the `scraper` folder:

```
python src/main.py
```

It writes `output/books.json` (validated records), `output/errors.json` (records that failed validation, with the reason) and `output/run-report.json` (what happened in the run). A first run fetches about 63 pages and takes roughly a minute; later runs read from the local `cache/` folder and take a few seconds.

## Record schema

Each record in `books.json` has these fields:

| Field | Type | Notes |
|---|---|---|
| `title` | string | required, not empty |
| `product_url` | string | required, must start with `https://`, used as the record's identity |
| `price_text` | string | raw text from the page, e.g. `£51.77` |
| `price_gbp` | number | clean value parsed from `price_text`, must be greater than 0 |
| `availability_text` | string | raw text, e.g. `In stock (22 available)` |
| `rating_text` | string or null | e.g. `Three` |
| `description` | string or null | `null` when the book has no description |
| `source_page` | string | the catalogue page the book was found on |
| `fetched_at` | string | UTC time the page was fetched (ISO 8601) |

## Politeness rules

- **User-agent:** every request says who I am: `polite-scraper-student-project/1.0 (learning assignment; jannatul-f-dev)`.
- **Delay:** 0.6 seconds before every real request. Cached pages need no delay.
- **Timeout:** a request gives up after 5 seconds.
- **Retries:** on a timeout or a 5xx server error, wait 2 seconds and try once more. A 404 or 403 is never retried.
- **Cache:** every page is saved to `cache/` and read from there on later runs, so the site is asked only once.

## Sample run report

A real `run-report.json` from my run (this run was served from the cache, so it shows cache hits instead of fetched pages):

```json
{
  "started_at": "2026-10-02T15:06:56Z",
  "duration_seconds": 2.57,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

This assignment needed no browser: the data is already in the HTML the server sends, so a browser would only add cost.

## Ethics note

If a site has an official API, I should use that instead of scraping. I should never bypass logins, paywalls, or blocks. I should collect only the data I actually need.

## Honest limitation

The scraper depends on the current HTML layout of the site. If the site changes its markup, pages will fail to parse or records will fail validation, and they will show up in `failed_pages` or `errors.json` instead of being collected.