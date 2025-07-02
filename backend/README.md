# Real Estate Backend API

This is the backend API for the Real Estate application built with FastAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload
# or use the run script:
python run.py --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### Properties

- `GET /api/v1/properties/` - List all properties
- `GET /api/v1/properties/{property_id}` - Get a specific property
- `POST /api/v1/properties/` - Create a new property
- `PUT /api/v1/properties/{property_id}` - Update a property
- `DELETE /api/v1/properties/{property_id}` - Delete a property 

