# 🔗 AI Design Research Semantic Network Dashboard

An interactive visualization tool for exploring keyword relationships in AI design research papers using Cytoscape.js.

## 🚀 Quick Start

### Option 1: Direct Browser Access (Recommended)
**No server needed - works offline!**

Simply open this file in your web browser:
```
self_contained_english_dashboard.html
```

Double-click the file or drag it to your browser - it will work immediately!

### Option 2: Local Server (Alternative)
```bash
# Start local server
python start_server.py

# Or manually:
python3 -m http.server 8080
```

Then open: `http://localhost:8080/self_contained_english_dashboard.html`

## 🎯 What You Can Explore

### 📊 Network Overview
- **198 keywords** extracted from 93 AI design research papers (2020-2024)
- **160 co-occurrence relationships** showing which keywords appear together
- **Color-coded by AI method**: Traditional ML (Green), Deep Learning (Blue), Generative AI (Red)
- **Node size** represents keyword frequency across papers

### 🔍 Interactive Features

#### 1. **Keyword Search & Exploration**
- **Search bar**: Type any keyword to instantly highlight it in the network
- **Click exploration**: Click on a keyword to see all its connections
- **Neighbor highlighting**: Connected keywords are automatically highlighted
- **Real-time feedback**: Instant visual response to your interactions

#### 2. **Advanced Filtering**
- **AI Method filters**: Show only Traditional ML, Deep Learning, or Generative AI keywords
- **Design Phase filters**: Filter by Discovery, Define, Develop, or Delivery phases
- **Combined filtering**: Mix and match filters to explore specific combinations
- **Real-time updates**: Network instantly adapts to your filter selections

#### 3. **Multiple Layout Options**
- **🌟 Force-directed (Best)**: Optimal for exploring clusters and connections
- **⭕ Circular Layout**: Keywords arranged in a circle
- **🔲 Grid Layout**: Organized grid arrangement
- **🌳 Hierarchical**: Tree-like structure
- **🎯 Concentric**: Keywords arranged by frequency
- **🍃 Cola Layout**: Alternative force-directed algorithm

#### 4. **Detailed Information**
- **Click any keyword** → Right panel shows:
  - Frequency of occurrence
  - AI method and design phase
  - Network centrality measures
  - List of connected keywords
- **Live statistics**: Real-time count of visible/selected nodes

## 🎮 Usage Examples

### Example 1: Explore Core Research Concepts
1. Search for **"artificial intelligence"**
2. Click on the highlighted node
3. Observe the **13 connected keywords** that frequently appear with AI
4. Notice how it bridges different research areas

### Example 2: Discover Generative AI Ecosystem  
1. Uncheck all AI methods except **"Generative AI"**
2. Switch to **"Circular Layout"**
3. Explore which keywords are central to generative AI research
4. Click on individual keywords to see their specific connections

### Example 3: Find Bridge Keywords
1. Search for **"product"** (the strongest bridge keyword)
2. Click on it to see its **30 connections**
3. Notice how it connects Traditional ML, Deep Learning, and Generative AI
4. Explore other high-frequency keywords in the sidebar list

### Example 4: Compare Design Phases
1. Select only **"Discovery"** and **"Delivery"** phases
2. Compare which keywords are used in early vs. late design phases
3. Identify gaps where certain AI methods are underutilized

## 📈 Key Insights You Can Discover

### 🔝 Top Bridge Keywords
These keywords connect different research areas:
1. **product** (22 occurrences) - Connects all AI methods and design phases
2. **user** (15 occurrences) - Central to user-centered design research
3. **artificial intelligence** (13 occurrences) - Hub for AI-related concepts
4. **interaction** (8 occurrences) - Key for interface design
5. **model** (8 occurrences) - Bridge between technical and design concepts

### 🌟 Rising Research Areas
- **Generative AI keywords** showing explosive growth since 2023
- **Multimodal** approaches gaining prominence
- **Conversational interfaces** emerging as key trend
- **Mobile** platform research maintaining strong presence

