from datetime import datetime, timezone
from uuid import uuid4

from flask import Flask, request, jsonify, render_template, session, redirect, url_for, abort
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import sqlite3

from db_utils import *
from utils import *
from costants import CONTENT_SECURITY_POLICY, ERROR_401_MESSAGE, API_PREFIX, FULL_NAME_PATTERN, COMPANY_NAME_PATTERN

app = Flask(__name__)

app.config.from_object("config.Config")
bcrypt = Bcrypt(app)
cors = CORS(app, resources=app.config["CORS_RESOURCES"])


@app.errorhandler(415)
def handle_415_error(error):
    error_description = "The content type of the request is not supported."
    return render_template("error_415.html", code=error.code, name=error.name, description=error_description), 415


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = CONTENT_SECURITY_POLICY
    return response


@app.route("/add-iban")
def add_iban_page():
    if "admin_id" not in session:
        abort(401, ERROR_401_MESSAGE)
    return render_template("add_iban.html")


def get_all_ibans():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        iban_records = selection_query_db(conn, "SELECT id, iban, first_name, last_name, company_name FROM iban_holders")

        def snake_to_camel(snake_str):
            words = snake_str.split('_')
            return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

        result = [{snake_to_camel(key): value for key, value in dict(iban).items()} for iban in iban_records]
        return jsonify(result), 200
    except sqlite3.Error as e:
        app.logger.error(f"Error executing query: {e}")
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        close_connection(conn)


def add_iban():
    data = request.json
    person_or_company_name, surname, iban = parse_input_data(data)
    error = validate_input(person_or_company_name, surname, iban)
    if error:
        return jsonify({"error": error}), 400
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        result = selection_query_db(conn, "SELECT * FROM iban_holders WHERE iban = ?", (iban,), one=True)
        if result:
            return jsonify({"error": "IBAN inserted already exists"}), 409
        if surname:
            action_query_db(conn, "INSERT INTO iban_holders (id, iban, first_name, last_name) VALUES (?, ?, ?, ?)",
                            (str(uuid4()), iban, person_or_company_name, surname))
        else:
            person_or_company_name = normalize_company_legal_form(person_or_company_name)
            action_query_db(conn, "INSERT INTO iban_holders (id, iban, company_name) VALUES (?, ?, ?)",
                            (str(uuid4()), iban, person_or_company_name))
        return jsonify({"message": "IBAN has been added successfully"}), 201
    except sqlite3.Error as e:
        app.logger.error(f"Error executing query: {e}")
        rollback_transaction(conn)
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        close_connection(conn)


@app.route(f"{API_PREFIX}/ibans", methods=["GET", "POST"])
def get_or_add_ibans():
    if "admin_id" not in session:
        abort(401, ERROR_401_MESSAGE)
    if request.method == "GET":
        return get_all_ibans()
    return add_iban()


@app.route("/remove-iban")
def remove_iban_page():
    if "admin_id" not in session:
        abort(401, ERROR_401_MESSAGE)
    return render_template("remove_iban.html")


@app.route("/modify-iban")
def modify_iban_page():
    if "admin_id" not in session:
        abort(401, ERROR_401_MESSAGE)
    return render_template("modify_iban.html")


def remove_iban(iban_id):
    error = validate_iban_id(iban_id)
    if error:
        return jsonify({"error": error}), 400
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        result = selection_query_db(conn, "SELECT * FROM iban_holders", one=True)
        if not result:
            return jsonify({"error": "There is no iban to remove"}), 404
        action_query_db(conn, "DELETE FROM iban_holders WHERE id = ?", (iban_id,))
        return jsonify({"message": "IBAN has been removed successfully"}), 200
    except sqlite3.Error as e:
        app.logger.error(f"Error executing query: {e}")
        rollback_transaction(conn)
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        close_connection(conn)


def modify_iban(old_iban_id):
    data = request.json
    person_or_company_name, surname, new_iban = parse_input_data(data)
    error = validate_input(person_or_company_name, surname, new_iban, old_iban_id)
    if error:
        return jsonify({"error": error}), 400
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        result = selection_query_db(conn, "SELECT * FROM iban_holders", one=True)
        if not result:
            return jsonify({"error": "There is no iban to modify"}), 404
        result = selection_query_db(conn, "SELECT * FROM iban_holders WHERE id = ?", (old_iban_id,), one=True)
        old_iban = result[1] if result else None
        if old_iban != new_iban:
            new_iban_result = selection_query_db(conn, "SELECT * FROM iban_holders WHERE iban = ?", (new_iban,), one=True)
            if new_iban_result:
                return jsonify({"error": "IBAN inserted already exists"}), 409
        if result:
            if not has_iban_record_changed(result, person_or_company_name, surname, new_iban):
                return jsonify({"message": "No changes have been made"}), 200
            update_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            if result[2] and result[3] and surname:
                action_query_db(conn,
                                "UPDATE iban_holders SET first_name = ?, last_name = ?, iban = ?, updated_at = ? WHERE iban = ?",
                                (person_or_company_name, surname, new_iban, update_timestamp, old_iban))
            elif result[4] and not surname:
                action_query_db(conn,
                                "UPDATE iban_holders SET company_name = ?, iban = ?, updated_at = ? WHERE iban = ?",
                                (person_or_company_name, new_iban, update_timestamp, old_iban))
        return jsonify({"message": "IBAN has been modified successfully"}), 200
    except sqlite3.Error as e:
        app.logger.error(f"Error executing query: {e}")
        rollback_transaction(conn)
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        close_connection(conn)


