#!/usr/bin/env python3
"""
myfootdr_scraper.py

Scrapes the archived My FootDr clinics page (Web Archive snapshot)
and visits each clinic page to extract:
- Name of Clinic
- Address
- Email
- Phone
- Services

Outputs: clinics_myfootdr.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from urllib.parse import urljoin

# === CONFIG ===
START_URL = "https://web.archive.org/web/20250708180027/https://www.myfootdr.com.au/our-clinics/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MyFootDrScraper/1.0; +https://example.com)"
}
OUTPUT_CSV = "clinics_myfootdr.csv"
DELAY_BETWEEN_REQUESTS = 0.6  # seconds (be polite)

# Helper patterns
phone_re = re.compile(r'(\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4})')
mailto_re = re.compile(r'^mailto:', re.I)

def text_or_none(el):
    return el.get_text(separator=" ", strip=True) if el else None

def extract_phone(text):
    if not text:
        return None
    m = phone_re.search(text)
    return m.group(1).strip() if m else None

def extract_email_from_soup(soup):
    # Look for mailto links first
    a_tags = soup.find_all('a', href=True)
    for a in a_tags:
        href = a['href'].strip()
        if mailto_re.match(href):
            email = href.split(':',1)[1].split('?')[0]
            return email.strip()
    # fallback: search for simple email pattern anywhere
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', soup.get_text(" ", strip=True))
    return emails[0].strip() if emails else None

def parse_clinic_page(clinic_url):
    try:
        r = requests.get(clinic_url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"ERROR fetching {clinic_url}: {e}")
        return None

    # Name: page <h1> or title
    name = None
    h1 = soup.find("h1")
    if h1:
        name = h1.get_text(strip=True)

    # Phone: look for patterns with 'Call' or 'Ph:' or 'b ' in page
    phone = None
    # common patterns: "Call 07 5562 5055", "Ph: 07 5562 5055", "b 07 5562 5055"
    body_text = soup.get_text(" ", strip=True)
    phone = extract_phone(body_text)

    # Address: look for address blocks - often inside <address>, or lines with postcode/state abbreviations (e.g., QLD, NSW, VIC, SA, WA, NT, TAS)
    address = None
    address_tag = soup.find("address")
    if address_tag:
        address = address_tag.get_text(separator=" ", strip=True)
    else:
        # look for patterns: lines that contain state and postcode
        # we'll search for lines that contain state abbreviations and a 4-digit postcode
        lines = [l.strip() for l in re.split(r'[\n\r]+', soup.get_text("\n", strip=True)) if l.strip()]
        for i, line in enumerate(lines):
            if re.search(r'\b(?:QLD|NSW|VIC|SA|WA|NT|TAS)\b', line) and re.search(r'\b\d{4}\b', line):
                # collect this and previous 1-2 lines as address
                addr_lines = [lines[j] for j in range(max(0, i-2), i+1)]
                address = ", ".join(addr_lines)
                break

    # Email
    email = extract_email_from_soup(soup)

    # Services: many pages have a section listing clinical services as bullet lists or paragraphs
    services = None
    # try to find common headings
    for header_text in ("Our Services", "Services", "Clinical Podiatry", "We provide", "We offer"):
        header = soup.find(lambda tag: tag.name in ["h2","h3","h4"] and header_text.lower() in tag.get_text(" ",True).lower())
        if header:
            # attempt to collect next <ul> or next sibling paragraphs
            ul = header.find_next_sibling("ul")
            if ul:
                items = [li.get_text(" ", strip=True) for li in ul.find_all("li")]
                services = " | ".join(items)
                break
            # else paragraphs until next header
            items = []
            node = header.find_next_sibling()
            while node and node.name and not node.name.startswith("h"):
                txt = node.get_text(" ", strip=True)
                if txt:
                    items.append(txt)
                node = node.find_next_sibling()
            if items:
                services = " | ".join(items)
                break

    # fallback: try to find lists in main content area
    if not services:
        ul = soup.find("ul")
        if ul:
            items = [li.get_text(" ", strip=True) for li in ul.find_all("li")]
            if items:
                services = " | ".join(items)

    return {
        "Name of Clinic": name or "",
        "Address": address or "",
        "Email": email or "",
        "Phone": phone or "",
        "Services": services or ""
    }

def main():
    # fetch the main archived listing
    print("Fetching main page:", START_URL)
    r = requests.get(START_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # The main listing has many "Book here" links leading to individual clinic pages.
    # We'll collect all <a> tags that have hrefs under /our-clinics/ (clinic pages).
    anchors = soup.find_all('a', href=True)
    clinic_links = {}
    for a in anchors:
        href = a['href']
        # normalize absolute/relative
        full = urljoin(START_URL, href)
        # clinics often have "/our-clinics/<slug>/" in URL
        if "/our-clinics/" in full and full.rstrip('/').count('/') >= 4:
            # use the link text as name fallback
            link_text = a.get_text(" ", strip=True)
            clinic_links[full] = link_text

    # also try to capture clinic names and the text that appears near "Book here"
    # plus fallback: some clinics are directly present as names in the HTML, so find the "####" headings (h4/h3)
    # gather unique links
    clinic_urls = sorted(set(clinic_links.keys()))
    print(f"Found {len(clinic_urls)} clinic links (candidates).")

    # If no direct links (because the snapshot uses JS), also parse the page blocks for "####  ClinicName" style
    if len(clinic_urls) < 10:
        print("Fallback: parsing listing blocks for clinic names/addresses (no direct links found).")
        # attempt to parse using the visible page text blocks for lines that look like clinics
        # find clinic headings - h3/h4 tags
        headings = soup.find_all(re.compile('^h[1-6]$'))
        for h in headings:
            txt = h.get_text(" ", strip=True)
            if txt and len(txt) < 120 and any(char.isalpha() for char in txt):
                # look for phone/address under this heading
                sibling_texts = []
                node = h.find_next_sibling()
                capture = []
                while node and len(capture) < 6:
                    t = node.get_text(" ", strip=True)
                    if t:
                        capture.append(t)
                    node = node.find_next_sibling()
                if capture:
                    # create a pseudo-record
                    name = txt
                    address = " | ".join(capture)
                    clinic_urls.append(f"TEXT-ONLY::{name}::")  # placeholder
                    clinic_links[f"TEXT-ONLY::{name}::"] = address

    # Now iterate each clinic URL and extract details
    results = []
    for idx, url in enumerate(clinic_urls, 1):
        print(f"[{idx}/{len(clinic_urls)}] Processing: {url}")
        if url.startswith("TEXT-ONLY::"):
            # placeholder entry from fallback: split and store basic data
            _, name, _ = url.split("::")
            results.append({
                "Name of Clinic": name,
                "Address": clinic_links.get(url, ""),
                "Email": "",
                "Phone": "",
                "Services": ""
            })
            continue

        # Many "Book here" links may point to booking widgets or anchors; attempt to fetch the URL and if it redirects to an internal clinic page, follow
        time.sleep(DELAY_BETWEEN_REQUESTS)
        clinic_data = parse_clinic_page(url)
        if clinic_data:
            results.append(clinic_data)
        else:
            # fallback: place an empty row with URL as name
            results.append({
                "Name of Clinic": url,
                "Address": "",
                "Email": "",
                "Phone": "",
                "Services": ""
            })

    # Write CSV
    fieldnames = ["Name of Clinic", "Address", "Email", "Phone", "Services"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Done. Wrote {len(results)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