### 🔍 Research Gaps Identified
- **Generative AI × Delivery**: Underexplored area with high potential
- **Deep Learning × Discovery**: Limited user research applications
- **Traditional ML × Discovery**: Statistical user research opportunities

## 🛠️ Technical Details

### Data Source
- **93 research papers** from AI design research (2020-2024)
- **TF-IDF keyword extraction** from paper abstracts
- **Co-occurrence analysis** using networkx
- **Centrality measures**: Betweenness, closeness, eigenvector

### Technology Stack
- **Frontend**: Cytoscape.js 3.26, Bootstrap 5, Vanilla JavaScript
- **Visualization**: Force-directed layouts, interactive filtering
- **Data**: Embedded JSON (no CORS issues)
- **Performance**: Optimized for 200+ nodes with smooth interactions

### Browser Compatibility
- ✅ **Chrome/Edge** (Recommended)
- ✅ **Firefox** 
- ✅ **Safari**
- ❌ **Internet Explorer** (Not supported)

## 🎨 Visual Guide

### Node Colors (AI Methods)
- 🟢 **Traditional ML** (#2E8B57) - Established machine learning approaches
- 🔵 **Deep Learning** (#4169E1) - Neural networks and deep architectures  
- 🔴 **Generative AI** (#DC143C) - GPT, diffusion models, generative approaches
- 🟠 **Exploratory Data Analysis** (#FF8C00) - Statistical analysis and EDA
- 🟣 **Multiple** (#9370DB) - Hybrid approaches using multiple AI methods

### Node Shapes (Design Tasks)
- ⭕ **Circle**: Discovery phase
- ⬜ **Square**: Define phase  
- 🔺 **Triangle**: Develop phase
- 💎 **Diamond**: Delivery phase
- ⭐ **Star**: Multiple phases

### Connection Strength
- **Thick lines**: High co-occurrence (keywords often appear together)
- **Thin lines**: Low co-occurrence (keywords occasionally appear together)
- **Line opacity**: Indicates relationship strength

## 🔧 Troubleshooting

### Dashboard Won't Load
1. **Check browser console** (F12) for error messages
2. **Try different browser** (Chrome recommended)
3. **Disable ad blockers** that might block CDN resources
4. **Use local server method** as alternative

### Performance Issues
1. **Use filtering** to reduce visible nodes
2. **Close other browser tabs** to free memory
3. **Try simpler layouts** (Grid or Circular)
4. **Refresh page** to reset state

### Keywords Not Visible
1. **Click "Fit View"** button to see all keywords
2. **Zoom out** using mouse wheel
3. **Check filters** - ensure desired categories are selected
4. **Try different layout** for better spacing

## 🎓 Research Applications

This dashboard is perfect for:

### 📚 Academic Research
- **Literature review** - Identify research trends and gaps
- **Concept mapping** - Understand relationships between research areas
- **Methodology selection** - See which AI methods are used for specific design tasks

### 🏢 Industry R&D
- **Technology roadmapping** - Identify emerging research directions
- **Innovation opportunities** - Find underexplored AI×Design combinations
- **Competitive analysis** - Understand current research landscape

### 👩‍🎓 Educational Use
- **Teaching aid** - Visualize connections between AI and design concepts
- **Student projects** - Explore research areas for thesis topics
- **Curriculum planning** - Identify important concepts to cover

## 📄 Data Attribution

Based on systematic review of 93 papers from AI design research:
- **Source period**: 2020-2024
- **Extraction method**: TF-IDF analysis of abstracts
- **Filtering criteria**: Minimum 2 co-occurrences
- **Network analysis**: NetworkX with centrality measures

## 🆘 Support

For issues or questions:
1. Check the **browser console** for technical errors
2. Try the **troubleshooting steps** above
3. Use **alternative access methods** (local server vs. direct file)

---

**🎉 Happy Network Exploration!**

*Discover the conceptual DNA of AI design research through interactive visualization.*