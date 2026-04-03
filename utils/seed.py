"""
Seed the database with sample products matching the ShopHub UI.
Run only once on first startup (checks if products exist already).
"""
from database import db
from models import Product
import logging

logger = logging.getLogger(__name__)

SEED_PRODUCTS = [
    # ── Clothing ──────────────────────────────────────────────────────────────
    {
        "name": "Pleated Midi Skirt", "brand": "ZARA", "category": "Clothing",
        "sub_category": "Skirts", "price": 4856, "original_price": 6474,
        "discount_pct": 25, "rating": 4.5, "review_count": 88,
        "image_url": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=400",
        "description": "Elegant pleated midi skirt perfect for any occasion.",
        "tags": "skirt,elegant,midi,women",
        "stock": 60, "emotion_tags": "happy,neutral,colorful",
    },
    {
        "name": "Slim Fit Chinos", "brand": "H&M", "category": "Clothing",
        "sub_category": "Trousers", "price": 3951, "original_price": 5644,
        "discount_pct": 30, "rating": 4.3, "review_count": 243,
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400",
        "description": "Classic slim fit chinos in premium stretch cotton.",
        "tags": "chinos,men,casual,trousers",
        "stock": 120, "emotion_tags": "neutral,classic,timeless",
    },
    {
        "name": "Tailored Linen Blazer", "brand": "GUCCI", "category": "Clothing",
        "sub_category": "Blazers", "price": 13944, "original_price": 17430,
        "discount_pct": 20, "rating": 4.6, "review_count": 67,
        "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
        "description": "Premium tailored linen blazer for a sophisticated look.",
        "tags": "blazer,formal,linen,premium",
        "stock": 35, "emotion_tags": "happy,neutral,statement,trending",
    },
    {
        "name": "Oversized Cotton Hoodie", "brand": "H&M", "category": "Clothing",
        "sub_category": "Hoodies", "price": 2199, "original_price": 3499,
        "discount_pct": 37, "rating": 4.7, "review_count": 512,
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f15732f2?w=400",
        "description": "Super soft oversized hoodie for maximum comfort.",
        "tags": "hoodie,oversized,comfy,casual",
        "stock": 200, "emotion_tags": "sad,cozy,comfort,warm,soft",
    },
    {
        "name": "Floral Summer Dress", "brand": "ZARA", "category": "Clothing",
        "sub_category": "Dresses", "price": 3499, "original_price": 4999,
        "discount_pct": 30, "rating": 4.8, "review_count": 395,
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400",
        "description": "Vibrant floral summer dress for sunny days.",
        "tags": "dress,floral,summer,women,vibrant",
        "stock": 80, "emotion_tags": "happy,colorful,vibrant,summer,party",
    },
    {
        "name": "Bomber Jacket", "brand": "GUCCI", "category": "Clothing",
        "sub_category": "Jackets", "price": 8490, "original_price": 10612,
        "discount_pct": 20, "rating": 4.4, "review_count": 178,
        "image_url": "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=400",
        "description": "Street-style bomber jacket with premium finish.",
        "tags": "jacket,bomber,streetwear,unisex",
        "stock": 45, "emotion_tags": "angry,bold,sport,statement,trending",
    },
    {
        "name": "Classic White Shirt", "brand": "H&M", "category": "Clothing",
        "sub_category": "Shirts", "price": 1799, "original_price": 2499,
        "discount_pct": 28, "rating": 4.5, "review_count": 623,
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400",
        "description": "Timeless crisp white shirt for every wardrobe.",
        "tags": "shirt,white,classic,formal,men",
        "stock": 150, "emotion_tags": "neutral,classic,minimal,simple,clean,timeless",
    },
    {
        "name": "Tie-Dye Graphic Tee", "brand": "NIKE", "category": "Clothing",
        "sub_category": "T-Shirts", "price": 1299, "original_price": 1999,
        "discount_pct": 35, "rating": 4.2, "review_count": 289,
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400",
        "description": "Bold tie-dye graphic tee for a colourful vibe.",
        "tags": "tshirt,tiedye,casual,colorful,unisex",
        "stock": 90, "emotion_tags": "happy,colorful,vibrant,surprise,unique",
    },

    # ── Footwear ───────────────────────────────────────────────────────────────
    {
        "name": "Pro Running Shoes", "brand": "NIKE", "category": "Footwear",
        "sub_category": "Sneakers", "price": 10624, "original_price": 13280,
        "discount_pct": 20, "rating": 4.9, "review_count": 445,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "description": "High-performance running shoes with responsive cushioning.",
        "tags": "running,sport,shoes,performance",
        "stock": 70, "emotion_tags": "angry,sport,activewear,running,training,bold",
    },
    {
        "name": "Platform Sandals", "brand": "ZARA", "category": "Footwear",
        "sub_category": "Sandals", "price": 4046, "original_price": 6225,
        "discount_pct": 35, "rating": 4.4, "review_count": 189,
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400",
        "description": "Trendy platform sandals with comfortable sole.",
        "tags": "sandals,platform,women,summer",
        "stock": 55, "emotion_tags": "happy,summer,vibrant,party",
    },
    {
        "name": "Espadrille Flats", "brand": "ZARA", "category": "Footwear",
        "sub_category": "Flats", "price": 4316, "original_price": 5395,
        "discount_pct": 20, "rating": 4.3, "review_count": 98,
        "image_url": "https://images.unsplash.com/photo-1518894781321-630e638d0742?w=400",
        "description": "Lightweight espadrille flats perfect for summer walks.",
        "tags": "espadrille,flats,women,casual,summer",
        "stock": 65, "emotion_tags": "neutral,casual,comfortable,basics",
    },
    {
        "name": "Leather Chelsea Boots", "brand": "H&M", "category": "Footwear",
        "sub_category": "Boots", "price": 6799, "original_price": 9999,
        "discount_pct": 32, "rating": 4.6, "review_count": 341,
        "image_url": "https://images.unsplash.com/photo-1542014740373-51ad6425a7b6?w=400",
        "description": "Premium leather Chelsea boots that go with everything.",
        "tags": "boots,chelsea,leather,premium,men",
        "stock": 40, "emotion_tags": "neutral,classic,timeless,minimal",
    },
    {
        "name": "High-Top Canvas Sneakers", "brand": "NIKE", "category": "Footwear",
        "sub_category": "Sneakers", "price": 3299, "original_price": 4999,
        "discount_pct": 34, "rating": 4.5, "review_count": 512,
        "image_url": "https://images.unsplash.com/photo-1463100099107-aa0980c362e6?w=400",
        "description": "Classic high-top canvas sneakers, a streetwear staple.",
        "tags": "sneakers,hightop,canvas,streetwear,unisex",
        "stock": 85, "emotion_tags": "happy,casual,trending,new",
    },

    # ── Accessories ────────────────────────────────────────────────────────────
    {
        "name": "Smart Fitness Band", "brand": "NIKE", "category": "Accessories",
        "sub_category": "Wearables", "price": 5752, "original_price": 8217,
        "discount_pct": 30, "rating": 4.2, "review_count": 378,
        "image_url": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400",
        "description": "Track your fitness journey with smart health monitoring.",
        "tags": "fitness,smartband,wearable,sport,tech",
        "stock": 95, "emotion_tags": "angry,sport,training,activewear",
    },
    {
        "name": "Canvas Tote Bag", "brand": "H&M", "category": "Accessories",
        "sub_category": "Bags", "price": 3424, "original_price": 4565,
        "discount_pct": 25, "rating": 4.4, "review_count": 267,
        "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?w=400",
        "description": "Spacious canvas tote bag for everyday use.",
        "tags": "tote,bag,canvas,casual,sustainable",
        "stock": 110, "emotion_tags": "neutral,casual,basics,essentials",
    },
    {
        "name": "Vintage Sunglasses", "brand": "GUCCI", "category": "Accessories",
        "sub_category": "Eyewear", "price": 7899, "original_price": 9999,
        "discount_pct": 21, "rating": 4.7, "review_count": 203,
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400",
        "description": "Vintage-inspired sunglasses with UV400 protection.",
        "tags": "sunglasses,vintage,summer,UV,unisex",
        "stock": 50, "emotion_tags": "happy,summer,vibrant,party,statement",
    },
    {
        "name": "Minimalist Watch", "brand": "ZARA", "category": "Accessories",
        "sub_category": "Watches", "price": 6499, "original_price": 9999,
        "discount_pct": 35, "rating": 4.8, "review_count": 456,
        "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400",
        "description": "Sleek minimalist watch with premium quartz movement.",
        "tags": "watch,minimalist,premium,unisex",
        "stock": 60, "emotion_tags": "neutral,minimal,clean,timeless,classic",
    },
    {
        "name": "Chunky Chain Necklace", "brand": "H&M", "category": "Accessories",
        "sub_category": "Jewellery", "price": 1299, "original_price": 1999,
        "discount_pct": 35, "rating": 4.3, "review_count": 178,
        "image_url": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=400",
        "description": "Statement chunky chain necklace to complete any look.",
        "tags": "necklace,chain,jewellery,statement,women",
        "stock": 130, "emotion_tags": "happy,surprise,statement,unique,trending,limited",
    },
    {
        "name": "Leather Belt", "brand": "GUCCI", "category": "Accessories",
        "sub_category": "Belts", "price": 4999, "original_price": 7999,
        "discount_pct": 37, "rating": 4.6, "review_count": 334,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
        "description": "Genuine leather belt with classic gold buckle.",
        "tags": "belt,leather,classic,premium,men",
        "stock": 75, "emotion_tags": "neutral,classic,minimal,timeless",
    },
    {
        "name": "Floral Silk Scarf", "brand": "ZARA", "category": "Accessories",
        "sub_category": "Scarves", "price": 2499, "original_price": 3499,
        "discount_pct": 28, "rating": 4.5, "review_count": 145,
        "image_url": "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400",
        "description": "Luxurious floral silk scarf for elegant styling.",
        "tags": "scarf,silk,floral,women,luxury",
        "stock": 85, "emotion_tags": "happy,colorful,vibrant,surprise,unique,limited",
    },
    {
        "name": "Cozy Wool Beanie", "brand": "H&M", "category": "Accessories",
        "sub_category": "Hats", "price": 899, "original_price": 1499,
        "discount_pct": 40, "rating": 4.4, "review_count": 222,
        "image_url": "https://images.unsplash.com/photo-1510598155022-83c0e0c7acba?w=400",
        "description": "Soft and warm wool beanie for cold days.",
        "tags": "beanie,wool,warm,winter,unisex",
        "stock": 160, "emotion_tags": "sad,cozy,comfort,warm,soft,home",
    },
]


def seed_products():
    if Product.query.count() > 0:
        logger.info("Products already seeded — skipping.")
        return

    for data in SEED_PRODUCTS:
        product = Product(**data)
        db.session.add(product)

    db.session.commit()
    logger.info(f"Seeded {len(SEED_PRODUCTS)} products into the database.")
