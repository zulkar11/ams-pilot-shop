"""Shipping quotes for the pilot shop."""

# Flat rate per country, in USD, for the first kilogram.
RATES = {
    "US": 5.00,
    "CA": 7.50,
    "GB": 9.00,
    "DE": 9.00,
    "JP": 12.00,
}

# Each kilogram after the first.
PER_EXTRA_KG = 1.50

# Orders at or above this subtotal ship free inside the US.
FREE_SHIPPING_US = 100.00

# Countries without their own rate ship at the international rate.
INTERNATIONAL = 15.00


def base_rate(country: str) -> float:
    return RATES.get(country, INTERNATIONAL)


def quote(order: dict) -> float:
    """The shipping cost of ``order``: ``{"country", "weight_kg", "subtotal"}``."""
    country = order["country"].upper()
    if country == "US" and order.get("subtotal", 0) >= FREE_SHIPPING_US:
        return 0.0
    extra_kg = max(0.0, float(order.get("weight_kg", 1)) - 1)
    return round(base_rate(country) + extra_kg * PER_EXTRA_KG, 2)
