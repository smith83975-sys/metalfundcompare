import csv,json
# Tax treatment templates (general US rules; site must link prospectus & say "not tax advice")
TAX={
 'grantor':'Grantor trust: taxed as collectibles (long-term gains max 28%); 1099',
 'pfic':'Canadian trust = PFIC; a timely QEF election (IRS Form 8621, filed annually) generally allows regular long-term capital-gains rates; no election = punitive PFIC rules',
 'k1':'Commodity pool (partnership): Section 1256 futures, 60% long-term/40% short-term each year (marked-to-market); Schedule K-1',
 'ric':'1940-Act fund (RIC): regular equity treatment (long-term gains 0/15/20%); 1099',
 'ric_opt':'1940-Act fund (RIC) using options/subsidiary: distributions may be ordinary income or return of capital; 1099 (check prospectus)',
 'ric_lev':'1940-Act leveraged/inverse fund: 1099; distributions often ordinary/short-term (check prospectus)',
 'etn':'ETN (unsecured debt of issuer): gain on sale generally capital gain, but tax treatment uncertain; issuer credit risk; 1099',
 'etn_cpn':'ETN with monthly coupons: coupons likely ordinary income; issuer credit risk; 1099',
 'ca':'Canadian-listed (TSX): Canadian tax rules; for US holders may be PFIC — verify',
}
SSGA='SSGA issuer page (fetched 2026-10-16)'; ISH='iShares product-screener JSON (fetched 2026-10-16)'; SPR='Sprott issuer page (fetched 2026-10-16)'
EDB='etfdb.com list page, data as of 2026-10-15 (third-party)'
F=[]
def add(t,name,issuer,typ,metal,er,er_src,aum_mm,aum_src,inc,inc_src,tax,url,status,notes='',exch='US'):
    F.append(dict(ticker=t,name=name,issuer=issuer,type=typ,metal=metal,listing=exch,expense_ratio_pct=er,expense_ratio_source=er_src,
        aum_usd_millions=aum_mm,aum_source=aum_src,inception=inc,inception_source=inc_src,tax_treatment=TAX[tax],tax_key=tax,official_url=url,verification=status,notes=notes))
