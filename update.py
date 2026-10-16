#!/usr/bin/env python3
"""MetalFund Compare daily update: fetch prices/NAV/premium-discount at low volume, cache raw, append history, rebuild site.
Usage:  .venv/bin/python update.py            (full run, then rebuild site)
        .venv/bin/python update.py --no-prices (skip the ~75 Nasdaq calls)
        .venv/bin/python update.py --offline   (no network; rebuild from cache)
        .venv/bin/python update.py --tickers=GLD,SLV (prices for these tickers only)
"""
import json, re, html, csv, os, sys, time, datetime as dt, subprocess, io
from pathlib import Path
ROOT = Path(__file__).resolve().parent
DATA = ROOT/'data'; RAW = ROOT/'raw'/'daily'/dt.date.today().isoformat()
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
DELAY = 1.2   # seconds between requests (be polite)
ARGS = set(sys.argv[1:]); OFFLINE = '--offline' in ARGS
LOG = []
def log(*a):
    m = ' '.join(str(x) for x in a); print(m); LOG.append(m)

def fetch(url, name, accept=None, binary=False):
    """GET with curl, cache to raw/daily/<date>/<name>. Returns text/bytes or None."""
    RAW.mkdir(parents=True, exist_ok=True); out = RAW/name
    if OFFLINE:
        if out.exists(): return out.read_bytes() if binary else out.read_text(errors='ignore')
        return None
    cmd = ["curl", "-sL", "-A", UA, "--max-time", "60", "-o", str(out), "-w", "%{http_code}", url]
    if accept: cmd[2:2] = ["-H", f"Accept: {accept}"]
    try: code = subprocess.run(cmd, capture_output=True, text=True, timeout=90).stdout
    except Exception as e: log('  ERR', name, e); return None
    time.sleep(DELAY)
    if code != '200' or not out.exists() or out.stat().st_size < 200:
        log('  FAIL', name, code); return None
    return out.read_bytes() if binary else out.read_text(errors='ignore')

def text_of(s):
    s = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s)))
def num(x):
    try: return float(str(x).replace(',', '').replace('$', '').strip())
    except: return None
def mdy(s):
    for f in ('%m/%d/%Y', '%B %d, %Y', '%b %d, %Y', '%d-%b-%Y'):
        try: return dt.datetime.strptime(s.strip(), f).date().isoformat()
        except: pass
    return None
def jload(p, default):
    try: return json.loads(Path(p).read_text())
    except: return default
def jsave(p, obj): Path(p).write_text(json.dumps(obj, indent=0 if isinstance(obj, list) else 1))

funds = jload(ROOT/'funds.json', {})['funds']
US = [f['ticker'] for f in funds if f['listing'] != 'TSX']
ONLY = [a.split('=',1)[1].upper().split(',') for a in sys.argv[1:] if a.startswith('--tickers=')]
PRICE_LIST = ONLY[0] if ONLY else US
live = jload(DATA/'live.json', {'funds': {}})
live.setdefault('funds', {})
def setlive(t, **kw):
    live['funds'].setdefault(t, {}).update({k: v for k, v in kw.items() if v is not None})

# ---------- 1. Prices: Nasdaq historical (unofficial endpoint, cache everything) ----------
def update_prices():
    today = dt.date.today()
    for i, t in enumerate(PRICE_LIST):
        p = DATA/'prices'/f'{t}.json'; hist = {r[0]: r[1:] for r in jload(p, [])}
        start = (today - dt.timedelta(days=400 if len(hist) < 200 else 20)).isoformat()
        rows = None
        for ac in ('etf', 'stocks'):
            s = fetch(f"https://api.nasdaq.com/api/quote/{t}/historical?assetclass={ac}&fromdate={start}&limit=9999&todate={today}",
                      f"nq_{t}.json", accept="application/json")
            try: rows = (json.loads(s)['data'] or {}).get('tradesTable', {}).get('rows') if s else None
            except Exception: rows = None
            if rows: break
        if not rows: log('  no prices', t); continue
        for r in rows:
            d = mdy(r['date']); c = num(r['close']); v = num(r.get('volume'))
            if d and c: hist[d] = [c, v]
        jsave(p, sorted([[d] + v for d, v in hist.items()]))
    log('prices: done', len(PRICE_LIST), 'tickers')

def closes(t):
    return {r[0]: r[1] for r in jload(DATA/'prices'/f'{t}.json', [])}

def add_nav(t, date, nav):
    if not (date and nav): return
    p = DATA/'nav'/f'{t}.json'; h = {r[0]: r[1] for r in jload(p, [])}; h[date] = nav
    jsave(p, sorted([[d, v] for d, v in h.items()]))

