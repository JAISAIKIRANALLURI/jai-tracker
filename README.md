# jai-tracker ✈️

Flight price tracker — monitors Google Flights via Amadeus API and sends push alerts to your phone when prices drop. Runs free on GitHub Actions.

---

## Setup (one-time, ~10 minutes)

### 1. SerpAPI Key (free)
1. Sign up at https://serpapi.com
2. Go to your dashboard — your **API Key** is shown on the home screen
3. Free tier: 100 searches/month — enough to track 1-2 routes for 14 days

### 2. ntfy Phone Notifications (free)
1. Install the **ntfy** app on your phone (iOS or Android — search "ntfy")
2. Pick a unique topic name, e.g. `jai-flights-abc123` (treat it like a password — anyone who knows it can subscribe)
3. In the app: tap **+** → enter your topic name → subscribe

### 3. Push this repo to GitHub
```bash
cd D:/jai-tracker
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/jai-tracker.git
git push -u origin main
```

### 4. Add GitHub Secrets
In your repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name   | Value                                      |
|---------------|--------------------------------------------|
| `SERPAPI_KEY` | from serpapi.com dashboard                 |
| `NTFY_TOPIC`  | your chosen topic name (e.g. jai-flights-abc123) |

---

## Tracking a Flight

1. Go to your repo on GitHub
2. Click **Actions** → **Track New Flight** → **Run workflow**
3. Fill in the form:

| Field           | Example         | Notes                              |
|-----------------|-----------------|------------------------------------|
| From Airport    | `BOS`           | IATA airport code                  |
| To Airport      | `LAX`           | IATA airport code                  |
| Departure Date  | `2026-05-10`    | YYYY-MM-DD                         |
| Round Trip?     | `true`          | Choose true or false               |
| Return Date     | `2026-05-17`    | Only needed for round trip         |

4. Click **Run workflow** — your phone buzzes with the baseline price within ~1 minute
5. Prices are checked **every 2 hours** for **14 days**
6. You get a push alert every time the price drops below the day-1 baseline

---

## How it works

```
[You trigger workflow] → adds route to data/routes.json + fetches baseline price
        ↓
[Every 2 hours — GitHub Actions cron]
        ↓
  fetch current cheapest price from Amadeus
        ↓
  price < baseline?
    YES → ntfy push alert to your phone 🔥
    NO  → silent (no spam)
        ↓
  route older than 14 days? → auto-removed
```

---

## Local Testing

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in .env

# Add a route manually
export $(cat .env | xargs)
FROM_AIRPORT=BOS TO_AIRPORT=LAX DEPARTURE_DATE=2026-05-10 ROUND_TRIP=false python src/add_route.py

# Run a price check
python src/price_checker.py
```

---

## IATA Airport Codes — Common Examples

| City          | Code |
|---------------|------|
| New York (JFK)| JFK  |
| Los Angeles   | LAX  |
| Chicago       | ORD  |
| Boston        | BOS  |
| San Francisco | SFO  |
| London        | LHR  |
| Paris         | CDG  |
| Delhi         | DEL  |
| Toronto       | YYZ  |
| Dubai         | DXB  |
