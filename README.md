# Real Estate Marketplace

A full-stack real estate marketplace built with Next.js, FastAPI, and Firebase.

## Features

- Property listing and search
- Property details view
- Filter properties by type, price, and location
- Responsive design
- Modern UI with Tailwind CSS

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React Query (for data fetching)

### Backend
- FastAPI
- Python 3.11+
- Firebase (Firestore)
- Pydantic

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Firebase account and credentials

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/real-estate.git
cd real-estate
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Create a `.env` file in the backend directory:
```env
FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json
```

5. Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
real-estate/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── hooks/
│   │   └── services/
│   └── package.json
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 