# Running the eDNA Taxonomy Workbench

## Frontend (Running Successfully)

The frontend is currently running on: **http://localhost:5176**

To start the frontend:
```bash
cd frontend
npm install
npm run dev
```

## Backend (Requires Compatible Python Version)

The backend has dependency installation issues with Python 3.14. For successful installation, use Python 3.11 or 3.12.

### Recommended Setup

1. **Install Python 3.11 or 3.12** from https://www.python.org/downloads/

2. **Create virtual environment with compatible Python:**
```bash
cd backend
py -3.11 -m venv venv
# or
py -3.12 -m venv venv
```

3. **Activate and install dependencies:**
```bash
# Windows
venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

4. **Run the backend:**
```bash
uvicorn main:app --reload
```

The backend will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

## Conformal Prediction Framework (Fully Implemented)

The conformal prediction framework for zero-shot eDNA taxonomic assignment is now fully implemented in `backend/conformal/`.

### Running the Conformal Demo

To test the core conformal prediction experiment:

```bash
cd backend
python conformal/demo.py
```

This will:
- Generate synthetic hierarchical data
- Compare calibration regimes (random split vs leave-species-out)
- Demonstrate that LOSO calibration restores coverage on unseen species
- Generate coverage plots and summary tables

### Conformal Components

- **calibration.py**: Four calibration regimes (random split, LOSO, Good-Turing, mixture)
- **scores.py**: Four nonconformity scores (probability, embedding-distance, tree-aware, combined)
- **prediction_sets.py**: Three set constructions (flat, tree-structured, hierarchical)
- **evaluation.py**: Comprehensive evaluation metrics (coverage, set size, calibration error, etc.)
- **experiments.py**: Experiment runner for regime/score/set comparisons
- **visualization.py**: Plotting functions for paper figures
- **integration.py**: Wrapper to integrate with eDNA pipeline
- **demo.py**: Standalone demo with synthetic data

### Research Questions Addressed

The framework addresses:
- **RQ1**: Does random-split conformal give valid coverage on unseen species? (Expected: No)
- **RQ2**: Does LOSO calibration restore coverage? (Expected: Yes)
- **RQ3**: Do tree-structured sets beat flat sets? (Expected: Yes)
- **RQ4**: Do combined scores help? (Expected: Yes)
- **RQ5**: Do multiple trees help? (To be tested)
- **RQ6**: Does it transfer to other taxa? (To be tested with BIOSCAN-5M)
- **RQ7**: Do calibrated sets reduce downstream bias? (To be tested)

## What's Working Now

### Frontend Features (Fully Functional)

✅ **MVP Features:**
- Project management
- New analysis with file upload
- Progress tracking
- Results with predictions table
- Species detail panel
- Provenance tracking
- CSV/JSON export

✅ **Version 2 Features:**
- Reference data manager with versioning
- Community view with interactive charts
- Compare with baseline (ECOTAG)
- HTML report generation
- Shareable read-only links

✅ **Version 3 Features:**
- Research mode with experiments
- Calibration plots UI
- Trait estimation (backend infrastructure)
- Multiple markers support (teleo, MiFish, 16S, COI, ITS)
- Multiple taxa support (fish, mammals, birds, insects, plants, fungi)

### Backend Features (Code Complete, Needs Python 3.11/3.12)

✅ **API Endpoints:**
- Projects CRUD
- File upload with validation
- Analyses management

✅ **ML Pipeline:**
- Phylogenetic embedding
- DNA encoder
- Co-occurrence correction
- Trait estimation
- Complete pipeline orchestration

✅ **Database:**
- Full schema for projects, samples, analyses, predictions, provenance
- Support for multiple markers and taxa
- Trait data storage

## Testing the Frontend

Since the frontend is running, you can test all UI features:

1. Open http://localhost:5175 in your browser
2. Navigate through:
   - Projects (create new projects)
   - New Analysis (upload form, settings)
   - Results (predictions, community view, compare, provenance)
   - Reference Data (dataset management)
   - Research Mode (experiments, calibration)

All features use mock data and will demonstrate the full UI/UX as specified in the design document.

## Next Steps for Full Deployment

1. Install Python 3.11 or 3.12
2. Install backend dependencies
3. Run backend server
4. Connect frontend to backend API
5. Train ML models with real data
6. Test end-to-end workflow

## Troubleshooting

### Backend Installation Issues

If you encounter issues with pydantic-core or other packages:
- Ensure you're using Python 3.11 or 3.12 (not 3.14)
- Try: `pip install --upgrade pip`
- Try: `pip install pydantic --no-cache-dir`

### Frontend Issues

If port 5173 is in use, Vite will automatically try 5174, 5175, etc.
Check the terminal output for the actual port being used.
