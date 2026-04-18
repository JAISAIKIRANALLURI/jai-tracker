import os
import smtplib
from email.mime.text import MIMEText


def _send_sms(subject, body):
    phone = os.environ["PHONE_NUMBER"]          # 10-digit, e.g. 6135551234
    gmail_user = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    sms_address = f"{phone}@txt.bell.ca"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = sms_address

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_app_password)
            server.sendmail(gmail_user, sms_address, msg.as_string())
        print(f"[notifier] SMS sent to {phone}")
    except Exception as e:
        print(f"[notifier] Failed to send SMS: {e}")


def send_baseline(route, price):
    trip = "Round Trip" if route.get("round_trip") else "One Way"
    dates = route["departure_date"]
    if route.get("return_date"):
        dates += f"-{route['return_date']}"

    _send_sms(
        subject=f"Tracking {route['from']}-{route['to']}",
        body=f"{trip} | {dates}\nBaseline: ${price:.2f}\nTracking 14 days.",
    )


def send_price_drop(route, current_price, baseline_price):
    drop_pct = (baseline_price - current_price) / baseline_price * 100
    trip = "Round Trip" if route.get("round_trip") else "One Way"
    dates = route["departure_date"]
    if route.get("return_date"):
        dates += f"-{route['return_date']}"

    _send_sms(
        subject=f"Price Drop! {route['from']}-{route['to']} {drop_pct:.0f}% off",
        body=f"{trip} | {dates}\nWas: ${baseline_price:.2f}\nNow: ${current_price:.2f}\nSave ${baseline_price - current_price:.2f}!",
    )
