import sqlite3
import random
from datetime import datetime, timezone
from uuid import uuid4

from flask_bcrypt import Bcrypt

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from db_utils import DATABASE

bcrypt = Bcrypt()
console = Console()


def generate_random_timestamp():
    year = random.choice([2023, 2024, 2025])
    if year == 2025:
        month = random.randint(1, 4)
    else:
        month = random.randint(1, 12)
    if month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_day = 29
        else:
            max_day = 28
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:
        max_day = 31
    day = random.randint(1, max_day)
    hour = random.randint(7, 21)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    timestamp = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def create_tables(cursor):
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS iban_holders (id CHAR(36) PRIMARY KEY, iban CHAR(27) UNIQUE NOT NULL, first_name VARCHAR(40), last_name "
        "VARCHAR(40), company_name VARCHAR(80), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS administrators (id CHAR(36) PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL, "
        "password CHAR(60) NOT NULL)")


def populate_iban_holders_table(cursor):
    iban_holders = [
        {"iban": "IT18Y0306905020051014470177", "name": "Luca", "surname": "Moretti"},
        {"iban": "IT83F0760116300001014243537", "name": "Francesca", "surname": "Russo"},
        {"iban": "IT54B0200805351000004968848", "name": "Andrea", "surname": "Romano"},
        {"iban": "IT08J0103081370000063115940", "name": "Elisa", "surname": "Conti"},
        {"iban": "IT87N0100581530000000218000", "name": "Marco", "surname": "De Luca"},
        {"iban": "IT55L0100503215000000011100", "name": "Maria Elena", "surname": "Galli"},
        {"iban": "IT77F0103014217000001113072", "company": "CyberSonic S.r.l."},
        {"iban": "IT39K0100003245350200020060", "company": "New Fashion Style S.p.A."},
        {"iban": "IT92C0306905091100000004583", "company": "Auto Service S.n.c. di Rizzo & C."},
        {"iban": "IT12Y0100003245350200020002", "company": "Costruzioni Ferraro S.p.A."},
        {"iban": "IT03Y0200830180000002168078", "company": "Design & Arredo Pugliese S.a.s."},
        {"iban": "IT35A0760111900000011662327", "company": "Sapori di Casa S.r.l."}
        # {"iban": "IT77F0103014217000001113072", "name": "Luigi Francesco", "surname": "Ricci"},
        # {"iban": "IT39K0100003245350200020060", "name": "Chiara", "surname": "Lo Monaco"},
        # {"iban": "IT92C0306905091100000004583", "name": "Giulia", "surname": "Ferraro"},
        # {"iban": "IT12Y0100003245350200020002", "name": "Matteo", "surname": "Bianchi"},
        # {"iban": "IT03Y0200830180000002168078", "name": "Davide", "surname": "Rizzo"},
        # {"iban": "IT35A0760111900000011662327", "name": "Serena", "surname": "Martini"},
    ]
    for record in iban_holders:
        creation_timestamp = generate_random_timestamp()
        if "name" in record:
            cursor.execute(
                f"INSERT INTO iban_holders (id, iban, first_name, last_name, created_at) VALUES (?, ?, ?, ?, ?)",
                (str(uuid4()), record["iban"], record["name"], record["surname"], creation_timestamp))
        else:
            cursor.execute(f"INSERT INTO iban_holders (id, iban, company_name, created_at) VALUES (?, ?, ?, ?)",
                           (str(uuid4()), record["iban"], record["company"], creation_timestamp))


def initialize_database():
    connection = None
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        create_tables(cursor)
        cursor.execute("SELECT COUNT(*) as total FROM iban_holders")
        records_count = cursor.fetchone()[0]
        if records_count < 1:
            populate_iban_holders_table(cursor)
            # "Paolo_Caruso_3cX6"
            admin_username = Prompt.ask("[bold yellow]Choose a username for the administrator[/bold yellow]")
            print()
            # "DyA7K2u1CZj9"
            admin_password = Prompt.ask("[bold yellow]Choose a strong password for the administrator[/bold yellow]")
            hashed_password = bcrypt.generate_password_hash(admin_password).decode("utf-8")
            cursor.execute("INSERT INTO administrators (id, username, password) VALUES (?, ?, ?)",
                           (str(uuid4()), admin_username, hashed_password))
            connection.commit()
            print()
            console.print(Panel.fit(
                f"[bold cyan]Username:[/bold cyan] {admin_username}\n[bold cyan]Password:[/bold cyan] {admin_password}",
                title="[bold magenta]Admin Credentials[/bold magenta]", padding=(1, 1)))
    except sqlite3.Error as e:
        console.print(f"[bold red]Database initialization failed:[/bold red] {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    initialize_database()
