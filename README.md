# Tales Hotel — Booking & Payment System
### "Where Luxury Meets Comfort"

A full Django web application for hotel booking and payment management.

---

## Quick Start

### 1. Install dependencies
```bash
pip install django pillow
```

### 2. Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed sample data (rooms, admin, demo guest)
```bash
python manage.py seed_data
```

### 4. Run the server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## Default Login Credentials

| Role  | Username | Password   |
|-------|----------|------------|
| Admin | admin    | admin1234  |
| Guest | guest1   | guest1234  |

---

## System Features

| # | Feature | URL |
|---|---------|-----|
| 1 | Guest Registration & Login | /register/, /login/ |
| 2 | Room Browsing & Booking | /rooms/, /rooms/<id>/book/ |
| 3 | Room Availability Schedule | /admin-panel/schedule/ |
| 4 | Booking Approval/Cancellation | /admin-panel/bookings/ |
| 5 | Admin Management Dashboard | /admin-panel/ |
| 6 | Guest Stay History & Notes | /my-history/, /admin-panel/guests/<id>/ |
| 7 | Contact & Feedback Form | /contact/ |

---

## Project Structure

```
tales_hotel/
├── tales_hotel/          ← Project settings
│   ├── settings.py
│   └── urls.py
├── bookings/             ← Main application
│   ├── models.py         ← 7 database models
│   ├── views.py          ← All views (guest + admin)
│   ├── forms.py          ← All forms
│   ├── urls.py           ← URL routing
│   ├── admin.py          ← Django admin config
│   ├── templates/        ← All HTML templates
│   └── management/       ← Custom management commands
│       └── commands/
│           └── seed_data.py
├── static/               ← CSS, JS
├── media/                ← Uploaded images
├── db.sqlite3            ← Database (auto-created)
└── manage.py
```

---

## Technology Stack
- **Backend:** Django 4.x (Python)
- **Frontend:** Django Templates + Bootstrap 5 + Custom CSS
- **Database:** SQLite3
- **Fonts:** Cormorant Garamond + Montserrat (Google Fonts)

---

## Coursework Details
- **Assignment:** Coursework 4 — Case Scenario B
- **System:** Hotel Booking and Payment System
- **Hotel Name:** Tales Hotel — Where Luxury Meets Comfort
- **Framework:** Django only (no DRF)
- **Database:** SQLite (via Django ORM)
