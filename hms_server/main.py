# hms_server/main.py
import logging
import os
from typing import List

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.responses import RedirectResponse

import crud
from analytics import calculate_hotel_analytics
from inject_test_data import DataInjector
from models import Base
from models import User
from schemas import CustomerCreate, CustomerRead, RoomCreate, RoomRead, ReservationCreate, ReservationRead, \
    TransactionCreate, TransactionRead, RoomServiceItemCreate, RoomServiceItemRead, RoomServiceOrderCreate, \
    RoomServiceOrderRead, LoginRequest, RegisterRequest, HotelAnalyticsRead
from security import create_access_token, JWTBearer, authenticate_user, get_current_user, require_role

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# Database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hotel Management System",
    description="A simple hotel management system API",
    version="0.1",
)


# Dependency injection for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWT Bearer Authentication Middleware
jwt_bearer = JWTBearer()


# ---------------------- User Authentication ----------------------

@app.post("/register", tags=["🔒 Security"], summary="Register a new user",
          description="Use this endpoint to register a new user.")
async def register(register_request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = crud.register_user(db, register_request)
        return JSONResponse(status_code=201, content={"message": "User registered successfully"})
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/login", tags=["🔒 Security"], summary="Login to get an access token",
          description="Use this endpoint to get an access token. You can use this token to access secure endpoints.")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.username, login_request.password)
    access_token = create_access_token(data={"sub": user.username})
    return JSONResponse(status_code=200, content={"access_token": access_token, "token_type": "bearer"})


# ---------------------- Customer Management ----------------------
@app.post("/customers/", response_model=CustomerRead, tags=["👤 Customers"], summary="Create a new customer",
          description="Create a new customer with the provided details.")
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_customer(db, customer)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/customers/", response_model=List[CustomerRead], tags=["👤 Customers"], summary="Get all customers",
         description="Get a list of all customers.")
async def get_customers(db: Session = Depends(get_db)):
    return crud.get_customers(db)


# ---------------------- Reservation Management ----------------------
@app.post("/reservations/", response_model=ReservationRead, tags=["🛎 Reservations"], summary="Create a new reservation",
          description="Create a new reservation with the provided details.")
async def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_reservation(db, reservation)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating reservation: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reservations/", response_model=List[ReservationRead], tags=["🛎 Reservations"],
         summary="Get all reservations", description="Get a list of all reservations.")
async def get_reservations(db: Session = Depends(get_db)):
    return crud.get_reservations(db)


@app.put("/reservations/{reservation_id}", response_model=ReservationRead, tags=["🛎 Reservations"],
         summary="Update a reservation", description="Update an existing reservation with the provided details.")
async def update_reservation(reservation_id: int, reservation: ReservationCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_reservation(db, reservation_id, reservation)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating reservation: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------- Transaction Management ----------------------
@app.post("/transactions/", response_model=TransactionRead, tags=["💳 Transactions"], summary="Create a new transaction",
          description="Create a new transaction with the provided details.")
async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_transaction(db, transaction)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/transactions/", response_model=List[TransactionRead], tags=["💳 Transactions"],
         summary="Get all transactions", description="Get a list of all transactions.")
async def get_transactions(db: Session = Depends(get_db)):
    return crud.get_transactions(db)


# ---------------------- Room Management ----------------------
@app.post("/rooms/", response_model=RoomRead, tags=["🏨 Rooms"], summary="Create a new room",
          description="Create a new room with the provided details.")
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_room(db, room)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating room: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/rooms/", response_model=List[RoomRead], tags=["🏨 Rooms"], summary="Get all rooms",
         description="Get a list of all rooms.")
async def get_rooms(db: Session = Depends(get_db)):
    return crud.get_rooms(db)


@app.put("/rooms/{room_id}", response_model=RoomRead, tags=["🏨 Rooms"], summary="Update a room",
         description="Update an existing room with the provided details.")
async def update_room(room_id: int, room: RoomCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_room(db, room_id, room)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating room: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------- Room Services ----------------------
@app.post("/room-services/items/", response_model=RoomServiceItemRead, tags=["🍽 Room Services"],
          summary="Create a new room service item",
          description="Create a new room service item with the provided details.")
async def create_room_service_item(item: RoomServiceItemCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_room_service_item(db, item)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating room service item: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/room-services/items/", response_model=List[RoomServiceItemRead], tags=["🍽 Room Services"],
         summary="Get all room service items", description="Get a list of all room service items.")
async def get_room_service_items(db: Session = Depends(get_db)):
    return crud.get_room_service_items(db)


@app.post("/room-services/orders/", response_model=RoomServiceOrderRead, tags=["🍽 Room Services"],
          summary="Create a new room service order",
          description="Create a new room service order with the provided details.")
async def create_room_service_order(order: RoomServiceOrderCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_room_service_order(db, order)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating room service order: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/room-services/orders/", response_model=List[RoomServiceOrderRead], tags=["🍽 Room Services"],
         summary="Get all room service orders", description="Get a list of all room service orders.")
async def get_room_service_orders(db: Session = Depends(get_db)):
    return crud.get_room_service_orders(db)


# ---------------------- Billing ----------------------
@app.get("/reservations/{reservation_id}/bill", tags=["💰 Billing"], summary="Get reservation bill",
         description="Get the total cost of a reservation.")
async def get_reservation_bill(reservation_id: int, db: Session = Depends(get_db)):
    total_cost = crud.get_reservation_bill(db, reservation_id)
    return JSONResponse(status_code=200, content={"total_cost": total_cost})


# ---------------------- Security ----------------------

@app.get("/secure/users", tags=["🔒 Security"], summary="Get user details",
         description="Get details of the authenticated user.")
@require_role("user")
async def get_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"message": f"Hello, {user.username}!"}


@app.post("/secure/admin-only-endpoint", tags=["🔒 Security"], summary="Admin only endpoint",
          description="Endpoint accessible only by admin users.")
@require_role("admin")
async def admin_only_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"message": "You are an admin"}


# -------------------- Analytics Endpoints --------------------


@app.get("/analytics", response_model=HotelAnalyticsRead, tags=["📊 Analytics"], summary="Get hotel analytics",
         description="Calculate and get hotel analytics.")
async def get_analytics(db: Session = Depends(get_db)):
    analytics = calculate_hotel_analytics(db)
    print(analytics)
    return analytics


# -------------------- Root and Health Check Endpoints --------------------
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["🏥 Health"], summary="Health check", description="Check the health status of the API.")
async def health():
    return {"status": "ok"}


# -------------------- Create Tables --------------------
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    injector = DataInjector()
    injector.inject_data()
    logger.info("Data injected")
    logger.info("Tables created")


# -------------------- Drop Tables --------------------
@app.on_event("shutdown")
def on_shutdown():
    Base.metadata.drop_all(bind=engine)
    logger.info("Tables dropped")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
