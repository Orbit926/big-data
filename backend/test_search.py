import os
import sys
import django

# Add the backend directory to sys.path so 'config' and 'apps' can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.search_engine.views import HotelSearchView

factory = RequestFactory()
request = factory.get('/api/search/hotels/?q=beach&page=1')
view = HotelSearchView.as_view()
response = view(request)
response.render()

print("Status Code:", response.status_code)
if hasattr(response, 'data'):
    print("Keys:", list(response.data.keys()))
    print("Count:", response.data.get('count'))
    if response.data.get('results'):
        print("First result name:", response.data['results'][0]['name'])
    else:
        print("No results found.")
