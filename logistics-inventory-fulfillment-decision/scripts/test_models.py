#!/usr/bin/env python3
import json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parent
def run(name,data,expect_ok=True):
    with tempfile.TemporaryDirectory() as td:
        i=Path(td)/"in.json";o=Path(td)/"out.json";i.write_text(json.dumps(data),encoding="utf-8")
        p=subprocess.run(["python3",str(ROOT/name),"--input",str(i),"--output",str(o)],capture_output=True,text=True)
        out=json.loads(o.read_text())
        if expect_ok and p.returncode: raise AssertionError(out)
        return out
class D07Models(unittest.TestCase):
    def test_route_enforces_capacity_and_cash_capacity(self):
        out=run("network_routing.py",{"required_flow":80,"required_cash":1000,"routes":[
            {"id":"cheap","compliance_pass":True,"sku_allowed":True,"documents_ready":True,"capacity":50,"cash_capacity":5000,"main_haul":1,"p90_days":5},
            {"id":"cash_short","compliance_pass":True,"sku_allowed":True,"documents_ready":True,"capacity":100,"cash_capacity":900,"main_haul":2,"p90_days":5},
            {"id":"feasible","compliance_pass":True,"sku_allowed":True,"documents_ready":True,"capacity":100,"cash_capacity":1200,"main_haul":3,"p90_days":5}]})
        self.assertEqual(out["recommended"]["id"],"feasible")
        rejected={x["id"]:x["reasons"] for x in out["rejected"]}
        self.assertIn("capacity",rejected["cheap"])
        self.assertIn("cash_capacity",rejected["cash_short"])

    def test_replenishment_emits_operational_dates(self):
        out=run("replenishment.py",{"order_date":"2026-07-17","expected_protection_demand":100,"target_demand_quantile":120,"target_inventory_position":150,"current_inventory_position":20,"supplier_confirmation_days":1,"production_days":4,"quality_release_days":1,"origin_handling_days":1,"main_haul_days":4,"customs_days":1,"inbound_days":2,"receiving_putaway_days":1})
        self.assertEqual(out["schedule"]["confirmed_date"],"2026-07-18")
        self.assertEqual(out["schedule"]["available_to_sell_date"],"2026-08-01")

    def test_forecast_interval_and_bias(self):
        out=run("demand_forecast.py",{"history":[10,12,11,13,14,15],"window":3,"horizon":2,"actual":[14,16],"forecast":[13,15]})
        self.assertGreaterEqual(out["upper"],out["lower"])
        self.assertIn("wape",out["metrics"])
    def test_intermittent_and_stockout_forecast_routes(self):
        out=run("demand_forecast.py",{"history":[0,0,8,0,0,10,0,0],"horizon":3,"stockout_flags":[False,False,False,False,True,False,False,False]})
        self.assertTrue(out["method"].startswith("croston"));self.assertEqual(out["decision_quality"],"conditional");self.assertEqual(len(out["forecast"]),3)

    def test_lead_time_uses_tail_probability(self):
        out=run("lead_time_service.py",{"lead_time_samples":[5,6,7,8,20],"promise_days":7,"target_probability":0.8})
        self.assertEqual(out["decision"],"blocked")
        self.assertGreaterEqual(out["p95"],out["p90"])

    def test_multiwarehouse_flow_conserves_and_reports_unmet(self):
        out=run("multi_warehouse_flow.py",{"warehouses":[{"id":"W1","capacity":5},{"id":"W2","capacity":4}],"destinations":[{"id":"A","demand":6},{"id":"B","demand":5}],"arcs":[{"warehouse":"W1","destination":"A","unit_cost":1,"capacity":5,"compliance_pass":True},{"warehouse":"W2","destination":"A","unit_cost":2,"capacity":4,"compliance_pass":True},{"warehouse":"W2","destination":"B","unit_cost":1,"capacity":4,"compliance_pass":True}]})
        self.assertEqual(out["decision"],"blocked")
        self.assertAlmostEqual(sum(x["qty"] for x in out["flows"]),9)
        self.assertAlmostEqual(sum(out["unmet"].values()),2)

    def test_multiwarehouse_flow_avoids_greedy_dead_end(self):
        out=run("multi_warehouse_flow.py",{"warehouses":[{"id":"W1","capacity":5},{"id":"W2","capacity":5}],"destinations":[{"id":"A","demand":5},{"id":"B","demand":5}],"arcs":[{"warehouse":"W1","destination":"A","unit_cost":1,"capacity":5,"compliance_pass":True},{"warehouse":"W1","destination":"B","unit_cost":2,"capacity":5,"compliance_pass":True},{"warehouse":"W2","destination":"A","unit_cost":3,"capacity":5,"compliance_pass":True}]})
        self.assertEqual(out["decision"],"pass")
        self.assertEqual(out["total_cost"],25)

    def test_warehouse_stage_bottleneck_and_queue(self):
        out=run("warehouse_capacity.py",{"opening_queue":0,"max_queue":100,"periods":[{"period":1,"arrivals":400,"receiving":640,"putaway":640,"internal_replenishment":640,"picking":640,"packing":320,"dispatch":640,"carrier_pickup":640}]})
        self.assertIn("packing",out["periods"][0]["bottlenecks"])
        self.assertEqual(out["decision"],"pass")

    def test_exit_discount_and_deadline(self):
        out=run("reverse_exit.py",{"expected_net_sales_proceeds":0,"annual_discount_rate":0.365,"paths":[{"id":"slow","cash_proceeds":120,"collection_probability":1,"cash_days":365,"deadline":"2026-08-10","risk_buffer_days":3,"execution_days":10,"compliance_pass":True,"title_clear":True},{"id":"fast","cash_proceeds":100,"collection_probability":1,"cash_days":0,"deadline":"2026-08-10","risk_buffer_days":3,"execution_days":3,"compliance_pass":True,"title_clear":True}]})
        self.assertEqual(out["recommended"]["id"],"fast")
        self.assertEqual(out["paths"][0]["latest_decision_date"],"2026-07-28")
    def test_costs(self):
        d=run("logistics_economics.py",{"purchase_price":10,"main_haul":2,"pick_pack":1,"carrier_base":3,"holding":1})
        self.assertEqual(d["landed_cost_per_unit"],12);self.assertEqual(d["total_relevant_cost"],17)
    def test_negative_contribution_blocks(self):
        d=run("logistics_economics.py",{"selling_price":10,"purchase_price":8,"main_haul":3,"carrier_base":4,"minimum_contribution":1});self.assertEqual(d["decision"],"blocked")
    def test_ledger_and_inbound_discount(self):
        d=run("inventory_ledger.py",{"sellable":10,"inbound":[{"qty":10,"eligibility":.5}],"opening_physical":10,"closing_physical":10})
        self.assertEqual(d["eligible_inbound"],5);self.assertTrue(d["balanced"])
    def test_ledger_blocks_imbalance(self):
        d=run("inventory_ledger.py",{"sellable":1,"opening_physical":10,"closing_physical":9})
        self.assertEqual(d["decision_gate"],"blocked")
    def test_replenishment_continuity(self):
        d=run("replenishment.py",{"expected_protection_demand":80,"target_demand_quantile":100,"target_inventory_position":150,"current_inventory_position":50,"moq":60,"case_pack":10,"timeline":[{"period":1,"demand":30,"protection_floor":10},{"period":2,"demand":30,"protection_floor":10}] ,"opening_available":50})
        self.assertEqual(d["safety_stock"],20);self.assertEqual(d["final_order_qty"],100);self.assertEqual(d["continuity"],"fail")
    def test_route_filters_gate(self):
        base={"capacity":100,"cash_capacity":100,"p90_days":20,"sku_allowed":True,"documents_ready":True}
        d=run("network_routing.py",{"required_flow":10,"max_p90_days":30,"routes":[{"id":"bad","compliance_pass":False,**base},{"id":"ok","compliance_pass":True,"main_haul":5,**base}]})
        self.assertEqual(d["recommended"]["id"],"ok");self.assertEqual(len(d["rejected"]),1)
    def test_allocation_conservation_and_negative_value(self):
        d=run("inventory_allocation.py",{"total_eligible_inventory":100,"operational_reserve":10,"platforms":[{"id":"a","base_protection":20,"max_extra":50,"incremental_contribution":5},{"id":"b","base_protection":20,"max_extra":50,"incremental_contribution":-1}]})
        self.assertTrue(d["conserved"]);self.assertEqual(next(x for x in d["allocations"] if x["id"]=="b")["extra"],0)
    def test_atp_ctp_bottleneck(self):
        data={"sellable":20,"confirmed_orders":5,"protected_reserved":5,"new_supply_within_window":100,"procurement_production_capacity":50,"transport_capacity":40,"customs_inbound_capacity":30,"warehouse_throughput":20,"last_mile_capacity":50,"cash_supported_capacity":50,"requested_qty":25}
        d=run("order_capacity.py",data);self.assertEqual(d["atp"],10);self.assertEqual(d["ctp"],30);self.assertIn("warehouse_throughput",d["bottlenecks"])
    def test_exit_blocks_unclear_title(self):
        d=run("reverse_exit.py",{"expected_net_sales_proceeds":5,"paths":[{"id":"buyer","cash_proceeds":100,"collection_probability":1,"compliance_pass":True,"title_clear":False}]})
        self.assertEqual(d["decision"],"hold");self.assertFalse(d["paths"][0]["eligible"])
    def test_exit_prefers_risk_adjusted_value(self):
        d=run("reverse_exit.py",{"expected_net_sales_proceeds":20,"additional_storage_handling":10,"paths":[{"id":"fast","cash_proceeds":30,"collection_probability":1,"compliance_pass":True,"title_clear":True,"cash_days":5}]})
        self.assertEqual(d["decision"],"dispose")
    def test_perfect_order_is_intersection(self):
        good={k:True for k in ["right_product","right_quantity","right_condition","right_customer_place","on_original_commit_date","documents_accurate","no_unexpected_claim"]};bad={**good,"documents_accurate":False}
        d=run("cost_to_serve.py",{"orders":[good,bad]});self.assertEqual(d["perfect_order_rate"],.5)
    def test_recall_cannot_overresolve(self):
        d=run("traceability_recall.py",{"on_hand":10,"recovered":11},False);self.assertEqual(d["status"],"error")
    def test_transformation_conservation(self):
        d=run("traceability_recall.py",{"on_hand":10,"transformations":[{"parent_qty":10,"child_qty":8,"documented_loss":1}]});self.assertFalse(d["transformation_conserved"])
    def test_nonfinite_rejected(self):
        d=run("logistics_economics.py",{"purchase_price":float("nan")},False);self.assertEqual(d["status"],"error")
    def test_scenario_registry(self):
        data=json.loads((ROOT.parent/"references"/"expert-scenarios.json").read_text())
        self.assertEqual(len(data),60);self.assertEqual(len({x["id"] for x in data}),60);self.assertTrue(all(x["expected_gate"] in {"pass","conditional","blocked"} for x in data))
if __name__=="__main__":unittest.main(verbosity=2)
