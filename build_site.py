#!/usr/bin/env python3
"""Static site generator for MetalFund Compare. Reads funds.json + data/ ; writes site/."""
import json, os, re, shutil, math, itertools, datetime as dt, html, csv
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
ROOT = Path(__file__).resolve().parent; OUT = ROOT/'site'; DATA = ROOT/'data'
SITE_URL = os.environ.get('METALFUND_SITE_URL', 'https://smith83975-sys.github.io/metalfundcompare').rstrip('/')
BASE_PATH = os.environ.get('METALFUND_BASE_PATH', '/metalfundcompare').rstrip('/')  # '' when served at a domain root
import re as _re
def rebase(h): return _re.sub(r'((?:href|src|action)=")/(?!/)', lambda m: m.group(1) + BASE_PATH + '/', h)
SITE_NAME = 'MetalFund Compare'
TODAY = dt.date.today().isoformat()

def jload(p, d):
    try: return json.loads(Path(p).read_text())
    except Exception: return d
src = jload(ROOT/'funds.json', {}); FUNDS = src['funds']; DATA_GEN = src.get('generated', TODAY)
live = jload(DATA/'live.json', {'funds': {}}); LIVE = live.get('funds', {}); UPDATED = live.get('updated', 'not yet run')

THIRD = ('etfdb', 'web search', 'third-party', 'stockanalysis', 'per web search', 'snippet')
def status(source):
    if not source: return 'missing'
    s = source.lower()
    return 'unverified' if any(k in s for k in THIRD) else 'verified'

def bucket(t):
    t = t.lower()
    if 'closed-end' in t: return 'closed-end'
    if 'hybrid' in t: return 'hybrid'
    if 'income' in t or 'buffer' in t: return 'income'
    if 'lever' in t or 'inverse' in t: return 'leveraged'
    if 'futures' in t: return 'futures'
    if 'miners' in t: return 'miners'
    if 'physical' in t: return 'physical'
    return 'other'
BUCKET_LABEL = {'physical': 'Physical trust', 'closed-end': 'Closed-end physical trust', 'hybrid': 'Hybrid', 'miners': 'Miners',
                'futures': 'Futures', 'leveraged': 'Leveraged / inverse', 'income': 'Income / options', 'other': 'Other'}
def metalkey(m):
    m = m.lower()
    if '+' in m or 'multi' in m: return 'multi'
    for k in ('gold', 'silver', 'platinum', 'palladium'):
        if m.startswith(k): return k
    return 'multi'
TAX_LABEL = {'grantor': 'Collectibles (28% max LT)', 'pfic': 'PFIC (QEF election)', 'k1': '60/40 futures, K-1', 'ric': 'Regular fund (1099)',
             'ric_opt': 'Fund, option income', 'ric_lev': 'Leveraged fund (1099)', 'etn': 'ETN (debt)', 'etn_cpn': 'ETN with coupons', 'ca': 'Canadian-listed'}

def series(path):
    return [(r[0], r[1]) for r in jload(path, []) if r and r[1] is not None]

DISC = {}
if (DATA/'discount_history.csv').exists():
    for r in csv.DictReader(open(DATA/'discount_history.csv')):
        DISC.setdefault(r['ticker'], []).append((r['date'], float(r['prem_disc_pct'])))

def fmt_aum(m):
    if m in ('', None): return '—'
    m = float(m)
    return f"${m/1000:,.1f}B" if m >= 1000 else f"${m:,.1f}M" if m >= 1 else f"${m*1000:,.0f}K"

