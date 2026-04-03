# CANTEEN_WEBSITE - Smart Food Ordering System

## Overview
A Flask-based smart canteen food ordering system that allows users to browse the menu, add items to a cart, and place orders.

## Tech Stack
- **Language:** Python 3.11
- **Framework:** Flask
- **Database:** SQLite (via Flask-SQLAlchemy)
- **Frontend:** Jinja2 templates + vanilla CSS/JS
- **Port:** 5000

## Project Structure
```
app.py              # Main Flask application
templates/          # Jinja2 HTML templates
  base.html         # Base layout with navbar
  index.html        # Menu/home page
  cart.html         # Shopping cart
  checkout.html     # Checkout form
  order_confirmation.html  # Order success page
  orders.html       # All orders list
static/
  css/style.css     # Application styles
instance/
  canteen.db        # SQLite database (auto-created)
```

## Features
- Browse food menu by category (Meals, Breakfast, Snacks, Beverages)
- Filter items by category
- Add/remove items from cart (session-based)
- Checkout with customer name
- Order confirmation and order history

## Running the App
```bash
python app.py
```
Runs on `0.0.0.0:5000`.

## Sample Data
The database is seeded with 12 sample menu items on first run.

## Dependencies
- flask
- flask-sqlalchemy
- flask-login
