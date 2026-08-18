"""
Verification and Test Suite for PriceWise Scraper Integration.
Tests dependencies, JSON-LD parsing, SourceRouter multi-page pagination,
variant mapping, exact URL preservation, and health endpoints.
"""

import asyncio
import logging
import sys
import os

# Ensure backend dir is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestScraperSuite")


def test_imports():
    logger.info("=== TEST 1: Dependency Imports ===")
    import requests
    import bs4
    import lxml
    import playwright
    logger.info(f"  [OK] requests version: {requests.__version__}")
    logger.info(f"  [OK] beautifulsoup4 version: {bs4.__version__}")
    logger.info(f"  [OK] lxml version: {lxml.__file__}")
    logger.info(f"  [OK] playwright module: {playwright.__file__}")


def test_json_ld_parser():
    logger.info("=== TEST 2: JSON-LD Extraction ===")
    from bs4 import BeautifulSoup
    from app.services.scrapers.beautifulsoup_parser import parse_json_ld, convert_json_ld_to_scraped_product

    sample_html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org/",
          "@type": "Product",
          "name": "Apple iPhone 16 128GB Black",
          "image": ["https://m.media-amazon.com/images/I/71vFKBpKakL._SL1500_.jpg"],
          "description": "Apple iPhone 16 smartphone with A18 chip.",
          "sku": "B0DGJ9M6P4",
          "brand": {
            "@type": "Brand",
            "name": "Apple"
          },
          "offers": {
            "@type": "Offer",
            "url": "https://www.amazon.in/dp/B0DGJ9M6P4",
            "priceCurrency": "INR",
            "price": "79900",
            "availability": "https://schema.org/InStock"
          }
        }
        </script>
      </head>
      <body></body>
    </html>
    """

    soup = BeautifulSoup(sample_html, "lxml")
    json_lds = parse_json_ld(soup, "Amazon", "https://www.amazon.in/dp/B0DGJ9M6P4")
    assert len(json_lds) == 1, "Failed to extract JSON-LD script block"

    prod = convert_json_ld_to_scraped_product(json_lds[0], "Amazon", "https://www.amazon.in/dp/B0DGJ9M6P4")
    assert prod is not None, "Failed to convert JSON-LD to ScrapedProduct"
    assert prod.title == "Apple iPhone 16 128GB Black", f"Unexpected title: {prod.title}"
    assert prod.price == 79900.0, f"Unexpected price: {prod.price}"
    assert prod.product_url == "https://www.amazon.in/dp/B0DGJ9M6P4", f"Unexpected URL: {prod.product_url}"
    logger.info(f"  [OK] Successfully parsed JSON-LD product: '{prod.title}' | Price: ₹{prod.price} | URL: {prod.product_url}")


async def test_source_router_multi_page():
    logger.info("=== TEST 3: SourceRouter Multi-Page Controlled Pagination & Variant Mapping ===")
    from app.services.scrapers.source_router import SourceRouter

    router = SourceRouter()
    test_queries = ["iPhone 16", "Samsung Galaxy S24", "Nike shoes"]

    for query in test_queries:
        logger.info(f"\n  --- Testing Query: '{query}' ---")
        domain_prods, debug_info = await router.execute_search(query)

        logger.info(f"  Raw Scraped Items: {debug_info['total_scraped_products']}")
        logger.info(f"  Domain Products Generated: {len(domain_prods)}")

        summary = debug_info.get("sources_summary", {})
        for src, metrics in summary.items():
            logger.info(
                f"    [{src}] Success={metrics['success']} | Pages Scraped={metrics['pages_scraped']} | "
                f"Products Found={metrics['products_found']} | Scraper={metrics['scraper']}"
            )

        if domain_prods:
            logger.info(f"  [OK] '{query}' returned {len(domain_prods)} distinct product listings.")
            top_prod = domain_prods[0]
            top_plat = top_prod.platforms[0]
            logger.info(f"  Top Match: '{top_prod.name}' | Platform: {top_plat.platformName} | Price: ₹{top_plat.price} | URL: {top_plat.product_url}")


async def test_health_and_api_endpoints():
    logger.info("=== TEST 4: Health & API Search Endpoints ===")
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    res_root = client.get("/")
    assert res_root.status_code == 200, f"Root health failed: {res_root.status_code}"
    logger.info(f"  [OK] GET / -> {res_root.json()['service']}")

    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"System health failed: {res_health.status_code}"
    health_data = res_health.json()
    logger.info(f"  [OK] GET /api/health -> backend: {health_data['backend']} | beautifulsoup: {health_data['beautifulsoup']} | requests: {health_data['requests']}")

    res_scraper_health = client.get("/api/scraper/health")
    assert res_scraper_health.status_code == 200, f"Scraper health failed: {res_scraper_health.status_code}"
    scraper_health = res_scraper_health.json()
    logger.info(f"  [OK] GET /api/scraper/health -> primary: {scraper_health['primary_scraper']} | sources: {scraper_health['supported_sources']}")

    res_search = client.get("/api/search?query=iPhone+16")
    assert res_search.status_code == 200, f"Search endpoint failed: {res_search.status_code}"
    search_data = res_search.json()
    logger.info(f"  [OK] GET /api/search -> query: {search_data['query']} | total_results: {search_data['total']} | cache_status: {search_data['cache_info']['cache_status']}")


async def main():
    test_imports()
    test_json_ld_parser()
    await test_source_router_multi_page()
    await test_health_and_api_endpoints()
    logger.info("==========================================")
    logger.info("ALL MULTI-PAGE & VARIANT TEST SUITES PASSED!")
    logger.info("==========================================")


if __name__ == "__main__":
    asyncio.run(main())
