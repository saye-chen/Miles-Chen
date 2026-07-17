#!/usr/bin/env python3
from common import main,n
STAGES=["receiving","putaway","internal_replenishment","picking","packing","dispatch","carrier_pickup"]
def run(d):
    queue=n(d,"opening_queue");rows=[];max_queue=queue
    for i,p in enumerate(d.get("periods",[])):
        caps={s:n(p,s) for s in STAGES};effective=min(caps.values());b=[s for s,v in caps.items() if v==effective]
        arrivals=n(p,"arrivals");queue=max(0,queue+arrivals-effective);max_queue=max(max_queue,queue)
        rows.append({"period":p.get("period",i),"effective_throughput":effective,"bottlenecks":b,"closing_queue":queue})
    target=n(d,"max_queue",0)
    return {"periods":rows,"max_queue":max_queue,"ending_queue":queue,"decision":"pass" if max_queue<=target else "constrain"}
if __name__=="__main__":main(run)
