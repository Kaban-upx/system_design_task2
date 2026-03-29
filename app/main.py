from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from app import storage, models, schemas, auth
from datetime import timedelta
import uvicorn

app = FastAPI(title="Delivery Service API", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")


# --- Dependency ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except auth.JWTError:
        raise credentials_exception

    # Find user in storage
    user = None
    for u in storage.users_db.values():
        if u.login == login:
            user = u
            break

    if user is None:
        raise credentials_exception
    return user


# --- Auth Endpoints ---
@app.post("/api/users/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user_data: schemas.UserCreate):
    # Check if login exists
    for u in storage.users_db.values():
        if u.login == user_data.login:
            raise HTTPException(status_code=400, detail="Login already registered")

    new_id = storage.get_next_user_id()
    new_user = models.User(
        id=new_id,
        login=user_data.login,
        password_hash=auth.get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    storage.users_db[new_id] = new_user
    return schemas.UserResponse(**new_user.__dict__)


@app.post("/api/users/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for u in storage.users_db.values():
        if u.login == form_data.username:
            user = u
            break

    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect login or password")

    access_token = auth.create_access_token(
        data={"sub": user.login},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- User Search Endpoints ---
@app.get("/api/users/search/login", response_model=List[schemas.UserResponse])
def search_user_by_login(login: str = Query(...)):
    results = []
    for u in storage.users_db.values():
        if login.lower() in u.login.lower():
            results.append(schemas.UserResponse(**u.__dict__))
    return results


@app.get("/api/users/search/name", response_model=List[schemas.UserResponse])
def search_user_by_name(name: Optional[str] = None, surname: Optional[str] = None):
    results = []
    for u in storage.users_db.values():
        match = True
        if name and name.lower() not in u.first_name.lower():
            match = False
        if surname and surname.lower() not in u.last_name.lower():
            match = False
        if match:
            results.append(schemas.UserResponse(**u.__dict__))
    return results


# --- Parcel Endpoints (Protected) ---
@app.post("/api/parcels", response_model=schemas.ParcelResponse, status_code=201)
def create_parcel(parcel: schemas.ParcelCreate, current_user: models.User = Depends(get_current_user)):
    new_id = storage.get_next_parcel_id()
    new_parcel = models.Parcel(
        id=new_id,
        owner_id=current_user.id,
        description=parcel.description,
        weight=parcel.weight
    )
    storage.parcels_db[new_id] = new_parcel
    return schemas.ParcelResponse(**new_parcel.__dict__)


@app.get("/api/parcels/me", response_model=List[schemas.ParcelResponse])
def get_my_parcels(current_user: models.User = Depends(get_current_user)):
    results = []
    for p in storage.parcels_db.values():
        if p.owner_id == current_user.id:
            results.append(schemas.ParcelResponse(**p.__dict__))
    return results


# --- Delivery Endpoints ---
@app.post("/api/deliveries", response_model=schemas.DeliveryResponse, status_code=201)
def create_delivery(delivery: schemas.DeliveryCreate, current_user: models.User = Depends(get_current_user)):
    # Check parcel exists and belongs to sender
    parcel = storage.parcels_db.get(delivery.parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    if parcel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this parcel")

    # Check recipient exists
    recipient = storage.users_db.get(delivery.recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    new_id = storage.get_next_delivery_id()
    new_delivery = models.Delivery(
        id=new_id,
        parcel_id=delivery.parcel_id,
        sender_id=current_user.id,
        recipient_id=delivery.recipient_id
    )
    storage.deliveries_db[new_id] = new_delivery
    return schemas.DeliveryResponse(**new_delivery.__dict__)


@app.get("/api/deliveries/recipient/{recipient_id}", response_model=List[schemas.DeliveryResponse])
def get_deliveries_by_recipient(recipient_id: int):
    results = []
    for d in storage.deliveries_db.values():
        if d.recipient_id == recipient_id:
            results.append(schemas.DeliveryResponse(**d.__dict__))
    return results


@app.get("/api/deliveries/sender/{sender_id}", response_model=List[schemas.DeliveryResponse])
def get_deliveries_by_sender(sender_id: int):
    results = []
    for d in storage.deliveries_db.values():
        if d.sender_id == sender_id:
            results.append(schemas.DeliveryResponse(**d.__dict__))
    return results

# python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 запуск