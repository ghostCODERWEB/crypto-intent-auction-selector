"""Validate solver offers against deadlines and minimum output and select net output after declared costs."""

from .common import (
    number,
    integer,
    identity,
    records,
    chronology,
    allocate,
    result,
    validate_document,
)
from decimal import Decimal


def _analyze(d):
    now = integer(d["now"])
    minout = integer(d["minimum_output"])
    deadline = integer(d["deadline"])
    offers = []
    for q in records(d["offers"], "id"):
        output = integer(q["output"])
        cost = integer(q["cost"])
        expiry = integer(q["expiry"])
        net = output - cost
        reasons = []
        if now > deadline:
            reasons.append("intent_expired")
        if now > expiry:
            reasons.append("offer_expired")
        if net < minout:
            reasons.append("below_minimum")
        offers.append(
            {
                "id": q["id"],
                "net_output": net,
                "eligible": not reasons,
                "reasons": reasons,
            }
        )
    valid = sorted(
        [q for q in offers if q["eligible"]], key=lambda q: (-q["net_output"], q["id"])
    )
    return {
        "offers": offers,
        "winner": valid[0]["id"] if valid else None,
        "winning_output": valid[0]["net_output"] if valid else 0,
    }


def analyze(document):
    validate_document(document)
    try:
        return result(_analyze(document))
    except (KeyError, TypeError, ArithmeticError, RecursionError) as error:
        raise ValueError("invalid domain input: " + str(error)) from error
