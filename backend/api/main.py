from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from typing import List, Dict, Any
from pydantic import BaseModel
from .function import read_file_and_extract_content
from typing import Optional
import logging
import os
import requests
import csv
from datetime import datetime

# Créer le moteur de base de données SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./manrs_2023-08/newdatabase.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Déclarer la base de données
Base = declarative_base()

# Créer la session de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modèle de données pour la table 'merged_df'
    


class DatasetASMappingTable(Base):
    __tablename__ = "dataset_as_mapping"

    id = Column(Integer, primary_key=True, index=True)
    asn = Column(String, nullable=True)
    status = Column(String, nullable=True)
    reference_orgs = Column(String, nullable=True)  # Stocker une liste de références d'organisations au format JSON
    sibling_asns = Column(String, nullable=True)     # Stocker une liste de frères ASN au format JSON
    name = Column(String, nullable=True)
    descr = Column(String, nullable=True)
    website = Column(String, nullable=True)
    comparison_with_ca20 = Column(String, nullable=True)
    comparison_with_pdb = Column(String, nullable=True)
    pdb_org_id = Column(String, nullable=True)
    pdb_org = Column(String, nullable=True)
    
class DelegatedStatsTable(Base):
    __tablename__ = "delegated_stats"

    id = Column(Integer, primary_key=True, index=True)
    registry = Column(String, nullable=True)
    cc = Column(String, nullable=True)
    type = Column(String, nullable=True)
    start = Column(String, nullable=True)
    value = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    status = Column(String, nullable=True)
    opaque_id = Column(String, nullable=True)
    extensions = Column(String, nullable=True)
    
class CategorizedAsnTable(Base):
    __tablename__ = "categorized_asn"

    id = Column(Integer, primary_key=True, index=True)
    asn = Column(String, unique=True)
    category_1 = Column(String, nullable=True)
    category_2 = Column(String, nullable=True)

class RelationshipAsnTable(Base):
    __tablename__ = "relationship_asn"

    id = Column(Integer, primary_key=True, index=True)
    asn = Column(String, unique=True)
    customer = Column(String, nullable=True)
    provider = Column(String, nullable=True)

    
class DatasetASMapping(BaseModel):
    asn: str
    status: str
    reference_orgs: str
    sibling_asns: str
    name: str
    descr: str
    website: str
    comparison_with_ca2O: str
    comparison_with_pdb: str
    pdb_org_id: str
    pdb_org: str
    
class DelegatedStatsRecord(BaseModel):
    registry: str
    cc: str
    type: str
    start: str
    value: str
    date: str
    status: str
    opaque_id: str
    extensions: str
    
class CategorizedAsn(BaseModel):
    asn: str
    category_1: str
    category_2: str

class RelationshipAsn(BaseModel):
    asn: str
    customer: Optional[str]
    provider: Optional[str]


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



