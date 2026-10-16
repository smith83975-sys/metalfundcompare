# MetalFund Compare — data foundation & build plan
_Prepared 2026-10-16. Nothing has been bought, signed up for, or sent. Every number below was fetched or cited from a named source; anything else is marked as a guess or "unverified"._

## 0. Files in this folder
| File | What it is |
|---|---|
| `funds.csv` / `funds.json` | 80 funds (75 US-listed + 5 TSX-only). Fields: ticker, name, issuer, type, metal, listing, expense ratio + source, AUM ($M) + source, inception + source, tax treatment, official URL, verification level, notes |
| `build_funds.py` | Script that generates the CSV/JSON (edit values here, then re-run) |
| `verify.py`, `urls.tsv`, `urls2.tsv` | Scripted issuer-page fetcher that pulls expense ratios off the pages (re-runnable) |
| `raw/` | Raw downloads used for verification (issuer HTML, SSGA XLSX, iShares JSON, Nasdaq JSON, SEC JSON) |

**How well verified:** 26 issuer-verified, 22 partly verified (fee checked on the issuer page, AUM/inception from etfdb.com 2026-10-15), 32 unverified (etfdb, web-search snippets, or blank).
**Mismatches found (why issuer data has to win):** etfdb lists PSLV at 0.67% and PHYS at 0.41%, but Sprott's own pages show 0.52% and 0.39% (MER). SIVR's page mentions a voluntary partial fee waiver, so the net fee still needs to be clarified. etfdb names SLVP "Silver Miners"; iShares' current official name is "iShares MSCI Global Silver and Metals Miners ETF".

### Fund count by type
| Type | Count |
|---|---|
| Physical grantor trusts (US) | 17 |
| Sprott closed-end physical trusts (PHYS, PSLV, CEF, SPPP) | 4 |
| Hybrid (SLVR, GDE, GDMN) | 3 |
| Miner ETFs (US) | 14 |
| Futures-based (DBP) | 1 |
| Leveraged/inverse (ETFs + ETNs) | 17 |
| Income / covered-call / buffer (ETFs + ETNs) | 19 |
| Canadian TSX-only (CGL, SVR, XGD, ZGD, MNT) — phase 2, unverified | 5 |
| **Total** | **80** |

Still open before launch: confirm the issuer URLs for SGOL, PPLT, PALL, GLTR (Aberdeen moved domains), FGDL, GOAU, the DB ETNs and MicroSectors; check fees on JS-rendered pages (BAR, PLTM, AAAU, USG, GLDN, SLVX, NUGY) against their SEC prospectuses; get YSAG's fee.

## 1. Data feeds — tested from this box on 2026-10-16
| Feed | Gives | Result | Notes |
|---|---|---|---|
| SSGA NAV history XLSX `ssga.com/.../navhist-us-en-{gld,gldm}.xlsx` | Daily NAV, shares outstanding, total net assets since inception (GLD file has 5,700 rows) | ✅ Works | Best source for GLD/GLDM NAV history. Ounces per share ≈ (TNA ÷ shares) ÷ gold price |
| iShares product-screener JSON (`product-screener-v3.1.jsn`) | Expense ratio, NAV, AUM, inception and page URL for every iShares fund in one call | ✅ Works (1.9 MB) | Covers IAU, IAUM, SLV, RING, SLVP |
| iShares product page HTML | "Ounces in Trust", premium/discount | ✅ Works (scrape) | The holdings-CSV `.ajax` link returned HTML, not CSV ❌ |
| Sprott trust pages (PHYS/PSLV/CEF/SPPP) | NAV/unit, market price, **premium/discount**, total oz, units outstanding, MER | ✅ Works (scrape) | Ounces per unit = total oz ÷ units. I found no history file, so discount history has to be built from daily snapshots going forward, or from Nasdaq close vs NAV |
| sprottetfs.com ETF pages (SGDM, SGDJ, SLVR, GBUG) | NAV, premium/discount, AUM, expense ratio | ✅ Works | |
| VanEck pages (GDX, GDXJ, OUNZ) | Expense ratio, AUM, inception | ✅ Works **only with a cookie jar** (`curl -c/-b`); without one it redirects to a cookie wall | |
| Direxion, ProShares, Global X, Amplify, Themes, First Trust, NEOS, Kurv, Defiance, YieldMax, Roundhill, Simplify | Expense ratio (+ often NAV/AUM/inception) | ✅ Works (scrape) | |
| GraniteShares, USCF, Goldman AM, Franklin, Nicholas | — | ⚠️ Values load via JavaScript | Needs a headless browser, or use the SEC prospectus |
| Invesco (HTTP 406), UBS ETRACS (500), WisdomTree (403), Aberdeen old URLs (404) | — | ❌ Blocked/failed from a script | Aberdeen's new `aberdeeninvestments.com/.../commodities/sivr` page works |
| **Nasdaq API** `api.nasdaq.com/api/quote/{T}/historical?assetclass=etf&fromdate=..&limit=9999` | Daily OHLC + volume, about 10 years (2,513 rows for GLD/PSLV/PHYS/GDX/NUGT; GDXU from 2020) | ✅ Works | **Main price source.** Unofficial and undocumented, so cache everything and keep a fallback |
| Yahoo `query1/query2 .../v8/finance/chart` | Prices | ❌ HTTP 429 from this box | Don't depend on it |
| Stooq CSV | Prices | ❌ JavaScript proof-of-work page; also needs an API key since 2026 | Not scriptable without a key |
| SEC EDGAR `sec.gov/files/company_tickers_exchange.json`, `data.sec.gov/submissions/CIK*.json` | Ticker→CIK map, filings list (prospectus/10-K, fee tables) | ✅ Works with a declared User-Agent | SEC requires a real contact email in the User-Agent; production needs Mark's/site email. Some ETF series (e.g. GDX) aren't in this map |
| LBMA prices JSON | Spot benchmark | ❌ 403 (Cloudflare) | Use issuer-implied spot instead (NAV ÷ oz per share) |

