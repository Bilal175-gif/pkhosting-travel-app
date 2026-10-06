"""PKHosting & Travel.pk — customer app (TechAbout Growth task).

Combined customer-facing app for two Pakistani brands:

- PKHosting: shared web-hosting plans, a domain name idea generator and a
  support FAQ.
- Travel.pk: a tour-package browser with filters and a booking enquiry form,
  plus a general contact enquiry form.

All prices, plans and packages are SAMPLE data for demonstration only.
Enquiries are session-only (nothing is sent anywhere); download them as CSV.
No backend, no secrets, no real customer data.
"""

from __future__ import annotations

import csv
import io
import os
import random
import re
import socket
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import streamlit as st

# ---------------------------------------------------------------------------
# Env configuration (all optional — see .env.example)
# ---------------------------------------------------------------------------

APP_TITLE = os.getenv("APP_TITLE", "PKHosting & Travel.pk — Customer App")
DEFAULT_TAB = os.getenv("DEFAULT_TAB", "Home")
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "+92 300 0000000")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@example.com")

SAMPLE_NOTE = (
    "All prices, plans and packages on this page are SAMPLE data "
    "for demonstration only."
)

# ---------------------------------------------------------------------------
# Data — PKHosting
# ---------------------------------------------------------------------------

HOSTING_PLANS = [
    {
        "name": "Starter",
        "storage": "10 GB SSD",
        "bandwidth": "100 GB / month",
        "domains": "1",
        "email_accounts": "5",
        "ssl": "Free",
        "price_pkr_year": 2500,
        "recommended_for": "Personal blogs & portfolios",
        "popular": False,
    },
    {
        "name": "Business",
        "storage": "50 GB SSD",
        "bandwidth": "Unlimited",
        "domains": "10",
        "email_accounts": "50",
        "ssl": "Free",
        "price_pkr_year": 6000,
        "recommended_for": "Small businesses & online shops",
        "popular": True,
    },
    {
        "name": "Pro",
        "storage": "200 GB SSD",
        "bandwidth": "Unlimited",
        "domains": "Unlimited",
        "email_accounts": "Unlimited",
        "ssl": "Free",
        "price_pkr_year": 12000,
        "recommended_for": "Agencies & high-traffic sites",
        "popular": False,
    },
]

FAQ_ITEMS = [
    (
        "What are PKHosting's nameservers?",
        "Sample answer: point your domain to ns1.pkhosting.example and "
        "ns2.pkhosting.example at your registrar, then allow up to 24–48 "
        "hours for DNS propagation.",
    ),
    (
        "Do I get a free SSL certificate?",
        "Yes — every plan in the table above includes a free SSL certificate "
        "so your site loads over HTTPS.",
    ),
    (
        "How often are backups taken?",
        "Sample policy: weekly off-site backups are included on Business and "
        "Pro plans; Starter plans can take manual backups from the control "
        "panel any time.",
    ),
    (
        "What is the refund policy?",
        "Sample policy: 7-day money-back guarantee on shared hosting plans. "
        "Domain registrations are non-refundable once the domain is booked.",
    ),
    (
        "How long does it take to point my domain to my hosting?",
        "Nameserver changes usually propagate within a few hours and can take "
        "up to 48 hours worldwide. Your site files can be uploaded right away.",
    ),
    (
        "Can I upgrade my plan later?",
        "Yes — upgrades are prorated, so you only pay the difference for the "
        "remaining billing period. Contact support and they will move you "
        "without downtime.",
    ),
]

# ---------------------------------------------------------------------------
# Data — domain idea generator
# ---------------------------------------------------------------------------

PREFIXES = [
    "get", "my", "try", "go", "e", "pro", "super", "best", "top",
    "new", "smart", "easy", "prime", "hyper",
]
SUFFIXES = [
    "hub", "ly", "lab", "labs", "pro", "store", "zone", "spot", "base",
    "nest", "wise", "ship", "stack", "cloud", "host", "ify",
]
NUMBER_BITS = ["24", "365", "360", "101", "hq"]
DOMAIN_TLDS = [".com", ".pk", ".net", ".io", ".org"]

