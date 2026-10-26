import json
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / 'catalog' / 'products.json'

def load_products():
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_products(category=None, max_price=None, vendor=None, query=None):
    """
    Tool function callable by the assistant to retrieve filtered products.
    """
    products = load_products()
    results = []

    for p in products:
        if category and p['category'].lower() != category.lower():
            continue
        if max_price is not None and p['price'] > float(max_price):
            continue
        if vendor and p['vendor'].lower() != vendor.lower():
            continue
        if query:
            q = query.lower()
            if q not in p['name'].lower() and q not in p['category'].lower() and q not in p['vendor'].lower():
                continue
        results.append(p)

    return results

def process_shopper_message(user_message, history=None):
    """
    Conversational shopper assistant.
    Maintains a rolling memory of the last 12 messages.
    Identifies tool call intents and returns curated product lists.
    """
    if history is None:
        history = []

    # Keep only the last 12 messages
    history = history[-12:]
    msg = user_message.lower().strip()

    category = None
    max_price = None
    query = None

    import re

    if re.search(r'\b(headphone|headphones|earbuds|audio|speaker|speakers|microphone|microphones|mic|mics)\b', msg):
        category = 'Audio'
    elif re.search(r'\b(keyboard|keyboards|mouse|mice|hardware|webcam|webcams|cable|cables|hub|hubs)\b', msg):
        category = 'Hardware'
    elif re.search(r'\b(desk|desks|chair|chairs|office|lamp|lamps|riser|risers|stand|stands)\b', msg):
        category = 'Office'
    elif re.search(r'\b(hoodie|hoodies|shirt|shirts|jacket|jackets|apparel|sweater|sweaters|joggers|socks)\b', msg):
        category = 'Apparel'



    # Check for price constraints (e.g. under 100, under 50)
    import re
    price_match = re.search(r'under\s+\$?(\d+)', msg)
    if price_match:
        max_price = float(price_match.group(1))

    # Fallback to general keyword match
    if not category:
        for word in msg.split():
            if len(word) > 3:
                query = word
                break

    matches = search_products(category=category, max_price=max_price, query=query)
    
    if matches:
        reply = f"I found {len(matches)} matching products in our catalog:"
    else:
        reply = "I could not find products matching that exact description in our catalog. Try asking for Audio, Hardware, Office, or Apparel."

    history.append({"role": "user", "text": user_message})
    history.append({"role": "assistant", "text": reply, "matches_count": len(matches)})

    return {
        "reply": reply,
        "products": matches[:6], # Display top 6 matches in list format
        "history": history
    }