# ---------- 2. Issuer NAV / AUM / premium-discount ----------
def sprott():
    pages = {'PHYS': 'gold', 'PSLV': 'silver', 'CEF': 'gold-and-silver', 'SPPP': 'platinum-and-palladium'}
    for t, slug in pages.items():
        s = fetch(f"https://sprott.com/investment-strategies/exchange-listed-products/physical-bullion-funds/{slug}/", f"sprott_{t}.html")
        if not s: continue
        x = text_of(s)
        asof = re.search(r'As of ([A-Z][a-z]+ \d{1,2}, \d{4}) NAV \$([\d.,]+)', x)
        mp = re.search(r'Market Price \$([\d.,]+) Premium / Discount (-?[\d.]+)%', x)
        tnav = re.search(r'Total Net Asset Value \$([\d.,]+) (Billion|Million)', x)
        mer = re.search(r'Management Expense Ratio ([\d.]+)%', x)
        units = re.search(r'Units Outstanding ([\d,]+)', x)
        oz = re.findall(r'Total Oz\. of (\w+) ([\d,]+)', x)
        if not (asof and mp): log('  sprott parse fail', t); continue
        d = mdy(asof.group(1)); nav = num(asof.group(2))
        aum = num(tnav.group(1)) * (1000 if tnav.group(2) == 'Billion' else 1) if tnav else None
        setlive(t, nav=nav, nav_date=d, market_price=num(mp.group(1)), prem_disc_pct=num(mp.group(2)),
                prem_disc_source='Sprott (published)', aum_usd_millions=aum, aum_date=d, aum_source='Sprott issuer page (Total NAV)',
                mer_pct=num(mer.group(1)) if mer else None, units=num(units.group(1)) if units else None,
                ounces={k.lower(): num(v) for k, v in dict(oz).items()} if oz else None)
        add_nav(t, d, nav)
        append_disc(d, t, nav, num(mp.group(1)), num(mp.group(2)), 'Sprott published')
    log('sprott: done')

def ishares():
    s = fetch("https://www.ishares.com/us/product-screener/product-screener-v3.1.jsn?dcrPath=/templatedata/config/product-screener-v3/data/en/us-ishares/ishares-product-screener-backend-config&siteEntryPassthrough=true", "ishares_screener.json")
    if not s: return
    try: d = json.loads(s)
    except Exception: log('  ishares bad json'); return
    want = {'IAU', 'IAUM', 'SLV', 'RING', 'SLVP'}
    for v in d.values():
        t = v.get('localExchangeTicker')
        if t not in want: continue
        nd = str(v.get('navAmountAsOf', {}).get('r', '')); nd = f"{nd[:4]}-{nd[4:6]}-{nd[6:]}" if len(nd) == 8 else None
        ad = str(v.get('totalNetAssetsFundAsOf', {}).get('r', '')); ad = f"{ad[:4]}-{ad[4:6]}-{ad[6:]}" if len(ad) == 8 else None
        nav = v.get('navAmount', {}).get('r'); aum = v.get('totalNetAssetsFund', {}).get('r')
        setlive(t, nav=nav, nav_date=nd, aum_usd_millions=round(aum/1e6, 1) if aum else None, aum_date=ad,
                aum_source='iShares product-screener JSON', fee_check=v.get('fees', {}).get('r'))
        add_nav(t, nd, nav)
    log('ishares: done')

def ssga():
    import openpyxl
    for t in ('GLD', 'GLDM'):
        b = fetch(f"https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/navhist-us-en-{t.lower()}.xlsx", f"ssga_{t}.xlsx", binary=True)
        if not b: continue
        try:
            ws = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True).active
        except Exception as e: log('  ssga xlsx error', t, e); continue
        rows = []
        for r in ws.iter_rows(values_only=True):
            d = mdy(str(r[0])) if r and r[0] else None
            if d and isinstance(r[1], (int, float)): rows.append((d, r[1], r[2], r[3]))
        if not rows: continue
        p = DATA/'nav'/f'{t}.json'; h = {x[0]: x[1] for x in jload(p, [])}
        for d, nav, sh, tna in rows: h[d] = nav
        jsave(p, sorted([[d, v] for d, v in h.items()]))
        d, nav, sh, tna = max(rows)
        setlive(t, nav=nav, nav_date=d, aum_usd_millions=round(tna/1e6, 1) if tna else None, aum_date=d, aum_source='SSGA NAV history XLSX (Total Net Assets)')
    log('ssga: done')

ABU = 'https://www.aberdeeninvestments.com/en-us/investor/funds/view-all-funds/'
ABR = {'SGOL': 'abrdn-physical-gold-shares-etf-us00326a1043', 'SIVR': 'abrdn-physical-silver-shares-etf-us0032641088',
       'PPLT': 'abrdn-physical-platinum-shares-etf-us0032601066', 'PALL': 'abrdn-physical-palladium-shares-etf-us0032621023',
       'GLTR': 'abrdn-physical-precious-metals-basket-shares-etf-us0032631006'}
