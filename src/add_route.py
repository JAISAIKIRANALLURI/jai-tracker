"""Called by the 'Track Flight' GitHub Actions workflow to register a new route."""
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from storage import load, save
from amadeus_client import get_cheapest_price
from notifier import send_baseline


def main():
    origin = os.environ["FROM_AIRPORT"].upper().strip()
    destination = os.environ["TO_AIRPORT"].upper().strip()
    departure_date = os.environ["DEPARTURE_DATE"].strip()
    round_trip = os.environ.get("ROUND_TRIP", "false").lower() == "true"
    return_date = os.environ.get("RETURN_DATE", "").strip() or None

    if round_trip and not return_date:
        print("ERROR: Round trip selected but no return date provided.")
        sys.exit(1)

    now = datetime.now(timezone.utc)
    route = {
        "id": str(uuid.uuid4())[:8],
        "from": origin,
        "to": destination,
        "departure_date": departure_date,
        "return_date": return_date if round_trip else None,
        "round_trip": round_trip,
        "added_at": now.isoformat(),
        "expires_at": (now + timedelta(days=14)).isoformat(),
        "baseline_price": None,
        "last_price": None,
        "currency": "USD",
    }

    # Fetch baseline price immediately when route is added
    print(f"Fetching baseline price for {origin} → {destination}...")
    try:
        price = get_cheapest_price(origin, destination, departure_date, return_date if round_trip else None)
        if price is not None:
            route["baseline_price"] = price
            route["last_price"] = price
            send_baseline(route, price)
            print(f"Baseline set: ${price:.2f}")
        else:
            print("No flights found — baseline will be set on first scheduled check.")
    except Exception as e:
        print(f"Warning: Could not fetch baseline price: {e}")
        print("Baseline will be set on first scheduled check.")

    data = load()
    data["routes"].append(route)
    save(data)

    trip_label = f"Round Trip (return {return_date})" if round_trip else "One Way"
    print(f"\nAdded route #{route['id']}: {origin} → {destination} | {departure_date} | {trip_label}")
    print(f"Tracking until: {route['expires_at']}")


if __name__ == "__main__":
    main()
