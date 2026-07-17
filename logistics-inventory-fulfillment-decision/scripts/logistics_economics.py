#!/usr/bin/env python3
from common import main,n
def run(d):
    landed_keys=["purchase_price","tooling_amortization","product_packaging","origin_handling","export_clearance","main_haul","insurance","import_duty","nonrecoverable_tax","brokerage","inbound_last_mile","receiving_putaway","expected_damage","expected_shortage","financing_until_available"]
    fulfillment_keys=["storage_allocation","pick_pack","order_packaging","carrier_base","surcharges","signature_insurance","failed_delivery","redelivery","outbound_loss","return_provision"]
    landed=sum(n(d,k) for k in landed_keys);fulfillment=sum(n(d,k) for k in fulfillment_keys)
    relevant=landed+fulfillment+sum(n(d,k) for k in ["holding","stockout_loss","obsolescence","reverse_loss","expedite_transfer","congestion","service_failure","switching_recovery"])
    out={"landed_cost_per_unit":round(landed,6),"fulfillment_cost_per_order":round(fulfillment,6),"total_relevant_cost":round(relevant,6)}
    if "selling_price" in d:
        contribution=n(d,"selling_price")-relevant;floor=n(d,"minimum_contribution",0)
        out.update({"contribution":round(contribution,6),"minimum_contribution":floor,"decision":"pass" if contribution>=floor else "blocked"})
    return out
if __name__=="__main__":main(run)
