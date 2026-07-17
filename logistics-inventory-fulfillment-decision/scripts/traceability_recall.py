#!/usr/bin/env python3
from common import main,n
def run(d):
    affected=sum(n(d,k) for k in ["on_hand","inbound","in_transit","delivered","returned","transformed_descendants"])
    resolved=sum(n(d,k) for k in ["isolated","recovered","verified_destroyed","legally_resolved"])
    if resolved>affected: raise ValueError("resolved recall quantity exceeds affected quantity")
    edges=d.get("transformations",[])
    bad=[]
    for i,e in enumerate(edges):
        if abs(n(e,"parent_qty")-n(e,"child_qty")-n(e,"documented_loss"))>n(d,"tolerance",0): bad.append(i)
    unresolved=affected-resolved
    return {"affected_quantity":round(affected,6),"resolved_quantity":round(resolved,6),"unresolved_quantity":round(unresolved,6),"transformation_conserved":not bad,"bad_transformations":bad,"decision":"closed" if unresolved==0 and not bad else "open"}
if __name__=="__main__":main(run)
