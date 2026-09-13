You are building a **separate testing environment for my airfare scraper project**.

IMPORTANT:

* Do NOT modify, rewrite, refactor, or include my existing scraper project.
* Do NOT build the scraper itself.
* Your only task is to build **5 standalone mock airfare websites/services** that my scraper can connect to and test against.
* These should run locally and be easy to host later.
* They should contain realistic airfare data and deliberately designed edge cases.
* The purpose is to test **scraping, API integration, parsing, cleaning, normalization, validation, duplicate handling, retry handling, and error handling** for my SIH airfare-price-index project.

## TECHNOLOGY

Use a simple stack:

* Python
* FastAPI or Flask for the server
* Plain HTML/CSS/JavaScript for the HTML websites
* JSON data files for seeded data
* SQLite is optional, but a database is NOT necessary unless it makes the mock websites easier
* Keep dependencies minimal
* Provide `requirements.txt`
* Provide a complete `README.md`

The entire project should run with:

```bash
pip install -r requirements.txt
python server.py
```

and then be accessible from:

```text
http://127.0.0.1:8765
```

Use one server if convenient, with different routes for the 5 sites.

---

# WEBSITE 1 — API AIRLINE

Create a mock airline API called:

**SkyFly**

Purpose:
Test a normal API-based scraper.

Endpoint example:

```http
GET /site1-api/flights
```

Parameters:

```text
origin
destination
travel_date
passengers
cabin
```

Require an API key:

```http
X-API-Key: TEST_API_KEY_SITE1_123
```

Return realistic JSON.

Example response structure:

```json
{
  "search": {
    "origin": "DEL",
    "destination": "BOM",
    "travel_date": "2026-10-20",
    "passengers": 1,
    "cabin": "economy"
  },
  "flights": [
    {
      "flight_number": "SF101",
      "departure_time": "08:30",
      "arrival_time": "10:40",
      "stops": 0,
      "cabin": "economy",
      "fare_family": "Saver",
      "base_fare": 4500,
      "taxes": 700,
      "other_charges": 99,
      "total_fare": 5299,
      "currency": "INR",
      "availability": "available"
    }
  ]
}
```

Seed multiple flights and fare classes.

This site must include test cases for:

1. Normal successful response
2. Multiple flights
3. Multiple fare classes for the same flight
4. Direct and connecting flights
5. Sold-out flight
6. No flights available
7. Missing `taxes`
8. Missing `other_charges`
9. `total_fare` inconsistent with components
10. `currency` not INR
11. Duplicate flight entries
12. Empty/null price
13. Wrong route returned
14. Wrong travel date returned

Also add dedicated test routes such as:

```text
/site1-api/test/no-results
/site1-api/test/sold-out
/site1-api/test/missing-fields
/site1-api/test/bad-total
/site1-api/test/wrong-route
/site1-api/test/wrong-date
/site1-api/test/duplicate
```

---

# WEBSITE 2 — API AIRLINE / UNSTABLE API

Create another mock airline API called:

**AeroNation**

Require:

```http
X-API-Key: TEST_API_KEY_SITE2_456
```

Endpoint:

```http
GET /site2-api/flights
```

Make this one specifically test robustness.

Include:

### HTTP status cases

```text
200
400
401
403
429
500
502
503
```

For `429`, include:

```http
Retry-After: 5
```

For 500/502/503 simulate temporary server failures.

Create routes:

```text
/site2-api/test/rate-limit
/site2-api/test/unauthorized
/site2-api/test/forbidden
/site2-api/test/server-error
/site2-api/test/malformed-json
/site2-api/test/timeout
```

The timeout endpoint should deliberately delay the response.

Also include messy fare representations such as:

```text
"₹5,499"
"INR 5,499"
"5499 INR"
"₹ 5,499"
"5,499"
```

and combinations such as:

```text
base_fare = "₹4,500"
taxes = "₹799"
other_charges = "Convenience Fee ₹100"
total_fare = "₹5,399"
```

This site is specifically intended to test:

* Authentication failure
* Forbidden access
* Rate limiting
* Retry logic
* Timeout handling
* Malformed response handling
* Money parsing
* Fee parsing
* Null fields
* Incorrect totals

---

# WEBSITE 3 — HTML SCRAPING WEBSITE

Create a realistic airline booking website called:

**JetVista**