V='issuer-verified'; P='partly verified'; U='unverified'
# ---- Physical (grantor trusts)
add('GLD','SPDR Gold Shares','State Street / World Gold Council','physical','gold',0.40,SSGA,141299.0,EDB,'2004-11-18',EDB,'grantor','https://www.ssga.com/us/en/intermediary/etfs/spdr-gold-shares-gld',P,'Daily NAV history XLSX available from SSGA')
add('GLDM','SPDR Gold MiniShares Trust','State Street / World Gold Council','physical','gold',0.10,SSGA,31028.6,EDB,'2018-06-25',EDB,'grantor','https://www.ssga.com/us/en/intermediary/etfs/spdr-gold-minishares-gldm',P)
add('IAU','iShares Gold Trust','BlackRock iShares','physical','gold',0.25,ISH,61817.2,ISH,'2005-01-21',ISH,'grantor','https://www.ishares.com/us/products/239561/ishares-gold-trust',V)
add('IAUM','iShares Gold Trust Micro','BlackRock iShares','physical','gold',0.09,ISH,7975.7,ISH,'2021-06-15',ISH,'grantor','https://www.ishares.com/us/products/306979/ishares-gold-trust-micro',V)
add('SGOL','abrdn Physical Gold Shares ETF','Aberdeen (abrdn)','physical','gold',0.17,EDB,7155.0,EDB,'2009-09-09',EDB,'grantor','https://www.aberdeeninvestments.com/en-us/investor/investment-solutions/commodities/sgol',U,'Aberdeen moved domains; SGOL page URL returned 404 from box — find correct URL')
add('OUNZ','VanEck Merk Gold ETF','VanEck / Merk','physical','gold',0.25,'VanEck issuer page (fetched 2026-10-16)',2700.0,'VanEck issuer page ($2.70B as of 2026-10-15)','2014-05-16','VanEck issuer page','grantor','https://www.vaneck.com/us/en/investments/merk-gold-etf-ounz/overview/',V,'Allows delivery of physical gold to holders')
add('AAAU','Goldman Sachs Physical Gold ETF','Goldman Sachs Asset Management','physical','gold',0.18,EDB,2659.1,EDB,'2018-07-26',EDB,'grantor','https://am.gs.com/en-us/advisors/funds/detail/PV103623/38150K103/goldman-sachs-physical-gold-etf',U,'Issuer page is JS-rendered; 0.18% also cited in GS ETF literature per search')
add('BAR','GraniteShares Gold Trust','GraniteShares','physical','gold',0.17,EDB,1337.6,EDB,'2017-08-31',EDB,'grantor','https://graniteshares.com/etfs/bar/',U,'Issuer page loads fee via JS; third-party sources disagree (0.17% vs 0.18%) — verify in prospectus')
add('FGDL','Franklin Responsibly Sourced Gold ETF','Franklin Templeton','physical','gold',0.15,EDB,432.7,EDB,'2022-06-30',EDB,'grantor','https://www.franklintempleton.com/',U,'Issuer page blocked/JS from box; exact product URL not confirmed')
add('YSAU',"Y'all Street Physical Gold ETF",'Teucrium (sponsor) / Texas Precious Metals (custodian)','physical','gold',0.24,'SEC 424B3 prospectus per web search (not fetched)','','','2026-07 (began trading per 2026-07-15 press release)','Nasdaq/GlobeNewswire press release','grantor','https://www.yallstreetetfs.com/etf/gold-etf/',U,'US-vaulted (Texas)')
add('YSAG',"Y'all Street Physical Silver ETF",'Teucrium (sponsor) / Texas Precious Metals (custodian)','physical','silver','', '', '','','2026-07 (began trading per 2026-07-15 press release)','Nasdaq/GlobeNewswire press release','grantor','https://www.yallstreetetfs.com/',U,'Fee not yet confirmed')
add('SLV','iShares Silver Trust','BlackRock iShares','physical','silver',0.50,ISH,28271.9,ISH,'2006-04-21',ISH,'grantor','https://www.ishares.com/us/products/239855/ishares-silver-trust',V)
add('SIVR','abrdn Physical Silver Shares ETF','Aberdeen (abrdn)','physical','silver',0.30,'Aberdeen issuer page (fetched 2026-10-16)',4073.6,EDB,'2009-07-20',EDB,'grantor','https://www.aberdeeninvestments.com/en-us/investor/investment-solutions/commodities/sivr',P,'Issuer page mentions a voluntary partial fee waiver (0.15%) — clarify net fee before publishing')
add('PPLT','abrdn Physical Platinum Shares ETF','Aberdeen (abrdn)','physical','platinum',0.60,EDB,2008.1,EDB,'2010-01-08',EDB,'grantor','https://www.aberdeeninvestments.com/',U,'Issuer URL not confirmed')
add('PLTM','GraniteShares Platinum Trust','GraniteShares','physical','platinum',0.50,EDB,171.4,EDB,'2018-01-22',EDB,'grantor','https://graniteshares.com/etfs/pltm/',U)
add('PALL','abrdn Physical Palladium Shares ETF','Aberdeen (abrdn)','physical','palladium',0.60,EDB,596.4,EDB,'2010-01-06',EDB,'grantor','https://www.aberdeeninvestments.com/',U,'Issuer URL not confirmed')
add('GLTR','abrdn Physical Precious Metals Basket Shares ETF','Aberdeen (abrdn)','physical','multi (Au/Ag/Pt/Pd)',0.60,EDB,2577.1,EDB,'2010-10-22',EDB,'grantor','https://www.aberdeeninvestments.com/',U,'Issuer URL not confirmed')
# ---- Sprott closed-end trusts
add('PHYS','Sprott Physical Gold Trust','Sprott Asset Management','closed-end physical trust','gold',0.39,SPR+' (MER)',15686.3,SPR+' (Total NAV)','2010-02-25',SPR,'pfic','https://sprott.com/investment-strategies/exchange-listed-products/physical-bullion-funds/gold/',V,'Page shows NAV, price, premium/discount, total oz, units; etfdb lists stale 0.41%',exch='NYSE Arca + TSX')
add('PSLV','Sprott Physical Silver Trust','Sprott Asset Management','closed-end physical trust','silver',0.52,SPR+' (MER)',11897.0,SPR+' (Total NAV, approx)','2010-10-27',SPR,'pfic','https://sprott.com/investment-strategies/exchange-listed-products/physical-bullion-funds/silver/',V,'Premium/discount -4.94% shown on page at fetch; etfdb lists stale 0.67%',exch='NYSE Arca + TSX')
add('CEF','Sprott Physical Gold and Silver Trust','Sprott Asset Management','closed-end physical trust','gold+silver',0.48,SPR+' (MER)',7243.0,SPR+' (Total NAV)','',"",'pfic','https://sprott.com/investment-strategies/exchange-listed-products/physical-bullion-funds/gold-and-silver/',P,'Inception not captured',exch='NYSE Arca + TSX')
add('SPPP','Sprott Physical Platinum and Palladium Trust','Sprott Asset Management','closed-end physical trust','platinum+palladium',0.78,SPR+' (MER)',502.0,SPR+' (Total NAV)','','','pfic','https://sprott.com/investment-strategies/exchange-listed-products/physical-bullion-funds/platinum-and-palladium/',P,'Inception not captured',exch='NYSE Arca + TSX')
# ---- Hybrid
add('SLVR','Sprott Silver Miners & Physical Silver ETF','Sprott Asset Management','hybrid (miners + physical)','silver',0.65,'Sprott ETFs issuer page (fetched 2026-10-16)',649.5,'Sprott ETFs issuer page','2025-01-14','Sprott ETFs issuer page','ric','https://sprottetfs.com/slvr-sprott-silver-miners-physical-silver-etf/',V,'Holds PSLV units plus miners')
add('GDE','WisdomTree Efficient Gold Plus Equity Strategy Fund','WisdomTree','hybrid (gold futures + US stocks)','gold',0.20,'web search snippet of issuer page (page 403 from box)','','','2022-03-17','web search snippet','ric','https://www.wisdomtree.com/us/products/capital-efficient/gde',U,'Directly relevant to gold-vs-stocks angle')
add('GDMN','WisdomTree Efficient Gold Plus Gold Miners Strategy Fund','WisdomTree','hybrid (gold futures + miners)','gold',0.45,'web search snippet of issuer page (page 403 from box)','','','2021-12-16','web search snippet','ric','https://www.wisdomtree.com/us/products/capital-efficient/gdmn',U)
# ---- Miner ETFs
VE='VanEck issuer page (fetched 2026-10-16)'
add('GDX','VanEck Gold Miners ETF','VanEck','miners','gold',0.51,VE,26420.0,VE+' ($26.42B as of 2026-10-15)','2006-05-16',VE,'ric','https://www.vaneck.com/us/en/investments/gold-miners-etf-gdx/overview/',V)
add('GDXJ','VanEck Junior Gold Miners ETF','VanEck','miners (junior)','gold',0.52,VE,8090.0,VE+' ($8.09B as of 2026-10-15)','2009-11-10',VE,'ric','https://www.vaneck.com/us/en/investments/junior-gold-miners-etf-gdxj/overview/',V)
add('RING','iShares MSCI Global Gold Miners ETF','BlackRock iShares','miners','gold',0.39,ISH,2320.7,ISH,'2012-01-31',ISH,'ric','https://www.ishares.com/us/products/239654/ishares-msci-global-gold-miners-etf',V)
SE='Sprott ETFs issuer page (fetched 2026-10-16)'
add('SGDM','Sprott Gold Miners ETF','Sprott Asset Management','miners','gold',0.46,SE+' (net total)',643.7,SE,'2014-07-14',SE,'ric','https://sprottetfs.com/sgdm-sprott-gold-miners-etf/',V,'etfdb shows inception 2014-07-15')
add('SGDJ','Sprott Junior Gold Miners ETF','Sprott Asset Management','miners (junior)','gold',0.50,SE+' (net total)',323.4,EDB,'2015-03-31',EDB,'ric','https://sprottetfs.com/sgdj-sprott-junior-gold-miners-etf/',P)
add('GBUG','Sprott Active Gold & Silver Miners ETF','Sprott Asset Management','miners (active)','gold+silver',0.90,SE+' (net total; footnote mentions 0.89% rate)',168.4,SE,'2025-02-19',SE,'ric','https://sprottetfs.com/gbug-sprott-active-gold-silver-miners-etf/',V)
add('GOAU','U.S. Global GO GOLD and Precious Metal Miners ETF','U.S. Global Investors','miners (royalty tilt)','gold',0.60,EDB,189.8,EDB,'2017-06-27',EDB,'ric','https://www.usglobaletfs.com/',U,'Issuer fund URL returned 404 from box')
add('GOEX','Global X Gold Explorers ETF','Global X','miners (explorers)','gold',0.65,'Global X issuer page (fetched 2026-10-16)',118.9,EDB,'2010-11-03',EDB,'ric','https://www.globalxetfs.com/funds/goex',P)
add('AUAU','Global X Gold Miners ETF','Global X','miners','gold',0.35,'Global X issuer page (fetched 2026-10-16)',6.0,EDB,'2025-12-09',EDB,'ric','https://www.globalxetfs.com/funds/auau',P)
add('AUMI','Themes Gold Miners ETF','Themes ETFs','miners','gold',0.35,'Themes issuer page (fetched 2026-10-16)',23.0,EDB,'2023-12-13',EDB,'ric','https://themesetfs.com/etfs/aumi',P)
add('SIL','Global X Silver Miners ETF','Global X','miners','silver',0.65,'Global X issuer page (fetched 2026-10-16)',4237.8,EDB,'2010-04-19',EDB,'ric','https://www.globalxetfs.com/funds/sil',P)
add('SILJ','Amplify Junior Silver Miners ETF','Amplify ETFs','miners (junior)','silver',0.69,'Amplify issuer page (fetched 2026-10-16)',3384.9,EDB,'2012-11-28',EDB,'ric','https://amplifyetfs.com/silj/',P)
add('SLVP','iShares MSCI Global Silver and Metals Miners ETF','BlackRock iShares','miners','silver (+other metals)',0.39,ISH,856.8,ISH,'2012-01-31',ISH,'ric','https://www.ishares.com/us/products/239656/ishares-msci-global-silver-and-metals-miners-etf',V,'Current official name includes "and Metals"')
add('AGMI','Themes Silver Miners ETF','Themes ETFs','miners','silver',0.35,'Themes issuer page (fetched 2026-10-16)','','','2024-05-03','Themes issuer page','ric','https://themesetfs.com/etfs/agmi',P)
# ---- Futures-based
add('DBP','Invesco DB Precious Metals Fund','Invesco','futures','gold+silver',0.77,EDB,218.3,EDB,'2007-01-05',EDB,'k1','https://www.invesco.com/us/financial-products/etfs/product-detail?audienceType=Investor&ticker=DBP',U,'Invesco page returned HTTP 406 to scripted fetch')
# ---- Leveraged / inverse
PS='ProShares issuer page (fetched 2026-10-16)'
add('UGL','ProShares Ultra Gold','ProShares','leveraged 2x','gold',0.95,PS,719.2,EDB,'2008-12-01',EDB,'k1','https://www.proshares.com/our-etfs/leveraged-and-inverse/ugl',P)
add('GLL','ProShares UltraShort Gold','ProShares','inverse -2x','gold',0.95,PS,96.1,EDB,'2008-12-01',EDB,'k1','https://www.proshares.com/our-etfs/leveraged-and-inverse/gll',P)
add('AGQ','ProShares Ultra Silver','ProShares','leveraged 2x','silver',0.95,PS,1217.8,EDB,'2008-12-01',EDB,'k1','https://www.proshares.com/our-etfs/leveraged-and-inverse/agq',P)
add('ZSL','ProShares UltraShort Silver','ProShares','inverse -2x','silver',0.95,PS,71.3,EDB,'2008-12-01',EDB,'k1','https://www.proshares.com/our-etfs/leveraged-and-inverse/zsl',P)
DX='Direxion issuer page (fetched 2026-10-16; net)'
add('UGLD','Direxion Daily Gold Bull 2X ETF','Direxion','leveraged 2x','gold',1.07,DX+' gross 1.09',13.4,EDB,'2026-05-27',DX,'ric_lev','https://www.direxion.com/product/daily-gold-bull-2x-etf',V)
add('USLV','Direxion Daily Silver Bull 2X ETF','Direxion','leveraged 2x','silver',1.10,DX+' gross 1.12',25.7,EDB,'2026-05-27',DX,'ric_lev','https://www.direxion.com/product/daily-silver-bull-2x-etf',V,'Same ticker as a delisted older ETN; new fund')
add('NUGT','Direxion Daily Gold Miners Index Bull 2X ETF','Direxion','leveraged 2x (miners)','gold',1.13,DX,992.8,EDB,'2010-12-08',DX,'ric_lev','https://www.direxion.com/product/daily-gold-miners-bull-bear-2x-etfs',V)
add('DUST','Direxion Daily Gold Miners Index Bear 2X ETF','Direxion','inverse -2x (miners)','gold',0.99,DX+' gross 1.04',89.1,EDB,'2010-12-08',DX,'ric_lev','https://www.direxion.com/product/daily-gold-miners-bull-bear-2x-etfs',V)
add('JNUG','Direxion Daily Junior Gold Miners Index Bull 2X ETF','Direxion','leveraged 2x (miners)','gold',1.03,DX,396.2,EDB,'2013-10-03',DX,'ric_lev','https://www.direxion.com/product/daily-junior-gold-miners-bull-bear-2x-etfs',V)
add('JDST','Direxion Daily Junior Gold Miners Index Bear 2X ETF','Direxion','inverse -2x (miners)','gold',0.92,DX,34.7,EDB,'2013-10-03',DX,'ric_lev','https://www.direxion.com/product/daily-junior-gold-miners-bull-bear-2x-etfs',V)
add('GDXU','MicroSectors Gold Miners 3X Leveraged ETN','BMO (MicroSectors)','leveraged 3x ETN (miners)','gold',0.95,EDB,1005.0,EDB,'2020-12-02',EDB,'etn','https://microsectors.com/',U)
add('GDXD','MicroSectors Gold Miners -3X Inverse Leveraged ETN','BMO (MicroSectors)','inverse -3x ETN (miners)','gold',0.95,EDB,158.9,EDB,'2020-12-02',EDB,'etn','https://microsectors.com/',U)
add('SHNY','MicroSectors Gold 3X Leveraged ETN','BMO (MicroSectors)','leveraged 3x ETN','gold',0.95,EDB,95.3,EDB,'2023-02-21',EDB,'etn','https://microsectors.com/gold/',U)
add('DULL','MicroSectors Gold -3X Inverse Leveraged ETN','BMO (MicroSectors)','inverse -3x ETN','gold',0.95,EDB,17.3,EDB,'2023-02-22',EDB,'etn','https://microsectors.com/gold/',U)
add('DGP','DB Gold Double Long ETN','Deutsche Bank','leveraged 2x ETN','gold',0.75,EDB,235.5,EDB,'2008-02-27',EDB,'etn','',U,'No issuer page found yet')
add('DGZ','DB Gold Short ETN','Deutsche Bank','inverse -1x ETN','gold',0.75,EDB,1.1,EDB,'2008-02-27',EDB,'etn','',U,'Tiny AUM')
add('DZZ','DB Gold Double Short ETN','Deutsche Bank','inverse -2x ETN','gold',0.75,EDB,0.9,EDB,'2008-02-27',EDB,'etn','',U,'Tiny AUM')
# ---- Income / options / buffer
add('IAUI','NEOS Gold High Income ETF','NEOS Investments','income/options','gold',0.79,'NEOS issuer page (mgmt fee 0.78%, total 0.79%)',652.4,'NEOS issuer page','2025-06-04','NEOS issuer page','ric_opt','https://neosfunds.com/iaui/',V,'etfdb shows inception 2025-06-05')
add('SLVI','NEOS Silver High Income ETF','NEOS Investments','income/options','silver',0.78,'NEOS issuer page',1.8,'NEOS issuer page','2026-10-06','NEOS issuer page','ric_opt','https://neosfunds.com/slvi/',V,'Launched Oct 2026')
add('IGLD','FT Vest Gold Strategy Target Income ETF','First Trust','income/options','gold',0.85,'First Trust issuer page (fetched 2026-10-16)',595.0,EDB,'2021-03-02',EDB,'ric_opt','https://www.ftportfolios.com/Retail/Etf/EtfSummary.aspx?Ticker=IGLD',P)
add('BGLD','FT Vest Gold Strategy Quarterly Buffer ETF','First Trust','buffer/options','gold',0.91,'First Trust issuer page (fetched 2026-10-16)',53.2,EDB,'2021-01-20',EDB,'ric_opt','https://www.ftportfolios.com/Retail/Etf/EtfSummary.aspx?Ticker=BGLD',P)
add('SLVY','FT Vest Silver Strategy & Target Income ETF','First Trust','income/options','silver',0.85,'First Trust issuer page (fetched 2026-10-16)',1.0,'First Trust issuer page','','','ric_opt','https://www.ftportfolios.com/Retail/Etf/EtfSummary.aspx?Ticker=SLVY',P)
add('KGLD','Kurv Gold Enhanced Income ETF','Kurv','income/options','gold',0.99,'Kurv issuer page',161.8,'Kurv issuer page','2025-07-08','Kurv issuer page','ric_opt','https://www.kurvinvest.com/etf/kgld',V)
add('KSLV','Kurv Silver Enhanced Income ETF','Kurv','income/options','silver',0.99,'Kurv issuer page',111.5,'Kurv issuer page','2025-09-29','Kurv issuer page','ric_opt','https://www.kurvinvest.com/etf/kslv',V)
add('GOLI','Defiance Gold Enhanced Options Income ETF','Defiance ETFs','income/options','gold',1.04,'Defiance issuer page (gross)',22.4,'Defiance issuer page','2025-04-01','Defiance issuer page','ric_opt','https://www.defianceetfs.com/goli/',V,'Ticker changed from GLDY on 2026-06-30')
add('GLDW','Roundhill Gold WeeklyPay ETF','Roundhill Investments','income/weekly pay','gold',0.99,'Roundhill issuer page (gross)',18.4,EDB,'2025-10-30','Roundhill issuer page','ric_opt','https://www.roundhillinvestments.com/etf/gldw/',P,'etfdb classifies as leveraged-style weekly pay; verify strategy')
add('USG','USCF Gold Strategy Plus Income Fund ETF','USCF Investments','income/options','gold',0.45,EDB,9.5,EDB,'2021-11-03',EDB,'ric_opt','https://www.uscfinvestments.com/usg',U,'Issuer page values JS-rendered')
add('YGLD','Simplify Gold Strategy ETF','Simplify','income/options','gold',0.53,'Simplify issuer page',32.6,'Simplify issuer page','2024-12-02','Simplify issuer page','ric_opt','https://www.simplify.us/etfs/ygld-simplify-gold-strategy-etf',V)
add('GLDI','UBS ETRACS Gold Shares Covered Call ETN','UBS','income ETN (covered call)','gold',0.65,EDB,181.0,EDB,'2013-01-28',EDB,'etn_cpn','https://etracs.ubs.com/product/detail/index/ticker/GLDI',U,'UBS page returned HTTP 500 to scripted fetch')
add('SLVO','UBS ETRACS Silver Shares Covered Call ETN','UBS','income ETN (covered call)','silver',0.65,EDB,401.0,EDB,'2013-04-16',EDB,'etn_cpn','https://etracs.ubs.com/product/detail/index/ticker/SLVO',U)
add('GLDN','Nicholas Gold Income ETF','Nicholas Wealth (XFUNDS) / Tidal','income/options (miners + metal ETPs)','gold','', '', 4.3,'stockanalysis covered-call list via search (third-party)','2026-02 (launch press release 2026-02-18)','BusinessWire press release','ric_opt','https://nicholasx.com/gldn/',U,'Issuer page JS-rendered')
add('SLVX','Nicholas Silver Income ETF','Nicholas Wealth (XFUNDS) / Tidal','income/options (miners + metal ETPs)','silver','', '', 8.8,'stockanalysis covered-call list via search (third-party)','2026-02 (launch press release 2026-02-18)','BusinessWire press release','ric_opt','https://nicholasx.com/slvx/',U,'Not the Canadian Global X SLVX (TSX)')
add('GDXY','YieldMax Gold Miners Option Income Strategy ETF','YieldMax (Tidal)','income/options (miners)','gold',1.00,'YieldMax issuer page (gross)',294.2,'YieldMax issuer page','2024-05-20','YieldMax issuer page','ric_opt','https://yieldmaxetfs.com/our-etfs/gdxy/',V)
add('GDXW','Roundhill Gold Miners WeeklyPay ETF','Roundhill Investments','income/weekly pay (miners)','gold',0.99,'Roundhill issuer page (gross)',82.4,EDB,'2025-10-30','Roundhill issuer page','ric_opt','https://www.roundhillinvestments.com/etf/gdxw/',P)
add('NUGY','GraniteShares YieldBOOST Gold Miners ETF','GraniteShares','income/options (miners)','gold',1.07,EDB,5.5,EDB,'2025-11-18',EDB,'ric_opt','https://graniteshares.com/etfs/nugy/',U)
add('SLJY','Amplify SILJ Junior Silver Miners Covered Call ETF','Amplify ETFs','income/options (miners)','silver',0.76,'Amplify issuer page (fetched 2026-10-16)',72.6,EDB,'2025-08-19',EDB,'ric_opt','https://amplifyetfs.com/sljy/',P)
# ---- Major Canadian-listed (TSX only) — phase 2, not verified
for t,n,i,typ,m in [('CGL','iShares Gold Bullion ETF','BlackRock iShares Canada','physical','gold'),('SVR','iShares Silver Bullion ETF','BlackRock iShares Canada','physical','silver'),('XGD','iShares S&P/TSX Global Gold Index ETF','BlackRock iShares Canada','miners','gold'),('ZGD','BMO Equal Weight Global Gold Index ETF','BMO Global Asset Management','miners','gold'),('MNT','Royal Canadian Mint Gold Reserves (ETR)','Royal Canadian Mint','physical (exchange-traded receipt)','gold')]:
    add(t,n,i,typ,m,'','','','','','','ca','',U,'Canadian-listed; included for completeness, all fields need verification',exch='TSX')