#Function
# Fonction pour obtenir le ratio le plus récent à partir du fichier CSV
def get_latest_ratio_from_csv(asn):
    latest_ratio = None
    url = f"https://rovista.netsecurelab.org/data/asn/{asn}.csv"
    response = requests.get(url)
    
    if response.status_code == 200:
        file_path = f"csv_files/{asn}.csv"  # Chemin où enregistrer le fichier
        with open(file_path, "wb") as file:
            file.write(response.content)
        try:
            with open(file_path, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if "date" in row and "ratio" in row:
                        ratio_date = datetime.strptime(row["date"], "%Y-%m-%d")
                        ratio = float(row["ratio"])
                        
                        if latest_ratio is None or ratio_date > latest_ratio["date"]:
                            latest_ratio = {"date": ratio_date, "ratio": ratio}
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        return latest_ratio
    else:
        print(f'error dowload: {response}')
        
    
def find_asn_data(db: Session, asn):
    dataset_mapping_data = db.query(DatasetASMappingTable).filter(DatasetASMappingTable.asn == asn).first()
    delegated_stats_data = db.query(DelegatedStatsTable).filter(DelegatedStatsTable.value == asn).first()
    categorized_asn_data = db.query(CategorizedAsnTable).filter(CategorizedAsnTable.asn == asn).first()
    relationship_asn_data = db.query(RelationshipAsnTable).filter(RelationshipAsnTable.asn == asn).all()
    print(dataset_mapping_data)
    merged_data = {
        "asn" : asn,
        "sibling_asns" : dataset_mapping_data.sibling_asns,
        "website" : dataset_mapping_data.website,
        "category_1" : categorized_asn_data.category_1,
        "category_2" : categorized_asn_data.category_2,
        "country_code": delegated_stats_data.cc,
        "customers": relationship_asn_data.customers,
        "providers": relationship_asn_data.providers,
        "name": dataset_mapping_data.name,
    }
    return merged_data

def extract_related_data(db: Session, related_asns):
    related_data_list = []
    for related_asn in related_asns:
        related_data = find_asn_data(db, related_asn)
        related_data_list.append(related_data)
    return related_data_list



def create_or_update_delegated_stats(db: Session, delegated_data: DelegatedStatsRecord):
    existing_entry = db.query(DelegatedStatsTable).filter_by(value=delegated_data.value).first()
    if existing_entry:
        for key, value in delegated_data.dict().items():
            setattr(existing_entry, key, value)
    else:
        db_entry = DelegatedStatsTable(**delegated_data.dict())
        db.add(db_entry)
    db.commit()
    
def create_or_update_dataset_mapping(db: Session, dataset_data: DatasetASMapping):
    existing_entry = db.query(DatasetASMappingTable).filter_by(asn=dataset_data.asn).first()
    if existing_entry:
        for key, value in dataset_data.dict().items():
            setattr(existing_entry, key, value)
    else:
        db_entry = DatasetASMappingTable(**dataset_data.dict())
        db.add(db_entry)
    db.commit()
    
def create_or_update_categorized_asn(db: Session, data: CategorizedAsn):
    existing_entry = db.query(CategorizedAsnTable).filter_by(asn=data.asn).first()
    if existing_entry:
        for key, value in data.dict().items():
            setattr(existing_entry, key, value)
    else:
        db_entry = CategorizedAsnTable(**data.dict())
        db.add(db_entry)
    db.commit()
    
def create_or_update_relationship_asn(db: Session, data: RelationshipAsn):
    existing_entry = db.query(RelationshipAsnTable).filter_by(asn=data.asn).first()
    if existing_entry:
        for key, value in data.dict().items():
            setattr(existing_entry, key, value)
    else:
        db_entry = RelationshipAsnTable(**data.dict())
        db.add(db_entry)
    db.commit()
    

def find_relationship_asn(db: Session, asn: str):
    existing_entry = db.query(RelationshipAsnTable).filter_by(asn=asn).first()
    if existing_entry:
        return existing_entry
    else:
       return None
   
def update_relationship_asn(db: Session, existing_entry: RelationshipAsnTable, data: RelationshipAsn):
    for key, value in data.dict().items():
            setattr(existing_entry, key, value)
    db.commit()
    
    
    
def delegated_stats_task(file_path: str, db: Session):
    content = read_file_and_extract_content(file_path)
    found_format_line = False
    
    for entry in content:
        if entry.startswith("iana|ZZ|asn|0|1|20140311|reserved|ietf|iana"):
            found_format_line = True
            continue
        
        if found_format_line and entry:
            entry = entry.strip().split('|')
            data = DatasetASMapping(
                registry = entry[0],
                cc = entry[1],
                type = entry[2],
                start = entry[3],
                value = entry[4],
                date = entry[5],
                status = entry[6],
                opaque_id = entry[7],
                extensions = entry[8]
            )      
            create_or_update_delegated_stats(db, data)
    
    logger.info("Processed ASN organization info from file: %s", file_path)
    
def dataset_as_mapping_task(file_path: str, db: Session):
    content = read_file_and_extract_content(file_path)

    for asn, data in content.items():
        reference_orgs =  data.get("Reference Orgs", [])
        
        sibling_asns = data.get("Sibling ASNs", [])
        print(sibling_asns
              )
        dataset_mapping = DatasetASMapping(
            asn=asn,
            status=data.get("Status", ""),
            reference_orgs=str(reference_orgs),
            sibling_asns=str(sibling_asns),
            name=data.get("Name", ""),
            descr=data.get("Descr", ""),
            website=data.get("Website", ""),
            comparison_with_ca2O=data.get("Comparison with CA2O", ""),
            comparison_with_pdb=data.get("Comparison with PDB", ""),
            pdb_org_id=data.get("PDB.org_id", ""),
            pdb_org=data.get("PDB.org", "")
        )
        
        create_or_update_dataset_mapping(db, dataset_mapping)  # Utiliser la fonction pour enregistrer ou mettre à jour
    logger.info("Processed ASN organization info from file: %s", file_path)   
    return {"message": "Processing started in background"}

    

def categorized_asn_task(file_path: str, db: Session):
    content = read_file_and_extract_content(file_path)

    for entry in content:
            data = CategorizedAsn(
                asn = entry['ASN'].replace('AS',''),
                category_1 = entry['Category 1 - Layer 1'],
                category_2 = entry['Category 1 - Layer 2'],
            )
            create_or_update_categorized_asn(db, data)

    logger.info("Processed Categories Data info from file: %s", file_path)

def relationship_asn_task(file_path: str, db: Session):
    content = read_file_and_extract_content(file_path)
    
    for entry in content:
        if entry.startswith("# step 1: set peering in clique"):
            continue
        if entry.startswith("# step 2: initial provider assignment"):
            continue
        entry = entry.strip().split('|')
        if len(entry) == 1:
            # Traitement pour une seule colonne
            continue
        if entry and entry[2]and entry[2]=='0':
            
            data = RelationshipAsn(
                asn = entry[0],
                provider = "",
                customer =  entry[1],
            )
            create_or_update_relationship_asn(db, data)
            
        if entry and entry[2]=='-1':
            check_data = find_relationship_asn(db, entry[0])
            if check_data is None:
                data = RelationshipAsn(
                    asn = entry[0],
                    provider = entry[1],
                    customer =  "",
                )
                create_or_update_relationship_asn(db, data)
            else:
                data = RelationshipAsn(
                    asn = entry[0],
                    provider = entry[1],
                    customer =  check_data.customer,
                )
                update_relationship_asn(db, check_data, data)
            

    logger.info("Processed Peering and Provider info from file: %s ", file_path)




#Route

@app.get("/asn/")
async def get_info_asn(
    asn: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: SessionLocal = Depends(get_db)
):
    if not asn:
        raise HTTPException(status_code=400, detail="asn is required")
    
    results = []
    total_results = 0
    
    if asn:
        asn_data = find_asn_data(db, asn)
         # Extract customer and provider details
            
        asn_data["sibling_asns"] = extract_related_data(db, asn_data["sibling_asns"])

        results = asn_data
        total_results = 1
    
    return {"total_results": total_results, "results": results}


"""@app.get("/asn/")
async def get_asn_by_country_or_category(
    country: str = Query(None),
    asn: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
    db: SessionLocal = Depends(get_db)
):
    if not any([country, category_1, category_2, asn]):
        raise HTTPException(status_code=400, detail="Au moins un paramètre de requête est requis.")
    
    results = []
    total_results = 0
    
    if asn:
        asn_data = find_asn_data(db, asn)
         # Extract customer and provider details
        customer_data_list = extract_related_data(db, asn_data["customers"])
        provider_data_list = extract_related_data(db, asn_data["providers"])
        
        # Add customer details for providers
        for provider_data in provider_data_list:
            provider_asn = provider_data["asn"]
            provider_data["level_1_providers"] = extract_related_data(db, provider_data["providers"])
            provider_data["level_1_customers"] = extract_related_data(db, provider_data["customers"])
            
            # Add customer details for level 1 providers
            for level_1_provider_data in provider_data["level_1_providers"]:
                level_1_provider_asn = level_1_provider_data["asn"]
                level_1_provider_data["providers"] = extract_related_data(db, level_1_provider_data["providers"])
                level_1_provider_data["customers"] = extract_related_data(db, level_1_provider_data["customers"])
            
        asn_data["customers_details"] = customer_data_list
        asn_data["providers_details"] = provider_data_list

        results = asn_data
        total_results = 1
    
    return {"total_results": total_results, "results": results}"""
