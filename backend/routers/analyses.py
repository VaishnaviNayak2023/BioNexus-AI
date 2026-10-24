from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Sample, Analysis, AnalysisStatus
from pydantic import BaseModel
from datetime import datetime
import os
import hashlib

router = APIRouter(prefix="/api/analyses", tags=["analyses"])

class AnalysisCreate(BaseModel):
    sample_id: int
    name: str
    marker: str = "teleo"
    taxon: str = "Ray-finned fish"
    region: str | None = None
    settings: dict | None = None

class AnalysisResponse(BaseModel):
    id: int
    sample_id: int
    name: str
    status: AnalysisStatus
    species_count: int
    high_confidence_count: int
    medium_confidence_count: int
    low_confidence_count: int
    created_at: datetime

    class Config:
        from_attributes = True

def calculate_file_checksum(file_path: str) -> str:
    """Calculate SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def validate_sequence_file(file_path: str) -> dict:
    """
    Validate a FASTA or FASTQ file.
    Returns validation report with:
    - valid: bool
    - format: str
    - sequence_count: int
    - length_range: tuple
    - errors: list
    """
    from Bio import SeqIO
    
    try:
        # Try to parse as FASTA
        sequences = list(SeqIO.parse(file_path, "fasta"))
        file_format = "fasta"
    except:
        try:
            # Try to parse as FASTQ
            sequences = list(SeqIO.parse(file_path, "fastq"))
            file_format = "fastq"
        except Exception as e:
            return {
                "valid": False,
                "format": "unknown",
                "sequence_count": 0,
                "length_range": (0, 0),
                "errors": [f"Cannot parse file: {str(e)}"]
            }
    
    if not sequences:
        return {
            "valid": False,
            "format": file_format,
            "sequence_count": 0,
            "length_range": (0, 0),
            "errors": ["No sequences found in file"]
        }
    
    # Calculate statistics
    lengths = [len(seq.seq) for seq in sequences]
    min_length = min(lengths)
    max_length = max(lengths)
    
    # Check for obvious issues
    errors = []
    warnings = []
    
    # Check for too many ambiguous bases
    for i, seq in enumerate(sequences):
        ambiguous_count = sum(1 for base in str(seq.seq) if base not in "ACGTacgt")
        if ambiguous_count > len(seq.seq) * 0.1:  # More than 10% ambiguous
            warnings.append(f"Sequence {i+1} has {ambiguous_count} ambiguous bases ({ambiguous_count/len(seq.seq)*100:.1f}%)")
    
    return {
        "valid": True,
        "format": file_format,
        "sequence_count": len(sequences),
        "length_range": (min_length, max_length),
        "errors": errors,
        "warnings": warnings
    }

@router.post("/upload", response_model=dict)
async def upload_sequence_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and validate a sequence file"""
    
    # Check file extension
    valid_extensions = ['.fasta', '.fa', '.fastq', '.gz']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Accepted: {', '.join(valid_extensions)}"
        )
    
    # Check file size (500 MB max)
    MAX_SIZE = 500 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 500 MB"
        )
    
    # Save file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{datetime.utcnow().timestamp()}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Validate file
    validation = validate_sequence_file(file_path)
    
    if not validation["valid"]:
        # Clean up invalid file
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=validation["errors"])
    
    # Calculate checksum
    checksum = calculate_file_checksum(file_path)
    
    return {
        "file_path": file_path,
        "filename": file.filename,
        "checksum": checksum,
        "validation": validation
    }

@router.post("", response_model=AnalysisResponse)
async def create_analysis(analysis: AnalysisCreate, db: Session = Depends(get_db)):
    """Create a new analysis"""
    
    # Check if sample exists
    sample = db.query(Sample).filter(Sample.id == analysis.sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    db_analysis = Analysis(
        sample_id=analysis.sample_id,
        name=analysis.name,
        marker=analysis.marker,
        taxon=analysis.taxon,
        region=analysis.region,
        settings=str(analysis.settings) if analysis.settings else None,
        status=AnalysisStatus.PENDING
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return db_analysis

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get analysis details"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.get("", response_model=List[AnalysisResponse])
async def get_analyses(db: Session = Depends(get_db)):
    """Get all analyses"""
    analyses = db.query(Analysis).all()
    return analyses
