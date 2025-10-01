from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path

app = FastAPI()

DATA_FILE = Path(__file__).with_name("mart_export(3).txt")

def load_genes() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)

@app.get("/genes", response_model=List[Dict[str, Any]])
def list_genes() -> List[Dict[str, Any]]:
    df = load_genes().copy()

    # Replace NaN/NaT with None so JSON can serialize it
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")

@app.get("/genes/{gene_name}", response_model=Dict[str, Any])
def get_gene_by_name(gene_name: str) -> Dict[str, Any]:
    df = load_genes().copy()
    df = df.where(pd.notnull(df), None)  # handle NaNs

    if "Gene name" in df.columns:  # adjust to actual column name in CSV
        col = "Gene name"
    elif "gene_name" in df.columns:
        col = "gene_name"
    else:
        raise HTTPException(status_code=500, detail="Dataset missing gene name column")

    mask = df[col].fillna("").str.lower() == gene_name.lower()
    gene = df[mask]

    if gene.empty:
        raise HTTPException(status_code=404, detail="Gene not found")

    return gene.to_dict(orient="records")[0]

@app.get("/")
def root():
    return {"message": "Welcome to Chromosome 21 Gene API"}
