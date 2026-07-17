#!/usr/bin/env python3
from common import main,n
def run(d):
    demands={x["id"]:n(x,"demand") for x in d.get("destinations",[])}
    warehouses={x["id"]:n(x,"capacity") for x in d.get("warehouses",[])}
    source="__S__";sink="__T__";graph={}
    def edge(u,v,cap,cost,meta=None):
        graph.setdefault(u,[]);graph.setdefault(v,[]);a=[v,cap,cost,len(graph[v]),meta];b=[u,0,-cost,len(graph[u]),None];graph[u].append(a);graph[v].append(b)
    for w,cap in warehouses.items(): edge(source,"W:"+w,cap,0)
    for dst,qty in demands.items(): edge("D:"+dst,sink,qty,0)
    for a in d.get("arcs",[]):
        if not a.get("compliance_pass",False): continue
        if a.get("warehouse") not in warehouses or a.get("destination") not in demands: raise ValueError("unknown warehouse or destination")
        edge("W:"+a["warehouse"],"D:"+a["destination"],n(a,"capacity"),n(a,"unit_cost"),(a["warehouse"],a["destination"],n(a,"unit_cost")))
    total=0;sent=0;target=sum(demands.values())
    while sent+1e-9<target:
        dist={source:0};parent={};nodes=list(graph)
        for _ in range(len(nodes)-1):
            changed=False
            for u in nodes:
                if u not in dist: continue
                for i,e in enumerate(graph[u]):
                    if e[1]>1e-9 and (e[0] not in dist or dist[e[0]]>dist[u]+e[2]+1e-12): dist[e[0]]=dist[u]+e[2];parent[e[0]]=(u,i);changed=True
            if not changed: break
        if sink not in parent: break
        qty=target-sent;v=sink
        while v!=source: u,i=parent[v];qty=min(qty,graph[u][i][1]);v=u
        v=sink
        while v!=source:
            u,i=parent[v];e=graph[u][i];e[1]-=qty;graph[v][e[3]][1]+=qty;total+=qty*e[2];v=u
        sent+=qty
    flows=[];remaining={}
    for w,cap in warehouses.items():
        used=cap-next(e[1] for e in graph[source] if e[0]=="W:"+w);remaining[w]=round(cap-used,6)
        for e in graph["W:"+w]:
            if e[4] and graph[e[0]][e[3]][1]>1e-9:
                meta=e[4];flows.append({"warehouse":meta[0],"destination":meta[1],"qty":round(graph[e[0]][e[3]][1],6),"unit_cost":meta[2]})
    delivered={k:0 for k in demands}
    for f in flows: delivered[f["destination"]]+=f["qty"]
    unmet={k:round(v-delivered[k],6) for k,v in demands.items() if v-delivered[k]>1e-9}
    return {"flows":flows,"total_cost":round(total,6),"unmet":unmet,"decision":"pass" if not unmet else "blocked","remaining_warehouse_capacity":remaining}
if __name__=="__main__":main(run)
