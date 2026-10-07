"""Relation extraction between entities."""
from __future__ import annotations

import logging

from shared.schemas import Entity, Relation

logger = logging.getLogger(__name__)


def extract_relations(text: str, entities: list[Entity]) -> list[Relation]:
    """Extract simple relations between entities via rules."""
    relations: list[Relation] = []

    by_type: dict[str, list[Entity]] = {}
    for e in entities:
        by_type.setdefault(e.type, []).append(e)

    parties = by_type.get("PARTY", [])
    amounts = by_type.get("AMOUNT", [])
    dates = by_type.get("DATE", [])
    invoices = by_type.get("INVOICE_ID", [])

    # Party owes Amount
    for party in parties:
        for amount in amounts:
            relations.append(
                Relation(
                    source=party.text,
                    relation="OWES",
                    target=amount.text,
                    confidence=0.7,
                )
            )

    # Party pays by Date
    for party in parties:
        for date in dates:
            relations.append(
                Relation(
                    source=party.text,
                    relation="PAYS_BY",
                    target=date.text,
                    confidence=0.7,
                )
            )

    # Party issued Invoice
    for party in parties:
        for inv in invoices:
            relations.append(
                Relation(
                    source=party.text,
                    relation="ISSUED",
                    target=inv.text,
                    confidence=0.7,
                )
            )

    logger.debug("extracted %d relations", len(relations))
    return relations