# api_client/config.py
# All tuneable constants. No logic lives here.

MAX_RETRIES: int = 5
BACKOFF_BASE: int = 1  # seconds; delay = BACKOFF_BASE * 2 ** attempt
MAXLAG_HEADER: str = "Retry-After"
