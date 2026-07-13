#!/usr/bin/env python3
"""Reconcile captured payments, discounts, refunds, taxes and contribution costs."""
import argparse,csv,json
from collections import defaultdict
from pathlib import Path

FIELDS=("captured_payment","recognized_discount","completed_refund","tax_excluded","cogs","fulfillment","platform_fee","payment_fee","return_loss","service_cost","incentive")
def num(row,key):
    try:return float(row.get(key) or 0)
    except ValueError:raise SystemExit(f"invalid number for {key}")
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True);p.add_argument("--tolerance",type=float,default=.01);a=p.parse_args()
    orders=defaultdict(lambda:defaultdict(float));meta={}
    with open(a.input,encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            oid=row.get("order_id")
            if not oid:raise SystemExit("order_id is required")
            for key in FIELDS:orders[oid][key]+=num(row,key)
            meta[oid]={"currency":row.get("currency"),"market":row.get("market"),"reported_net_revenue":row.get("reported_net_revenue")}
    results=[]
    for oid,v in sorted(orders.items()):
        net=v["captured_payment"]-v["recognized_discount"]-v["completed_refund"]-v["tax_excluded"]
        costs=sum(v[k] for k in FIELDS[4:]);cm=net-costs;reported=meta[oid]["reported_net_revenue"]
        difference=None if reported in (None,"") else net-float(reported)
        results.append({"order_id":oid,**meta[oid],"calculated_net_revenue":net,"contribution_margin":cm,"difference":difference,"reconciled":difference is None or abs(difference)<=a.tolerance})
    out={"orders":results,"reconciled":all(x["reconciled"] for x in results),"formula":"captured_payment-recognized_discount-completed_refund-tax_excluded"}
    Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
