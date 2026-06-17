# Restaurant Automation System — Backend
<img width="1483" height="560" alt="image" src="https://github.com/user-attachments/assets/faa30b9b-c51c-4f81-9200-9c1f46227b56" />
<img width="1479" height="774" alt="image" src="https://github.com/user-attachments/assets/091a3694-c8fe-42ed-af60-29e07b1458b9" />
<img width="1468" height="817" alt="image" src="https://github.com/user-attachments/assets/02100ac1-f32c-47fa-a606-66c8977cb1e6" />

Backend service for a restaurant management system built with FastAPI.<br>
[Frontend Repository](https://github.com/realasdfg/restaurant_frontend)

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
