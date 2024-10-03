import datetime
import logging

from fastapi import HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from models import Reservation, Customer, Room, RoomServiceOrder, Transaction, HotelAnalytics, RoomServiceOrderItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_hotel_analytics(db: Session):
    try:
        today = datetime.datetime.utcnow()

        total_reservations = db.query(Reservation).count()
        total_customers = db.query(Customer).count()
        total_revenue = db.query(Transaction).with_entities(func.sum(Transaction.amount)).scalar() or 0
        room_revenue = db.query(Reservation).with_entities(func.sum(Reservation.total_cost)).scalar() or 0
        room_service_revenue = db.query(RoomServiceOrder).with_entities(
            func.sum(RoomServiceOrder.total_cost)).scalar() or 0
        occupied_rooms = db.query(Room).filter(Room.is_available == False).count()
        total_rooms = db.query(Room).count()
        average_daily_rate = room_revenue / total_reservations if total_reservations else 0
        revenue_per_available_room = total_revenue / total_rooms if total_rooms else 0
        average_occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms else 0

        most_popular_room_type = db.query(Room.room_type, func.count(Room.room_type).label('count')).group_by(
            Room.room_type).order_by(desc('count')).first()
        most_popular_service_item = db.query(RoomServiceOrderItem.room_service_item_id,
                                             func.count(RoomServiceOrderItem.room_service_item_id).label(
                                                 'count')).group_by(
            RoomServiceOrderItem.room_service_item_id).order_by(desc('count')).first()

        analytics = HotelAnalytics(
            date=today,
            total_reservations=total_reservations,
            total_customers=total_customers,
            total_revenue=total_revenue,
            room_revenue=room_revenue,
            room_service_revenue=room_service_revenue,
            occupied_rooms=occupied_rooms,
            total_rooms=total_rooms,
            average_daily_rate=average_daily_rate,
            revenue_per_available_room=revenue_per_available_room,
            average_occupancy_rate=average_occupancy_rate,
            most_popular_room_type=most_popular_room_type[0] if most_popular_room_type else None,
            most_popular_service_item=most_popular_service_item[0] if most_popular_service_item else None
        )

        db.add(analytics)
        db.commit()
        logger.info("Hotel analytics calculated and saved successfully.")
        return analytics

    except Exception as e:
        db.rollback()
        logger.error(f"Error calculating hotel analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
