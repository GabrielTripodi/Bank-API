API_PREFIX = "/api/v1"

CONTENT_SECURITY_POLICY = "default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " \
                          "script-src 'self' 'sha256-QJamAcIceIM9NR8F7WkzTuJx2U9cAgS1aqV/jjjfk8Q=' " \
                          "'sha256-1NO0GGtrRFTLlCsqy+i+Ff+7Y5QQYIuf9erhVGUmUlk='; font-src https://fonts.gstatic.com; " \
                          "object-src 'none'; frame-src 'none'; base-uri 'none'; "
# "img-src 'self' data:; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none';"

IBAN_PATTERN = r"IT[0-9]{2}[A-Z]{1}[0-9]{10}[A-Z0-9]{12}"

COMPANY_NAME_PATTERN = r"[\p{L} \d'’\-&.,]{1,80}"

FIRST_NAME_PATTERN = r"[\p{L} '’\-]{1,40}"

LAST_NAME_PATTERN = r"[\p{L} '’\-]{1,50}"

FULL_NAME_PATTERN = r"[\p{L} '’\-]{1,90}"

UUID_V4_PATTERN = r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}"

LEGAL_FORMS_PATTERN = r"\b(ss|snc|sas|spa|srls|srl|sapa)\b"

LEGAL_FORMS = [
    r"\bs\.?s\.?\b", r"\bs\.?n\.?c\.?\b", r"\bs\.?a\.?s\.?\b", r"\bs\.?p\.?a\.?\b", r"\bs\.?r\.?l\.?s\.?\b",
    r"\bs\.?r\.?l\.?\b", r"\bs\.?a\.?p\.?a\.?\b"
]

ERROR_401_MESSAGE = "You must log in with valid credentials to access the URL requested."