@app.route(f"{API_PREFIX}/ibans/<uuid:iban_id>", methods=["PUT", "DELETE"])
def remove_or_modify_iban(iban_id):
    if "admin_id" not in session:
        abort(401, ERROR_401_MESSAGE)
    iban_id = str(iban_id)
    if request.method == "DELETE":
        return remove_iban(iban_id)
    return modify_iban(iban_id)


@app.route(f"{API_PREFIX}/iban-verification", methods=["POST"])
def verify_iban():
    data = request.json
    person_or_company_name, surname, iban = parse_input_data(data)
    error = validate_input(person_or_company_name, surname, iban)
    if error:
        return jsonify({"error": error}), 400
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        result = selection_query_db(conn, "SELECT * FROM iban_holders WHERE iban=?", (iban,), one=True)
        if not result:
            return jsonify({"error": "IBAN not found"}), 404
        person_or_company_name = to_lower(person_or_company_name)
        if result[2] and result[3]:
            db_first_name, db_last_name = to_lower(result[2]), to_lower(result[3])
            if db_first_name == person_or_company_name and db_last_name == to_lower(surname):
                return jsonify({"message": "IBAN matches"}), 200
            return jsonify({"message": "IBAN does not match"}), 200
        db_company_name = to_lower(result[4])
        if not surname and are_company_names_similar(person_or_company_name, db_company_name):
            if is_correct_input_legal_form(person_or_company_name, db_company_name):
                return jsonify({"message": "IBAN matches"}), 200
        return jsonify({"message": "IBAN does not match"}), 200
    except sqlite3.Error as e:
        app.logger.error(f"Error executing query: {e}")
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        close_connection(conn)


@app.route(f"{API_PREFIX}/sender-iban-verification", methods=["POST"])
def verify_sender_iban():
    data = request.json
    sender_name, iban = parse_sender_data(data)
    error = validate_iban(iban)
    if error:
        return jsonify({"error": error}), 400
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        result = selection_query_db(conn, "SELECT * FROM iban_holders WHERE iban = ?", (iban,), one=True)
        if not result:
            return jsonify({"error": "IBAN not found"}), 404
        if result[2] and result[3]:
            if not (regex.fullmatch(FULL_NAME_PATTERN, sender_name) or regex.fullmatch(COMPANY_NAME_PATTERN, sender_name)):
                return jsonify({"error": "Sender name is not valid"}), 400
            db_first_name, db_last_name = to_lower(result[2]), to_lower(result[3])
            if db_first_name in to_lower(sender_name) and db_last_name in to_lower(sender_name):
                return jsonify({"message": "IBAN matches"}), 200
            return jsonify({"message": "IBAN does not match"}), 200
        if not regex.fullmatch(COMPANY_NAME_PATTERN, sender_name):
            return jsonify({"error": "Sender name is not valid"}), 400
        db_company_name = to_lower(result[4])
        if are_company_names_similar(to_lower(sender_name), db_company_name):
            return jsonify({"message": "IBAN matches"}), 200
        return jsonify({"message": "IBAN does not match"}), 200
    except sqlite3.Error as e:
        app.logger.error(f"Error executing query: {e}")
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        close_connection(conn)


@app.route("/admin-HaZiNgTLamSe", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        username = str(data["username"])
        password = str(data["password"])
        conn = None
        try:
            conn = sqlite3.connect(DATABASE)
            admin = selection_query_db(conn, "SELECT * FROM administrators WHERE username = ?", (username,), one=True)
            if admin and bcrypt.check_password_hash(admin[2], password):
                session["admin_id"] = admin[0]
                return jsonify({"message": "Login successful"}), 200
            return jsonify({"error": "Invalid username or password"}), 400
        except sqlite3.Error as e:
            app.logger.error(f"Error executing query: {e}")
            return jsonify({"error": "Something went wrong"}), 500
        finally:
            close_connection(conn)
    if "admin_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout-mPAcTuGbItYR")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    if "admin_id" not in session:
        abort(401, ERROR_401_MESSAGE)
    return render_template("home.html")


if __name__ == '__main__':
    app.run(host="localhost", debug=True)
