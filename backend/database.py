from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

SQLALCHEMY_DATABASE_URL = "sqlite:///./edna.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ConfidenceLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaxonomicRank(str, enum.Enum):
    SPECIES = "species"
    GENUS = "genus"
    FAMILY = "family"
    ORDER = "order"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    samples = relationship("Sample", back_populates="project")

class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String)
    date_collected = Column(DateTime)
    marker = Column(String, default="teleo")  # teleo, MiFish, 16S, COI, etc.
    taxon = Column(String, default="Ray-finned fish")  # Can be: fish, mammals, birds, insects, etc.
    region = Column(String)
    file_path = Column(String)
    file_checksum = Column(String)
    sequence_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="samples")
    analyses = relationship("Analysis", back_populates="sample")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    model_version = Column(String)
    reference_db_version = Column(String)
    phylogeny_version = Column(String)
    cooccurrence_sources = Column(Text)
    settings = Column(Text)  # JSON string
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    species_count = Column(Integer, default=0)
    high_confidence_count = Column(Integer, default=0)
    medium_confidence_count = Column(Integer, default=0)
    low_confidence_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    sample = relationship("Sample", back_populates="analyses")
    predictions = relationship("Prediction", back_populates="analysis")
    provenance = relationship("Provenance", back_populates="analysis", uselist=False)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    sequence_group = Column(String, nullable=False)  # MOTU_001, etc.
    predicted_species = Column(String)
    predicted_genus = Column(String)
    predicted_family = Column(String)
    predicted_order = Column(String)
    best_rank = Column(Enum(TaxonomicRank))
    confidence = Column(Float)  # 0-1
    confidence_level = Column(Enum(ConfidenceLevel))
    read_count = Column(Integer)
    is_zero_shot = Column(Boolean, default=False)
    closest_reference_identity = Column(Float)
    seen_in_region = Column(Boolean)
    # Trait data (JSON string for flexibility)
    traits = Column(Text)  # {"max_length": 70, "trophic_level": 3.2, "habitat": "Reef", "estimated": true}
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="predictions")

class Provenance(Base):
    __tablename__ = "provenance"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, unique=True)
    model_name = Column(String)
    model_version = Column(String)
    reference_db_name = Column(String)
    reference_db_version = Column(String)
    reference_db_date = Column(DateTime)
    phylogeny_version = Column(String)
    cooccurrence_sources = Column(Text)
    settings = Column(Text)  # JSON string
    file_checksum = Column(String)
    app_version = Column(String)
    run_date = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="provenance")

class ReferenceDataset(Base):
    __tablename__ = "reference_datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dataset_type = Column(String, nullable=False)  # sequences, phylogeny, cooccurrence, traits
    source = Column(String)
    version = Column(String)
    date = Column(DateTime)
    record_count = Column(Integer)
    status = Column(String, default="Active")  # Active, Outdated, Draft
    file_path = Column(String)
    validation_report = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    split = Column(String)
    model_config = Column(Text)  # JSON string
    status = Column(String, default="pending")
    species_accuracy = Column(Float)
    genus_accuracy = Column(Float)
    family_accuracy = Column(Float)
    order_accuracy = Column(Float)
    ece = Column(Float)  # Expected calibration error
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
