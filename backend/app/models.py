from datetime import date
from typing import Literal
from pydantic import BaseModel,Field,field_validator
Metric=Literal['revenue','operating_income','net_income','total_assets']
class DataIn(BaseModel):
    date:date
    value:float=Field(ge=-1e12,le=1e12)
    memo:Metric
    fiscal_year:int=Field(ge=1990,le=2100)
    fiscal_quarter:Literal['Q1','Q2','Q3','Q4']
    unit:Literal['USD millions']='USD millions'
    source_document:str=Field(default='manual',max_length=120)
    sec_accession:str=Field(default='',max_length=60)
    method:str=Field(default='manual',max_length=80)
    calculation_note:str=Field(default='',max_length=500)
    @field_validator('value')
    @classmethod
    def finite(cls,v):
        import math
        if not math.isfinite(v):raise ValueError('Must be finite')
        return v
class ConversationIn(BaseModel):
    title:str=Field(default='Financial conversation',max_length=160)
    messages:list[dict]=Field(min_length=1,max_length=60)
class ChatIn(BaseModel):
    message:str=Field(min_length=1,max_length=2000)
    conversation_id:str|None=None
