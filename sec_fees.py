import json,re,html,time,subprocess,sys
UA="MetalFundCompare preview research (non-commercial, low volume)"
def get(u,out):
    p=subprocess.run(["curl","-s","-A",UA,"--max-time","60","-o",out,"-w","%{http_code}",u],capture_output=True,text=True); time.sleep(0.4); return p.stdout
CIKS={'SIVR':1450922,'SGOL':1450923,'PALL':1459862,'PPLT':1460235,'GLTR':1483386,'BAR':1690437,'PLTM':1690842,'AAAU':1708646,'FGDL':1858258,'YSAG':2087989}
res={}
for t,c in CIKS.items():
    f=f"raw/sec/sub_{t}.json"; code=get(f"https://data.sec.gov/submissions/CIK{c:010d}.json",f)
    try: d=json.load(open(f))
    except Exception as e: print(t,code,'bad'); continue
    r=d['filings']['recent']
    picks=[i for i,fm in enumerate(r['form']) if fm in ('10-K','10-Q','424B3','S-1','S-1/A','POS AM','424B4')]
    out=[]
    for i in picks[:4]:
        acc=r['accessionNumber'][i].replace('-',''); doc=r['primaryDocument'][i]
        u=f"https://www.sec.gov/Archives/edgar/data/{c}/{acc}/{doc}"
        fn=f"raw/sec/{t}_{r['form'][i].replace('/','')}_{r['filingDate'][i]}.htm"; code=get(u,fn)
        s=open(fn,errors='ignore').read(); s=re.sub(r'<[^>]+>',' ',s); s=html.unescape(s); s=re.sub(r'\s+',' ',s)
        hits=[s[max(0,m.start()-150):m.start()+250] for m in re.finditer(r"(?i)sponsor.{0,3}s fee|sponsor fee|waive",s)][:3]
        out.append(dict(form=r['form'][i],date=r['filingDate'][i],url=u,code=code,hits=hits))
        if hits and r['form'][i] in ('10-K','10-Q','424B3','424B4'): break
    res[t]=out
json.dump(res,open('raw/sec/fees.json','w'),indent=1)
for t,o in res.items():
    print('=====',t)
    for x in o:
        print(x['form'],x['date'],x['code'],x['url'])
        for h in x['hits']: print('   >',h[:400])
