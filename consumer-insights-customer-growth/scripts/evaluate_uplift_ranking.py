#!/usr/bin/env python3
"""Evaluate observed randomized uplift ranking by cumulative incremental outcomes."""
import argparse,csv,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);p.add_argument("--bins",type=int,default=10);a=p.parse_args();rows=[]
    with open(a.input,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):rows.append({"score":float(r["uplift_score"]),"t":int(r["treatment"]),"y":float(r["outcome"])})
    rows.sort(key=lambda x:x["score"],reverse=True);bins=[];n=len(rows)
    for i in range(a.bins):
        part=rows[i*n//a.bins:(i+1)*n//a.bins];tr=[x["y"] for x in part if x["t"]==1];co=[x["y"] for x in part if x["t"]==0]
        effect=None if not tr or not co else sum(tr)/len(tr)-sum(co)/len(co)
        bins.append({"bin":i+1,"n":len(part),"treatment_n":len(tr),"control_n":len(co),"observed_effect":effect})
    valid=[x for x in bins if x["observed_effect"] is not None]
    out={"rows":n,"bins":bins,"top_minus_bottom":None if len(valid)<2 else valid[0]["observed_effect"]-valid[-1]["observed_effect"],"warning":"仅适用于可靠随机分配和真实曝光；分箱效应不是个人因果事实"}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
