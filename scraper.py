import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
from typing import List, Dict, Optional
import time


class EvvAzScraper:
    def __init__(self):
        self.base_url = "https://www.evv.az"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'DNT': '1'
        }
        self.listings = []
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

    async def fetch(self, session: aiohttp.ClientSession, url: str, method: str = 'GET', **kwargs) -> str:
        """Fetch a URL with rate limiting"""
        async with self.semaphore:
            try:
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.text()
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                return ""

    async def get_listing_urls(self, session: aiohttp.ClientSession, page_offset: int, page_num: int) -> List[str]:
        """Extract listing URLs from a page"""
        if page_offset == 0:
            url = f"{self.base_url}/dasinmaz-emlak-elanlari"
        else:
            url = f"{self.base_url}/dasinmaz-emlak-elanlari?page={page_offset}"

        print(f"[Page {page_num}] Fetching: {url}")

        html = await self.fetch(session, url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')

        # Find all listing cards
        listing_links = []
        listings_container = soup.find('div', class_='row g-lg-4 g-md-3 g-sm-3 g-3')

        if listings_container:
            # Find all anchor tags with class "img_link"
            for link in listings_container.find_all('a', class_='img_link'):
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    listing_links.append(full_url)

        print(f"[Page {page_num}] Found {len(listing_links)} listings")
        return listing_links

    async def get_phone_number(self, session: aiohttp.ClientSession, listing_id: str) -> str:
        """Get phone number using API"""
        url = f"{self.base_url}/evvaz/get_phone"

        headers = {
            **self.headers,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': '*/*',
            'Origin': self.base_url,
            'Referer': f"{self.base_url}/",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

        data = {'id': listing_id}

        try:
            html = await self.fetch(session, url, method='POST', headers=headers, data=data)
            if not html:
                return "N/A"

            # Parse the phone number from response
            soup = BeautifulSoup(html, 'html.parser')
            phone_tag = soup.find('img', class_='phone_icon')
            if phone_tag and phone_tag.parent:
                phone_text = phone_tag.parent.get_text(strip=True)
                return phone_text

            return "N/A"
        except Exception as e:
            print(f"Error fetching phone for listing {listing_id}: {str(e)}")
            return "N/A"

    async def scrape_listing_details(self, session: aiohttp.ClientSession, url: str, idx: int, total: int) -> Optional[Dict]:
        """Scrape details from a single listing page"""
        print(f"[{idx}/{total}] Scraping: {url}")

        html = await self.fetch(session, url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        details = {
            'url': url,
            'listing_id': '',
            'title': '',
            'price': '',
            'property_type': '',
            'city': '',
            'document': '',
            'floor': '',
            'area': '',
            'rooms': '',
            'mortgage': '',
            'furnished': '',
            'description': '',
            'location': '',
            'seller_name': '',
            'seller_type': '',
            'phone': '',
            'views': '',
            'post_date': '',
            'update_date': '',
            'land_area': ''
        }

        # Extract listing ID from URL or page
        listing_id_elem = soup.find('span', class_='estate_id')
        if listing_id_elem:
            details['listing_id'] = listing_id_elem.get_text(strip=True)
        else:
            # Try to extract from URL
            url_parts = url.rstrip('/').split('-')
            if url_parts:
                details['listing_id'] = url_parts[-1]

        # Get phone number using API
        if details['listing_id']:
            await asyncio.sleep(0.3)  # Be polite to the server
            details['phone'] = await self.get_phone_number(session, details['listing_id'])

        # Extract title from breadcrumb or page
        title_elem = soup.find('h1')
        if title_elem:
            details['title'] = title_elem.get_text(strip=True)

        # Extract price
        price_elem = soup.find('div', class_='price_val')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            details['price'] = price_text.replace('₼', '').strip()

        # Extract seller information
        seller_name_elem = soup.find('h5', class_='card-title')
        if seller_name_elem:
            details['seller_name'] = seller_name_elem.get_text(strip=True)

        seller_type_elem = soup.find('p', class_='text-muted')
        if seller_type_elem:
            details['seller_type'] = seller_type_elem.get_text(strip=True)

        # Extract all options from the details section
        options = soup.find_all('div', class_='options')
        for option in options:
            label_elem = option.find('span', class_='float-start')
            value_elem = option.find('span', class_='float-end')

            if label_elem and value_elem:
                label = label_elem.get_text(strip=True)
                value = value_elem.get_text(strip=True)

                if 'Mülkün növü' in label:
                    details['property_type'] = value
                elif 'Şəhər' in label:
                    details['city'] = value
                elif 'Sənədi' in label:
                    details['document'] = value
                elif 'Mərtəbə' in label:
                    details['floor'] = value
                elif 'Sahəsi' in label:
                    details['area'] = value
                elif 'Otaq sayı' in label:
                    details['rooms'] = value
                elif 'İpoteka' in label:
                    details['mortgage'] = value
                elif 'Əşyası' in label:
                    details['furnished'] = value
                elif 'Torpaq sahəsi' in label:
                    details['land_area'] = value

        # Extract description
        description_elem = soup.find('blockquote')
        if description_elem:
            details['description'] = description_elem.get_text(strip=True)

        # Extract location
        location_card = soup.find('div', class_='card-body')
        if location_card:
            location_text = location_card.get_text(strip=True)
            if 'Gəncə' in location_text or 'Bakı' in location_text or 'ş.' in location_text or 'qəs.' in location_text:
                details['location'] = location_text

        # Extract views, post date, update date
        prop_tools = soup.find_all('ul', class_='prop_tools')
        for tool_list in prop_tools:
            list_items = tool_list.find_all('li')
            for item in list_items:
                text = item.get_text(strip=True)

                if 'Baxışların sayı:' in text:
                    details['views'] = text.split(':')[-1].strip()
                elif 'Elanın tarixi:' in text:
                    details['post_date'] = text.split(':')[-1].strip()
                elif 'Yenilənmə tarixi' in text:
                    time_elem = item.find('time')
                    if time_elem:
                        details['update_date'] = time_elem.get_text(strip=True)

        return details

    async def detect_total_pages(self, session: aiohttp.ClientSession) -> int:
        """Detect total number of pages by checking pagination"""
        url = f"{self.base_url}/dasinmaz-emlak-elanlari"
        html = await self.fetch(session, url)

        if not html:
            return 1

        soup = BeautifulSoup(html, 'html.parser')

        # Look for pagination links
        pagination = soup.find('ul', class_='pagination')
        if not pagination:
            return 1

        # Find all page links
        page_links = pagination.find_all('a')
        max_page_offset = 0

        for link in page_links:
            href = link.get('href', '')
            if 'page=' in href:
                try:
                    # Extract the page offset (e.g., 24, 48, 72...)
                    page_offset = int(href.split('page=')[1].split('&')[0])
                    max_page_offset = max(max_page_offset, page_offset)
                except:
                    pass

        # Total pages = (max_offset / 24) + 1
        # e.g., if max_offset = 16560, then total_pages = 16560/24 + 1 = 691
        total_pages = (max_page_offset // 24) + 1 if max_page_offset > 0 else 1

        print(f"Max page offset detected: {max_page_offset}")
        print(f"Calculated total pages: {total_pages}")

        return total_pages

    async def scrape_pages(self, num_pages: int = None, scrape_all: bool = False):
        """Scrape multiple pages

        Args:
            num_pages: Number of pages to scrape (if None and scrape_all=True, scrapes all)
            scrape_all: If True, scrapes all available pages
        """
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        ) as session:
            # Determine how many pages to scrape
            if scrape_all or num_pages is None:
                print("Detecting total number of pages...")
                total_pages = await self.detect_total_pages(session)
                print(f"Total pages detected: {total_pages}\n")
                num_pages = total_pages

            print(f"Starting to scrape {num_pages} page(s)...\n")

            # First, collect all listing URLs from all pages
            page_tasks = []
            for i in range(num_pages):
                page_offset = i * 24
                page_tasks.append(self.get_listing_urls(session, page_offset, i + 1))

            # Wait for all page fetches to complete
            all_listing_urls_nested = await asyncio.gather(*page_tasks)

            # Flatten the list of lists
            all_listing_urls = [url for sublist in all_listing_urls_nested for url in sublist]

            print(f"\n{'='*60}")
            print(f"Total listings found: {len(all_listing_urls)}")
            print(f"{'='*60}\n")

            # Now scrape each listing
            detail_tasks = []
            for idx, url in enumerate(all_listing_urls, 1):
                detail_tasks.append(
                    self.scrape_listing_details(session, url, idx, len(all_listing_urls))
                )

            # Wait for all detail scrapes to complete
            all_details = await asyncio.gather(*detail_tasks)

            # Filter out None values
            self.listings = [d for d in all_details if d is not None]

        return self.listings

    def save_to_csv(self, filename: str = 'output/evv_az_listings.csv'):
        """Save scraped data to CSV"""
        if not self.listings:
            print("No listings to save!")
            return

        # Create output directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        fieldnames = [
            'listing_id', 'url', 'title', 'price', 'property_type', 'city',
            'location', 'document', 'floor', 'area', 'land_area', 'rooms',
            'mortgage', 'furnished', 'description', 'seller_name', 'seller_type',
            'phone', 'views', 'post_date', 'update_date'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.listings)

        print(f"\nSaved {len(self.listings)} listings to {filename}")


async def main():
    import os
    scraper = EvvAzScraper()

    # Check environment variable for scraping mode
    scrape_all = os.getenv('SCRAPE_ALL', 'true').lower() == 'true'
    num_pages = os.getenv('NUM_PAGES')

    if num_pages:
        # If NUM_PAGES is specified, use it
        await scraper.scrape_pages(num_pages=int(num_pages))
    elif scrape_all:
        # Otherwise scrape all pages
        await scraper.scrape_pages(scrape_all=True)
    else:
        # Default to 3 pages
        await scraper.scrape_pages(num_pages=3)

    # Save to CSV
    scraper.save_to_csv()


if __name__ == "__main__":
    asyncio.run(main())
