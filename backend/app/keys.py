"""License key generation and offline format checking.

Key format:  SKU-XXXXX-XXXXX-XXXXX-CCCCC

The three XXXXX groups are random characters; CCCCC is an HMAC of the SKU and
random part. That lets us reject typos and forged keys before touching the
database, while the database stays the source of truth for status.
"""

import hashlib
import hmac
import re
import secrets

# Crockford-style alphabet: no I, L, O, U, so keys are easy to read aloud.
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
GROUP_LEN = 5
RANDOM_GROUPS = 3

KEY_PATTERN = re.compile(
    rf"^(?P<sku>[A-Z0-9]{{2,16}})-(?P<body>(?:[{ALPHABET}]{{{GROUP_LEN}}}-){{{RANDOM_GROUPS}}})"
    rf"(?P<check>[{ALPHABET}]{{{GROUP_LEN}}})$"
)


def _checksum(sku: str, body: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), f"{sku}-{body}".encode(), hashlib.sha256).digest()
    return "".join(ALPHABET[b % len(ALPHABET)] for b in digest[:GROUP_LEN])


def normalize(key: str) -> str:
    return key.strip().upper()


def generate_key(sku: str, secret: str) -> str:
    sku = sku.upper()
    groups = ["".join(secrets.choice(ALPHABET) for _ in range(GROUP_LEN)) for _ in range(RANDOM_GROUPS)]
    body = "-".join(groups)
    return f"{sku}-{body}-{_checksum(sku, body, secret)}"


def is_well_formed(key: str, secret: str) -> bool:
    """True if the key has the right shape and a valid checksum."""
    match = KEY_PATTERN.match(normalize(key))
    if not match:
        return False
    body = match["body"].rstrip("-")
    expected = _checksum(match["sku"], body, secret)
    return hmac.compare_digest(expected, match["check"])
