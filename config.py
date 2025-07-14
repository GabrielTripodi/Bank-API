import secrets


class Config:
    SECRET_KEY = secrets.token_hex(16)
    SESSION_COOKIE_SAMESITE = "Lax"
    # SESSION_COOKIE_SECURE=True,  # Send cookie only over HTTPS
    CORS_RESOURCES = {
        r"/api/v1/iban-verification": {
            "origins": [r"moz-extension://*"],
            "methods": ["POST"],
            "allow_headers": ["Content-Type"]
        },
        r"/api/v1/sender-iban-verification": {
            "origins": [r"moz-extension://*"],
            "methods": ["POST"],
            "allow_headers": ["Content-Type"]
        },
    }
