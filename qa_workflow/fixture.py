"""System under test, deliberately independent of the review oracle."""

import re
from decimal import Decimal


def submit_batch(payments: list[dict], *, seeded_bug=False) -> dict:
    if not 1 <= len(payments) <= 100:
        return {"status": 422, "imported": 0}
    seen = set()
    for p in payments:
        ref, amount, currency = p["reference"], p["amount"], p["currency"]
        valid = bool(re.fullmatch(r"[A-Za-z0-9_-]{1,40}", ref)) and ref not in seen
        valid = (
            valid
            and bool(re.fullmatch(r"[0-9]{1,7}\.[0-9]{2}", amount))
            and currency == "GBP"
        )
        if not valid:
            return {"status": 422, "imported": 0}
        value = Decimal(amount)
        lower = Decimal("0.00") if seeded_bug else Decimal("0.01")
        if not lower <= value <= Decimal("1000000.00"):
            return {"status": 422, "imported": 0}
        seen.add(ref)
    return {"status": 201, "imported": len(payments)}
