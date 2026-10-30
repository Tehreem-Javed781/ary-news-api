"""Selenium + headless Chrome scraper for ARY News Pakistan (arynews.tv)."""
import re
from urllib.parse import quote_plus, urlparse, parse_qs, unquote

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://arynews.tv"
DOMAIN = "arynews.tv"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

# path prefixes that are listing pages, not articles
NON_ARTICLE = ("category", "tag", "author", "page", "wp-content", "wp-admin", "feed",
               "live", "videos", "video", "about", "contact", "privacy", "terms", "search")


def make_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1366,900")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    opts.page_load_strategy = "eager"
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)
    driver.set_page_load_timeout(60)
    return driver


def is_article_url(href):
    if not href:
        return False
    p = urlparse(href)
    if not p.netloc.endswith(DOMAIN) or p.query or p.fragment:
        return False
    if p.netloc not in (DOMAIN, "www." + DOMAIN):  # skip urdu./sports. subdomains
        return False
    segs = [s for s in p.path.split("/") if s]
    if not segs or segs[0].lower() in NON_ARTICLE:
        return False
    slug = segs[-1]
    return slug.count("-") >= 3  # article slugs look like "pm-shehbaz-meets-..."


def _collect_article_links(driver):
    links = []
    # prefer links inside the main content area, then fall back to the whole page
    for selector in ("main a", "article a", "#content a", ".search-results a", "a"):
        for a in driver.find_elements(By.CSS_SELECTOR, selector):
            try:
                href = (a.get_attribute("href") or "").split("#")[0]
            except Exception:
                continue
            if is_article_url(href) and href not in links:
                links.append(href)
        if links:
            break
    return links


def search_ary(driver, keyword):
    """Use ARY News' own search page and return the first article URL."""
    driver.get(f"{BASE_URL}/?s={quote_plus(keyword)}")
    try:
        WebDriverWait(driver, 20).until(lambda d: len(_collect_article_links(d)) > 0)
    except Exception:
        pass
    links = _collect_article_links(driver)
    kw_words = [w for w in keyword.lower().split() if len(w) > 2]
    # pick the first link whose slug contains a keyword word, else the first link
    for href in links:
        if any(w in href.lower() for w in kw_words):
            return href
    return links[0] if links else None


def search_fallback(driver, keyword):
    """Fallback: DuckDuckGo HTML search restricted to arynews.tv."""
    driver.get(f"https://html.duckduckgo.com/html/?q={quote_plus('site:arynews.tv ' + keyword)}")
    for a in driver.find_elements(By.CSS_SELECTOR, "a.result__a"):
        href = a.get_attribute("href") or ""
        if "uddg=" in href:
            href = unquote(parse_qs(urlparse(href).query).get("uddg", [""])[0])
        if is_article_url(href):
            return href
    return None


def extract_article_text(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(lambda d: len(d.find_elements(By.TAG_NAME, "p")) > 3)
    except Exception:
        pass
    title = ""
    try:
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except Exception:
        pass

    paragraphs = []
    for selector in (".tdb-block-inner p", ".td-post-content p", ".entry-content p", "article p", "main p", "p"):
        paragraphs = [p.text.strip() for p in driver.find_elements(By.CSS_SELECTOR, selector)]
        paragraphs = [t for t in paragraphs if len(t) > 40 and "©" not in t]
        if len(paragraphs) >= 2:
            break
    return title, "\n".join(paragraphs)


def fetch_news(keyword):
    driver = make_driver()
    try:
        url = None
        try:
            url = search_ary(driver, keyword)
        except Exception:
            url = None
        if not url:
            url = search_fallback(driver, keyword)
        if not url:
            return None, "", ""
        title, text = extract_article_text(driver, url)
        return url, title, text
    finally:
        driver.quit()
