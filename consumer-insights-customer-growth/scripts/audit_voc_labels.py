#!/usr/bin/env python3
"""Audit dual-coded VOC labels by language/market with Cohen's kappa."""
import argparse,csv,json
from collections import Counter,defaultdict
from pathlib import Path

def metrics(rows):
    n=len(rows)
    if not n:return {"n":0,"agreement":None,"kappa":None}
    agree=sum(a==b for a,b in rows);ca=Counter(a for a,_ in rows);cb=Counter(b for _,b in rows)
    pe=sum(ca[k]*cb[k] for k in set(ca)|set(cb))/(n*n);po=agree/n;k=None if pe==1 else (po-pe)/(1-pe)
    return {"n":n,"agreement":po,"kappa":k}
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);a=p.parse_args();groups=defaultdict(list);low=0;total=0
    with open(a.input,encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            total+=1;groups[(row.get("language") or "unknown",row.get("market") or "unknown")].append((row.get("label_a"),row.get("label_b")))
            if row.get("confidence") in {"low",""}:low+=1
    out={"total":total,"low_confidence":{"numerator":low,"denominator":total,"rate":None if not total else low/total},"groups":[{"language":k[0],"market":k[1],**metrics(v)} for k,v in sorted(groups.items())]}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
