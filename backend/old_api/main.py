from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from typing import List, Dict, Any
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Optional
import logging
import os
import requests
import csv
from datetime import datetime
import ast, json

# Créer le moteur de base de données SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./script/database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Déclarer la base de données
Base = declarative_base()

# Créer la session de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modèle de données pour la table 'merged_df'
    
class ManrsTable(Base):
    __tablename__ = "manrs"
    id = Column(Integer, primary_key=True, index=True)
    registry = Column(String, index=True)
    cc = Column(String)
    asn = Column(String)
    date = Column(String)
    sibling_asns = Column(String)
    name = Column(String)
    website = Column(String)
    category_1 = Column(String)
    category_2 = Column(String)
    providers = Column(String)
    customers = Column(String)
    ratio_rov = Column(String)
    created_at = Column(Date)

# Modèle Pydantic pour la classe Manrs and AsnMetrics
class Manrs(BaseModel):
    registry: str
    cc: str
    asn : str
    date : str
    sibling_asns : str
    name : str
    website : str
    category_1 : str
    category_2 : str
    providers : str
    customers : str
    ratio_rov : str
    created_at : str
# Créer toutes les tables dans la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurer les logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fonction pour obtenir la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
        
    
def find_asn_data(db: Session, asn):
    merged_data = db.query(ManrsTable).filter(ManrsTable.asn == asn).first()
    return merged_data

def find_by_category(db: Session, category: str):
    data1 = db.query(ManrsTable).filter(ManrsTable.category_1 == category).all()
    data2 = db.query(ManrsTable).filter(ManrsTable.category_1 == category).all()
    merged_data = list(set(data1 + data2))
    return merged_data

def find_by_country(db: Session, country: str):
    merged_data = db.query(ManrsTable).filter(ManrsTable.cc == country).all()
    print(merged_data)
    return merged_data

def get_detail_data_asn(db: Session, asn_data):
    if asn_data.sibling_asns != []:
        sibling_asns_list = extract_related_data(db, asn_data.sibling_asns)   
        asn_data.sibling_asns = sibling_asns_list
    return asn_data

def extract_related_data(db: Session, related_asns):
    related_data_list = []
    related_asns = ast.literal_eval(related_asns)
    for related_asn in related_asns:
        related_data = find_asn_data(db, related_asn)
        related_data_list.append(related_data)
    return related_data_list


@app.get("/asn/")
async def get_asn_by_country_or_category(
    country: str = Query(None),
    category: str = Query(None),
    asn: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: SessionLocal = Depends(get_db)
):
    if not any([country, category, asn]):
        raise HTTPException(status_code=400, detail="Au moins un paramètre de requête est requis.")
    
    results = []
    results_1 = []
    results_2 = []
    results_3 = []
    total_results = 0
    total_results_1 = 0
    total_results_2 = 0
    total_results_3 = 0

    if asn:
        response = find_asn_data(db, asn)
        results_1.append(get_detail_data_asn(db, response))
        total_results_1 = len(results_1)

    if country and  len(country) <= 2:
        results_2 = find_by_country(db, country.upper())
        results_2= get_detail_data_asn(db, results_2)
        total_results_2 = len(results_2)
    elif country:
        raise HTTPException(status_code=400, detail="Review length of country. Max: 2 word") 
    
    if category:
        results_3 = find_by_category(db, category)
        results_3= get_detail_data_asn(db, results_3)
        total_results_3 = len(results_3)
    
    total_results= total_results_1 + total_results_2 + total_results_3   
    results = results_1 + results_2 + results_3
    return {"total_results": total_results, "results": results}
