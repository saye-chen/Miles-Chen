#!/usr/bin/env python3
from common import main,n,num
def run(d):
    total=n(d,"total_eligible_inventory");oper=n(d,"operational_reserve")
    rows=[];base_total=0
    for x in d.get("platforms",[]):
        base=n(x,"base_protection")+n(x,"event_reservation")+n(x,"after_sales_reserve");base_total+=base
        contribution=num(x.get("incremental_contribution",0),"incremental_contribution")
        value=n(x,"avoided_stockout_loss")+contribution+n(x,"service_value")-n(x,"incremental_fulfillment")-n(x,"transfer_cost")-n(x,"misallocation_risk")
        rows.append({"id":x.get("id"),"base":base,"value":value,"max_extra":n(x,"max_extra")})
    pool=total-oper-base_total
    if pool<0: return {"decision":"blocked","shortfall":round(-pool,6),"allocations":rows}
    for x in sorted(rows,key=lambda z:(-z["value"],str(z["id"]))):
        extra=min(pool,x["max_extra"]) if x["value"]>0 else 0;x["extra"]=extra;x["total"]=x["base"]+extra;pool-=extra
    for x in rows:
        x.setdefault("extra",0);x.setdefault("total",x["base"])
    return {"decision":"allocate","shared_pool_initial":round(total-oper-base_total,6),"unallocated":round(pool,6),"allocations":rows,"conserved":abs(sum(x["total"] for x in rows)+oper+pool-total)<1e-9}
if __name__=="__main__":main(run)
