import json
import os
from django.conf import settings

def load_hotels():
    file_path = os.path.join(settings.BASE_DIR, 'apps', 'search_engine', 'data', 'hotels.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def search_hotels(query_params):
    hotels = load_hotels()
    
    q = query_params.get('q', '').lower()
    city = query_params.get('city', '').lower()
    country = query_params.get('country', '').lower()
    amenity = query_params.get('amenity', '').lower()
    tag = query_params.get('tag', '').lower()
    min_rating = query_params.get('min_rating')
    
    filtered = []
    for hotel in hotels:
        if q:
            query_words = q.split()
            match_q = True
            for word in query_words:
                word_match = (
                    word in hotel.get('name', '').lower() or
                    word in hotel.get('description', '').lower() or
                    word in hotel.get('city', '').lower() or
                    word in hotel.get('country', '').lower() or
                    any(word in a.lower() for a in hotel.get('amenities', [])) or
                    any(word in t.lower() for t in hotel.get('tags', []))
                )
                if not word_match:
                    match_q = False
                    break
            if not match_q:
                continue
                
        if city and city not in hotel.get('city', '').lower():
            continue
            
        if country and country not in hotel.get('country', '').lower():
            continue
            
        if amenity and not any(amenity in a.lower() for a in hotel.get('amenities', [])):
            continue
            
        if tag and not any(tag in t.lower() for t in hotel.get('tags', [])):
            continue
            
        if min_rating:
            try:
                if hotel.get('rating', 0) < float(min_rating):
                    continue
            except ValueError:
                pass
                
        filtered.append(hotel)
        
    return filtered
