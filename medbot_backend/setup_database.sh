#!/bin/bash

# MedBot Database Setup Script
echo "Setting up PostgreSQL database for MedBot..."

# Get current username
CURRENT_USER=$(whoami)

echo "Current user: $CURRENT_USER"

# Option 1: Create database with current user
echo "Creating PostgreSQL user and database..."

# Create PostgreSQL user with same name as system user
sudo -u postgres createuser --interactive --pwprompt $CURRENT_USER

# Create database
sudo -u postgres createdb -O $CURRENT_USER medbot

echo "Database setup complete!"
echo ""
echo "Now update your .env file with these settings:"
echo "DB_NAME=medbot"
echo "DB_USER=$CURRENT_USER"
echo "DB_PASSWORD=your_password_here"
echo "DB_HOST=localhost"
echo "DB_PORT=5432"
echo ""
echo "Or run this command to update .env automatically:"
echo "sed -i 's/DB_USER=postgres/DB_USER=$CURRENT_USER/' .env"
