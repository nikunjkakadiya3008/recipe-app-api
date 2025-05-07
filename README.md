# Recipe-App-Api

Recipe-App-Api is a backend API built with Django Rest Framework that allows users to add and manage recipes. Each recipe includes a name, ingredients, tags, category, image, and preparation time.

## Features

- Add and retrieve recipes
- Each recipe includes:
  - Name
  - Ingredients
  - Tags
  - Category
  - Image upload
  - Preparation time

## Technologies Used

- Python 3.x
- Django
- Django REST Framework
- SQLite (or your configured database)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Recipe-App-Api.git
cd Recipe-App-Api
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv env
source env/bin/activate  # For Linux/Mac
env\Scripts\activate     # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

- API documentation is available via Swagger UI at `http://127.0.0.1:8000/api/docs/`

## License

This project is licensed under the MIT License.

## Author

- Nikunj Kakadiya