F = {}
for f in FUNDS:
    t = f['ticker']; L = LIVE.get(t, {}); x = dict(f)
    x['slug'] = t.lower(); x['bucket'] = bucket(f['type']); x['bucket_label'] = BUCKET_LABEL[x['bucket']]; x['metalkey'] = metalkey(f['metal'])
    x['fee'] = f['expense_ratio_pct'] if f['expense_ratio_pct'] != '' else None
    x['fee_status'] = status(f['expense_ratio_source']) if x['fee'] is not None else 'missing'
    if L.get('aum_usd_millions'):
        x['aum'] = L['aum_usd_millions']; x['aum_src'] = L.get('aum_source', 'issuer') + (f" (as of {L['aum_date']})" if L.get('aum_date') else ''); x['aum_status'] = 'verified'; x['aum_date'] = L.get('aum_date')
    else:
        x['aum'] = f['aum_usd_millions'] if f['aum_usd_millions'] != '' else None; x['aum_src'] = f['aum_source']; x['aum_status'] = status(f['aum_source']) if x['aum'] else 'missing'; x['aum_date'] = None
    x['aum_fmt'] = fmt_aum(x['aum'])
    x['inc_status'] = status(f['inception_source']) if f['inception'] else 'missing'
    x['tax_label'] = TAX_LABEL.get(f['tax_key'], f['tax_key'])
    x['pd'] = L.get('prem_disc_pct'); x['pd_date'] = L.get('prem_disc_date') or L.get('nav_date'); x['pd_src'] = L.get('prem_disc_source'); x['pd_flag'] = L.get('prem_disc_flag', False); x['pd_kind'] = 'published' if 'Sprott' in (L.get('prem_disc_source') or '') else 'indicative'
    x['nav'] = L.get('nav'); x['nav_date'] = L.get('nav_date'); x['close'] = L.get('close'); x['close_date'] = L.get('close_date')
    x['prices'] = series(DATA/'prices'/f'{t}.json')
    x['disc'] = sorted(DISC.get(t, []))
    vols = [r[2] for r in jload(DATA/'prices'/f'{t}.json', [])[-30:] if len(r) > 2 and r[2]]
    x['avg_vol'] = sum(vols)/len(vols) if vols else None
    x['dollar_vol'] = x['avg_vol'] * x['close'] if x['avg_vol'] and x['close'] else None
    x['ounces'] = L.get('ounces')
    x['inc_note'] = ''; x['units'] = L.get('units')
    x['is_us'] = f['listing'] != 'TSX'
    F[t] = x
ORDER = sorted(F, key=lambda t: (-(F[t]['aum'] or 0)))

# ---------- fee drag ----------
def drag(fee, years, amount=10000):
    if fee is None: return None
    return amount * (1 - (1 - fee/100) ** years)

# ---------- SVG charts ----------
def svg_line(points, w=640, h=180, zero=False, pct=False, color='#1f6f5c'):
    pts = [(d, v) for d, v in points if v is not None]
    if len(pts) < 2: return ''
    vs = [v for _, v in pts]; lo, hi = min(vs), max(vs)
    if zero: lo, hi = min(lo, 0), max(hi, 0)
    if hi == lo: hi += 1; lo -= 1
    pad = 28; n = len(pts)
    X = lambda i: pad + i * (w - pad - 8) / (n - 1); Y = lambda v: 8 + (hi - v) * (h - 36) / (hi - lo)
    path = ' '.join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, (_, v) in enumerate(pts))
    lab = (lambda v: f"{v:+.1f}%") if pct else (lambda v: f"${v:,.2f}")
    z = f'<line x1="{pad}" x2="{w-8}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="#999" stroke-dasharray="3 3"/>' if zero else ''
    return (f'<svg viewBox="0 0 {w} {h}" class="chart" role="img" aria-label="chart from {pts[0][0]} to {pts[-1][0]}">'
            f'<text x="2" y="14" class="ax">{lab(hi)}</text><text x="2" y="{h-24}" class="ax">{lab(lo)}</text>{z}'
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.8"/>'
            f'<text x="{pad}" y="{h-6}" class="ax">{pts[0][0]}</text><text x="{w-8}" y="{h-6}" class="ax" text-anchor="end">{pts[-1][0]}</text></svg>')

# ---------- comparison pairs ----------
POPULAR = [('GLD', 'GLDM', 'IAU'), ('SLV', 'PSLV', 'SIVR'), ('GLD', 'GDX'), ('GLD', 'IAU'), ('GLD', 'GLDM'), ('GLDM', 'IAU'), ('IAU', 'IAUM'),
           ('GLDM', 'IAUM'), ('SLV', 'PSLV'), ('SLV', 'SIVR'), ('PSLV', 'SIVR'), ('PHYS', 'GLD'), ('PHYS', 'IAU'), ('PHYS', 'GLDM'), ('PHYS', 'PSLV'),
           ('GDX', 'GDXJ'), ('GDX', 'RING'), ('GDX', 'SGDM'), ('SIL', 'SILJ'), ('SLV', 'SIL'), ('PSLV', 'SIL'), ('SLVR', 'SIL'), ('SLVR', 'PSLV'),
           ('CEF', 'GLTR'), ('PPLT', 'PLTM'), ('PPLT', 'SPPP'), ('PALL', 'SPPP'), ('GLD', 'SLV'), ('GLD', 'SGOL'), ('IAU', 'SGOL'), ('GLD', 'UGL'),
           ('NUGT', 'GDX'), ('GDX', 'GDXY'), ('OUNZ', 'GLD'), ('BAR', 'GLDM')]