# ---- Verification pass 2026-10-16 (round 2): issuer pages + SEC filings
SECQ='SEC 10-Q for quarter ended 2026-06-30 (filed 2026-08-07)'
AB='Aberdeen fund page (AUM as of 2026-10-15)'
ABU='https://www.aberdeeninvestments.com/en-us/investor/funds/view-all-funds/'
OV={
 'SGOL':dict(expense_ratio_pct=0.17,expense_ratio_source=SECQ+': Sponsor fee 0.17% annualized',aum_usd_millions=7125.3,aum_source=AB,official_url=ABU+'abrdn-physical-gold-shares-etf-us00326a1043',verification='partly verified',notes='Fee (SEC) and AUM (issuer) verified; inception from etfdb'),
 'PPLT':dict(expense_ratio_pct=0.60,expense_ratio_source=SECQ+': Sponsor fee 0.60% annualized',aum_usd_millions=1922.3,aum_source=AB,official_url=ABU+'abrdn-physical-platinum-shares-etf-us0032601066',verification='partly verified',notes='Fee (SEC) and AUM (issuer) verified; inception from etfdb. 10-Q notes a share action after the close on 2026-05-14'),
 'PALL':dict(expense_ratio_pct=0.60,expense_ratio_source=SECQ+': Sponsor fee 0.60% annualized',aum_usd_millions=590.9,aum_source=AB,official_url=ABU+'abrdn-physical-palladium-shares-etf-us0032621023',verification='partly verified',notes='Fee (SEC) and AUM (issuer) verified; inception from etfdb. 10-Q notes a share action after the close on 2026-05-14'),
 'GLTR':dict(expense_ratio_pct=0.60,expense_ratio_source=SECQ+': Sponsor fee 0.60% annualized',aum_usd_millions=2518.6,aum_source=AB,official_url=ABU+'abrdn-physical-precious-metals-basket-shares-etf-us0032631006',verification='partly verified',notes='Fee (SEC) and AUM (issuer) verified; inception from etfdb'),
 'SIVR':dict(expense_ratio_pct=0.30,expense_ratio_gross_pct=0.45,expense_ratio_source=SECQ+': gross Sponsor fee 0.45%, net 0.30% after a voluntary 0.15% waiver (issuer page: waiver continues until further notice)',aum_usd_millions=3869.4,aum_source=AB,official_url=ABU+'abrdn-physical-silver-shares-etf-us0032641088',verification='partly verified',notes='Net fee 0.30% depends on a voluntary waiver the sponsor can end; inception from etfdb'),
 'AAAU':dict(expense_ratio_source='SEC 10-Q for quarter ended 2026-06-30 (filed 2026-08-07): Sponsor fee 0.18% annualized',verification='partly verified',notes='Fee verified in SEC filing; AUM/inception from etfdb'),
 'BAR':dict(expense_ratio_pct=0.1749,expense_ratio_source='SEC 10-K for FY ended 2026-06-30 (filed 2026-08-13): Sponsor fee 0.1749% annualized',verification='partly verified',notes='Fee verified in SEC filing (third parties round to 0.17%/0.18%); AUM/inception from etfdb'),
 'PLTM':dict(expense_ratio_source='SEC 10-K for FY ended 2026-06-30 (filed 2026-08-13): Sponsor fee 0.50% annualized',verification='partly verified',notes='Fee verified in SEC filing; AUM/inception from etfdb'),
 'FGDL':dict(expense_ratio_source='SEC 10-Q (filed 2026-08-14): Sponsor fee 0.15% of NAV',official_url='https://www.franklintempleton.com/investments/options/exchange-traded-funds/products/39720/SINGLCLASS/franklin-responsibly-sourced-gold-etf/FGDL',verification='partly verified',notes='Fee verified in SEC filing; issuer page is JS-rendered; AUM/inception from etfdb'),
 'YSAU':dict(expense_ratio_source="Y'all Street issuer page + SEC 424B3 (2026-07-13): 0.24%",aum_usd_millions=7.06,aum_source="Y'all Street issuer page (as of 2026-10-14)",inception='2026-07-15',inception_source="Y'all Street issuer page",official_url='https://www.yallstreetetfs.com/etf/gold-etf/',verification='issuer-verified',notes='US-vaulted (Texas); very small fund'),
 'YSAG':dict(expense_ratio_pct=0.39,expense_ratio_source="Y'all Street issuer page + SEC 424B3 (2026-07-13): 0.39%",aum_usd_millions=2.83,aum_source="Y'all Street issuer page (as of 2026-10-14)",inception='2026-07-15',inception_source="Y'all Street issuer page",official_url='https://www.yallstreetetfs.com/etf/silver-etf/',verification='issuer-verified',notes='US-vaulted (Texas); very small fund'),
 'GOAU':dict(expense_ratio_source='U.S. Global issuer page (data as of 2026-10-14)',aum_usd_millions=182.1,aum_source='U.S. Global issuer page (as of 2026-10-14)',inception='2017-06-27',inception_source='U.S. Global issuer page',official_url='https://usglobaletfs.com/fund/goau/',verification='issuer-verified',notes=''),
 'PHYS':dict(expense_ratio_source=SPR+' (MER, as of 2026-10-15)',notes='MER 0.39% per Sprott (etfdb shows a stale 0.41%)'),
 'PSLV':dict(expense_ratio_source=SPR+' (MER, as of 2026-10-15)',aum_usd_millions=11900.0,aum_source=SPR+' (Total NAV $11.90B as of 2026-10-15)',notes='MER 0.52% per Sprott (etfdb shows a stale 0.67%)'),
 'CEF':dict(inception='2018-01-16',inception_source=SPR+' ("Since Inception" date for the current Sprott trust; predecessor Central Fund of Canada is older)',verification='issuer-verified',notes='MER 0.48% per Sprott'),
 'SPPP':dict(inception='2012-12-18',inception_source=SPR+' ("Since Inception")',verification='issuer-verified',notes='MER 0.78% per Sprott'),
 'SLVP':dict(notes='Official name is "iShares MSCI Global Silver and Metals Miners ETF" (etfdb uses an older "Silver Miners" name)'),
}
for x in F:
    x.setdefault('expense_ratio_gross_pct','')
    if x['ticker'] in OV: x.update(OV[x['ticker']])

keys=list(F[0].keys())
with open('funds.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(F)
json.dump(dict(generated='2026-10-16',note='Expense ratios/AUM change; re-verify before publishing. Tax notes are general, not advice.',funds=F),open('funds.json','w'),indent=1)
from collections import Counter
def bucket(t):
    t=t.lower()
    if 'etn' in t and ('lever' in t or 'inverse' in t): return 'leveraged/inverse'
    for k,b in [('closed-end','Sprott closed-end trusts'),('hybrid','hybrid'),('income','income/options/buffer'),('buffer','income/options/buffer'),('lever','leveraged/inverse'),('inverse','leveraged/inverse'),('futures','futures-based'),('miners','miners'),('physical','physical')]:
        if k in t: return b
    return t
c=Counter((bucket(x['type']),x['listing']=='TSX') for x in F)
print(len(F)); [print(k,v) for k,v in sorted(c.items())]
print(Counter(x['verification'] for x in F))
