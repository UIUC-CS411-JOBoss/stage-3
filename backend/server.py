from typing import Optional
from fastapi import FastAPI
import csv
import gensim
import pandas as pd
from gensim.utils import simple_preprocess, tokenize
from rank_bm25 import BM25Okapi

def train_query_job(fn="jobs-2022-04-01.csv"):
    df = pd.read_csv(fn)
    df = df[['id', 'title', 'text_description']]
    df['text_description_tokenized'] = df['text_description'].apply(lambda x: simple_preprocess(x))
    return BM25Okapi(df['text_description_tokenized']), df
    
bm25, df = train_query_job()
def query_job(query, n=40):
    q_totenized = simple_preprocess(query)
    return bm25.get_top_n(q_totenized, df['id'], n=n)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/job/query/{query_word}")
def read_query_job(query_word: str, q: Optional[str] = None):
    res = query_job(query_word)
    res = [job_id.item() for job_id in res]
    return {"query_jobs": res}