def cgroup(x):
    b = x['bucket']
    if not x['is_us']: return None
    if b in ('physical', 'closed-end'): return ('physical', x['metalkey'])
    if b in ('miners', 'income'): return (b, x['metalkey'])
    if b == 'leveraged': return (x['type'], x['metalkey'])
    return None
seen = set(); COMPARES = []
def add_cmp(ts, popular=False):
    ts = tuple(t for t in ts if t in F)
    if len(ts) < 2: return
    key = frozenset(ts)
    if key in seen: return
    seen.add(key); COMPARES.append(dict(tickers=ts, slug='-vs-'.join(t.lower() for t in ts), popular=popular))
for p in POPULAR: add_cmp(p, True)
groups = {}
for t in ORDER:
    g = cgroup(F[t])
    if g: groups.setdefault(g, []).append(t)
for g, ts in groups.items():
    for a, b in itertools.combinations(ts, 2): add_cmp((a, b))   # larger fund first
CMP_BY_T = {}
for c in COMPARES:
    for t in c['tickers']: CMP_BY_T.setdefault(t, []).append(c)

STRUCT = {'physical': 'a US grantor trust that holds the metal', 'closed-end': 'a Canadian closed-end trust that holds the metal and can trade away from NAV',
          'hybrid': 'a hybrid fund', 'miners': 'a fund of mining-company stocks', 'futures': 'a futures-based commodity pool',
          'leveraged': 'a leveraged/inverse product that resets daily', 'income': 'an options-income strategy fund'}
def verdict(ts):
    xs = [F[t] for t in ts]; out = []
    fees = [(x['fee'], x['ticker']) for x in xs if x['fee'] is not None]
    if len(fees) == len(xs):
        fees.sort(); lo, hi = fees[0], fees[-1]
        if hi[0] > lo[0]:
            diff = (hi[0] - lo[0]) * 100  # $ per $10k per year (approx)
            out.append(f"{lo[1]} has the lowest stated expense ratio ({lo[0]:.2f}%). On $10,000, that is about ${diff:,.0f} a year less than {hi[1]} ({hi[0]:.2f}%), "
                       f"or about ${drag(hi[0],10)-drag(lo[0],10):,.0f} over 10 years if the metal price stayed flat.")
        else: out.append(f"All have the same stated expense ratio ({lo[0]:.2f}%).")
        for x in xs:
            if x.get('expense_ratio_gross_pct'): out.append(f"{x['ticker']}'s {x['fee']:.2f}% is net of a voluntary fee waiver the sponsor can end (gross {x['expense_ratio_gross_pct']}%).")
            if x['fee_status'] == 'unverified': out.append(f"{x['ticker']}'s fee is a third-party figure not yet verified with the issuer.")
    else: out.append("At least one fee is not yet verified/available, so no fee verdict is shown.")
    if len({x['bucket'] for x in xs}) > 1:
        out.append('Structure differs: ' + '; '.join(f"{x['ticker']} is {STRUCT.get(x['bucket'], x['type'])}" for x in xs) + '.')
    if len({x['tax_key'] for x in xs}) > 1:
        out.append('US tax treatment differs: ' + '; '.join(f"{x['ticker']}: {x['tax_label']}" for x in xs) + '. See the tax guide.')
    a = [(x['aum'], x['ticker']) for x in xs if x['aum']]
    if len(a) == len(xs):
        a.sort(reverse=True); out.append(f"{a[0][1]} is the largest by assets ({fmt_aum(a[0][0])}).")
    dv = [(x['dollar_vol'], x['ticker']) for x in xs if x['dollar_vol']]
    if len(dv) == len(xs):
        dv.sort(reverse=True); out.append(f"{dv[0][1]} trades the most (about {fmt_aum(dv[0][0]/1e6)} a day over the last 30 sessions), which usually means tighter spreads.")
    for x in xs:
        if x['pd'] is not None and x['pd_kind'] == 'published' and abs(x['pd']) >= 1:
            out.append(f"{x['ticker']} last traded at a {'discount' if x['pd']<0 else 'premium'} of {abs(x['pd']):.2f}% to NAV ({x['pd_date']}).")
    if any(x['bucket'] == 'leveraged' for x in xs): out.append('Leveraged/inverse products reset daily and are generally meant for short holding periods.')
    return out


