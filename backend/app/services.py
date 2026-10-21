from collections import defaultdict

def summarize(rows):
    metrics=['revenue','operating_income','net_income','total_assets']
    groups=defaultdict(dict)
    for r in rows:
        if r.get('memo') in metrics:
            key=(int(r['fiscal_year']),r['fiscal_quarter'])
            groups[key][r['memo']]=float(r['value'])
    keys=sorted(groups,key=lambda x:(x[0],int(x[1][1:])))
    latest=keys[-1] if keys else None
    totals={m:round(sum(v.get(m,0) for k,v in groups.items() if m in v and m!='total_assets'),2) for m in metrics if m!='total_assets'}
    latest_metrics=groups[latest].copy() if latest else {}
    if latest and latest_metrics.get('revenue'):
        latest_metrics['operating_margin_pct']=round(latest_metrics.get('operating_income',0)/latest_metrics['revenue']*100,2)
    trends={}
    for m in metrics:
        vals=[(k,groups[k][m]) for k in keys if m in groups[k]]
        if vals:
            last=vals[-1][1];prev=vals[-2][1] if len(vals)>1 else None
            pct=round((last-prev)/abs(prev)*100,2) if prev not in (None,0) else None
            trends[m]={'latest':last,'previous':prev,'qoq_pct':pct,'direction':'increase' if pct is not None and pct>1 else 'decrease' if pct is not None and pct< -1 else 'stable' if pct is not None else 'unavailable'}
    return {'period':f'{keys[0][0]} {keys[0][1]} – {keys[-1][0]} {keys[-1][1]}' if keys else None,'count':len(rows),'quarters':len(keys),'metric_counts':{m:sum(m in v for v in groups.values()) for m in metrics},'latest_quarter':f'{latest[0]} {latest[1]}' if latest else None,'latest_metrics':latest_metrics,'totals_excluding_balance_sheet':totals,'trend':trends,'note':'USD millions; Total Assets is a point-in-time balance, never summed. Income and revenue are quarterly flows. Metrics describe reported numbers, not causal explanations.'}
