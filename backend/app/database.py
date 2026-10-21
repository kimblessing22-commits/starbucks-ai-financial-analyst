import json,base64
import firebase_admin
from firebase_admin import credentials,firestore
from .config import env

def db():
    if not firebase_admin._apps:
        raw=env('FIREBASE_SERVICE_ACCOUNT_JSON')
        path=env('FIREBASE_SERVICE_ACCOUNT_PATH')
        if raw:
            try: account=json.loads(raw)
            except json.JSONDecodeError: account=json.loads(base64.b64decode(raw).decode())
            firebase_admin.initialize_app(credentials.Certificate(account))
        elif path:firebase_admin.initialize_app(credentials.Certificate(path))
        else:raise RuntimeError('Firebase credentials are not configured')
    return firestore.client()
