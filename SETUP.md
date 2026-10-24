# eDNA Taxonomy Workbench - Setup Guide

This guide will help you set up and run the eDNA Taxonomy Workbench on your local machine.

## Prerequisites

- **Node.js** (v18 or higher) - for the frontend
- **Python** (3.11 or higher) - for the backend
- **Git** - for version control
- **CUDA** (optional, for GPU acceleration of ML models)

## Installation

### 1. Clone the Repository

```bash
cd C:/Users/prash/OneDrive/Desktop/PROJECTS/eDNA
```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

### 3. Backend Setup

Navigate to the backend directory and create a virtual environment:

```bash
cd ../backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Backend

In the backend directory (with virtual environment activated):

```bash
uvicorn main:app --reload
```

The backend API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Start the Frontend

In a new terminal, navigate to the frontend directory:

```bash
cd frontend
npm run dev
```

The frontend will be available at:
- Application: http://localhost:5173

## Project Structure

```
eDNA/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── analysis/     # Analysis-specific components
│   │   │   ├── layout/       # Layout components (Sidebar, etc.)
│   │   │   └── ui/           # Base UI components (Button, Badge, etc.)
│   │   ├── lib/              # Utility functions
│   │   ├── pages/            # Page components
│   │   ├── App.tsx           # Main app component with routing
│   │   └── main.tsx          # Entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── backend/                  # FastAPI backend
│   ├── ml/                  # Machine learning pipeline
│   │   ├── phylogenetic_embedding.py  # Stage 1: Phylogenetic embedding
│   │   ├── dna_encoder.py             # Stage 2: DNA encoder
│   │   ├── cooccurrence_correction.py # Stage 3: Co-occurrence correction
│   │   └── pipeline.py                # Complete pipeline
│   ├── routers/             # API route handlers
│   │   ├── projects.py
│   │   └── analyses.py
│   ├── database.py         # Database models and configuration
│   ├── main.py            # FastAPI application
│   └── requirements.txt
│
└── README.md              # Project overview
```

## Database

The application uses SQLite for development (automatically created as `edna.db` in the backend directory). For production, consider switching to PostgreSQL.

### Database Schema

- **Projects**: Container for related analyses
- **Samples**: Individual eDNA samples with metadata
- **Analyses**: Analysis runs with settings and status
- **Predictions**: Species predictions for each sequence
- **Provenance**: Reproducibility information for each analysis
- **ReferenceDatasets**: Versioned reference data
- **Experiments**: Research mode experiment tracking

## ML Pipeline

The ML pipeline consists of three stages:

1. **Phylogenetic Embedding**: Learns 64-dimensional species embeddings from phylogenetic tree
2. **DNA Encoder**: Maps DNA sequences to the embedding space
3. **Co-occurrence Correction**: Adjusts predictions using species co-occurrence patterns

### Training the Models

See `backend/ml/pipeline.py` for the complete pipeline implementation. Example usage:

```python
from ml.pipeline import eDNAPipeline

# Initialize pipeline
pipeline = eDNAPipeline(num_species=31500)

# Train Stage 1: Phylogenetic embedding
tree_distance = load_tree_distance_matrix()  # Your tree distance matrix
pipeline.train_stage1(tree_distance, epochs=100)

# Train Stage 2: DNA encoder
sequences = load_training_sequences()
species_labels = load_species_labels()
pipeline.train_stage2(sequences, species_labels, epochs=50)

# Train Stage 3: Co-occurrence correction
cooccurrence_data = load_cooccurrence_data()
pipeline.train_stage3(sequence_embeddings, cooccurrence_data, epochs=50)

# Save models
pipeline.save_models("models/checkpoint.pt")

# Make predictions
predictions = pipeline.predict(new_sequences)
```

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create a new project
- `GET /api/projects/{id}` - Get project details
- `DELETE /api/projects/{id}` - Delete a project

### Analyses
- `POST /api/analyses/upload` - Upload and validate sequence file
- `POST /api/analyses` - Create a new analysis
- `GET /api/analyses` - List all analyses
- `GET /api/analyses/{id}` - Get analysis details

## Development

### Frontend Development

The frontend uses:
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **React Router** for navigation
- **TanStack Table** for data tables
- **Recharts** for visualizations

### Backend Development

The backend uses:
- **FastAPI** for the API
- **SQLAlchemy** for database ORM
- **PyTorch** for ML models
- **Biopython** for sequence processing
- **Celery** (optional) for background tasks

## Testing

### Frontend Tests

```bash
cd frontend
npm test
```

### Backend Tests

```bash
cd backend
pytest
```

## Troubleshooting

### Frontend Issues

**Problem**: Port 5173 already in use
- **Solution**: Edit `vite.config.ts` to change the port, or kill the process using port 5173

**Problem**: npm install fails
- **Solution**: Delete `node_modules` and `package-lock.json`, then run `npm install` again

### Backend Issues

**Problem**: Module not found errors
- **Solution**: Ensure virtual environment is activated and all dependencies are installed

**Problem**: Database locked error
- **Solution**: Ensure only one instance of the backend is running

### ML Pipeline Issues

**Problem**: CUDA out of memory
- **Solution**: Reduce batch size or use CPU instead of GPU

**Problem**: Training takes too long
- **Solution**: Reduce number of epochs or use a smaller subset of data for testing

## Next Steps

1. **Data Preparation**: Gather reference sequences, phylogenetic tree, and co-occurrence data
2. **Model Training**: Train the ML pipeline on your data
3. **Integration**: Connect the frontend to the backend API
4. **Testing**: Test with real eDNA samples
5. **Deployment**: Deploy to production (consider Docker for containerization)

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Biopython Documentation](https://biopython.org/wiki/Documentation)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check the implementation plan document for detailed methodology
