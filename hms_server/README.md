# Hotel Management System

## Overview

The Hotel Management System is a comprehensive API designed to manage various aspects of hotel operations, including user authentication, customer management, room reservations, transactions, room services, and analytics.

## Features

- **User Authentication**: Register and login users with JWT-based authentication.
- **Customer Management**: Create, read, update, and delete customer information.
- **Room Management**: Manage room details and availability.
- **Reservation Management**: Create, read, update, and delete reservations.
- **Transaction Management**: Handle transactions related to reservations.
- **Room Services**: Manage room service items and orders.
- **Analytics**: Generate and retrieve hotel analytics.

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **JWT**: JSON Web Tokens for authentication.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **PostgreSQL**: Database for storing application data.    

## API Endpoints

### User Authentication

- **Register a new user**: `POST /register`
- **Login to get an access token**: `POST /login`

### Customer Management

- **Create a new customer**: `POST /customers/`
- **Get all customers**: `GET /customers/`

### Room Management

- **Create a new room**: `POST /rooms/`
- **Get all rooms**: `GET /rooms/`
- **Update a room**: `PUT /rooms/{room_id}`

### Reservation Management

- **Create a new reservation**: `POST /reservations/`
- **Get all reservations**: `GET /reservations/`
- **Update a reservation**: `PUT /reservations/{reservation_id}`

### Transaction Management

- **Create a new transaction**: `POST /transactions/`
- **Get all transactions**: `GET /transactions/`

### Room Services

- **Create a new room service item**: `POST /room-services/items/`
- **Get all room service items**: `GET /room-services/items/`
- **Create a new room service order**: `POST /room-services/orders/`
- **Get all room service orders**: `GET /room-services/orders/`

### Billing

- **Get reservation bill**: `GET /reservations/{reservation_id}/bill`

### Security

- **Get user details**: `GET /secure/users`
- **Admin only endpoint**: `POST /secure/admin-only-endpoint`

### Analytics

- **Get hotel analytics**: `GET /analytics`

### Health Check

- **Health check**: `GET /health`