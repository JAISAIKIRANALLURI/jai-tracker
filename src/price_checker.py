"""Scheduled price checker — runs every 6 hours via GitHub Actions."""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from storage import load, save
from amadeus_client import get_cheapest_price
from notifier import send_baseline, send_price_drop


def main():
    data = load()
    now = datetime.now(timezone.utc)

    active_routes = []
    for route in data["routes"]:
        expires_at = datetime.fromisoformat(route["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            print(f"[{route['id']}] Expired — removing {route['from']}→{route['to']}")
            continue

        active_routes.append(route)
        _check_route(route)

    data["routes"] = active_routes
    save(data)
    print(f"\nDone. {len(active_routes)} active route(s).")


def _check_route(route):
    label = f"[{route['id']}] {route['from']}→{route['to']} {route['departure_date']}"
    try:
        price = get_cheapest_price(
            route["from"],
            route["to"],
            route["departure_date"],
            route.get("return_date"),
        )
    except Exception as e:
        print(f"{label} ERROR: {e}")
        return

    if price is None:
        print(f"{label} No offers returned.")
        return

    if route["baseline_price"] is None:
        route["baseline_price"] = price
        route["last_price"] = price
        send_baseline(route, price)
        print(f"{label} Baseline set: ${price:.2f}")
        return

    baseline = route["baseline_price"]
    route["last_price"] = price

    if price < baseline:
        drop_pct = (baseline - price) / baseline * 100
        send_price_drop(route, price, baseline)
        print(f"{label} PRICE DROP: ${baseline:.2f} → ${price:.2f} ({drop_pct:.1f}% off) — alert sent!")
    else:
        print(f"{label} No drop: ${price:.2f} (baseline ${baseline:.2f})")


if __name__ == "__main__":
    main()
