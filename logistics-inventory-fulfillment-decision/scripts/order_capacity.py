#!/usr/bin/env python3
from common import main,n
def run(d):
    atp=n(d,"sellable")+n(d,"eligible_inbound_within_window")-n(d,"confirmed_orders")-n(d,"protected_reserved")-n(d,"operational_reserve")
    atp=max(0,atp)
    capacities={k:n(d,k) for k in ["procurement_production_capacity","transport_capacity","customs_inbound_capacity","warehouse_throughput","last_mile_capacity","cash_supported_capacity"]}
    executable=min(capacities.values()) if capacities else 0
    feasible_new=min(n(d,"new_supply_within_window"),executable)
    ctp=atp+feasible_new
    req=n(d,"demand_requirement")+n(d,"protection_requirement")
    available=n(d,"available_eligible_supply")
    gap=max(0,req-min(available,executable))
    bottlenecks=[k for k,v in capacities.items() if v==executable]
    return {"atp":round(atp,6),"ctp":round(ctp,6),"executable_capacity":round(executable,6),"capacity_gap":round(gap,6),"bottlenecks":bottlenecks,"decision":"promise" if ctp>=n(d,"requested_qty") else "constrain"}
if __name__=="__main__":main(run)
