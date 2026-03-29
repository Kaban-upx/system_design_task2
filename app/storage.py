from typing import Dict, List, Optional
from app.models import User, Parcel, Delivery

# In-memory DB
users_db: Dict[int, User] = {}
parcels_db: Dict[int, Parcel] = {}
deliveries_db: Dict[int, Delivery] = {}

# Counters for IDs
user_id_counter = 1
parcel_id_counter = 1
delivery_id_counter = 1

def get_next_user_id():
    global user_id_counter
    current = user_id_counter
    user_id_counter += 1
    return current

def get_next_parcel_id():
    global parcel_id_counter
    current = parcel_id_counter
    parcel_id_counter += 1
    return current

def get_next_delivery_id():
    global delivery_id_counter
    current = delivery_id_counter
    delivery_id_counter += 1
    return current