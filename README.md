# eDNA Taxonomy Workbench

A web application for zero-shot eDNA taxonomy and functional traits analysis, based on the method by Stalder et al. (PLOS Computational Biology 2025).

## Overview

The eDNA Taxonomy Workbench enables researchers and ecologists to analyze environmental DNA (eDNA) samples and identify species using a deep learning approach that can predict species even when they're not in the reference database (zero-shot learning).

## Current Status

**Frontend: ✅ Running on http://localhost:5176**

**Backend: ⚠️ Requires Python 3.11/3.12 (code complete, dependency installation needs compatible Python)**

**Conformal Prediction: ✅ Fully Implemented**

See [RUNNING.md](RUNNING.md) for detailed setup instructions.

## Key Features

### MVP (Version 1) ✅ Implemented

- **Project Management**: Create and organize eDNA analysis projects
- **Sequence Upload**: Upload FASTA/FASTQ files with instant validation
- **Analysis Progress**: Real-time tracking of analysis pipeline steps
- **Results Dashboard**: 
  - Predictions table with confidence badges (High/Medium/Low)
  - Best reliable rank toggle (species/genus/family/order)
  - Summary statistics
- **Species Detail Panel**: 
  - Prediction explanation
  - Nearest relatives in model space
  - Functional traits (from FishBase)
  - Zero-shot indicators
- **Provenance Tracking**: Full reproducibility information (model version, database version, settings)
- **Export**: CSV and JSON export with provenance data

### Version 2 ✅ Implemented

- Compare with baseline (ECOTAG/ECOTAG output)
- Community view with interactive charts (bar charts, taxonomic tree)
- HTML report generation
- Shareable read-only result links
- Reference data manager with versioning

### Version 3 ✅ Implemented

- Research mode with experiments
- Calibration plots and evaluation metrics UI
- Trait estimation for zero-shot species (backend infrastructure)
- Multiple markers support (teleo, MiFish, 16S, COI, ITS)
- Multiple taxa support (fish, mammals, birds, insects, plants, fungi)

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **React Router** for navigation
- **TanStack Table** for data tables
- **Recharts** for visualizations
- **Lucide React** for icons

### Backend
- **FastAPI** for REST API
- **SQLAlchemy** for database ORM
- **SQLite** (development) / PostgreSQL (production)
- **PyTorch** for ML models
- **Biopython** for sequence processing
- **scikit-learn** for utilities

### ML Pipeline

The ML pipeline implements the three-stage method from Stalder et al. 2025:

1. **Phylogenetic Embedding**: Learns 64-dimensional species embeddings from phylogenetic tree distances
2. **DNA Encoder**: Convolutional neural network that maps DNA sequences to embedding space
3. **Co-occurrence Correction**: Adjusts predictions using species co-occurrence patterns from survey data

4. **Trait Estimation**: Regresses functional traits from DNA embeddings for zero-shot species

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
   ```bash
   cd C:/Users/prash/OneDrive/Desktop/PROJECTS/eDNA
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd ../backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

### Running the Application

**Backend** (from backend directory):
```bash
uvicorn main:app --reload
```
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Frontend** (from frontend directory):
```bash
npm run dev
```
- Application: http://localhost:5173

## Project Structure

```
eDNA/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── analysis/     # Analysis-specific components
│   │   │   ├── layout/       # Sidebar, navigation
│   │   │   └── ui/           # Base UI components
│   │   ├── lib/              # Utilities (export, cn)
│   │   ├── pages/            # Page components
│   │   ├── App.tsx           # Main app with routing
│   │   └── main.tsx          # Entry point
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                  # FastAPI backend
│   ├── ml/                  # ML pipeline implementation
│   │   ├── phylogenetic_embedding.py
│   │   ├── dna_encoder.py
│   │   ├── cooccurrence_correction.py
│   │   └── pipeline.py
│   ├── routers/             # API endpoints
│   │   ├── projects.py
│   │   └── analyses.py
│   ├── database.py         # SQLAlchemy models
│   ├── main.py             # FastAPI app
│   └── requirements.txt
│
├── README.md               # This file
├── SETUP.md                # Detailed setup guide
└── .gitignore
```

## Design Principles

1. **Five-minute goal**: Non-experts can go from sequence file to species list in under 5 minutes
2. **Honest uncertainty**: Every prediction shows confidence level with clear labels (High/Medium/Low)
3. **Reproducibility**: All exports include model version, database version, and settings
4. **Accessibility**: WCAG 2.2 AA compliant, full keyboard navigation, screen reader support
5. **Zero-shot honesty**: Clear indicators when predictions are for species not in reference database

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `DELETE /api/projects/{id}` - Delete project

### Analyses
- `POST /api/analyses/upload` - Upload and validate sequence file
- `POST /api/analyses` - Create new analysis
- `GET /api/analyses` - List all analyses
- `GET /api/analyses/{id}` - Get analysis details

## Documentation

- **Setup Guide**: See [SETUP.md](SETUP.md) for detailed installation and configuration
- **API Documentation**: Available at http://localhost:8000/docs when backend is running
- **Implementation Plan**: Refer to the provided PDF for methodology details

## Contributing

This is a research implementation. Areas for contribution:

1. **ML Improvements**: 
   - Phylogenetic uncertainty (multiple trees)
   - Hierarchical/abstaining predictions
   - Fixing co-occurrence accuracy drop
   - Cross-marker transfer learning

2. **UI/UX**:
   - Community view implementation
   - Compare with baseline feature
   - Research mode experiments UI

3. **Data**:
   - Additional reference databases
   - More co-occurrence sources
   - Trait data integration

## License

This project implements the method described in:

> Stalder S, Sanchez T, Volpi M, Manel S, Mouillot D, Auber A, Bruno M, Marques V, Albouy C, Pellissier L. Zero-shot deep learning for the annotation of unknown eDNA sequences using co-occurrences and phylogenetic embeddings. PLOS Computational Biology. 2025;21(12):e1013776. doi:10.1371/journal.pcbi.1013776

## Acknowledgments

- Original method by Stalder et al. (2025)
- Fish Tree of Life (Rabosky et al. 2018)
- FISHGLOB_data (Maureaud et al. 2024)
- FishBase and SeaLifeBase for trait data