def aberdeen():
    for t, slug in ABR.items():
        s = fetch(ABU + slug + '?subTab=keyInformationTab', f"abrdn_{t}.html")
        if not s: continue
        x = text_of(s)
        m = re.search(r'NAV \$ ?([\d.,]+) (\d{2}/\d{2}/\d{4})', x); a = re.search(r'AUM ([\d.]+)([BM]) USD (\d{2}/\d{2}/\d{4})', x)
        if m:
            d = mdy(m.group(2)); setlive(t, nav=num(m.group(1)), nav_date=d); add_nav(t, d, num(m.group(1)))
        if a:
            setlive(t, aum_usd_millions=num(a.group(1)) * (1000 if a.group(2) == 'B' else 1), aum_date=mdy(a.group(3)), aum_source='Aberdeen fund page')
        if not m: log('  aberdeen parse fail', t)
    log('aberdeen: done')

def small_issuers():
    s = fetch("https://usglobaletfs.com/fund/goau/", "goau.html")
    if s:
        x = text_of(s); m = re.search(r'Data as of (\d{2}/\d{2}/\d{4}) Net Assets \$([\d,]+)', x)
        if m: setlive('GOAU', aum_usd_millions=round(num(m.group(2))/1e6, 1), aum_date=mdy(m.group(1)), aum_source='U.S. Global issuer page')
    for t, slug in (('YSAU', 'gold-etf'), ('YSAG', 'silver-etf')):
        s = fetch(f"https://www.yallstreetetfs.com/etf/{slug}/", f"{t}.html")
        if not s: continue
        x = text_of(s)
        nav = re.search(r'NAV \$([\d.,]+) as of ([A-Z][a-z]{2} \d{1,2}, \d{4})', x)
        aum = re.search(r'AUM \$([\d.]+)M as of', x)
        if nav:
            d = mdy(nav.group(2)); setlive(t, nav=num(nav.group(1)), nav_date=d); add_nav(t, d, num(nav.group(1)))
        if aum: setlive(t, aum_usd_millions=num(aum.group(1)), aum_date=mdy(nav.group(2)) if nav else None, aum_source="Y'all Street issuer page")
    log('small issuers: done')

# ---------- 3. Premium/discount history ----------
DH = DATA/'discount_history.csv'
_dh = {}
def load_dh():
    if DH.exists():
        for r in csv.DictReader(open(DH)): _dh[(r['date'], r['ticker'])] = r
def append_disc(d, t, nav, close, pd, src):
    if d and t and pd is not None:
        _dh[(d, t)] = dict(date=d, ticker=t, nav=nav, close=close, prem_disc_pct=round(pd, 3), source=src)
def compute_disc():
    """Premium/discount = Nasdaq close / issuer NAV - 1, for each date where both exist (Sprott published values are kept)."""
    for f in (DATA/'nav').glob('*.json'):
        t = f.stem; c = closes(t)
        if not c: continue
        for d, nav in jload(f, []):
            if (d, t) in _dh and 'Sprott' in _dh[(d, t)]['source']: continue
            if d in c and nav:
                append_disc(d, t, nav, c[d], (c[d]/nav - 1) * 100, 'Nasdaq close vs issuer NAV')
        # latest computed value -> live
        rows = [r for (d, tt), r in sorted(_dh.items(), key=lambda kv: kv[0]) if tt == t]
        if rows and t not in ('PHYS', 'PSLV', 'CEF', 'SPPP'):
            r = rows[-1]; pd = float(r['prem_disc_pct'])
            flag = abs(pd) > 3   # grantor trusts rarely deviate >3%; likely a date mismatch -> show as "check"
            setlive(t, prem_disc_pct=pd, prem_disc_date=r['date'], prem_disc_source='Computed: Nasdaq close vs issuer NAV', prem_disc_flag=flag)
    with open(DH, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['date', 'ticker', 'nav', 'close', 'prem_disc_pct', 'source']); w.writeheader()
        for k in sorted(_dh): w.writerow(_dh[k])
    log('discount history rows:', len(_dh))

def latest_prices():
    for t in US:
        c = closes(t)
        if c:
            d = max(c); setlive(t, close=c[d], close_date=d)

if __name__ == '__main__':
    load_dh()
    if '--no-prices' not in ARGS: update_prices()
    for step in (sprott, ishares, ssga, aberdeen, small_issuers):
        try: step()
        except Exception as e: log('STEP FAILED', step.__name__, repr(e))
    latest_prices(); compute_disc()
    live['updated'] = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'); live['log'] = LOG[-40:]
    jsave(DATA/'live.json', live)
    r = subprocess.run([sys.executable, str(ROOT/'build_site.py')]); sys.exit(r.returncode)