# ---------------------------------------------------------------------------
# Data — Travel.pk packages (SAMPLE)
# ---------------------------------------------------------------------------

PACKAGES = [
    {
        "name": "Hunza Valley Explorer",
        "destination": "Hunza, Gilgit-Baltistan",
        "trip_type": "Domestic",
        "duration_days": 8,
        "price_pkr": 85000,
        "highlights": "Karimabad Bazaar, Attabad Lake, Khunjerab Pass, Eagle's Nest sunset",
    },
    {
        "name": "Skardu & Deosai Adventure",
        "destination": "Skardu, Gilgit-Baltistan",
        "trip_type": "Domestic",
        "duration_days": 6,
        "price_pkr": 72000,
        "highlights": "Shigar Fort, Deosai Plains, Satpara Lake, Shangrila Resort",
    },
    {
        "name": "Naran Kaghan Escape",
        "destination": "Naran, Khyber Pakhtunkhwa",
        "trip_type": "Domestic",
        "duration_days": 3,
        "price_pkr": 32000,
        "highlights": "Saif-ul-Malook Lake, Babusar Top, Lulusar Lake",
    },
    {
        "name": "Swat Valley Retreat",
        "destination": "Swat, Khyber Pakhtunkhwa",
        "trip_type": "Domestic",
        "duration_days": 3,
        "price_pkr": 30000,
        "highlights": "Malam Jabba, Kalam Valley, Mahodand Lake",
    },
    {
        "name": "Kashmir Discovery",
        "destination": "Neelum Valley, Azad Kashmir",
        "trip_type": "Domestic",
        "duration_days": 4,
        "price_pkr": 42000,
        "highlights": "Muzaffarabad, Sharda, Kel & Arang Kel cable car",
    },
    {
        "name": "Fairy Meadows Trek",
        "destination": "Diamer, Gilgit-Baltistan",
        "trip_type": "Domestic",
        "duration_days": 5,
        "price_pkr": 55000,
        "highlights": "Nanga Parbat viewpoint, Beyal Camp, guided trek",
    },
    {
        "name": "Dubai Highlights",
        "destination": "Dubai, UAE",
        "trip_type": "International",
        "duration_days": 4,
        "price_pkr": 145000,
        "highlights": "Burj Khalifa, Desert Safari, Marina dinner cruise",
    },
    {
        "name": "Turkey Grand Tour",
        "destination": "Istanbul & Cappadocia, Turkey",
        "trip_type": "International",
        "duration_days": 7,
        "price_pkr": 320000,
        "highlights": "Blue Mosque, hot-air balloon ride, Pamukkale terraces",
    },
    {
        "name": "Malaysia Explorer",
        "destination": "Kuala Lumpur, Langkawi & Penang",
        "trip_type": "International",
        "duration_days": 10,
        "price_pkr": 385000,
        "highlights": "Petronas Towers, Langkawi cable car, Penang street food",
    },
    {
        "name": "Baku City Break",
        "destination": "Baku, Azerbaijan",
        "trip_type": "International",
        "duration_days": 5,
        "price_pkr": 195000,
        "highlights": "Old City, Flame Towers, Gobustan mud volcanoes",
    },
    {
        "name": "Umrah Economy",
        "destination": "Makkah & Madinah, Saudi Arabia",
        "trip_type": "Umrah",
        "duration_days": 15,
        "price_pkr": 265000,
        "highlights": "3-star hotels, shared transport, guided ziyarat tours",
    },
    {
        "name": "Umrah Standard",
        "destination": "Makkah & Madinah, Saudi Arabia",
        "trip_type": "Umrah",
        "duration_days": 7,
        "price_pkr": 225000,
        "highlights": "4-star hotels near Haram, private transport, guided ziyarat",
    },
]

