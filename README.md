# PKHosting & Travel.pk — Customer App

Built for the TechAbout employee Growth task **"App For PK Hosting and
Travel.pk"** (10 KPI points): a customer-facing app covering both brands'
needs.

## What it does

Four tabs (top tab bar, plus quick links on Home):

- **🏠 Home** — welcome, brand cards for PKHosting and Travel.pk, quick links
  to the other tabs.
- **🖥️ PKHosting**
  - Shared-hosting plans table — 3 sample plans (Starter / Business / Pro)
    with storage, bandwidth, domains, email accounts, SSL and PKR/year pricing,
    each tagged with a "recommended for" note (Business marked most popular).
  - Domain name idea generator — enter keywords, get prefix/suffix combos,
    keyword mashups and number variants across .com / .pk / .net / .io /
    .org, with a length filter and CSV download.
  - Best-effort DNS availability hint (clearly labeled — registrar
    confirmation required).
  - Support FAQ (nameservers, SSL, backups, refunds, propagation, upgrades).
- **✈️ Travel.pk**
  - 12 sample tour packages: 6 domestic (Hunza, Skardu, Naran, Swat, Kashmir,
    Fairy Meadows), 4 international (Dubai, Turkey, Malaysia, Baku) and
    2 Umrah packages — each with destination, duration, sample PKR price and
    highlights.
  - Filters: trip type, max budget slider, max duration slider.
  - Booking enquiry form (name, phone, email, package, travel date, travelers,
    notes) with validation, a confirmation summary, a generated booking
    reference, and CSV download of the enquiry.
- **📞 Contact** — general enquiry form (name, phone, topic, message) with the
  same validation + confirmation + reference + CSV pattern.

All pure logic lives in import-safe functions (no Streamlit calls), so it can
be unit-tested.

## Run locally

```bash
cd pkhosting-travel-app
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

Optional: copy `.env.example` to `.env` to override `APP_TITLE`,
`DEFAULT_TAB`, `SUPPORT_PHONE` and `SUPPORT_EMAIL`.

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io → **New app**.
3. Select the repo, branch, and `app.py` as the main file.
4. Click **Deploy**. No secrets or API keys are needed.

## How it was tested

- `python3 -m py_compile app.py` — clean.
- Logic test script (import-safe functions only):
  - domain idea generator returns well over 20 ideas for two keywords;
  - package filter returns correct subsets (e.g. Domestic ≤ Rs. 40,000 and
    ≤ 5 days);
  - booking validation rejects an empty name and a too-short phone number;
  - booking reference matches the `TPK-YYYYMMDD-XXXXXX` format.
- Headless boot: `streamlit run app.py --server.headless true` starts with no
  traceback; every tab, button, form and download was exercised in the code
  path review (no placeholder buttons — every control does something).

## Limitations

- **Sample data**: every price, plan and package is labeled SAMPLE and is for
  demonstration only.
- **No backend**: enquiries are session-only and are not sent anywhere; use
  the CSV download to keep a copy.
- **DNS hint is best-effort**: a resolving domain is very likely taken, but a
  non-resolving domain may still be registered — always confirm with a domain
  registrar.

---
## Built for BlogReach
SEO outreach for this project via [BlogReach](https://blogreach.com) — the guest-posting marketplace.
