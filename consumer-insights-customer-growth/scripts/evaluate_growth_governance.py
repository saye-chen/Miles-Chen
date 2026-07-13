#!/usr/bin/env python3
"""Summarize calibration, drift and group selection outcomes for governance review."""
import argparse,csv,json,math
from collections import defaultdict
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);a=p.parse_args();rows=[]
    with open(a.input,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):rows.append({"p":float(r["prediction"]),"y":float(r["outcome"]),"group":r.get("group") or "all","selected":int(r.get("selected") or 0),"period":r.get("period") or "current"})
    brier=sum((x["p"]-x["y"])**2 for x in rows)/len(rows) if rows else None;groups=[]
    by=defaultdict(list)
    for x in rows:by[x["group"]].append(x)
    for g,v in sorted(by.items()):groups.append({"group":g,"n":len(v),"mean_prediction":sum(x["p"] for x in v)/len(v),"outcome_rate":sum(x["y"] for x in v)/len(v),"selection_rate":sum(x["selected"] for x in v)/len(v)})
    periods=defaultdict(list)
    for x in rows:periods[x["period"]].append(x["p"])
    drift=None
    if "baseline" in periods and "current" in periods:
        drift=abs(sum(periods["current"])/len(periods["current"])-sum(periods["baseline"])/len(periods["baseline"]))
    out={"n":len(rows),"brier":brier,"mean_prediction_drift":drift,"groups":groups,"decision":"review" if not rows or drift is None else "continue_with_review","warning":"群体差异和漂移只触发调查，不自动证明原因或公平性违规"}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
