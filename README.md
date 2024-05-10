# Vendor Management System API

Vendor Management System API is a Django-based system for managing vendors.

## Installation Guide

Follow these steps to set up and run the project on your local machine.

### 1. Create a Virtual Environment

Create a virtual environment to manage dependencies and keep your system clean.

On Windows:

python3 -m venv .venv

On Unix or MacOS:

python3 -m venv .venv

rename .sample_env to .env

### 2. Activate the Virtual Environment

Activate the virtual environment using the following command:

On Windows:

.venv\Scripts\activate

On Unix or MacOS:

source .venv/bin/activate

### 3. Install Dependencies

Install the dependencies using the following command:

pip install -r requirements.txt

### 4. Run Migrations

Run migrations to create the database schema:

python manage.py makemigrations
python manage.py migrate

### 5. Create Superuser (Optional but Recommended)

Create a superuser to access the Django admin panel:

python manage.py createsuperuser

### 6. Start the Server

Start the Django server (default port 8000):

python manage.py runserver

### 7. Running Tests

Pytest is used to implement testing. In the project directory, run the following command to execute tests:

pytest

This will run all the tests implemented in the project.
