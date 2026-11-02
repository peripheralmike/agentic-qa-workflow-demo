"""Executable specification checks. Never trusts generated assertions or code."""

import re
from .models import Plan

REQUIRED = {
    "minimum",
    "maximum",
    "zero",
    "precision",
    "currency",
    "duplicate",
    "empty",
    "atomicity",
}


def expected(payments):
    # Integer-pence oracle deliberately differs from the Decimal-based SUT.
    seen = set()
    if not 1 <= len(payments) <= 100:
        return 422, 0
    for p in payments:
        if (
            not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", p.reference)
            or p.reference in seen
            or p.currency != "GBP"
        ):
            return 422, 0
        if not re.fullmatch(r"[0-9]{1,7}\.[0-9]{2}", p.amount):
            return 422, 0
        whole, fraction = p.amount.split(".")
        if not 1 <= int(whole) * 100 + int(fraction) <= 100000000:
            return 422, 0
        seen.add(p.reference)
    return 201, len(payments)


def coverage(s):
    tags = set()
    values = [p.amount for p in s.payments]
    if s.expected_status == 201:
        if "0.01" in values:
            tags.add("minimum")
        if "1000000.00" in values:
            tags.add("maximum")
    if not s.payments:
        tags.add("empty")
    if s.expected_status == 422:
        if "0.00" in values:
            tags.add("zero")
        if any(re.fullmatch(r"[0-9]+\.[0-9]{3,}", v) for v in values):
            tags.add("precision")
        if any(p.currency != "GBP" for p in s.payments):
            tags.add("currency")
        if len({p.reference for p in s.payments}) < len(s.payments):
            tags.add("duplicate")
        if (
            len(s.payments) > 1
            and any(expected([p])[0] == 201 for p in s.payments)
            and any(expected([p])[0] == 422 for p in s.payments)
        ):
            tags.add("atomicity")
    return tags


def review_plan(plan: Plan):
    accepted, rejected, seen, tags = [], [], set(), set()
    for s in plan.scenarios:
        reason = None
        if s.id in seen:
            reason = "Duplicate scenario id"
        elif (s.expected_status, s.expected_imported) != expected(s.payments):
            reason = "Expected result contradicts the executable specification"
        seen.add(s.id)
        if reason:
            rejected.append({"id": s.id, "reason": reason})
        else:
            accepted.append(s)
            tags |= coverage(s)
    missing = sorted(REQUIRED - tags)
    return accepted, {
        "accepted": [s.id for s in accepted],
        "rejected": rejected,
        "missing_coverage": missing,
        "executable": not missing,
    }
