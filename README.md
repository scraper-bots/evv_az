# EVV.AZ Real Estate Scraper

Asynchronous web scraper for evv.az real estate listings with Docker support.

## Features

- ✅ Async scraping using `aiohttp` and `asyncio`
- ✅ Pagination support (configurable number of pages)
- ✅ Phone number extraction via API
- ✅ CSV export
- ✅ Docker containerization
- ✅ Rate limiting and polite scraping

## Quick Start

### Using Docker (Recommended)

1. Build and run:
```bash
docker-compose up --build
```

2. Find output in `./output/evv_az_listings.csv`

### Using Docker without docker-compose

1. Build the image:
```bash
docker build -t evv-scraper .
```

2. Run the container:
```bash
docker run -v $(pwd)/output:/app/output evv-scraper
```

### Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the scraper:
```bash
python scraper.py
```

## Configuration

### Environment Variables

- `SCRAPE_ALL=true` - Scrape all available pages (default)
- `NUM_PAGES=10` - Scrape specific number of pages

### Docker Configuration

Edit `docker-compose.yml`:

```yaml
environment:
  - SCRAPE_ALL=true  # Scrape all pages
  # - NUM_PAGES=5    # Or scrape 5 pages
```

### Local Configuration

```bash
# Scrape all pages (default)
python scraper.py

# Scrape specific number of pages
NUM_PAGES=5 python scraper.py

# Scrape only 3 pages
SCRAPE_ALL=false NUM_PAGES=3 python scraper.py
```

## Output Fields

The CSV contains the following fields:

- `listing_id` - Unique listing identifier
- `url` - Listing page URL
- `title` - Property title
- `price` - Price in AZN
- `property_type` - Type (Köhnə tikili, Yeni tikili, etc.)
- `city` - City/location
- `location` - Detailed location
- `document` - Document type (Kupça, etc.)
- `floor` - Floor number/total floors
- `area` - Area in m²
- `land_area` - Land area in sot (if applicable)
- `rooms` - Number of rooms
- `mortgage` - Mortgage availability
- `furnished` - Furnishing status
- `description` - Property description
- `seller_name` - Seller name
- `seller_type` - Seller type (Sahibindən, Vasitəçi)
- `phone` - Contact phone number
- `views` - Number of views
- `post_date` - Original post date
- `update_date` - Last update date

## Notes

- The scraper implements rate limiting to be respectful to the server
- Pages are numbered with 24 listings each (page 0, 24, 48, ...)
- Phone numbers are fetched via separate API calls
- Output is saved in UTF-8 encoding for proper character support

## License

MIT
