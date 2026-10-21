"""Run manually after Firebase credentials are configured. Import CSV without duplicates."""
import csv,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from app.database import db
from app.models import DataIn

def main(path):
  coll=db().collection('data');n=0
  for row in csv.DictReader(open(path,encoding='utf-8-sig')):
    payload={key:row[key] for key in ('date','value','memo','fiscal_year','fiscal_quarter','unit','source_document','sec_accession','method','calculation_note')}
    d=DataIn.model_validate(payload).model_dump(mode='json');d['import_source']='SEC user-supplied JSON'
    doc_id=f"sbux_{d['fiscal_year']}_{d['fiscal_quarter']}_{d['memo']}"
    coll.document(doc_id).set(d);n+=1
  print(f'Upserted {n} validated records to Firestore')
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else '../data/starbucks_2019_2025.csv')
