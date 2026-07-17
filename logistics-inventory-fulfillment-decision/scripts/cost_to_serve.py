#!/usr/bin/env python3
from common import main,n
def run(d):
    contract=n(d,"quoted_base")+n(d,"contract_surcharges")+n(d,"operational_extras")+n(d,"penalties_minimums")+n(d,"switching_termination")-n(d,"discounts")-n(d,"sla_credits")-n(d,"claims_recovery")-n(d,"insurance_recovery")
    cts=sum(n(d,k) for k in ["allocated_inbound","holding","warehouse_handling","outbound_fulfillment","customer_service","return_recovery","failure_claim"])-n(d,"recoveries_credits")
    orders=d.get("orders",[]);eligible=len(orders);perfect=0
    required=["right_product","right_quantity","right_condition","right_customer_place","on_original_commit_date","documents_accurate","no_unexpected_claim"]
    for o in orders:
        if all(o.get(k) is True for k in required): perfect+=1
    return {"final_net_logistics_cost":round(contract,6),"cost_to_serve":round(cts,6),"eligible_orders":eligible,"perfect_orders":perfect,"perfect_order_rate":round(perfect/eligible,6) if eligible else None}
if __name__=="__main__":main(run)