TRIP_TYPES = ["All", "Domestic", "International", "Umrah"]
CONTACT_TOPICS = ["Hosting", "Travel", "Other"]

# ---------------------------------------------------------------------------
# Pure logic (import-safe: no Streamlit calls in here)
# ---------------------------------------------------------------------------


def clean_keyword(raw: str) -> str:
    """Lowercase, strip, keep only a-z and 0-9."""
    return re.sub(r"[^a-z0-9]", "", (raw or "").strip().lower())


def generate_domain_ideas(
    keywords: list[str],
    tlds: list[str] | None = None,
    max_len: int = 15,
    allow_hyphens: bool = False,
    allow_numbers: bool = True,
) -> list[dict]:
    """Build domain-name ideas from keywords.

    Returns a list of dicts with keys: label, tld, domain, method.
    Combines prefixes, suffixes, keyword mashups and optional number bits
    across the requested TLDs. Pure function — safe to unit-test.
    """
    tlds = tlds or DOMAIN_TLDS
    kws = [clean_keyword(k) for k in (keywords or [])]
    kws = [k for k in kws if k]
    if not kws:
        return []

    ideas: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(label: str, tld: str, method: str) -> None:
        if not label or len(label) > max_len:
            return
        key = (label, tld)
        if key in seen:
            return
        seen.add(key)
        ideas.append(
            {"label": label, "tld": tld, "domain": label + tld, "method": method}
        )

    for kw in kws:
        for tld in tlds:
            for pre in PREFIXES:
                add(pre + kw, tld, "prefix")
            for suf in SUFFIXES:
                add(kw + suf, tld, "suffix")
            if allow_numbers:
                for nb in NUMBER_BITS:
                    add(kw + nb, tld, "number")
    if len(kws) > 1:
        first, second = kws[0], kws[1]
        for tld in tlds:
            add(first + second, tld, "mashup")
            if allow_hyphens:
                add(first + "-" + second, tld, "hyphen")
    return ideas


def ideas_to_csv(ideas: list[dict]) -> str:
    """Serialise domain ideas to a CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["domain", "label", "tld", "method"])
    writer.writeheader()
    for idea in ideas:
        writer.writerow(
            {
                "domain": idea["domain"],
                "label": idea["label"],
                "tld": idea["tld"],
                "method": idea["method"],
            }
        )
    return buf.getvalue()


def dns_resolves(domain: str, timeout: float = 3.0) -> bool | None:
    """Best-effort DNS check: does the domain resolve?

    Returns True (resolves — very likely taken), False (does not resolve —
    may still be registered), or None on lookup error. This is a hint only;
    real availability must be confirmed with a domain registrar.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(domain)
        return True
    except OSError:
        return False
    except Exception:
        return None
    finally:
        try:
            socket.setdefaulttimeout(None)
        except OSError:
            pass


def filter_packages(
    trip_type: str = "All",
    max_budget_pkr: int = 400000,
    max_days: int = 15,
) -> list[dict]:
    """Return packages matching the filters. Pure function."""
    out = []
    for pkg in PACKAGES:
        if trip_type != "All" and pkg["trip_type"] != trip_type:
            continue
        if pkg["price_pkr"] > max_budget_pkr:
            continue
        if pkg["duration_days"] > max_days:
            continue
        out.append(pkg)
    return out


def search_packages(packages: list[dict], query: str) -> list[dict]:
    """Filter a package list by free-text query (name/destination/highlights).

    Case-insensitive, matches any word in the query. Pure function.
    """
    q = (query or "").strip().lower()
    if not q:
        return list(packages)
    words = q.split()
    out = []
    for pkg in packages:
        hay = " ".join(
            str(pkg.get(k, "")) for k in ("name", "destination", "highlights")
        ).lower()
        if all(w in hay for w in words):
            out.append(pkg)
    return out


SORT_OPTIONS = [
    "Recommended",
    "Price: low to high",
    "Price: high to low",
    "Shortest duration first",
]


