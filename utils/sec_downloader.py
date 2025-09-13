# utils/sec_downloader.py
import os
import requests
from bs4 import BeautifulSoup
import time

BASE = 'https://www.sec.gov'
HEADERS = {
    'User-Agent': 'UniqusRecruitmentBot - email@example.com'
}


def find_10k_urls_for_cik(cik):
    # returns list of filing page URLs; we will look for 10-K HTML or PDF links
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={cik}&type=10-K&count=100&owner=exclude"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = []
    for a in soup.select('a'):
        href = a.get('href','')
        if 'Archives/edgar/data' in href and href.endswith('.htm'):
            links.append(BASE + href if href.startswith('/') else href)
    return links


def download_10k_filings_for_companies(companies, years, out_dir='data'):
    os.makedirs(out_dir, exist_ok=True)
    for ticker, cik in companies.items():
        for year in years:
            # naive approach: browse filing page list and pick filings where year in filing name
            print('Searching', ticker, 'CIK', cik, 'year', year)
            urls = find_10k_urls_for_cik(cik)
            saved = False
            for filing_page in urls:
                try:
                    r = requests.get(filing_page, headers=HEADERS)
                    soup = BeautifulSoup(r.text, 'html.parser')
                    # find document table
                    rows = soup.select('table.tableFile a')
                    for a in rows:
                        href = a.get('href')
                        if not href:
                            continue
                        if any(ext in href for ext in ['.pdf', '.htm']):
                            # try to filter by year in the surrounding text
                            if str(year) in filing_page or str(year) in a.text:
                                file_url = BASE + href if href.startswith('/') else href
                                out_path = os.path.join(out_dir, ticker, str(year))
                                os.makedirs(out_path, exist_ok=True)
                                fname = file_url.split('/')[-1]
                                full = os.path.join(out_path, fname)
                                if os.path.exists(full):
                                    print('Already downloaded', full)
                                    saved = True
                                    break
                                print('Downloading', file_url)
                                rr = requests.get(file_url, headers=HEADERS)
                                with open(full, 'wb') as f:
                                    f.write(rr.content)
                                saved = True
                                time.sleep(0.5)
                                break
                    if saved:
                        break
                except Exception as e:
                    print('Error fetching filing page', filing_page, e)
            if not saved:
                print('Could not automatically find 10-K for', ticker, year, ' — consider manual download')
