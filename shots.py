from playwright.sync_api import sync_playwright
B='http://127.0.0.1:8080'
shots=[('home_desktop','/',1366,900,True),('fund_pslv','/fund/pslv/',1366,900,True),('fund_gld','/fund/gld/',1366,900,True),
       ('compare_gld_gldm_iau','/compare/gld-vs-gldm-vs-iau/',1366,900,True),('compare_slv_pslv_sivr','/compare/slv-vs-pslv-vs-sivr/',1366,900,True),
       ('fee_calculator','/tools/fee-drag/',1366,900,False),('home_mobile','/',390,844,False),('compare_mobile','/compare/gld-vs-gdx/',390,844,False)]
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,path,w,h,full in shots:
        pg=b.new_page(viewport={'width':w,'height':h}); errs=[]
        pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto(B+path,wait_until='networkidle'); pg.wait_for_timeout(300)
        pg.screenshot(path=f'shots/{name}.png',full_page=full and name.startswith('home') is False)
        if name=='home_desktop': pg.screenshot(path='shots/home_desktop_full.png',full_page=True)
        print(name,'errors:',errs)
    # interaction test: filter + sort
    pg=b.new_page(); pg.goto(B+'/'); pg.select_option('#f-metal','silver'); pg.click('th[data-k=fee]')
    print('silver rows visible:',pg.eval_on_selector_all('#funds tbody tr',"rs=>rs.filter(r=>r.style.display!=='none').map(r=>r.dataset.t).slice(0,8)"))
    pg.goto(B+'/tools/fee-drag/'); print('calc:',pg.inner_text('#out')[:300])
    b.close()
