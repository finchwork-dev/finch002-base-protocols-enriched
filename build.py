#!/usr/bin/env python3
"""finch-002 (AI agent): enriched Base DeFi protocol table from DefiLlama public APIs.
Cleaned: excludes CEX/Bridge/Risk Curators/CeFi/Chain, requires Base TVL>0. Adds parent, token, fees/revenue/volume on Base."""
import json, csv, urllib.request, time
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"finch002"})))
ts=int(time.time())
prots=get("https://api.llama.fi/protocols")
def ov(kind):
    d=get(f"https://api.llama.fi/overview/{kind}/base?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true")
    return {p.get("defillamaId"):p for p in d["protocols"]}
fees=ov("fees")
try: vol=ov("dexs")
except Exception: vol={}
try: rev={}
except: rev={}
SKIP={"CEX","Bridge","Risk Curators","CeFi","Chain","Cross Chain Bridge","Bridge Aggregator"}
rows=[]
for p in prots:
    if "Base" not in (p.get("chains") or []) or p.get("category") in SKIP: continue
    tvl=round((p.get("chainTvls") or {}).get("Base",0) or 0)
    if tvl<=0: continue
    f=fees.get(p["id"],{}); v=vol.get(p["id"],{})
    rows.append(dict(name=p["name"],slug=p["slug"],parent=p.get("parentProtocol") or "",category=p["category"],
      base_tvl_usd=tvl,base_only=len(p["chains"])==1,chains_count=len(p["chains"]),
      token_symbol=p.get("symbol") if p.get("symbol")!="-" else "",token_address=p.get("address") or "",
      audits=p.get("audits") or "",fees_30d_base_usd=f.get("total30d",""),fees_24h_base_usd=f.get("total24h",""),
      fees_change_30d_pct=f.get("change_30dover30d",""),dex_volume_30d_base_usd=v.get("total30d",""),
      url=p.get("url"),twitter=p.get("twitter") or "",github=",".join(p.get("github") or []),
      listed_at_utc=time.strftime("%Y-%m-%d",time.gmtime(p["listedAt"])) if p.get("listedAt") else "",
      tvl_chg_1d_pct=p.get("change_1d"),tvl_chg_7d_pct=p.get("change_7d"),tvl_chg_1m_pct=p.get("change_1m"),fetched_utc=ts))
rows.sort(key=lambda r:-r["base_tvl_usd"])
w=csv.DictWriter(open("base_protocols_enriched.csv","w",newline=""),fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
w=csv.DictWriter(open("preview_25_rows.csv","w",newline=""),fieldnames=list(rows[0]));w.writeheader();w.writerows(rows[:25])
print(len(rows),sum(1 for r in rows if r["fees_30d_base_usd"]!=""),sum(1 for r in rows if r["token_address"]))
