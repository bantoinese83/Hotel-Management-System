import datetime
import hashlib
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Customer, Room, Reservation, Transaction, User, RoomServiceItem, RoomServiceOrder, \
    RoomServiceOrderItem

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


class DataInjector:
    def __init__(self, database_url=SQLALCHEMY_DATABASE_URL):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def inject_data(self):
        session = self.SessionLocal()

        # Sample data for injection
        customer_names = ["John Doe", "Jane Smith", "Peter Jones", "Mary Brown", "David Wilson", "Linda Davis",
                          "Michael Thomas", "Jennifer Garcia", "Robert Martinez", "Barbara Rodriguez"]
        room_types = ["Single", "Double", "Suite", "Deluxe"]

        # -------------------- Inject Customer Data --------------------
        for i in range(100):
            email = f"customer{i}@example.com"
            if not session.query(Customer).filter_by(email=email).first():
                customer = Customer(
                    name=f"{customer_names[i % len(customer_names)]} {i}",
                    email=email,
                    phone_number=f"+1555123456{i}"
                )
                session.add(customer)

        session.commit()
        print("Customer data injected!")

        # -------------------- Inject Room Data --------------------
        for i in range(100):
            room_number = i + 1
            if not session.query(Room).filter_by(room_number=room_number).first():
                room = Room(
                    room_number=room_number,
                    room_type=room_types[i % len(room_types)],
                    price_per_night=100 + i * 5
                )
                session.add(room)

        session.commit()
        print("Room data injected!")

        # -------------------- Inject Reservation Data --------------------
        for i in range(100):
            customer_id = (i % 10) + 1  # Random customer
            room_id = (i % 10) + 1  # Random room
            check_in_date = datetime.datetime(2024, 1, min(i + 1, 31))
            check_out_date = datetime.datetime(2024, 1, min(i + 1 + 3, 31))
            room = session.query(Room).filter_by(id=room_id).first()
            if not session.query(Reservation).filter_by(customer_id=customer_id, room_id=room_id,
                                                        check_in_date=check_in_date).first():
                duration = (check_out_date - check_in_date).days
                total_cost = duration * room.price_per_night
                reservation = Reservation(
                    customer_id=customer_id,
                    room_id=room_id,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    total_cost=total_cost
                )
                session.add(reservation)
                room.is_available = False  # Set room as occupied

        session.commit()
        print("Reservation data injected!")

        # -------------------- Inject Transaction Data --------------------
        for i in range(100):
            reservation_id = (i % 10) + 1  # Random reservation
            if not session.query(Transaction).filter_by(reservation_id=reservation_id).first():
                transaction = Transaction(
                    reservation_id=reservation_id,
                    amount=100 + i * 2,
                    payment_method="Credit Card"
                )
                session.add(transaction)

        session.commit()
        print("Transaction data injected!")

        # -------------------- Inject User Data --------------------
        for i in range(100):
            username = f"user{i}"
            if not session.query(User).filter_by(username=username).first():
                password = hashlib.sha256(f"password{i}".encode()).hexdigest()
                user = User(
                    username=username,
                    password=password
                )
                session.add(user)

        session.commit()
        print("User data injected!")

        # -------------------- Inject Room Service Item Data --------------------
        room_service_items = ["Breakfast", "Lunch", "Dinner", "Coffee", "Tea", "Water", "Soft Drinks", "Wine", "Beer"]
        for i in range(100):
            name = room_service_items[i % len(room_service_items)]
            if not session.query(RoomServiceItem).filter_by(name=name).first():
                item = RoomServiceItem(
                    name=name,
                    description=f"Room service item {i}",
                    price=i * 2 + 5
                )
                session.add(item)

        session.commit()
        print("Room service item data injected!")

        # -------------------- Inject Room Service Order Data --------------------
        for i in range(100):
            reservation_id = (i % 10) + 1  # Random reservation
            if not session.query(RoomServiceOrder).filter_by(reservation_id=reservation_id).first():
                order = RoomServiceOrder(
                    reservation_id=reservation_id,
                    total_cost=0
                )
                session.add(order)
                session.commit()  # Commit to get the order.id

                total_cost = 0
                # Add some items to the order
                for j in range(3):
                    item_id = (i + j) % 10 + 1  # Random item
                    item = session.query(RoomServiceItem).filter_by(id=item_id).first()
                    order_item = RoomServiceOrderItem(
                        room_service_order_id=order.id,
                        room_service_item_id=item_id,
                        quantity=j + 1
                    )
                    session.add(order_item)
                    total_cost += item.price * (j + 1)

                order.total_cost = total_cost
                session.commit()

        print("Room service order data injected!")

        session.close()
        print("All data injected successfully!")
