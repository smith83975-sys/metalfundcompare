import re,html,subprocess,concurrent.futures as cf,json,sys
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[1]) if l.strip()]
def go(r):
    t,u=r; f=f"raw/pages/{t}.html"
    p=subprocess.run(["curl","-sL","-A",UA,"--max-time","30","-o",f,"-w","%{http_code} %{url_effective}",u],capture_output=True,text=True)
    code,eff=(p.stdout.split(' ',1)+[''])[:2]
    try: s=open(f,encoding='utf-8',errors='ignore').read()
    except: s=''
    s=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.S); s=html.unescape(re.sub(r'<[^>]+>',' ',s)); s=re.sub(r'\s+',' ',s)
    ers=re.findall(r'(?:Expense Ratio|Expense ratio|Management Fee|Sponsor Fee|Sponsor’s Fee|Sponsor\'s Fee|Total Annual|Net Expense|Gross Expense|MER)[^%]{0,60}?(\d\.\d{2})\s?%',s)
    return dict(ticker=t,url=u,code=code,final=eff,len=len(s),has_ticker=t in s,ers=ers[:6])
with cf.ThreadPoolExecutor(10) as ex:
    out=list(ex.map(go,rows))
json.dump(out,open(sys.argv[2],'w'),indent=1)
for o in out: print(o['ticker'],o['code'],o['len'],o['has_ticker'],o['ers'],o['final'][:90] if o['final']!=o['url'] else '')
