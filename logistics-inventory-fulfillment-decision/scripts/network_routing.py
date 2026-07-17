#!/usr/bin/env python3
from common import main,n
COSTS=["origin","main_haul","insurance","duty_tax","customs","inbound_last_mile","receiving_putaway","storage","outbound_handling","customer_last_mile","expected_transfer","expected_stockout","expected_damage_loss","financing","disruption_recovery"]
def run(d):
    feasible=[];rejected=[]
    for r in d.get("routes",[]):
        reasons=[]
        for gate in ["compliance_pass","sku_allowed","documents_ready"]:
            if not r.get(gate,False): reasons.append(gate)
        for cap,need_key in [("capacity","required_flow"),("cash_capacity","required_cash")]:
            if n(r,cap)<n(d,need_key): reasons.append(cap)
        if "max_p90_days" in d and n(r,"p90_days")>n(d,"max_p90_days"): reasons.append("p90_days")
        total=sum(n(r,k) for k in COSTS)
        item={"id":r.get("id"),"total_cost":round(total,6),"p90_days":n(r,"p90_days"),"reasons":reasons}
        (rejected if reasons else feasible).append(item)
    feasible.sort(key=lambda x:(x["total_cost"],x["p90_days"],str(x["id"])))
    return {"feasible":feasible,"rejected":rejected,"recommended":feasible[0] if feasible else None,"decision":"select" if feasible else "blocked"}
if __name__=="__main__":main(run)
