# Restaurant Automation System — Backend

Backend service for a restaurant management system built with FastAPI using Onion Architecture.<br>
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
* Statistics

## Screenshots

<img width="1451" height="875" alt="image" src="https://github.com/user-attachments/assets/65496d06-3c9a-41ba-b90f-59a26a898c99" />
<img width="1457" height="768" alt="image" src="https://github.com/user-attachments/assets/2f5a0f58-833a-4ad9-b0e3-b4dbb26a9909" />
<img width="1450" height="550" alt="image" src="https://github.com/user-attachments/assets/a42f1400-20db-4d01-a403-e78273ea0d08" />


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
