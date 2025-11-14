My FootDr Clinic AI Scraper

Scrapes the archived My FootDr clinic directory from the Wayback Machine and exports a structured CSV file containing clinic details.

This project automatically collects:

Name of Clinic

Address

Email

Phone

Services

from every clinic page listed under:

📌 Archived URL:
https://web.archive.org/web/20250708180027/https://www.myfootdr.com.au/our-clinics/

📌 Features

Fully automated scraping of all regions and clinics

Extracts and cleans clinic information

Writes all results into clinics_myfootdr.csv

Graceful error handling & rate-limiting

Uses lightweight stack: requests + BeautifulSoup

📂 Project Structure
├── myfootdr_scraper.py      # Main scraping script
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation

🚀 Getting Started
1. Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2. Install dependencies
pip install -r requirements.txt

3. Run the scraper
python myfootdr_scraper.py


After running, you will find:

clinics_myfootdr.csv


in the project directory.

📝 Output Format

The generated CSV file contains the following columns:

Column Name	Description
Name of Clinic	The official clinic name
Address	Full physical address
Email	Clinic email address (if available)
Phone	Contact phone number
Services	List of services offered
⚠️ Notes & Limitations

Data is scraped from a Wayback Machine snapshot, so some pages may be incomplete.

Certain clinics may not have email or services listed.

Fallback logic handles missing structure, but results may vary.

🛠️ Technologies Used

Python 3

Requests

BeautifulSoup4

🤝 Contributing

Pull requests are welcome!
If you’d like to improve parsing, add validations, or contribute enhancements, feel free to open an issue.

📄 License

This project is licensed under the MIT License