def sort_packages(packages: list[dict], sort_key: str) -> list[dict]:
    """Sort a package list by the given key. Pure function."""
    items = list(packages)
    if sort_key == "Price: low to high":
        items.sort(key=lambda p: p["price_pkr"])
    elif sort_key == "Price: high to low":
        items.sort(key=lambda p: p["price_pkr"], reverse=True)
    elif sort_key == "Shortest duration first":
        items.sort(key=lambda p: p["duration_days"])
    return items


def _valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone or "")
    return len(digits) >= 7


def _valid_email(email: str) -> bool:
    if not email:
        return True  # optional field
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()) is not None


def validate_booking(
    name: str,
    phone: str,
    email: str,
    package: str,
    travelers: int,
) -> list[str]:
    """Validate the booking enquiry form. Returns a list of error messages."""
    errors: list[str] = []
    if not (name or "").strip():
        errors.append("Name is required.")
    if not _valid_phone(phone):
        errors.append("Enter a valid phone number (at least 7 digits).")
    if not _valid_email(email):
        errors.append("Email address looks invalid.")
    if not package:
        errors.append("Please select a package.")
    if travelers < 1:
        errors.append("Number of travelers must be at least 1.")
    return errors


def validate_contact(name: str, phone: str, message: str) -> list[str]:
    """Validate the general contact form. Returns a list of error messages."""
    errors: list[str] = []
    if not (name or "").strip():
        errors.append("Name is required.")
    if not _valid_phone(phone):
        errors.append("Enter a valid phone number (at least 7 digits).")
    if not (message or "").strip():
        errors.append("Message is required.")
    return errors


def make_booking_ref(prefix: str = "TPK") -> str:
    """Generate a booking/enquiry reference like TPK-20261005-A1B2C3."""
    rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{date.today().strftime('%Y%m%d')}-{rand}"


