#!/bin/bash

# Real Estate Application Startup Script
# This script starts both the frontend and backend servers

# Text color variables
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Real Estate Application Startup ===${NC}"

# Check if .env file exists in backend directory
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}WARNING: No .env file found in backend directory${NC}"
    echo -e "${YELLOW}Using mock Firebase implementation by default${NC}"
    
    # Create minimal .env file for backend
    echo "USE_MOCK_FIREBASE=true" > backend/.env
    echo "API_HOST=127.0.0.1" >> backend/.env
    echo "API_PORT=8000" >> backend/.env
    echo "API_RELOAD=true" >> backend/.env
    echo "ALLOWED_ORIGINS=*" >> backend/.env
    
    echo -e "${YELLOW}Created minimal .env file for development${NC}"
fi

# Start backend server in background
echo -e "${GREEN}Starting backend server...${NC}"
cd backend && python run.py --skip-env-check &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}Backend server running (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}Failed to start backend server${NC}"
    exit 1
fi

# Start frontend in background
echo -e "${GREEN}Starting frontend...${NC}"
cd ../frontend && npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
sleep 5

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}Frontend running (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}Failed to start frontend${NC}"
    kill $BACKEND_PID
    exit 1
fi

echo -e "${GREEN}Both servers are now running!${NC}"
echo -e "${BLUE}Backend:${NC} http://localhost:8000"
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Function to handle shutdown
shutdown() {
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $FRONTEND_PID
    kill $BACKEND_PID
    echo -e "${GREEN}Servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C and call shutdown function
trap shutdown SIGINT

# Keep script running
wait 