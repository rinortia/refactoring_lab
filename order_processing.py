DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21

COUPON_CODES = {
    "SAVE10": 0.10,
    "SAVE20": 0.20,
    "SAVE20_FALLBACK": 0.05,
}

MIN_AMOUNT_FOR_SAVE20 = 200
MIN_AMOUNT_FOR_VIP_DISCOUNT = 100

VIP_DISCOUNT = 50
VIP_SMALL_DISCOUNT = 10

def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def validate_order_data(user_id, items, currency):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if currency is None:
        currency = DEFAULT_CURRENCY
    
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError(" item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")
    
    return currency

def calculate_subtotal(items):
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["qty"]
    return subtotal

def calculate_discount(coupon, subtotal):    
    if not coupon or coupon == "":
        return 0
    
    if coupon == "SAVE10":
        return int(subtotal * COUPON_CODES["SAVE10"])
    
    if coupon == "SAVE20":
        if subtotal >= MIN_AMOUNT_FOR_SAVE20:
            return int(subtotal * COUPON_CODES["SAVE20"])
        else:
            return int(subtotal * COUPON_CODES["SAVE20_FALLBACK"])
    
    if coupon == "VIP":
        if subtotal < MIN_AMOUNT_FOR_VIP_DISCOUNT:
            return VIP_SMALL_DISCOUNT
        return VIP_DISCOUNT
    
    raise ValueError("unknown coupon")


def calculate_tax(amount):    
    return int(amount * TAX_RATE)

def generate_order_id(user_id, items_count):
    return f"{user_id}-{items_count}-X"

def process_checkout(request: dict) -> dict:    

    user_id, items, coupon, currency = parse_request(request)
    currency = validate_order_data(user_id, items, currency)
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(coupon, subtotal)
    
    total_after_discount = subtotal - discount
    if total_after_discount < 0:
        total_after_discount = 0
    
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax
    order_id = generate_order_id(user_id, len(items))
    
    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
