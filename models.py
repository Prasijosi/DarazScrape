from pydantic import BaseModel
from typing import List, Optional


class ProductModel(BaseModel):
    title: str
    price: str
    original_price: Optional[str] = None
    discount: Optional[str] = None
    rating: str
    reviews: str
    image_url: str
    product_url: str
    category: str
    page: int


class ScrapeRequest(BaseModel):
    category: str
    start_page: int = 1
    end_page: int = 1
    use_selenium: bool = True


class ScrapeResponse(BaseModel):
    status: str
    count: int
    products: List[ProductModel]
    message: Optional[str] = None 