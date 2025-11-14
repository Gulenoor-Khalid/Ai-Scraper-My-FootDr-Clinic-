import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://web.archive.org/web/20250708180027/https://www.myfootdr.com.au/our-clinics/"


def get_soup(url):
    res = requests.get(url, timeout=15)
    res.raise_for_status()
    return BeautifulSoup(res.text, "lxml")


def extract_clinic_links():
    """Extract all clinic page links from all regions."""
    soup = get_soup(BASE_URL)

    clinic_links = []
    region_links = soup.select(".card a")

    for tag in region_links:
        region_url = tag.get("href")
        if not region_url:
            continue

        full_region_url = "https://web.archive.org" + region_url
        region_soup = get_soup(full_region_url)

        clinic_tags = region_soup.select(".card a")
        for c in clinic_tags:
            href = c.get("href")
            if href:
                clinic_links.append("https://web.archive.org" + href)

    return list(set(clinic_links))  # Remove duplicates


def parse_clinic_page(url):
    """Extract required details from a clinic page."""
    soup = get_soup(url)

    name = soup.select_one("h1")
    name = name.get_text(strip=True) if name else ""

    address = soup.select_one(".clinic-info__address")
    address = address.get_text(" ", strip=True) if address else ""

    phone = soup.select_one("a[href^='tel:']")
    phone = phone.get_text(strip=True) if phone else ""

    email = soup.select_one("a[href^='mailto:']")
    email = email.get_text(strip=True) if email else ""

    services_list = soup.select(".services-list li")
    services = ", ".join(li.get_text(strip=True) for li in services_list)

    return {
        "Name of Clinic": name,
        "Address": address,
        "Email": email,
        "Phone": phone,
        "Services": services,
    }


def scrape_clinics():
    """Returns the list of all scraped clinic dictionaries."""
    clinics = extract_clinic_links()
    print(f"Found {len(clinics)} unique clinics… scraping now.\n")

    results = []

    for url in tqdm(clinics):
        try:
            results.append(parse_clinic_page(url))
        except Exception as e:
            print("Error parsing:", url, e)

    return results