**Premium/discount method:** closing price (Nasdaq) vs. official NAV (issuer) → `(price/NAV − 1)`. Issuer-published premium/discount is used where it exists (Sprott, iShares, Defiance, YieldMax, Simplify).
**Ounces per share:** SPDR (TNA/shares/spot), iShares (oz in trust ÷ shares outstanding), Sprott (published total oz ÷ units).

## 2. Site structure
1. **Home / Fund table**: sortable and filterable by metal, type, fee, AUM, tax, discount; "cheapest physical gold", "biggest discount today" callouts.
2. **Per-fund pages** `/fund/gldm/`: key facts with source and "last verified" date, fee-drag over 1/5/10/20 yrs on $10k, price/NAV chart, premium/discount history chart, ounces-per-share decay chart (physical funds), tax box, official links (prospectus/fact sheet), "where to buy" broker block (affiliate).
3. **Auto-generated X-vs-Y pages** `/compare/pslv-vs-slv/`: generated for pairs inside the same metal + type group (e.g. the 10 US physical gold funds → 45 pairs), plus hand-picked cross pairs (PSLV vs SLV, GLD vs GDX, PHYS vs GLD, SLVR vs SIL). Each page has a templated verdict from the data (fee gap $, tax difference, discount, liquidity). This targets searches like "pslv vs slv" and "gld vs iau".
4. **Discount tracker** `/discounts/`: Sprott trusts + every fund with NAV; daily table + history charts (history starts accruing from launch day).
5. **Fee-drag calculator** `/tools/fee-drag/`: amount, years, two funds → dollar difference; client-side JS.
6. **Tax explainer** `/tax/`: grantor-trust collectibles 28%, PFIC/QEF (Form 8621), Section 1256 60/40 (K-1), ETN credit risk; each fund linked.
7. **Newsletter signup** on every page: weekly email with "fee cuts, new launches, discount moves, biggest flows".
8. **Methodology + sources + disclaimers** pages.

## 3. Tech stack (static site, daily rebuild)
- **Data job (Python):** `fetch_prices.py` (Nasdaq), `fetch_issuers.py` (SSGA XLSX, iShares JSON, Sprott and other HTML scrapers, VanEck with cookie jar), `build_db.py` → SQLite/Parquet + JSON per fund. A sanity check skips publishing a value if it moves more than X% day-over-day or a scrape returns empty, and flags it.
- **Site generator:** Astro or Eleventy (static HTML, fast, SEO-friendly); charts with a small library (uPlot or Chart.js) reading per-fund JSON.
- **Scheduler options:** (a) cron on this box, which already reaches every working feed; or (b) GitHub Actions cron (free for public repos; 2,000 min/month on private repos, per GitHub docs via search). Cloud runner IPs may be blocked by some issuer sites, so test before relying on (b).
- **Hosting (free):** Cloudflare Pages (free plan: 500 builds/month per Cloudflare docs via search; direct Wrangler uploads from CI avoid the build quota), GitHub Pages, or Netlify free.
- **Analytics:** Cloudflare Web Analytics (free) or Plausible (paid).