# ---------- newsletter archive (newsletter/issue-NNN.md, auto-discovered) ----------
import markdown as _md
def load_issues():
    out = []
    for fp in sorted((ROOT/'newsletter').glob('issue-[0-9][0-9][0-9].md')):
        raw = fp.read_text(); meta = {}; body = raw
        if raw.startswith('---\n'):
            fm, body = raw[4:].split('\n---\n', 1)
            for line in fm.splitlines():
                if line and not line.startswith((' ', '-')) and ':' in line:
                    k, v = line.split(':', 1); meta[k.strip()] = v.strip().strip('"')
        lines = body.strip().splitlines(); kicker = ''
        if lines and lines[0].startswith('# '): kicker = lines.pop(0)[2:].strip()
        lines = [l for l in lines if not l.startswith("*You're getting this")]   # email-only footer
        html_body = _md.markdown('\n'.join(lines), extensions=['extra', 'sane_lists'])
        html_body = html_body.replace('href="' + SITE_URL + '/', 'href="/')   # make site links relative (rebased later)
        slug = fp.stem; d = meta.get('date', '')
        try: dlabel = dt.date.fromisoformat(d).strftime('%b %-d, %Y')
        except Exception: dlabel = d
        out.append(dict(slug=slug, num=int(slug.split('-')[1]), title=meta.get('subject', kicker or slug), kicker=kicker or f'Issue #{int(slug.split("-")[1])}',
                        date=d, date_label=dlabel, data_as_of=meta.get('data_as_of', ''), preview=meta.get('preview', ''), html=html_body))
    return sorted(out, key=lambda x: x['num'], reverse=True)
ISSUES = load_issues()

# ---------- render ----------
env = Environment(loader=FileSystemLoader(ROOT/'templates'), autoescape=select_autoescape(['html']))
def pct(v, d=2): return '—' if v is None else f"{v:.{d}f}%"
env.filters['pct'] = pct
env.filters['money'] = lambda v: '—' if v is None else f"${v:,.0f}"
env.globals.update(SITE_NAME=SITE_NAME, SITE_URL=SITE_URL, UPDATED=UPDATED, DATA_GEN=DATA_GEN, TODAY=TODAY, BUCKET_LABEL=BUCKET_LABEL, drag=drag)
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(); shutil.copytree(ROOT/'static', OUT/'static')
PAGES = []
def write(path, tpl, **ctx):
    p = OUT/path.strip('/')/'index.html' if not path.endswith('.html') else OUT/path.strip('/')
    p.parent.mkdir(parents=True, exist_ok=True)
    ctx.setdefault('canonical', SITE_URL + path)
    p.write_text(rebase(env.get_template(tpl).render(path=path, **ctx))); PAGES.append(path)

us = [F[t] for t in ORDER if F[t]['is_us']]; ca = [F[t] for t in ORDER if not F[t]['is_us']]
cheapest_gold = min((x for x in us if x['bucket'] == 'physical' and x['metalkey'] == 'gold' and x['fee'] is not None and x['fee_status'] == 'verified'), key=lambda x: x['fee'], default=None)
cheapest_silver = min((x for x in us if x['bucket'] in ('physical', 'closed-end') and x['metalkey'] == 'silver' and x['fee'] is not None and x['fee_status'] == 'verified'), key=lambda x: x['fee'], default=None)
disc_now = sorted([x for x in us if x['pd'] is not None and x['pd_kind'] == 'published'], key=lambda x: x['pd'])
write('/', 'index.html', funds=us + ca, cheapest_gold=cheapest_gold, cheapest_silver=cheapest_silver, biggest_disc=disc_now[0] if disc_now else None,
      popular=[c for c in COMPARES if c['popular']][:12], title=f'{SITE_NAME}: compare gold, silver & precious-metal ETFs by fee, size and tax',
      description='Free, sourced comparison of 80 gold, silver, platinum and palladium funds: expense ratios, assets, premium/discount to NAV and US tax treatment.')
