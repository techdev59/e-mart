from .models import Store, Location
from accounts.models import User

def get_all_store_ids(user_id):
    user = User.objects.get(id = user_id)
    stores_ids = []
        
    user_locations = Location.objects.filter(location_manager = user.id).values_list("id", flat=True)
    user_stores = Store.objects.filter(store_manager = user.id).values_list("id", flat=True)
    location_stores = Store.objects.filter(store_location_id__in = user_locations).values_list("id", flat=True)
    stores_ids = list(stores_ids) + list(location_stores) + list(user_stores)
    stores_ids = set(stores_ids)
    stores_ids = list(stores_ids)
    return stores_ids