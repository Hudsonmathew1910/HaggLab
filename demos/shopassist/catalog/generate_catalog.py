import json
from pathlib import Path

# Generate 60 realistic demo products across 4 categories (Hardware, Audio, Office, Apparel)
PRODUCTS = []
categories = {
    "Hardware": [
        ("Ergonomic Keyboard", 89.00, "ApexTech"),
        ("Precision Wireless Mouse", 49.00, "ApexTech"),
        ("USB-C 7-in-1 Hub", 39.00, "ConnectPro"),
        ("Laptop Cooling Pad", 29.00, "ConnectPro"),
        ("4K Ultra HD Webcam", 119.00, "Visionary"),
        ("Mechanical Macropad", 59.00, "CustomKey"),
        ("Braided DisplayPort Cable", 19.00, "CableCraft"),
        ("Fast Wireless Charger Stand", 35.00, "PowerGrid"),
        ("External SSD Enclosure", 45.00, "DriveFast"),
        ("Monitor Light Bar", 65.00, "GlowDesk"),
        ("Noise-Cancelling USB Mic", 99.00, "AudioLab"),
        ("Microphone Boom Arm", 45.00, "AudioLab"),
        ("Cable Management Tray", 25.00, "CleanDesk"),
        ("Under-Desk Headphone Hook", 15.00, "CleanDesk"),
        ("Dual Monitor Arm", 85.00, "Visionary")
    ],
    "Audio": [
        ("Studio Reference Headphones", 149.00, "SoundCraft"),
        ("Active Noise Cancelling Earbuds", 129.00, "SoundCraft"),
        ("Desktop Bluetooth Speakers", 110.00, "WaveForm"),
        ("Portable Waterproof Speaker", 55.00, "WaveForm"),
        ("Hi-Fi Headphone Amplifier", 89.00, "AmpStudio"),
        ("Dynamic Podcast Microphone", 119.00, "AudioLab"),
        ("Wireless Lavalier Mic Set", 95.00, "AudioLab"),
        ("Foam Acoustic Isolation Pads", 22.00, "SoundCraft"),
        ("Pop Filter & Shockmount Kit", 34.00, "AudioLab"),
        ("Over-Ear Wireless Headset", 79.00, "WaveForm"),
        ("Noise Isolation IEMs", 49.00, "SoundCraft"),
        ("Mini Desktop Subwoofer", 139.00, "WaveForm"),
        ("Gold-Plated Audio Cable", 18.00, "CableCraft"),
        ("Studio Monitor Desk Stands", 42.00, "SoundCraft"),
        ("Compact USB Audio Interface", 109.00, "AmpStudio")
    ],
    "Office": [
        ("Height Adjustable Standing Desk", 320.00, "WorkWell"),
        ("High-Back Mesh Desk Chair", 240.00, "WorkWell"),
        ("Faux Leather Desk Mat", 28.00, "CleanDesk"),
        ("Memory Foam Footrest", 38.00, "ComfortPlus"),
        ("Ergonomic Lumbar Support Pillow", 32.00, "ComfortPlus"),
        ("Bamboo Monitor Riser", 39.00, "CleanDesk"),
        ("Desktop Whiteboard with Storage", 45.00, "DeskPilot"),
        ("Aluminum Laptop Stand", 36.00, "ApexTech"),
        ("Vertical Document Organizer", 24.00, "DeskPilot"),
        ("Under-Desk Foot Hammock", 20.00, "ComfortPlus"),
        ("LED Desk Lamp with Qi Charging", 58.00, "GlowDesk"),
        ("Cable Clip Pack (6-Pack)", 12.00, "CleanDesk"),
        ("Silent Wall Clock for Focus", 26.00, "DeskPilot"),
        ("Spill-Proof Insulated Mug", 29.00, "WorkWell"),
        ("Mini Air Purifier for Desk", 68.00, "WorkWell")
    ],
    "Apparel": [
        ("Heavyweight Cotton Studio Hoodie", 65.00, "MonoWear"),
        ("Minimalist Logo T-Shirt", 32.00, "MonoWear"),
        ("Merino Wool Crewneck Sweater", 88.00, "NordicCraft"),
        ("Technical Water-Resistant Jacket", 145.00, "NordicCraft"),
        ("Relaxed Fit Work Chinos", 74.00, "MonoWear"),
        ("Structured Cotton Baseball Cap", 28.00, "MonoWear"),
        ("Everyday Canvas Tote Bag", 24.00, "MonoWear"),
        ("Wool Knit Beanie", 26.00, "NordicCraft"),
        ("Breathable Studio Joggers", 58.00, "MonoWear"),
        ("Cushioned Bamboo Crew Socks (3-Pack)", 18.00, "ComfortPlus"),
        ("Insulated Thermal Vest", 92.00, "NordicCraft"),
        ("Weatherproof Roll-Top Backpack", 110.00, "NordicCraft"),
        ("Linen Button-Down Overshirt", 68.00, "MonoWear"),
        ("Fleece-Lined Winter Gloves", 34.00, "NordicCraft"),
        ("Leather Minimalist Bifold Wallet", 45.00, "MonoWear")
    ]
}

p_id = 1
for cat, items in categories.items():
    for name, price, vendor in items:
        PRODUCTS.append({
            "id": p_id,
            "name": name,
            "category": cat,
            "price": price,
            "vendor": vendor,
            "in_stock": True,
            "url": f"/catalog/{p_id}/"
        })
        p_id += 1

CATALOG_PATH = Path(__file__).resolve().parent.parent / 'catalog' / 'products.json'
with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(PRODUCTS, f, indent=2)

print(f"Generated {len(PRODUCTS)} products across 4 categories.")
