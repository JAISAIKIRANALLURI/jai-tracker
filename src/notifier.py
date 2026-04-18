import os
import requests


def _topic():
    return os.environ["NTFY_TOPIC"]


def send_baseline(route, price):
    trip = "Round Trip" if route.get("round_trip") else "One Way"
    dates = route["departure_date"]
    if route.get("return_date"):
        dates += f" → {route['return_date']}"

    _post(
        title=f"✈️ Tracking: {route['from']} → {route['to']}",
        body=f"{trip} | {dates}\nBaseline price: ${price:.2f}\nTracking for 14 days — you'll be alerted on any drop.",
        priority="default",
        tags="airplane,white_check_mark",
    )


def send_price_drop(route, current_price, baseline_price):
    drop_pct = (baseline_price - current_price) / baseline_price * 100
    trip = "Round Trip" if route.get("round_trip") else "One Way"
    dates = route["departure_date"]
    if route.get("return_date"):
        dates += f" → {route['return_date']}"

    _post(
        title=f"🔥 Price Drop! {route['from']} → {route['to']} ({drop_pct:.0f}% off)",
        body=f"{trip} | {dates}\nWas: ${baseline_price:.2f}  →  Now: ${current_price:.2f}\nSave ${baseline_price - current_price:.2f}!",
        priority="high",
        tags="airplane,money_with_wings",
    )


def _post(title, body, priority="default", tags="airplane"):
    topic = _topic()
    try:
        resp = requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": priority,
                "Tags": tags,
            },
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[notifier] Failed to send notification: {e}")
