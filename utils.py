import re
import regex
from rapidfuzz import fuzz

from costants import IBAN_PATTERN, LEGAL_FORMS, COMPANY_NAME_PATTERN, FIRST_NAME_PATTERN, LAST_NAME_PATTERN, \
    LEGAL_FORMS_PATTERN, UUID_V4_PATTERN


def close_connection(connection):
    if connection:
        connection.close()


def rollback_transaction(connection):
    if connection:
        connection.rollback()


def remove_spaces(input_string, input_field="iban"):
    if input_field == "iban":
        return re.sub(r"\s+", "", input_string)
    return re.sub(r"\s{2,}", " ", input_string).strip()


def is_valid_iban(iban):
    rearranged_iban = iban[4:] + iban[:4]
    remainder = 0

    for i in range(len(rearranged_iban)):
        char_code = ord(rearranged_iban[i])
        if 48 <= char_code <= 57:
            numeric_value = char_code - 48
        else:
            numeric_value = char_code - 55

        if numeric_value > 9:
            remainder = (100 * remainder + numeric_value) % 97
        else:
            remainder = (10 * remainder + numeric_value) % 97

    return remainder == 1


def parse_input_data(data):
    person_or_company_name = remove_spaces(str(data["name"]), "name")
    surname = remove_spaces(str(data["surname"]), "surname") if "surname" in data else None
    iban = remove_spaces(str(data["iban"])).upper()
    return person_or_company_name, surname, iban


def parse_sender_data(data):
    sender_name = remove_spaces(str(data["sender"]), "sender")
    iban = remove_spaces(str(data["iban"]))
    return sender_name, iban


def validate_input(person_or_company_name, surname, iban, old_iban_id=None):
    if surname is not None:
        if person_or_company_name == "" or surname == "" or iban == "":
            return "All fields are required"
        if not regex.fullmatch(FIRST_NAME_PATTERN, person_or_company_name):
            return "Name is not valid"
        if not regex.fullmatch(LAST_NAME_PATTERN, surname):
            return "Surname is not valid"
    else:
        if person_or_company_name == "" or iban == "":
            return "Company name and IBAN are required"
        if not regex.fullmatch(COMPANY_NAME_PATTERN, person_or_company_name):
            return "Company name is not valid"

    if not re.fullmatch(IBAN_PATTERN, iban) or not is_valid_iban(iban):
        return "IBAN is not valid"

    if old_iban_id is not None:
        if not re.fullmatch(UUID_V4_PATTERN, old_iban_id):
            return "IBAN id is not valid"
    return ""


def validate_iban_id(iban_id):
    if not re.fullmatch(UUID_V4_PATTERN, iban_id):
        return "IBAN id is not valid"
    return ""


def validate_iban(iban):
    if not re.fullmatch(IBAN_PATTERN, iban) or not is_valid_iban(iban):
        return "IBAN is not valid"
    return ""


def normalize_company_legal_form(person_or_company_name):
    def add_dots(match):
        return ".".join(match.group(1)) + "."

    return re.sub(LEGAL_FORMS_PATTERN, add_dots, person_or_company_name, flags=re.IGNORECASE)


def has_iban_record_changed(record, person_or_company_name, surname, new_iban):
    db_iban = record[1]
    if record[2] and record[3]:
        db_first_name = record[2]
        db_last_name = record[3]
        if person_or_company_name != db_first_name or surname != db_last_name or new_iban != db_iban:
            return True
    if record[4]:
        db_company_name = record[4]
        if person_or_company_name != db_company_name or new_iban != db_iban:
            return True
    return False


def to_lower(string):
    return string.casefold() if string is not None else None


def extract_legal_form(company_name):
    for pattern in LEGAL_FORMS:
        match = re.search(pattern, company_name, re.IGNORECASE)
        if match:
            return match.group(0).replace(".", "").casefold()
    return None


def is_correct_input_legal_form(input_company_name, db_company_name):
    input_legal_form = extract_legal_form(input_company_name)
    if not input_legal_form:
        return True
    registered_legal_form = extract_legal_form(db_company_name)
    return input_legal_form == registered_legal_form


def strip_company_partners(db_company_name):
    cleaned_company_name = regex.sub(r"\bdi\b[\p{L} '’\-]+(&\sc.)?$", "", db_company_name, flags=re.IGNORECASE)
    return cleaned_company_name


def compute_similarity_score(input_company_name, db_company_name):
    ratio = fuzz.ratio(input_company_name, db_company_name)
    partial_ratio = fuzz.partial_ratio(input_company_name, db_company_name)
    weighted_ratio = fuzz.WRatio(input_company_name, db_company_name)
    weighted_score = (0.4 * ratio + 0.2 * partial_ratio + 0.4 * weighted_ratio)
    return round(weighted_score)


def are_company_names_similar(input_company_name, db_company_name):
    full_name_score = compute_similarity_score(input_company_name, db_company_name)
    if full_name_score >= 85:
        return True
    stripped_company_name = to_lower(strip_company_partners(db_company_name))
    if stripped_company_name != db_company_name:
        stripped_name_score = compute_similarity_score(input_company_name, stripped_company_name)
        if stripped_name_score >= 85:
            return True
    return False

