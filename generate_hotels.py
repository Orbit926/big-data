import json
import random

cities_countries = [
    ("Cancun", "Mexico"), ("Tulum", "Mexico"), ("Guadalajara", "Mexico"), 
    ("CDMX", "Mexico"), ("Monterrey", "Mexico"), ("Puerto Vallarta", "Mexico"),
    ("Miami", "USA"), ("New York", "USA"), ("Madrid", "Spain"), 
    ("Paris", "France"), ("Tokyo", "Japan"), ("Rome", "Italy")
]

amenities_list = [
    "wifi", "pool", "spa", "gym", "restaurant", "bar", 
    "parking", "breakfast", "pet_friendly", "air_conditioning", "ocean_view"
]

tags_list = [
    "luxury", "budget", "business", "family", "romantic", 
    "beach", "city", "nature", "all_inclusive"
]

images = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945",
    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",
    "https://images.unsplash.com/photo-1542314831-c6a4d14d2301",
    "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9",
    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4",
    "https://images.unsplash.com/photo-1564501049412-61c2a3083791",
    "https://images.unsplash.com/photo-1551882547-ff40c0d5bf8f",
    "https://images.unsplash.com/photo-1578683010236-d716f9a3f461",
    "https://images.unsplash.com/photo-1584132967334-10e028bd69f7",
    "https://images.unsplash.com/photo-1611892440504-42a792e24d32"
]

hotel_names = [
    "Grand Resort", "Palace", "Plaza", "Inn", "Suites", "Boutique", "Lodge", "Retreat", "Haven"
]

adjectives = ["Royal", "Sunset", "Ocean", "Golden", "Majestic", "Crystal", "Emerald", "Oasis", "Serene", "Urban"]

hotels = []
for i in range(1, 201):
    city, country = random.choice(cities_countries)
    name = f"{random.choice(adjectives)} {random.choice(hotel_names)} {city}"
    
    # ensure realistic matching for tags based on city
    available_tags = tags_list.copy()
    if city in ["Cancun", "Tulum", "Puerto Vallarta", "Miami"]:
        available_tags.append("beach")
        available_tags.append("all_inclusive")
        
    num_amenities = random.randint(3, 8)
    num_tags = random.randint(1, 4)
    
    hotel = {
        "id": i,
        "name": name,
        "city": city,
        "country": country,
        "rating": round(random.uniform(3.0, 5.0), 1),
        "reviews": random.randint(10, 5000),
        "price_per_night": random.randint(50, 800),
        "currency": "USD",
        "description": f"Beautiful {random.choice(tags_list)} hotel located in the heart of {city}. Enjoy our wonderful amenities and exceptional service.",
        "amenities": random.sample(amenities_list, num_amenities),
        "tags": list(set(random.sample(available_tags, min(num_tags, len(available_tags))))),
        "image_url": random.choice(images),
        "available": random.choice([True, True, True, False])
    }
    hotels.append(hotel)

with open('backend/apps/search_engine/data/hotels.json', 'w') as f:
    json.dump(hotels, f, indent=2)

print(f"Generated {len(hotels)} hotels in hotels.json")
