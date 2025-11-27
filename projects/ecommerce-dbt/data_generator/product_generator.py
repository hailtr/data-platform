"""
Generate synthetic product catalog
"""
import random
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Product:
    """Product for data generation"""
    product_id: str
    category: str
    price: float
    supplier: str


class ProductGenerator:
    """Generate synthetic product catalog"""
    
    SUPPLIERS = [
        "TechCorp", "FashionHub", "HomeGoods", "SportsPro",
        "BookWorld", "ToyLand", "BeautyPlus", "FoodMart"
    ]
    
    # Price ranges by category (min, max)
    PRICE_RANGES = {
        "Electronics": (50.0, 2000.0),
        "Clothing": (10.0, 500.0),
        "Home & Garden": (20.0, 800.0),
        "Sports": (15.0, 600.0),
        "Books": (5.0, 50.0),
        "Toys": (10.0, 200.0),
        "Beauty": (8.0, 150.0),
        "Food": (3.0, 100.0)
    }
    
    def __init__(self, total_products: int = 500, categories: List[str] = None):
        self.total_products = total_products
        self.categories = categories or [
            "Electronics", "Clothing", "Home & Garden",
            "Sports", "Books", "Toys", "Beauty", "Food"
        ]
        self.products: List[Product] = []
        self._generate_products()
    
    def _generate_products(self):
        """Generate product catalog"""
        # Distribute products across categories
        products_per_category = self.total_products // len(self.categories)
        
        product_id = 1
        for category in self.categories:
            for _ in range(products_per_category):
                price_min, price_max = self.PRICE_RANGES.get(
                    category,
                    (10.0, 500.0)  # Default range
                )
                
                # Price distribution (more lower-priced items)
                price = round(
                    random.triangular(price_min, price_max, price_min * 1.5),
                    2
                )
                
                supplier = random.choice(self.SUPPLIERS)
                
                self.products.append(Product(
                    product_id=f"prod_{product_id:06d}",
                    category=category,
                    price=price,
                    supplier=supplier
                ))
                product_id += 1
    
    def get_random_product(self) -> Product:
        """Get a random product"""
        return random.choice(self.products)
    
    def get_popular_products(self, count: int) -> List[Product]:
        """Get popular products (weighted - some products are more popular)"""
        # Create popularity weights (Pareto distribution - few products are very popular)
        weights = [random.paretovariate(1.5) for _ in self.products]
        return random.choices(self.products, weights=weights, k=count)
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get all products in a category"""
        return [p for p in self.products if p.category == category]

