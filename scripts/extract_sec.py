"""Extract fiscal-quarter facts from user-supplied SEC companyfacts JSON; no web requests."""
import argparse,csv,json,datetime
from pathlib import Path
from decimal import Decimal
METRICS={'revenue':'Revenues','operating_income':'OperatingIncomeLoss','net_income':'NetIncomeLoss','total_assets':'Assets'}
FIELDS=['date','value','memo','company','fiscal_year','fiscal_quarter','unit','source_document','source_report_page','source_pdf_page','method','calculation_note','secondary_source','sec_accession','filed','start','sec_tag']

def days(v):return datetime.date.fromisoformat(v)
def choose(items,fy,fp,kind):
    arr=[v for v in items if v.get('fy')==fy and v.get('fp')==fp and v.get('form') in ('10-Q','10-K') and v.get('val') is not None]
    if kind=='instant':
        arr=[v for v in arr if 'start' not in v]
    else:
        lo,hi={'quarter':(75,105),'year':(350,375),'nine':(255,290)}[kind]
        arr=[v for v in arr if v.get('start') and lo <= (days(v['end'])-days(v['start'])).days+1 <= hi]
    if not arr:return None
    # prefer the original fiscal-year filing; duplicates for comparative periods removed using end/filing.
    arr.sort(key=lambda v:(v['end'],v.get('filed',''),v['accn']))
    return arr[-1]

def extract(source,years=range(2019,2026)):
    facts=json.loads(Path(source).read_text(encoding='utf-8'))
    assert facts['cik']==829224,'Incorrect CIK'
    out=[];missing=[]
    for year in years:
      for metric,tag in METRICS.items():
       units=facts['facts']['us-gaap'].get(tag,{}).get('units',{}).get('USD',[])
       for q in (1,2,3,4):
        fp=f'Q{q}' if q<4 else 'FY'
        if metric=='total_assets':
          point=choose(units,year,fp,'instant'); amount=point['val'] if point else None
          method='direct_reported';note='Instant balance at fiscal quarter end'
        elif q<4:
          point=choose(units,year,fp,'quarter'); amount=point['val'] if point else None
          method='direct_reported';note='Standalone fiscal quarter (not cumulative)'
        else:
          point=choose(units,year,'FY','year'); nine=choose(units,year,'Q3','nine')
          amount=point['val']-nine['val'] if point and nine else None
          method='calculated_fy_minus_9m';note=(f"FY {point['val']} USD - 9M {nine['val']} USD; 9M accession {nine['accn']}" if amount is not None else '')
        if amount is None:
          missing.append(f'{year} Q{q} {metric}');continue
        out.append(dict(date=point['end'],value=str(Decimal(amount)/Decimal(1000000)),memo=metric,company='Starbucks Corporation',fiscal_year=year,fiscal_quarter=f'Q{q}',unit='USD millions',source_document=point['form'],source_report_page='',source_pdf_page='',method=method,calculation_note=note,secondary_source='',sec_accession=point['accn'],filed=point['filed'],start=point.get('start',''),sec_tag=tag))
    return sorted(out,key=lambda r:(r['date'],r['memo'])),missing

def main():
 p=argparse.ArgumentParser();p.add_argument('json');p.add_argument('--out',default='data/starbucks_2019_2025.csv');a=p.parse_args()
 rec,missing=extract(a.json)
 path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rec)
 print(f'Wrote {len(rec)} records to {path}. Missing {len(missing)}: {missing}')
if __name__=='__main__':main()
