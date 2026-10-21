import os
from dotenv import load_dotenv
load_dotenv()

def env(name,default=''):return os.getenv(name,default)

def origins():return [x.strip().rstrip('/') for x in env('ALLOWED_ORIGINS','http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000').split(',') if x.strip()]