## 4. Newsletter tool options (free tiers, per vendor pages via web search, Oct 2026)
| Tool | Free tier |
|---|---|
| Kit (ConvertKit) | up to 10,000 subscribers |
| beehiiv | up to 2,500 subscribers |
| MailerLite | 250 active subscribers / 2,500 emails per month (per search; verify) |
| Buttondown | first 100 subscribers |
Recommendation: **Kit or beehiiv** (embed form on static site; beehiiv also has a built-in ad network later).

## 5. Monetization
**Broker affiliates (each needs an application by Mark):**
| Program | How to apply | Payout (sourced) |
|---|---|---|
| Webull | Official page act.webullapp.com/mktb/partners/us/individual: sign in with a Webull brokerage account, submit application (≈3 business days), sign agreement | Official page gives no rate; third-party reports $20–70 per funded account |
| Moomoo | Via FlexOffers or Impact networks | Reported $40 (FlexOffers) / $60 (Impact) per qualifying deposit |
| Public.com | Via Impact partner portal (manual approval) | Reported ~$10 per qualified account; consumer referral program can't be used commercially |
| Interactive Brokers | CPC Publisher Program: publishers@interactivebrokers.com (official page) | Cost-per-click; rate and monthly cap set per publisher (official page) |
**Issuer sponsorships (later, needs traffic):** fund issuers are the natural sponsors (newer/smaller funds: YSAU/YSAG, Kurv, NEOS, Themes, Sprott ETFs). Pitch outline: "X monthly visitors comparing metal funds; sponsored newsletter slot + 'featured fund' badge clearly labeled as paid; data rankings never for sale." No pitch has been sent.
**Also possible:** bullion-dealer affiliates (JM Bullion via Awin, $25/new customer per earlier research) on "ETF vs physical" pages. Keep these separate from VaultPulse topics (no dealer-premium tracking here).

## 6. Disclaimers (on every page + footer)
- "For information only, not investment, tax or legal advice. Data may be delayed or wrong; check the fund's prospectus."
- Data sources and "last verified" date on every fund page; issuer data wins over third-party data.
- Affiliate disclosure (FTC): "We may earn a commission if you open an account through links on this site."
- Leveraged/inverse and ETN warnings (daily reset, issuer credit risk).
- Tax section: general rules only; PFIC/QEF and K-1 notes link to IRS forms; "consult a tax professional".
- Respect site terms: cache, low request rates, identify the bot; drop any source whose terms forbid reuse (check Nasdaq/issuer terms before launch).

## 7. Needs Mark's approval or money
| # | Decision | Cost |
|---|---|---|
| 1 | **Domain**: pick one (all returned "not registered" in Verisign RDAP on 2026-10-16; premium status shows only at checkout) | .com: Porkbun $11.08/yr (fetched); Cloudflare ≈$10.46/yr at cost through Oct 15, expected ≈$11.17 after Verisign's Nov 1, 2026 fee rise (third-party source) |
|   | • metalfundcompare.com (matches the name) • goldetfcompare.com • comparegoldetfs.com • metalfundhq.com • metalfundtracker.com (also free: bullionfundcompare.com, metalfundwatch.com, goldfundcompare.com) | |
| 2 | Hosting account (Cloudflare Pages or GitHub) | Free |
| 3 | Newsletter account (Kit or beehiiv) | Free tier |
| 4 | Broker affiliate applications (Webull needs Mark's own Webull account; Moomoo/Public via FlexOffers/Impact; IBKR via email) | Free; needs Mark's identity/tax info |
| 5 | Real contact email for the SEC User-Agent / site contact (could use the Grok Bot inbox) | Free |
| 6 | OK to scrape issuer sites and the unofficial Nasdaq endpoint daily at low volume (check their terms) | — |
| 7 | Scheduler: run cron on this box vs GitHub Actions | Free |

## 8. Build order (once approved)
1. Finish verification for the 32 unverified rows (prospectus/SEC) → `funds.csv` v2.
2. Write fetchers + daily job; backfill 10y prices (Nasdaq) and SSGA NAV history.
3. Generate site (table, fund pages, compare pages, fee calculator, tax page).
4. Deploy, submit sitemap to Google Search Console, start newsletter, post data findings (e.g. "PSLV discount this week") in r/Silverbugs and r/ETFs where rules allow.
