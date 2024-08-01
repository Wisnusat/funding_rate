#!/bin/sh

# Run migrations
flask db init
flask db migrate -m "Initial migration."
flask db upgrade

# Start the Flask application
flask run --host=0.0.0.0 --port=8000
