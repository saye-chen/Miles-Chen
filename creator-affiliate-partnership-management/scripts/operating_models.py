#!/usr/bin/env python3
"""CAPM C05/C06/C10/C11 operating models with explicit action ceilings."""
from __future__ import annotations
import argparse
from capm_common import emit, load_json, require_number, sha256_json

def sample_loss(data: dict) -> dict:
    count = require_number(data.get("sample_count"), "sample_count")
    if not count.is_integer(): raise ValueError("sample_count must be an integer")
    unit_product = require_number(data.get("unit_product_cost"), "unit_product_cost")
    unit_logistics = require_number(data.get("unit_logistics_cost"), "unit_logistics_cost")
    publication_rate = require_number(data.get("publication_rate"), "publication_rate", maximum=1.0)
    recoverable_rate = require_number(data.get("recoverable_rate", 0), "recoverable_rate", maximum=1.0)
    published_cost = count * publication_rate * (unit_product + unit_logistics)
    unpublished_count = count * (1 - publication_rate)
    unrecovered_loss = unpublished_count * (unit_logistics + unit_product * (1 - recoverable_rate))
    return {"status":"validated", "published_cost":published_cost, "unpublished_count":unpublished_count,
            "unrecovered_sample_loss":unrecovered_loss, "cash_outflow":count * (unit_product + unit_logistics)}

def rights_commercial_feasibility(data: dict) -> dict:
    fee = require_number(data.get("rights_fee"), "rights_fee")
    ceiling = require_number(data.get("commercial_cost_ceiling"), "commercial_cost_ceiling")
    required = set(data.get("required_rights", [])); granted = set(data.get("granted_rights", []))
    missing = sorted(required - granted)
    if missing: return {"status":"blocked", "rights_ready":False, "cost_ready":fee <= ceiling, "missing_rights":missing,
                        "blocked_actions":["use_ungranted_rights"], "aamo_status":"not_assessed"}
    if fee > ceiling: return {"status":"blocked", "rights_ready":True, "cost_ready":False, "missing_rights":[],
                             "blocked_actions":["new_cash_commitment"], "aamo_status":"not_assessed"}
    return {"status":"validated", "rights_ready":True, "cost_ready":True, "missing_rights":[],
            "blocked_actions":[], "aamo_status":"candidate_only", "forbidden_claim":"paid_media_incrementality"}

def creator_ltv(data: dict) -> dict:
    contributions = data.get("contribution_by_period")
    if not isinstance(contributions, list) or not contributions: raise ValueError("contribution_by_period must be non-empty")
    retention = require_number(data.get("retention_rate"), "retention_rate", maximum=1.0)
    discount = require_number(data.get("discount_rate"), "discount_rate", maximum=1.0)
    values = [require_number(v, f"contribution_by_period[{i}]", minimum=None) for i, v in enumerate(contributions)]
    discounted = [value * (retention ** i) / ((1 + discount) ** i) for i, value in enumerate(values)]
    return {"status":"validated" if sum(discounted) > 0 else "blocked", "creator_ltv":sum(discounted),
            "discounted_contributions":discounted, "periods":len(values)}

def workforce_productivity(data: dict) -> dict:
    publications = require_number(data.get("effective_publications"), "effective_publications")
    staff = require_number(data.get("bd_fte"), "bd_fte", minimum=1e-12)
    periods = require_number(data.get("periods"), "periods", minimum=1e-12)
    managed = require_number(data.get("managed_partners", 0), "managed_partners")
    return {"status":"validated", "publications_per_fte_period":publications / staff / periods,
            "partners_per_fte":managed / staff, "capacity_claim":"descriptive_only"}

ACTIONS = {"sample_loss":sample_loss, "rights_commercial_feasibility":rights_commercial_feasibility,
           "creator_ltv":creator_ltv, "workforce_productivity":workforce_productivity}

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("action",choices=ACTIONS); p.add_argument("input",nargs="?"); a=p.parse_args()
    data=load_json(a.input); result=ACTIONS[a.action](data); result.update({"runtime_version":"CAPM-2026.07","input_hash":sha256_json(data)}); emit(result)
