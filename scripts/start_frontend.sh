#!/bin/bash
# SarkariBot Frontend Development Server

echo "Starting SarkariBot Frontend..."

cd "/home/lavku/govt/sarkaribot/frontend"

echo "Installing dependencies..."
npm install

echo "Building frontend..."
npm run build

echo "Starting frontend server on http://localhost:3000"
npx serve -s build -p 3000
