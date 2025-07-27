import pandas as pd
import sys
from scraper_core import DarazScraper


def run_cli():
    """CLI mode for direct usage"""
    scraper = DarazScraper(use_selenium=True)
    
    try:
        print("Daraz Nepal Product Scraper (CLI Mode)")
        print("=" * 40)
        
        category = input("Enter category (e.g., mobile-cases-covers): ").strip()
        start_page = int(input("Enter start page (default 1): ") or "1")
        end_page = int(input("Enter end page (default 1): ") or "1")
        
        print(f"\nScraping {category} from page {start_page} to {end_page}...")
        products = scraper.scrape_category(category, start_page, end_page)
        
        if products:
            df = pd.DataFrame(products)
            csv_file = f"daraz_{category}_p{start_page}-{end_page}.csv"
            df.to_csv(csv_file, index=False)
            
            print(f"\n✅ Successfully scraped {len(products)} products!")
            print(f"📁 Saved to: {csv_file}")
            print("\n📊 Sample products:")
            print(df[['title', 'price', 'rating']].head(3).to_string(index=False))
        else:
            print("❌ No products were scraped.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        scraper.close_driver()


if __name__ == "__main__":
    run_cli() 