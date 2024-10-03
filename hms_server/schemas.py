from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field
from pydantic.v1 import validator


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20, pattern=r'^\+?\d{10,20}$')


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int


class RoomBase(BaseModel):
    room_number: int = Field(..., gt=0)
    room_type: str = Field(..., min_length=1, max_length=50)
    price_per_night: float = Field(..., gt=0)
    is_available: bool = True


class RoomCreate(RoomBase):
    pass


class RoomRead(RoomBase):
    id: int


class ReservationBase(BaseModel):
    customer_id: int
    room_id: int
    check_in_date: datetime
    check_out_date: datetime
    total_cost: float = Field(..., ge=0)

    @validator('check_out_date')
    def check_dates(cls, check_out_date, values):
        if 'check_in_date' in values and check_out_date <= values['check_in_date']:
            raise ValueError('check_out_date must be after check_in_date')
        return check_out_date


class ReservationCreate(ReservationBase):
    pass


class ReservationRead(ReservationBase):
    id: int


class TransactionBase(BaseModel):
    reservation_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1, max_length=50)


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int
    date: datetime


class RoomServiceItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)


class RoomServiceItemCreate(RoomServiceItemBase):
    pass


class RoomServiceItemRead(RoomServiceItemBase):
    id: int


class RoomServiceOrderItem(BaseModel):
    room_service_item_id: int
    quantity: int = Field(1, gt=0)


class RoomServiceOrderBase(BaseModel):
    reservation_id: int
    items: List[RoomServiceOrderItem] = []
    total_cost: float = Field(0, ge=0)


class RoomServiceOrderCreate(RoomServiceOrderBase):
    pass


class RoomServiceOrderRead(RoomServiceOrderBase):
    id: int


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int


class LoginRequest(BaseModel):
    username: str = Field("testuser", min_length=1, max_length=50)
    password: str = Field("test_password", min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field("testuser", min_length=1, max_length=50)
    password: str = Field("test_password", min_length=8, max_length=128)
    role: str = Field("user", min_length=1, max_length=50)  # Add this line


class HotelAnalyticsRead(BaseModel):
    date: datetime
    total_reservations: int
    total_customers: int
    total_revenue: float
    room_revenue: float
    room_service_revenue: float
    occupied_rooms: int
    total_rooms: int
    average_daily_rate: float
    revenue_per_available_room: float
    average_occupancy_rate: float
    most_popular_room_type: str
    most_popular_service_item: str

    class Config:
        from_attributes = True
