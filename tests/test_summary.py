import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'backend'))
from app.services import summarize

def test_summary():
 rows=[{'date':'2025-03-30','fiscal_year':2025,'fiscal_quarter':'Q2','memo':'revenue','value':100},{'date':'2025-03-30','fiscal_year':2025,'fiscal_quarter':'Q2','memo':'operating_income','value':15},{'date':'2025-03-30','fiscal_year':2025,'fiscal_quarter':'Q2','memo':'total_assets','value':600}]
 s=summarize(rows)
 assert s['count']==3 and s['latest_metrics']['operating_margin_pct']==15
 assert s['totals_excluding_balance_sheet']['revenue']==100