for t, x in F.items():
    write(f'/fund/{x["slug"]}/', 'fund.html', f=x, compares=CMP_BY_T.get(t, [])[:24],
          price_svg=svg_line(x['prices'][-260:]), disc_svg=svg_line(x['disc'][-260:], zero=True, pct=True, color='#b5532b'),
          drags=[(n, drag(x['fee'], n)) for n in (1, 5, 10, 20)],
          title=f"{t}: {x['name']} — fee, assets, tax | {SITE_NAME}",
          description=f"{x['name']} ({t}): expense ratio {pct(x['fee'])}, assets {x['aum_fmt']}, {x['bucket_label'].lower()}, US tax: {x['tax_label']}. Sources and data dates listed.")
for c in COMPARES:
    xs = [F[t] for t in c['tickers']]; names = ' vs '.join(c['tickers'])
    write(f'/compare/{c["slug"]}/', 'compare.html', xs=xs, c=c, verdict=verdict(c['tickers']),
          drags={x['ticker']: [drag(x['fee'], n) for n in (1, 5, 10, 20)] for x in xs},
          title=f"{names}: which is better? Fees, tax, size compared | {SITE_NAME}",
          description=f"{names} side by side: expense ratio, 10-year fee cost on $10,000, assets, trading volume, premium/discount and US tax treatment.")
write('/compare/', 'compare_index.html', compares=COMPARES, F=F, title=f'All fund comparisons | {SITE_NAME}', description='Every head-to-head comparison of gold, silver and precious-metal funds on MetalFund Compare.')
calc_funds = [dict(t=x['ticker'], n=x['name'], fee=x['fee'], s=x['fee_status']) for x in us if x['fee'] is not None]
write('/tools/fee-drag/', 'fee_drag.html', calc_json=json.dumps(calc_funds), title=f'Fee drag calculator for gold & silver ETFs | {SITE_NAME}',
      description='See how much an ETF expense ratio costs you over time. Compare up to three gold, silver or precious-metal funds.')
write('/tax/', 'tax.html', funds=us + ca, title=f'How gold & silver ETFs are taxed (US): collectibles, PFIC, 60/40 | {SITE_NAME}',
      description='Plain-English guide to US tax treatment of physical metal trusts (28% collectibles rate), Sprott PFIC trusts, futures funds (60/40), miners ETFs and ETNs.')
write('/discounts/', 'discounts.html', rows=[x for x in us if x['pd'] is not None], sprott=[(F[t], svg_line(F[t]['disc'], zero=True, pct=True, color='#b5532b')) for t in ('PSLV', 'PHYS', 'CEF', 'SPPP')],
      title=f'Premium / discount to NAV: Sprott trusts and metal ETFs | {SITE_NAME}', description='Daily premium/discount to NAV for PSLV, PHYS, CEF, SPPP and physically backed metal ETFs, with history.')
write('/methodology/', 'methodology.html', counts={k: sum(1 for x in F.values() if x['verification'] == k) for k in ('issuer-verified', 'partly verified', 'unverified')},
      log=live.get('log', []), title=f'Methodology & sources | {SITE_NAME}', description='Where every number on MetalFund Compare comes from and how it is checked.')
write('/disclaimer/', 'disclaimer.html', title=f'Disclaimer | {SITE_NAME}', description='MetalFund Compare is for information only and is not investment, tax or legal advice.')
write('/newsletter/', 'newsletter.html', issues=ISSUES, title=f'Weekly metal-fund newsletter | {SITE_NAME}', description='Fee cuts, new launches and discount moves in gold and silver funds, once a week.')
for it in ISSUES:
    write(f'/newsletter/{it["slug"]}/', 'issue.html', it=it, title=f"{it['title']} | MetalFund Weekly Brief", description=it['preview'] or it['title'])
(OUT/'404.html').write_text(rebase(env.get_template('404.html').render(path='/404', title='Page not found', description='', canonical=SITE_URL + '/404')))
# SEO files
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in PAGES: sm.append(f'<url><loc>{html.escape(SITE_URL + p)}</loc><lastmod>{TODAY}</lastmod></url>')
sm.append('</urlset>'); (OUT/'sitemap.xml').write_text('\n'.join(sm))
(OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
print(f"built {len(PAGES)} pages: {sum(1 for p in PAGES if p.startswith('/fund/'))} fund, {sum(1 for p in PAGES if p.startswith('/compare/') and p != '/compare/')} compare, {len(PAGES) - sum(1 for p in PAGES if p.startswith(('/fund/','/compare/')))+1} other")
