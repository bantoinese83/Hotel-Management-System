# hms_server/crud.py
import datetime
import hashlib
import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Customer, Room, Reservation, Transaction, RoomServiceItem, RoomServiceOrder, RoomServiceOrderItem, \
    User
from schemas import CustomerCreate, ReservationCreate, RoomCreate, TransactionCreate, RoomServiceItemCreate, \
    RoomServiceOrderCreate, RegisterRequest

logger = logging.getLogger(__name__)


def register_user(db: Session, user: RegisterRequest):
    try:
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        db_user = User(username=user.username, password=hashed_password, role=user.role)  # Add role here
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=400, detail="Error registering user")

# Customer CRUD
def create_customer(db: Session, customer: CustomerCreate):
    try:
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=400, detail="Error creating customer")


def get_customers(db: Session):
    try:
        return db.query(Customer).all()
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise HTTPException(status_code=400, detail="Error fetching customers")


# Reservation CRUD
def create_reservation(db: Session, reservation: ReservationCreate):
    try:
        customer = db.query(Customer).filter(Customer.id == reservation.customer_id).first()
        room = db.query(Room).filter(Room.id == reservation.room_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if not room.is_available:
            raise HTTPException(status_code=400, detail="Room is not available")

        # Calculate the duration of the stay
        duration = (reservation.check_out_date - reservation.check_in_date).days
        if duration <= 0:
            raise HTTPException(status_code=400, detail="Check-out date must be after check-in date")

        # Calculate the total cost
        total_cost = duration * room.price_per_night

        db_reservation = Reservation(
            customer_id=reservation.customer_id,
            room_id=reservation.room_id,
            check_in_date=reservation.check_in_date,
            check_out_date=reservation.check_out_date,
            total_cost=total_cost
        )
        db.add(db_reservation)
        room.is_available = False
        db.commit()
        db.refresh(db_reservation)
        return db_reservation
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating reservation: {e}")
        raise HTTPException(status_code=400, detail="Error creating reservation")


def get_reservations(db: Session):
    try:
        return db.query(Reservation).all()
    except Exception as e:
        logger.error(f"Error fetching reservations: {e}")
        raise HTTPException(status_code=400, detail="Error fetching reservations")


def update_reservation(db: Session, reservation_id: int, reservation: ReservationCreate):
    try:
        db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not db_reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        for key, value in reservation.dict(exclude_unset=True).items():
            setattr(db_reservation, key, value)

        db.commit()
        db.refresh(db_reservation)
        return db_reservation
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating reservation: {e}")
        raise HTTPException(status_code=400, detail="Error updating reservation")


# Transaction CRUD
def create_transaction(db: Session, transaction: TransactionCreate):
    try:
        reservation = db.query(Reservation).filter(Reservation.id == transaction.reservation_id).first()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        db_transaction = Transaction(
            reservation_id=transaction.reservation_id,
            amount=transaction.amount,
            payment_method=transaction.payment_method,
            date=datetime.datetime.now()
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=400, detail="Error creating transaction")


def get_transactions(db: Session):
    try:
        return db.query(Transaction).all()
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=400, detail="Error fetching transactions")


# Room CRUD
def create_room(db: Session, room: RoomCreate):
    try:
        db_room = Room(**room.dict())
        db.add(db_room)
        db.commit()
        db.refresh(db_room)
        return db_room
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating room: {e}")
        raise HTTPException(status_code=400, detail="Error creating room")


def get_rooms(db: Session):
    try:
        return db.query(Room).all()
    except Exception as e:
        logger.error(f"Error fetching rooms: {e}")
        raise HTTPException(status_code=400, detail="Error fetching rooms")


def update_room(db: Session, room_id: int, room: RoomCreate):
    try:
        db_room = db.query(Room).filter(Room.id == room_id).first()
        if not db_room:
            raise HTTPException(status_code=404, detail="Room not found")

        for key, value in room.dict(exclude_unset=True).items():
            setattr(db_room, key, value)

        db.commit()
        db.refresh(db_room)
        return db_room
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating room: {e}")
        raise HTTPException(status_code=400, detail="Error updating room")


# Room Service CRUD
def create_room_service_item(db: Session, item: RoomServiceItemCreate):
    try:
        db_item = RoomServiceItem(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating room service item: {e}")
        raise HTTPException(status_code=400, detail="Error creating room service item")


def get_room_service_items(db: Session):
    try:
        return db.query(RoomServiceItem).all()
    except Exception as e:
        logger.error(f"Error fetching room service items: {e}")
        raise HTTPException(status_code=400, detail="Error fetching room service items")


def create_room_service_order(db: Session, order: RoomServiceOrderCreate):
    try:
        reservation = db.query(Reservation).filter(Reservation.id == order.reservation_id).first()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        db_order = RoomServiceOrder(reservation_id=order.reservation_id)
        total_cost = 0

        for item_data in order.items:
            item = db.query(RoomServiceItem).filter(RoomServiceItem.id == item_data.room_service_item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="Room service item not found")

            order_item = RoomServiceOrderItem(
                room_service_order_id=db_order.id,
                room_service_item_id=item.id,
                quantity=item_data.quantity
            )
            db.add(order_item)
            total_cost += item.price * item_data.quantity

        db_order.total_cost = total_cost
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating room service order: {e}")
        raise HTTPException(status_code=400, detail="Error creating room service order")


def get_room_service_orders(db: Session):
    try:
        return db.query(RoomServiceOrder).all()
    except Exception as e:
        logger.error(f"Error fetching room service orders: {e}")
        raise HTTPException(status_code=400, detail="Error fetching room service orders")


def get_reservation_bill(db: Session, reservation_id: int):
    try:
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        total_cost = reservation.total_cost
        room_service_orders = db.query(RoomServiceOrder).filter(RoomServiceOrder.reservation_id == reservation_id).all()
        for order in room_service_orders:
            total_cost += order.total_cost

        return total_cost
    except Exception as e:
        logger.error(f"Error calculating reservation bill: {e}")
        raise HTTPException(status_code=400, detail="Error calculating reservation bill")
