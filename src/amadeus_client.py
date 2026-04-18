import os
from serpapi import GoogleSearch


def get_cheapest_price(origin, destination, departure_date, return_date=None):
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "currency": "USD",
        "hl": "en",
        "type": "1" if return_date else "2",  # 1=round trip, 2=one way
        "api_key": os.environ["SERPAPI_KEY"],
    }
    if return_date:
        params["return_date"] = return_date

    search = GoogleSearch(params)
    results = search.get_dict()

    if "error" in results:
        raise RuntimeError(f"SerpAPI error: {results['error']}")

    prices = []
    for section in ("best_flights", "other_flights"):
        for flight in results.get(section, []):
            price = flight.get("price")
            if price is not None:
                prices.append(float(price))

    return round(min(prices), 2) if prices else None
