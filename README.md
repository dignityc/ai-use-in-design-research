# Paper Review with LLM

A comprehensive research paper analysis and classification system powered by AI/LLM technologies.

## Overview

This project provides an automated workflow for analyzing academic papers in the field of AI-driven design research. It combines NLP analysis, topic modeling, semantic network analysis, and interactive visualizations to explore the research landscape systematically.

## Key Features

### 📈 Analysis Workflow
- **Data Normalization & Insights Analysis**: Systematically categorize AI methods and design tasks into 4-5 main groups
- **BERTopic Topic Modeling**: Discover 9 major research topics with domain-specific information preservation
- **Semantic Network Analysis**: Build and visualize semantic relationships between papers
- **Interactive Dashboard**: Self-contained HTML dashboard (38KB) for exploring all analysis results
- **4D Cross-dimensional Analysis**: Topics × AI Methods × Data Modality × Design Practice

### 🔧 Coding Workflow
- **Google Sheets Integration**: Automated paper classification workflow connected to "Coding & screening works" spreadsheet
- **PDF Analysis System**: Automatic classification based on 7 criteria using Claude API
- **Resume & Retry System**: Index-based deduplication with automatic resume capability
- **Metadata Merging**: Automatic integration of accurate paper metadata from Google Sheets
- **Cell Notes Attachment**: Classification reasoning attached as hover notes in spreadsheet cells

## Project Structure

```
paper_review_with_llm/
├── source/                    # Source data files
├── analysis_work/             # Analysis workflow (7-13 steps)
│   ├── scripts/              # Analysis scripts (13 files)
│   └── results/              # Analysis outputs
├── coding_work/               # Paper classification automation
│   ├── scripts/              # Classification scripts (8 files)
│   ├── logs/                 # Log files
│   └── results/              # Processing results
├── ai_evolution_diagram/      # AI evolution visualizations
├── requirements.txt           # Python dependencies
└── research_report.md         # AI methodology evolution essay
```

## Tech Stack

### Python Libraries
- **BERTopic**: Transformer-based topic modeling
- **sentence-transformers**: Abstract embedding generation
- **spaCy**: Text preprocessing and lemmatization
- **scikit-learn**: Traditional ML analysis
- **matplotlib/seaborn**: Static visualizations
- **plotly**: Interactive visualizations
- **pandas**: Data processing
- **networkx**: Network analysis

### APIs & Services
- **Google Sheets API**: Service account authentication
- **Claude API**: AI-powered paper classification
- **GitHub CLI**: Repository management

## Getting Started

### Prerequisites
```bash
python 3.8+
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Running Analysis Workflow
```bash
# Activate virtual environment
source venv/bin/activate

# Navigate to analysis scripts
cd analysis_work/scripts

# Run analysis pipeline (steps 7-13)
python improved_nlp_analysis.py
python topic_modeling_analysis.py
python create_dashboard_data.py
python create_self_contained_dashboard.py
python semantic_network_builder.py
python semantic_network_visualizer.py
python network_insights_analyzer.py
```

### Viewing Results
```bash
# Start local server
cd ../results
python3 -m http.server 8000 --bind 127.0.0.1

# Open browser to:
# http://127.0.0.1:8000/interactive_topic_dashboard_en.html
```

## Key Insights

### AI Methodology Evolution (2020-2025)
- **Deep Learning**: 50% → 21.1% (28.9%p decline)
- **Generative AI**: 0% → 23.7% (23.7%p surge) - 2023 turning point
- **Traditional ML**: Still mainstream (51/93 papers)

### Major Topics Discovered (BERTopic Analysis)
1. **Interaction + User + Technology** (18 papers) - Gen AI focused
2. **Design + Case + Research** (10 papers) - Traditional ML focused
3. **Emotion + Emotional + Recognition** (9 papers) - Deep Learning focused
4. **Product + Customer + Review** (9 papers) - Traditional ML, Define phase focused

### Data Normalization Achievements
- **Data Modality**: 22 → 5 categories (78% simplification)
- **Design Practice**: 6 → 4 categories (complete removal of "Others")

## Research Database

- **Spreadsheet**: "Coding & screening works"
- **Scale**: 900 papers × 18 columns
- **Classification Status**: 525 classified (58.3%), 375 unclassified (41.7%)

## Contributing

This is a private research project. For questions or collaboration inquiries, please contact the repository owner.

## License

Private research project - All rights reserved.

## Project Status

- ✅ Analysis system completed
- ✅ Paper classification in progress (13 papers completed)
- ✅ PDF analyzer with structured output (Enum validation, Multiple format)
- ✅ Google Sheets auto-upload system (metadata merging, cell notes)

**Last Updated**: October 2025