def enquiry_to_csv(rows: list[dict], fieldnames: list[str]) -> str:
    """Serialise enquiry rows to a CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})
    return buf.getvalue()


def tab_index_for(name: str, tabs: list[str]) -> int:
    """Map a DEFAULT_TAB-style name to a tab index (case-insensitive)."""
    want = (name or "").strip().lower()
    for i, tab in enumerate(tabs):
        if want and want in tab.lower():
            return i
    return 0

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

TABS = ["🏠 Home", "🖥️ PKHosting", "✈️ Travel.pk", "📞 Contact"]


def render_tab_bar() -> None:
    """Custom tab bar (real navigation, incl. quick links from Home)."""
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = tab_index_for(DEFAULT_TAB, TABS)
    cols = st.columns(len(TABS))
    for i, label in enumerate(TABS):
        with cols[i]:
            btn_type = (
                "primary" if st.session_state.active_tab == i else "secondary"
            )
            if st.button(
                label,
                key=f"tab_{i}",
                type=btn_type,
                use_container_width=True,
            ):
                st.session_state.active_tab = i
                st.rerun()


def go_to_tab(index: int) -> None:
    """Quick-link helper: switch to another tab."""
    st.session_state.active_tab = index
    st.rerun()


def render_home() -> None:
    st.header("Welcome to PKHosting & Travel.pk")
    st.caption(SAMPLE_NOTE)
    st.write(
        "One app for two customer needs: reliable **web hosting & domains** "
        "from PKHosting, and **tours, Umrah packages, flights & visas** from "
        "Travel.pk. Pick a section below to get started."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🖥️ PKHosting")
        st.write(
            "**Shared hosting for Pakistani businesses** — pick a plan, "
            "brainstorm a domain name, and check the support FAQ."
        )
        st.write("- 3 shared-hosting plans (sample pricing in PKR/year)")
        st.write("- Domain name idea generator with availability hints")
        st.write("- Support FAQ: nameservers, SSL, backups, refunds")
        if st.button("Explore hosting plans →", key="home_go_hosting",
                     use_container_width=True):
            go_to_tab(1)
    with col2:
        st.subheader("✈️ Travel.pk")
        st.write(
            "**Tours & travel** — browse domestic, international and Umrah "
            "packages, filter by budget and duration, and send a booking enquiry."
        )
        st.write("- 12 tour packages across Pakistan and abroad")
        st.write("- Search, sort and budget/duration filters")
        st.write("- Booking enquiry form with instant reference number")
        if st.button("Browse tour packages →", key="home_go_travel",
                     use_container_width=True):
            go_to_tab(2)

    st.divider()
    st.write(
        f"Need help? Call **{SUPPORT_PHONE}** or email **{SUPPORT_EMAIL}** — "
        "or use the Contact tab."
    )
    if st.button("📞 Go to contact form →", key="home_go_contact"):
        go_to_tab(3)


def render_pkhosting() -> None:
    st.header("🖥️ PKHosting — Web Hosting & Domains")
    st.caption(SAMPLE_NOTE)

    st.subheader("Shared hosting plans")
    popular = next(p for p in HOSTING_PLANS if p["popular"])
    st.info(
        f"⭐ Most popular: **{popular['name']}** — "
        f"{popular['recommended_for']}."
    )
    table_rows = [
        {
            "Plan": p["name"],
            "Storage": p["storage"],
            "Bandwidth": p["bandwidth"],
            "Domains": p["domains"],
            "Email accounts": p["email_accounts"],
            "SSL": p["ssl"],
            "Price (PKR/year)": f"{p['price_pkr_year']:,}",
            "Recommended for": p["recommended_for"],
        }
        for p in HOSTING_PLANS
    ]
    st.table(table_rows)

    st.divider()
    st.subheader("Domain name idea generator")
    st.write(
        "Describe your business and get domain ideas. Availability hints are "
        "best-effort DNS lookups — **always confirm with a domain registrar** "
        "before assuming a name is free."
    )
    kw_input = st.text_input(
        "Business name or keywords (comma-separated)",
        placeholder="e.g. hotel, lahore",
        key="domain_keywords",
    )
    tlds = st.multiselect(
        "Preferred extensions",
        DOMAIN_TLDS,
        default=DOMAIN_TLDS,
        key="domain_tlds",
    )
    col_a, col_b = st.columns(2)
    with col_a:
        max_len = st.slider(
            "Max name length (before the dot)", 3, 25, 15, key="domain_maxlen"
        )
    with col_b:
        allow_hyphens = st.checkbox("Allow hyphens", value=False,
                                    key="domain_hyphens")
        allow_numbers = st.checkbox("Allow numbers", value=True,
                                    key="domain_numbers")

    if st.button("Generate ideas", key="domain_generate", type="primary"):
        keywords = [k.strip() for k in kw_input.split(",")]
        ideas = generate_domain_ideas(
            keywords,
            tlds=tlds,
            max_len=max_len,
            allow_hyphens=allow_hyphens,
            allow_numbers=allow_numbers,
        )
        if not ideas:
            st.warning("Enter at least one keyword to generate ideas.")
        else:
            st.session_state["domain_ideas"] = ideas
            st.success(f"Generated {len(ideas)} ideas (showing first 80).")

    ideas = st.session_state.get("domain_ideas", [])
    if ideas:
        show = ideas[:80]
        st.table(
            [
                {
                    "Domain": i["domain"],
                    "How it was made": i["method"],
                }
                for i in show
            ]
        )
        st.download_button(
            "Download ideas as CSV",
            data=ideas_to_csv(ideas),
            file_name="domain-ideas.csv",
            mime="text/csv",
            key="domain_csv",
        )

        st.divider()
        st.subheader("Availability hint (best-effort)")
        st.warning(
            "Hint only: a resolving domain is very likely taken; a "
            "non-resolving domain may still be registered. Confirm real "
            "availability with a registrar."
        )
        options = [i["domain"] for i in ideas[:20]]
        chosen = st.multiselect(
            "Pick domains to check (up to 8)",
            options,
            default=options[:5],
            key="dns_pick",
        )
        if st.button("Check availability hint", key="dns_check"):
            picked = chosen[:8]
            if not picked:
                st.warning("Pick at least one domain first.")
            else:
                results = []
                with st.spinner("Checking DNS…"):
                    with ThreadPoolExecutor(max_workers=8) as pool:
                        future_map = {
                            pool.submit(dns_resolves, d): d for d in picked
                        }
                        for fut in as_completed(future_map):
                            d = future_map[fut]
                            try:
                                status = fut.result()
                            except Exception:
                                status = None
                            if status is True:
                                hint = "Resolves — very likely taken (hint)"
                            elif status is False:
                                hint = ("Does not resolve — may still be "
                                        "registered (hint)")
                            else:
                                hint = "Lookup failed — try again (hint)"
                            results.append({"Domain": d, "Hint": hint})
                st.table(results)

    st.divider()
    st.subheader("Support FAQ")
    for q, a in FAQ_ITEMS:
        with st.expander(q):
            st.write(a)

def render_travel() -> None:
    st.header("✈️ Travel.pk — Tours & Packages")
    st.caption(SAMPLE_NOTE)

    st.subheader("Find a package")
    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        search_query = st.text_input(
            "Search packages",
            placeholder="e.g. hunza, lake, umrah",
            key="pkg_search",
        )
    with col_s2:
        sort_key = st.selectbox("Sort by", SORT_OPTIONS, key="pkg_sort")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        trip_type = st.radio("Trip type", TRIP_TYPES, key="pkg_triptype")
    with col_f2:
        max_budget = st.slider(
            "Max budget (PKR per person)",
            30000, 400000, 400000, step=5000,
            key="pkg_budget",
        )
    with col_f3:
        max_days = st.slider("Max duration (days)", 3, 15, 15, key="pkg_days")

    matches = sort_packages(
        search_packages(filter_packages(trip_type, max_budget, max_days),
                        search_query),
        sort_key,
    )
    st.write(f"**{len(matches)}** package(s) match your filters.")
    for pkg in matches:
        with st.container(border=True):
            st.subheader(f"{pkg['name']} — Rs. {pkg['price_pkr']:,}")
            st.write(
                f"📍 {pkg['destination']} · 🕒 {pkg['duration_days']} days · "
                f"🏷️ {pkg['trip_type']} · *sample price per person*"
            )
            st.write(f"✨ {pkg['highlights']}")
    if not matches:
        st.info("No packages match — try raising the budget or duration.")

    st.divider()
    st.subheader("Booking enquiry")
    st.write(
        "Fill in the form and we will get back to you. Nothing is sent "
        "anywhere — download your enquiry as CSV for your records."
    )
    with st.form("booking_form"):
        b_name = st.text_input("Full name *", key="b_name")
        b_phone = st.text_input("Phone / WhatsApp *", key="b_phone",
                                placeholder="+92 3XX XXXXXXX")
        b_email = st.text_input("Email (optional)", key="b_email")
        b_package = st.selectbox(
            "Package *",
            [""] + [p["name"] for p in PACKAGES],
            key="b_package",
        )
        b_date = st.date_input("Preferred travel date", value=date.today(),
                               key="b_date")
        b_travelers = st.number_input("Number of travelers *", min_value=1,
                                      max_value=100, value=2, key="b_travelers")
        b_notes = st.text_area("Notes (optional)", key="b_notes",
                               placeholder="Anything we should know?")
        submitted = st.form_submit_button("Send booking enquiry",
                                          type="primary")

    if submitted:
        errors = validate_booking(b_name, b_phone, b_email, b_package,
                                  int(b_travelers))
        if errors:
            for e in errors:
                st.error(e)
        else:
            ref = make_booking_ref("TPK")
            pkg = next(p for p in PACKAGES if p["name"] == b_package)
            st.success(f"Enquiry received! Your booking reference is **{ref}**.")
            st.write("**Summary**")
            st.table([
                {"Field": "Reference", "Value": ref},
                {"Field": "Name", "Value": b_name.strip()},
                {"Field": "Phone", "Value": b_phone.strip()},
                {"Field": "Email", "Value": b_email.strip() or "—"},
                {"Field": "Package", "Value": b_package},
                {"Field": "Package price (sample, per person)",
                 "Value": f"Rs. {pkg['price_pkr']:,}"},
                {"Field": "Travel date", "Value": str(b_date)},
                {"Field": "Travelers", "Value": str(int(b_travelers))},
                {"Field": "Notes", "Value": b_notes.strip() or "—"},
            ])
            st.info(
                "Sample data — our team will confirm real availability and "
                f"pricing on {SUPPORT_PHONE}."
            )
            csv_data = enquiry_to_csv(
                [{
                    "reference": ref,
                    "name": b_name.strip(),
                    "phone": b_phone.strip(),
                    "email": b_email.strip(),
                    "package": b_package,
                    "travel_date": str(b_date),
                    "travelers": int(b_travelers),
                    "notes": b_notes.strip(),
                }],
                ["reference", "name", "phone", "email", "package",
                 "travel_date", "travelers", "notes"],
            )
            st.download_button(
                "Download enquiry as CSV",
                data=csv_data,
                file_name=f"booking-{ref}.csv",
                mime="text/csv",
                key="b_csv",
            )


def render_contact() -> None:
    st.header("📞 Contact us")
    st.write(
        f"Questions about hosting or travel? Call **{SUPPORT_PHONE}**, email "
        f"**{SUPPORT_EMAIL}**, or send the form below."
    )
    with st.form("contact_form"):
        c_name = st.text_input("Full name *", key="c_name")
        c_phone = st.text_input("Phone / WhatsApp *", key="c_phone",
                                placeholder="+92 3XX XXXXXXX")
        c_topic = st.selectbox("Topic *", CONTACT_TOPICS, key="c_topic")
        c_message = st.text_area("Message *", key="c_message",
                                 placeholder="How can we help?")
        c_sent = st.form_submit_button("Send message", type="primary")

    if c_sent:
        errors = validate_contact(c_name, c_phone, c_message)
        if errors:
            for e in errors:
                st.error(e)
        else:
            ref = make_booking_ref("QRY")
            st.success(
                f"Message received! Your enquiry reference is **{ref}**. "
                f"We will reply on {SUPPORT_PHONE} / {SUPPORT_EMAIL}."
            )
            st.table([
                {"Field": "Reference", "Value": ref},
                {"Field": "Name", "Value": c_name.strip()},
                {"Field": "Phone", "Value": c_phone.strip()},
                {"Field": "Topic", "Value": c_topic},
                {"Field": "Message", "Value": c_message.strip()},
            ])
            csv_data = enquiry_to_csv(
                [{
                    "reference": ref,
                    "name": c_name.strip(),
                    "phone": c_phone.strip(),
                    "topic": c_topic,
                    "message": c_message.strip(),
                }],
                ["reference", "name", "phone", "topic", "message"],
            )
            st.download_button(
                "Download enquiry as CSV",
                data=csv_data,
                file_name=f"contact-{ref}.csv",
                mime="text/csv",
                key="c_csv",
            )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    render_tab_bar()
    st.divider()
    active = st.session_state.get("active_tab", 0)
    if active == 1:
        render_pkhosting()
    elif active == 2:
        render_travel()
    elif active == 3:
        render_contact()
    else:
        render_home()
    st.divider()
    st.caption(
        f"{APP_TITLE} · Sample demo app — no real bookings or payments. "
        f"Support: {SUPPORT_PHONE} · {SUPPORT_EMAIL}"
    )


if __name__ == "__main__":
    main()
