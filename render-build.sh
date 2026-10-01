#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Building Frontend (React)..."
cd frontend
npm install
npm run build
cd ..

echo "Installing Backend Dependencies..."
cd backend
pip install -r requirements.txt
