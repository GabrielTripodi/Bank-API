# Banking RESTful API

**Available languages / Lingue disponibili**: [IT](README.md) | [EN](README-en.md)

This repository contains the source code for the **Banking RESTful API**, developed with Flask. This API serves as the backend for the Thunderbird extension [**IBAN Guard**](https://github.com/GabrielTripodi/IBAN-Guard).

The project was created as part of a thesis for the Master's degree in Artificial Intelligence and Computer Science at the University of Calabria. The API simulates a real banking service capable of verifying the ownership of an IBAN code, a fundamental component for preventing fraud related to Business Email Compromise (BEC) attacks.

---

## 🛡️ Goal

Simulate a service provided by a national banking institution, able to verify whether an IBAN code found in an email or its attachment actually belongs to the sender of the message. The goal is to prevent frauds where the IBAN is manipulated by an attacker.

---

## 🏗️ Architecture

The API is designed to be lightweight, secure, and scalable, following REST architectural principles.

* **Backend:** [Flask](https://flask.palletsprojects.com/) (Python)  
* **Database:** [SQLite](https://www.sqlite.org/index.html) (a serverless, file-based relational database)  
* **Admin Interface:** Flask web app + HTML/CSS/JS (Bootstrap, SweetAlert2)  
* **Main Libraries**:  
    * `Flask-Cors`: For managing Cross-Origin Resource Sharing (CORS) policies  
    * `rapidfuzz`: To implement fuzzy string matching, used for verifying IBANs registered to companies  
    * `bcrypt`: For secure hashing of administrator passwords  
    * `Rich`: To enhance the command-line interface of the initialization script  

---

## 📦 Features

* **Intelligent IBAN Verification**: The API can verify IBANs both for **individuals** and **companies**. For companies, it uses a *fuzzy matching* algorithm to tolerate minor variations in names (e.g., "CyberSonic" vs "CyberSonic S.r.l.").  
* **Web Admin Interface**: A simple yet functional web interface ("IBAN Admin Manager") is included for administrators to perform CRUD (Create, Read, Update, Delete) operations on the actual IBAN holders table.  
* **Robust Security**: Multiple security measures have been implemented to protect the API and its data.  
* **Modular Structure**: Code is organized into modules with specific responsibilities (`app.py`, `utils.py`, `db_utils.py`, etc.) to promote maintainability and readability.  
* **Endpoint Versioning**: All endpoints are prefixed with `/api/v1/` to ensure backward compatibility in future updates.  

---

## 🗃️ Database Structure

### `iban_holders`
| Field         | Type         | Description                          |
|---------------|--------------|------------------------------------|
| `id`          | CHAR(36)     | Unique identifier of type UUID v4  |
| `iban`        | CHAR(27)     | IBAN code (27 characters)           |
| `first_name`  | VARCHAR(40) (optional) | Account holder's first name (individual) |
| `last_name`   | VARCHAR(50) (optional) | Account holder's last name (individual)  |
| `company_name`| VARCHAR(80) (optional) | Company name                          |
| `created_at`  | TIMESTAMP    | Record creation date and time       |
| `updated_at`  | TIMESTAMP    | Last modification date and time     |

### `administrators`
| Field        | Type         | Description                           |
|--------------|--------------|-------------------------------------|
| `id`         | CHAR(36)     | Unique identifier of type UUID v4   |
| `username`   | VARCHAR(50)  | Administrator's username             |
| `password`   | CHAR(60)     | Password hash generated with Bcrypt |

---

## 📡 API Endpoints

The API exposes the following main endpoints.

### Public Endpoints (for the IBAN Guard extension)

These endpoints are protected by a restrictive CORS policy allowing requests only from the Thunderbird extension origin.

* `POST /api/v1/sender-iban-verification`  
    * **Purpose**: Automatic verification of the IBAN against the sender's name in an email.  
    * **Request body**: `{"sender": "Sender Name", "iban": "IT..."}`  
    * **Responses**:  
        * `200 OK`: Verification succeeded (positive or negative).  
        * `400 Bad Request`: Invalid input data.  
        * `404 Not Found`: IBAN not found in the database.  
        * `500 Internal Server Error`: Server error.

* `POST /api/v1/iban-verification`  
    * **Purpose**: Manual verification of an IBAN provided by the user.  
    * **Request body (Individual)**: `{"name": "First Name", "surname": "Last Name", "iban": "IT..."}`  
    * **Request body (Company)**: `{"name": "Company Name Srl", "iban": "IT..."}`  
    * **Responses**: Same as the previous endpoint.

### Administrative Endpoints (authentication required)

These endpoints are used by the admin interface for CRUD operations and require an authenticated session.

* `GET /api/v1/ibans`: Retrieve the list of all IBANs and their holders.  
* `POST /api/v1/ibans`: Add a new IBAN and its holder.  
* `PUT /api/v1/ibans/<uuid:iban_id>`: Modify an existing IBAN and/or holder.  
* `DELETE /api/v1/ibans/<uuid:iban_id>`: Delete an IBAN from the database.

---

## 🛠️ Admin Interface

To manage data in the database, you can access the web administration interface.

1. Open your browser and navigate to the login URL. For security reasons, the URL is not standard but deliberately hard to guess:  
   `http://127.0.0.1:5000/admin-HaZiNgTLamSe`  
2. Log in using the administrator credentials created during initialization.  
3. From the dashboard, you can add, edit, or remove IBAN records and their holders.

---

## 🔐 Security Measures

Main implemented security measures include:

* **Strict Input Validation**: All data received by endpoints is validated using regular expressions to prevent malformed data.  
* **SQL Injection Protection**: Database interaction is done exclusively via parameterized queries.  
* **Cross-Origin Resource Sharing (CORS)**: Security mechanism allowing requests only from explicitly authorized origins (such as the Thunderbird extension), preventing unauthorized access from external domains.  
* **Content Security Policy (CSP)**: Restrictive configuration that limits active content sources (scripts, styles, images, etc.) to prevent XSS and other threats.  
* **Secure Authentication**: The admin session is protected by cryptographically signed cookies with `HttpOnly`, `Secure`, and `SameSite="Lax"` flags to prevent tampering and CSRF attacks.  
* **Password Hashing**: Admin passwords are stored in the database hashed with Bcrypt.  
* **HTTP Security Headers**: The API and admin interface include headers like `Strict-Transport-Security`, `X-Frame-Options`, and `X-Content-Type-Options` to enhance client-side security.

---

## 🚀 Installation Guide

Follow these steps to set up and run the API in a local development environment.

### Prerequisites

* Python 3.x  
* `pip` (Python package manager)

### Installation and Setup

1. **Clone the repository**:  
    ```bash
    git clone https://github.com/GabrielTripodi/Banking-API.git
    cd Banking-API
    ```

2. **Create and activate a virtual environment** (recommended):  
    ```bash
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. **Install dependencies**:  
    ```bash
    pip install -r requirements.txt
    ```

4. **Initialize the simulated database**:  
    Run the initialization script. This will create the `BankDatabase.db` file, populate the `iban_holders` table with sample data, and prompt you to create credentials for the first administrator user.  
    ```bash
    python initialize_database.py
    ```  
    Keep the credentials you create; you will need them to access the admin interface.

5. **Start the Flask server**:  
    ```bash
    python app.py
    ```  
    The API will now be running and accessible at `http://localhost:5000`.

---

> ⚠️ Note: This project was developed for academic purposes. The simulated banking API has no legal value and does not access real data.
