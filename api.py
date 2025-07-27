import time
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from scraper_core import DarazScraper
from models import ScrapeRequest, ScrapeResponse, ProductModel


# Initialize FastAPI app
app = FastAPI(
    title="Daraz Nepal Product Scraper API",
    description="API for scraping product data from Daraz Nepal",
    version="2.0.0"
)

# Global scraper instance
scraper_instance = None


@app.on_event("startup")
async def startup_event():
    """Initialize scraper on startup"""
    global scraper_instance
    scraper_instance = DarazScraper(use_selenium=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global scraper_instance
    if scraper_instance:
        scraper_instance.close_driver()


@app.get("/")
async def root():
    return {
        "message": "Daraz Nepal Product Scraper API",
        "version": "2.0.0",
        "endpoints": {
            "scrape": "/scrape",
            "categories": "/categories"
        }
    }


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_products(request: ScrapeRequest):
    """Scrape products from a category"""
    global scraper_instance
    
    try:
        if not scraper_instance:
            scraper_instance = DarazScraper(use_selenium=request.use_selenium)
        
        print(f"Starting scrape for category: {request.category}")
        products = scraper_instance.scrape_category(
            request.category, 
            request.start_page, 
            request.end_page
        )
        
        # Convert to Pydantic models
        product_models = []
        for product in products:
            try:
                product_models.append(ProductModel(**product))
            except Exception as e:
                print(f"Error creating product model: {e}")
                continue
        
        return ScrapeResponse(
            status="success",
            count=len(product_models),
            products=product_models,
            message=f"Successfully scraped {len(product_models)} products"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.get("/scrape")
async def scrape_products_get(
    category: str = Query(..., description="Category to scrape (e.g., mobile-cases-covers)"),
    start_page: int = Query(1, description="Start page number"),
    end_page: int = Query(1, description="End page number"),
    use_selenium: bool = Query(True, description="Use Selenium for dynamic content"),
    format: str = Query("json", description="Response format: json or csv")
):
    """GET endpoint for scraping products"""
    global scraper_instance
    
    try:
        if not scraper_instance:
            scraper_instance = DarazScraper(use_selenium=use_selenium)
        
        products = scraper_instance.scrape_category(category, start_page, end_page)
        
        if format.lower() == "csv":
            # Return CSV data
            df = pd.DataFrame(products)
            csv_content = df.to_csv(index=False)
            return {"csv_data": csv_content, "count": len(products)}
        
        return {
            "status": "success",
            "count": len(products),
            "products": products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories")
async def get_popular_categories():
    """Get list of popular categories"""
    return {
        "categories": [
            "mobile-cases-covers",
            "smartphones",
            "laptops",
            "fashion-womens",
            "fashion-mens",
            "electronics",
            "home-garden",
            "sports-outdoor",
            "health-beauty",
            "baby-toys"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global scraper_instance
    return {
        "status": "healthy",
        "selenium_available": scraper_instance and scraper_instance.use_selenium,
        "timestamp": time.time()
    }


def run_api_server():
    """Run the FastAPI server"""
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run_api_server() 