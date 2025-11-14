#!/usr/bin/env python3
"""
scraper.py
Improved + DEBUG version
Scrapes archived MyFootDr clinic listings.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from tqdm import tqdm

# ---- CONSTANTS ----
BASE_URL = "https://web.archive.org/web/20250708180027/https://www.myfootdr.com.au/our-clinics/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MyFootDrScraper/DEBUG; +https://example.com)"
}

# ---- BASIC HELPERS ----
def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"ERROR fetching {url}: {e}")
        return None


# ---- EXTRACT LINKS (DEBUG LEVEL) ----
def extract_clinic_links():
    soup = get_soup(BASE_URL)
    if not soup:
        print("ERROR: Could not fetch main page.")
        return []

    print("DEBUG: main page loaded.")

    anchors = soup.find_all("a", href=True)
    print(f"DEBUG: total <a> tags found: {len(anchors)}")

    links = []

    for a in anchors:
        href = a["href"].strip()

        # Keep ANYTHING containing /our-clinics/
        if "/our-clinics/" in href:
            # Full link
            if href.startswith("http"):
                full = href
            elif href.startswith("//"):
                full = "https:" + href
            else:
                full = urljoin(BASE_URL, href)

            # Remove URL fragments
            full = full.split("#")[0].rstrip("/")

            links.append(full)

    unique_links = sorted(set(links))

    print(f"DEBUG: {len(unique_links)} unique candidate links:")
    for i, link in enumerate(unique_links[:20]):
        print(f"   [{i+1}] {link}")

    return unique_links


# ---- SCRAPE INDIVIDUAL CLINIC PAGE ----
def parse_clinic_page(url):
    soup = get_soup(url)
    if not soup:
        print(f"ERROR: Failed to load clinic page {url}")
        return None

    # Extract title (usually clinic name)
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip().split("|")[0].strip()

    # Extract email
    email = ""
    email_tag = soup.find("a", href=re.compile("mailto:", re.I))
    if email_tag:
        email = email_tag["href"].replace("mailto:", "").strip()

    # Extract phone
    phone = ""
    phone_match = soup.get_text(" ", strip=True)
    m = re.search(r"(?:Ph|Phone|Call)[:\s]*([0-9\+\-\s\(\)]{6,})", phone_match, re.I)
    if m:
        phone = m.group(1).strip()

    # Extract address using <address> tag
    address = ""
    addr_tag = soup.find("address")
    if addr_tag:
        address = addr_tag.get_text(" ", strip=True)

    # Extract services (any bulleted list)
    services = ""
    ul = soup.find("ul")
    if ul:
        items = [li.get_text(" ", strip=True) for li in ul.find_all("li")]
        services = " | ".join(items)

    return {
        "Name of Clinic": title,
        "Address": address,
        "Email": email,
        "Phone": phone,
        "Services": services,
        "Clinic Page URL": url
    }


# ---- MAIN SCRAPER LOGIC USED BY main.py ----
def scrape_clinics():
    print("Fetching clinic links...")
    links = extract_clinic_links()

    if not links:
        print("Found 0 clinic links! Something is wrong.")
        return []

    print(f"Found {len(links)} raw clinic URLs… scraping now.\n")

    results = []
    for url in tqdm(links, desc="Scraping pages"):
        rec = parse_clinic_page(url)
        if rec:
            results.append(rec)

    print(f"\nCompleted scraping. Total records: {len(results)}")
    return results