This one must be a normal HTML website that a browser scraper can scrape.

Routes:

```text
/site3/
 /site3/search
 /site3/normal
 /site3/multiple-fares
 /site3/sold-out
 /site3/no-results
```

Make the HTML look like a real airline search results page.

Use realistic elements such as:

```html
<div class="flight-card">
    <span class="airline-name">JetVista</span>
    <span class="flight-number">JV301</span>
    <span class="route">DEL → BOM</span>
    <span class="departure">08:30</span>
    <span class="arrival">10:40</span>
    <span class="stops">Non-stop</span>
    <span class="cabin">Economy</span>
    <span class="fare-family">Saver</span>
    <span class="price">₹ 5,499</span>
</div>
```

Include realistic messy cases:

1. Price with commas
2. Price with `₹`
3. `"From ₹4,999"` promotional text
4. Base fare + taxes + fee shown separately
5. Multiple flights
6. Multiple fare families
7. Sold-out flights
8. No results
9. Missing taxes
10. Missing fee
11. Direct vs connecting
12. Coupon/discount shown separately
13. Baggage information affecting fare
14. A flight where price is hidden behind `"Login to view price"`

Create pages that intentionally use slightly different HTML structures so that the scraper must not assume the entire website has one identical DOM.

---

# WEBSITE 4 — DYNAMIC HTML SCRAPING WEBSITE

Create:

**FlySphere**

This must simulate a modern JavaScript-heavy airline website.

Use HTML + JavaScript.

Routes:

```text
/site4/
/site4/search
/site4/delayed
/site4/wrong-search
/site4/fee-mismatch
/site4/expired-session
```

Important behavior:

### `/site4/delayed`

Do not display flight results immediately.

Show:

```text
Loading flight results...
```

Then after around 3 seconds dynamically insert the flight cards.

This tests whether a browser scraper correctly waits for elements instead of immediately reading the HTML.

### `/site4/wrong-search`

If scraper requests:

```text
DEL → BOM
2026-10-20
```

return results labelled as:

```text
DEL → BLR
2026-10-21
```

This is intentional and should test result verification.

### `/site4/fee-mismatch`

Show:

```text
Base Fare: ₹4,500
Taxes: ₹700
Convenience Fee: ₹100
Displayed Total: ₹5,999
```

This should test fare validation.

### `/site4/expired-session`

Display:

```text
Your session has expired. Please search again.
```

Include realistic page markup.

Also include:

* direct and connecting flights
* midnight flight
* arrival on next day
* multiple fare classes
* missing fields
* sold-out flight

---

# WEBSITE 5 — HTML SCRAPING + FAILURE CASES

Create:

**AirZen**

This should be the most difficult test website.

Routes:

```text
/site5/
/site5/normal
/site5/captcha
/site5/login
/site5/malformed
/site5/sold-out
/site5/no-results
/site5/stale-results
```

Cases:

### `/site5/normal`

Normal valid flight results.

### `/site5/captcha`

Display a realistic challenge page containing text such as:

```text
Verify you are human
```

Do NOT implement any CAPTCHA-solving functionality.

This is only a test page so that my scraper can detect that access is blocked.

### `/site5/login`

Display:

```text
Please log in to view fares.
```

No actual price.

### `/site5/malformed`

Include malformed fare information such as:

```text
₹??
N/A
--
Price unavailable
```

### `/site5/sold-out`

Show flights but mark them:

```text
Sold Out
```

### `/site5/no-results`

Show:

```text
No flights available for your search.
```

### `/site5/stale-results`

The requested search should be:

```text
BOM → BLR
2026-10-20
```

but the page intentionally displays:

```text
DEL → BOM
2026-10-19
```

This tests whether my scraper verifies the returned route/date rather than blindly trusting the page.

---

# DATA REQUIREMENTS

Across the 5 websites, seed enough data to test:

### Routes

Include at least:

```text
DEL-BOM
DEL-BLR
BOM-BLR
DEL-CCU
BLR-HYD
MAA-DEL
```

### Dates

Use future travel dates around:

```text
2026-09-15
2026-09-20
2026-09-30
2026-10-15
2026-10-20
2026-10-30
```

### Advance windows

Make data suitable for testing:

```text
T-45
T-30
T-15
T-7
T-1
```

The response should contain enough metadata for my scraper to verify:

```text
origin
destination
travel_date
```

against the requested search.

---

# DATA QUALITY / NORMALIZATION CASES

The seeded data MUST deliberately contain these forms:

### Valid money

```text
₹4,999
₹ 4,999
₹4999
INR 4,999
4999 INR
4999
```

### Invalid/missing money

```text
null
""
"N/A"
"--"
"₹??"
```

### Fare breakdowns

Include examples where:

```text
base + taxes + fees = total
```

and examples where:

```text
base + taxes + fees != total
```

### Availability

Include:

```text
available
sold_out
not_available
```

### Stops

Include:

```text
0
1
2
```

### Cabin

Include:

```text
economy
business
```

### Fare families

Include:

```text
Saver
Standard
Flex
Business
```

---

# SEARCH VALIDATION

Every website should support enough data so my scraper can test:

```text
1 passenger
one-way
economy
INR
specific origin
specific destination
specific travel date
```

Make sure the returned data explicitly exposes route/date metadata so my scraper can verify that it received the correct search results.

---

# LEGAL / ETHICAL TESTING

These are **local mock websites created specifically for authorized scraper testing**.

Include:

```text
/robots.txt
/terms
```

for the three HTML scraping websites.

Their `/terms` page should explicitly state that:

* automated testing is permitted
* scraping is permitted
* the service is a local test fixture
* data is synthetic
* no production airline data is being represented

Example:

```text
This is a synthetic local testing service created for authorized
web-scraper development and testing. Automated access and scraping
of this test service are permitted.
```

Do NOT use real airline branding, copyrighted website copies, real credentials, or real customer information.

---

# UI REQUIREMENTS

Each website should have a simple but realistic UI.

At the homepage, show:

* website name
* description
* test scenarios available
* links to each test scenario

Example:

```text
JetVista Test Website

[Normal Search]
[Multiple Fares]
[Sold Out]
[No Results]
```

Do not make the UI unnecessarily complicated.

---

# DATA STORAGE

Keep the seeded data in separate JSON files:

```text
data/
  site1.json
  site2.json
  site3.json
  site4.json
  site5.json
```

This allows me to easily edit the test data later.

---

# PROJECT STRUCTURE

Use this structure:

```text
five-airfare-test-sites/
│
├── server.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── site1.json
│   ├── site2.json
│   ├── site3.json
│   ├── site4.json
│   └── site5.json
│
├── site1-api/
│   ├── index.html
│   ├── terms.html
│   └── robots.txt
│
├── site2-api/
│   ├── index.html
│   ├── terms.html
│   └── robots.txt
│
├── site3-html/
│   ├── index.html
│   ├── normal.html
│   ├── multiple_fares.html
│   ├── sold_out.html
│   ├── no_results.html
│   ├── terms.html
│   └── robots.txt
│
├── site4-html/
│   ├── index.html
│   ├── normal.html
│   ├── delayed.html
│   ├── wrong_search.html
│   ├── fee_mismatch.html
│   ├── expired_session.html
│   ├── terms.html
│   └── robots.txt
│
└── site5-html/
    ├── index.html
    ├── normal.html
    ├── captcha.html
    ├── login.html
    ├── malformed.html
    ├── sold_out.html
    ├── no_results.html
    ├── stale_results.html
    ├── terms.html
    └── robots.txt
```

You may improve this structure if necessary, but DO NOT omit the actual HTML files. Every HTML test page must contain real visible test data.

---

# FINAL REQUIREMENTS

Before finishing:

1. Actually run the server.
2. Test every API endpoint.
3. Test every HTML page.
4. Verify all pages return HTTP 200 except intentionally failing API test routes.
5. Verify API keys work.
6. Verify invalid API keys return 401.
7. Verify 429/5xx test cases behave correctly.
8. Verify delayed JavaScript content really appears after a delay.
9. Verify the HTML pages contain actual flight data.
10. Verify `robots.txt` and `terms` exist for all three scraping sites.
11. Make sure no HTML file is empty.
12. Make sure all seeded data is included.
13. Make sure the project can be run from a clean environment using the README instructions.

Create a ZIP file containing the complete project.

At the end, provide:

* the ZIP
* a concise explanation of each of the 5 websites
* a table mapping each test scenario to the corresponding URL
* exact commands to run the server
* API keys for the two mock API websites