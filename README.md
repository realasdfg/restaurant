# Restaurant Automation System — Backend

Backend service for a restaurant management system built with FastAPI.

## Features

* JWT authentication and authorization
* Role-based access control
* Menu and category management
* Order management
* Table management
* QR payment support
* Real-time updates via WebSockets
* PostgreSQL integration using SQLAlchemy

## Tech Stack

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* SQLAlchemy
* Alembic
* JWT
* WebSockets

## Getting Started

### Clone the repository

```bash
git clone https://github.com/realasdfg/restaurant.git
cd restaurant
```

### Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file:

```env
DB_URI=your_db_uri
SQLALCHEMY_ENGINE_URI=your_engine_uri
SECRET_KEY=your_secret_key
```

### Apply migrations

```bash
alembic upgrade head
```

### Run the server

```bash
python main.py
```

## API Documentation

After starting the application:

* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

## Main Modules

* Authentication
* User Management
* Menu Management
* Order Processing
* Table Management

## Project Structure

```text
app/
├── models/
├── repositories/
├── routers/
├── schemas/
├── services/
├── utils/
migration/
main.py
```

## License

MIT
