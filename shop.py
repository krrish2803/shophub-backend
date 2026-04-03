"""
Shop / Product Routes
GET  /api/shop/products           - list with filters & pagination
GET  /api/shop/products/<id>      - single product
GET  /api/shop/categories         - category list
GET  /api/shop/brands             - brand list
GET  /api/shop/search             - full-text search
GET  /api/shop/featured           - featured / new-arrivals
"""
from flask import Blueprint, request, jsonify
from models import Product
from config import Config

shop_bp = Blueprint("shop", __name__)


# ── Products list ─────────────────────────────────────────────────────────────
@shop_bp.route("/products", methods=["GET"])
def get_products():
    page        = request.args.get("page",     1,    type=int)
    per_page    = request.args.get("per_page", Config.PRODUCTS_PER_PAGE, type=int)
    category    = request.args.get("category", None)
    brand       = request.args.get("brand",    None)
    min_price   = request.args.get("min_price",None, type=float)
    max_price   = request.args.get("max_price",None, type=float)
    min_rating  = request.args.get("min_rating",None,type=float)
    sort_by     = request.args.get("sort",     "recommended")

    query = Product.query

    if category and category.lower() != "all":
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if brand and brand.lower() != "all":
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)

    # Sorting
    sort_map = {
        "price_asc":    Product.price.asc(),
        "price_desc":   Product.price.desc(),
        "rating":       Product.rating.desc(),
        "newest":       Product.created_at.desc(),
        "discount":     Product.discount_pct.desc(),
        "recommended":  Product.rating.desc(),
    }
    query = query.order_by(sort_map.get(sort_by, Product.rating.desc()))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "products":    [p.to_dict() for p in paginated.items],
        "total":       paginated.total,
        "page":        paginated.page,
        "pages":       paginated.pages,
        "per_page":    per_page,
        "has_next":    paginated.has_next,
        "has_prev":    paginated.has_prev,
    }), 200


# ── Single product ────────────────────────────────────────────────────────────
@shop_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({"product": product.to_dict()}), 200


# ── Categories ────────────────────────────────────────────────────────────────
@shop_bp.route("/categories", methods=["GET"])
def get_categories():
    rows = (
        Product.query
        .with_entities(Product.category)
        .distinct()
        .all()
    )
    categories = [r.category for r in rows if r.category]
    return jsonify({"categories": ["All"] + sorted(categories)}), 200


# ── Brands ────────────────────────────────────────────────────────────────────
@shop_bp.route("/brands", methods=["GET"])
def get_brands():
    rows = (
        Product.query
        .with_entities(Product.brand)
        .distinct()
        .all()
    )
    brands = [r.brand for r in rows if r.brand]
    return jsonify({"brands": ["All"] + sorted(brands)}), 200


# ── Full-text search ──────────────────────────────────────────────────────────
@shop_bp.route("/search", methods=["GET"])
def search_products():
    q        = request.args.get("q", "").strip()
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", Config.PRODUCTS_PER_PAGE, type=int)

    if not q:
        return jsonify({"products": [], "total": 0}), 200

    like = f"%{q}%"
    query = Product.query.filter(
        Product.name.ilike(like)
        | Product.brand.ilike(like)
        | Product.category.ilike(like)
        | Product.tags.ilike(like)
        | Product.description.ilike(like)
    )

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "products":  [p.to_dict() for p in paginated.items],
        "total":     paginated.total,
        "query":     q,
    }), 200


# ── Featured / New Arrivals ───────────────────────────────────────────────────
@shop_bp.route("/featured", methods=["GET"])
def get_featured():
    featured = (
        Product.query
        .filter(Product.discount_pct >= 20)
        .order_by(Product.discount_pct.desc())
        .limit(8)
        .all()
    )
    new_arrivals = (
        Product.query
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )
    top_rated = (
        Product.query
        .filter(Product.rating >= 4.5)
        .order_by(Product.rating.desc())
        .limit(8)
        .all()
    )
    return jsonify({
        "featured":     [p.to_dict() for p in featured],
        "new_arrivals": [p.to_dict() for p in new_arrivals],
        "top_rated":    [p.to_dict() for p in top_rated],
    }), 200
