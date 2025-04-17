# Manage My Business - Backend

Django REST API backend for the Manage My Business app. Handles authentication, user roles, and CRUD operations for clients, employees, and tasks.

## Features

- JWT-based authentication
- Role-based access control
- RESTful API endpoints for business entities
- PostgreSQL integration
- Secure and scalable backend architecture

## Tech Stack

- Django
- Django REST Framework
- PostgreSQL
- JWT

## Getting Started

1. Clone the repo:
```bash
git clone https://github.com/yourusername/manage-my-business-backend.git
```

2. Set up virtual environment:
```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r req.txt
```

4. Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

- `POST /api/auth/login/` – Login
- `GET /api/clients/` – List clients
- `POST /api/employees/` – Create employee
- `PUT /api/tasks/<id>/` – Update task

## Author

Essam Eldin Ali  [GitHub](https://github.com/3ssam-ali-98)

Abd-Allah Reda   [GitHub](https://github.com/3ssam-ali-98)

Hosam Ahmed      [GitHub](https://github.com/3ssam-ali-98)

Youstina William [GitHub](https://github.com/3ssam-ali-98)
