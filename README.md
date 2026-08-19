# HealthForge AI - Merged Role-Based Application

This project merges:
- HealthForge2 patient portal (Flask + SQLite + SQLAlchemy)
- HealthForge AI doctor portal
- A receptionist portal

## Flow

Run the app and open `/`.

1. Choose Patient, Doctor, or Receptionist.
2. Log in for that role.
3. The correct dashboard opens.

## Demo credentials

Doctor:
- Email: `doctor@healthforge.ai`
- Password: `doctor123`

Receptionist:
- Email: `receptionist@healthforge.ai`
- Password: `reception123`

Patient:
- Register a patient account from the Patient login page.
- Existing patient data remains in `instance/healthforge.db`.

## Important

The old `venv` folders were intentionally removed. Create one fresh virtual environment on your computer.
