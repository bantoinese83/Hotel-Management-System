import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<Customer(name={self.name}, email={self.email})>"


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    room_number = Column(Integer, unique=True, nullable=False, index=True)
    room_type = Column(String(50), nullable=False)
    price_per_night = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Room(room_number={self.room_number}, room_type={self.room_type})>"


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    total_cost = Column(Float, nullable=False)

    customer = relationship("Customer", backref="reservations", lazy="joined")
    room = relationship("Room", backref="reservations", lazy="joined")

    def __repr__(self):
        return f"<Reservation(customer_id={self.customer_id}, room_id={self.room_id})>"


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    reservation = relationship("Reservation", backref="transactions", lazy="joined")

    def __repr__(self):
        return f"<Transaction(reservation_id={self.reservation_id}, amount={self.amount})>"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    role = Column(String(50), nullable=False, default="user")  # user, admin

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


class RoomServiceItem(Base):
    __tablename__ = "room_service_items"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<RoomServiceItem(name={self.name}, price={self.price})>"


class RoomServiceOrder(Base):
    __tablename__ = "room_service_orders"
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    total_cost = Column(Float, nullable=False)
    status = Column(String(20), default="Pending")

    items = relationship("RoomServiceOrderItem", backref="order", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
        return f"<RoomServiceOrder(reservation_id={self.reservation_id}, total_cost={self.total_cost})>"


class RoomServiceOrderItem(Base):
    __tablename__ = "room_service_order_items"
    id = Column(Integer, primary_key=True)
    room_service_order_id = Column(Integer, ForeignKey("room_service_orders.id"), nullable=False)
    room_service_item_id = Column(Integer, ForeignKey("room_service_items.id"), nullable=False)
    quantity = Column(Integer, default=1)

    item = relationship("RoomServiceItem", backref="order_items", lazy="joined")

    def __repr__(self):
        return (f"<RoomServiceOrderItem(order_id={self.room_service_order_id}, item_id={self.room_service_item_id}, "
                f"quantity={self.quantity})>")


class HotelAnalytics(Base):
    __tablename__ = "hotel_analytics"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    total_reservations = Column(Integer, nullable=False)
    total_customers = Column(Integer, nullable=False)
    total_revenue = Column(Float, nullable=False)
    room_revenue = Column(Float, nullable=False)
    room_service_revenue = Column(Float, nullable=False)
    occupied_rooms = Column(Integer, nullable=False)
    total_rooms = Column(Integer, nullable=False)
    average_daily_rate = Column(Float, nullable=False)
    revenue_per_available_room = Column(Float, nullable=False)
    average_occupancy_rate = Column(Float, nullable=False)
    most_popular_room_type = Column(String(50), nullable=False)
    most_popular_service_item = Column(String(100), nullable=False)

    def __repr__(self):
        return (f"<HotelAnalytics(date={self.date}, total_reservations={self.total_reservations}, "
                f"total_customers={self.total_customers}, total_revenue={self.total_revenue}, "
                f"room_revenue={self.room_revenue}, room_service_revenue={self.room_service_revenue}, "
                f"occupied_rooms={self.occupied_rooms}, total_rooms={self.total_rooms}, "
                f"average_daily_rate={self.average_daily_rate}, "
                f"revenue_per_available_room={self.revenue_per_available_room}, "
                f"average_occupancy_rate={self.average_occupancy_rate}, "
                f"most_popular_room_type={self.most_popular_room_type}, "
                f"most_popular_service_item={self.most_popular_service_item})>")
