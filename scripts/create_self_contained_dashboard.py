#!/usr/bin/env python3
"""
자체 완성형 인터랙티브 대시보드 생성기
JSON 데이터를 HTML 파일에 인라인으로 삽입하여 CORS 문제 해결
"""

import pandas as pd
import json
import os

def create_self_contained_dashboard():
    """CORS 문제 없는 자체 완성형 대시보드 생성"""
    
    print("🔧 자체 완성형 대시보드 생성 중...")
    
    # 데이터 로드
    data_dir = '/Users/outcode.jongmokim/Documents/paper_review_with_llm/output/semantic_network_analysis/interactive/data'
    
    # JSON 데이터 로드
    with open(os.path.join(data_dir, 'network_data.json'), 'r', encoding='utf-8') as f:
        network_data = json.load(f)
    
    with open(os.path.join(data_dir, 'metadata.json'), 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"✅ 데이터 로드: {len(network_data['elements']['nodes'])}개 노드, {len(network_data['elements']['edges'])}개 엣지")
    
    # HTML 템플릿 생성
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Design Research - Semantic Network Explorer</title>
    
    <!-- CDN Libraries -->
    <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
    <script src="https://unpkg.com/cytoscape-cose-bilkent@4.1.0/cytoscape-cose-bilkent.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <style>
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #2E8B57;
            --info-color: #4169E1;
            --danger-color: #DC143C;
            --warning-color: #FF8C00;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .dashboard-container {{
            display: flex;
            height: 100vh;
            max-width: 100vw;
        }}
        
        .sidebar {{
            width: 320px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-right: 2px solid #e9ecef;
            overflow-y: auto;
            padding: 20px;
            box-shadow: 2px 0 20px rgba(0,0,0,0.1);
        }}
        
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            margin: 8px 0 0 0;
            opacity: 0.9;
            font-size: 1rem;
        }}
        
        #cy {{
            width: 100%;
            height: calc(100vh - 140px);
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border: none;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.05);
        }}
        
        .control-section {{
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .control-section h3 {{
            color: #495057;
            font-size: 1.1rem;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
        }}
        
        .control-section h3 i {{
            margin-right: 10px;
            color: var(--primary-color);
            width: 20px;
        }}
        
        .search-box {{
            position: relative;
            margin-bottom: 15px;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 12px 40px 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.9);
        }}
        
        .search-box input:focus {{
            border-color: var(--primary-color);
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: white;
        }}
        
        .search-box i {{
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #6c757d;
        }}
        
        .filter-options {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .filter-option {{
            display: flex;
            align-items: center;
            padding: 10px 15px;
            background: rgba(255,255,255,0.7);
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid transparent;
        }}
        
        .filter-option:hover {{
            background: rgba(102, 126, 234, 0.1);
            border-color: var(--primary-color);
            transform: translateX(3px);
        }}
        
        .filter-option.active {{
            background: var(--primary-color);
            color: white;
        }}
        
        .filter-option input[type="checkbox"] {{
            margin-right: 12px;
            transform: scale(1.2);
        }}
        
        .filter-option label {{
            margin: 0;
            cursor: pointer;
            font-size: 0.9rem;
            flex: 1;
            font-weight: 500;
        }}
        
        .color-indicator {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            margin-left: 12px;
            border: 2px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        
        .layout-selector select {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .layout-selector select:focus {{
            border-color: var(--primary-color);
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .stats-panel {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
        }}
        
        .stats-panel h4 {{
            margin: 0 0 15px 0;
            font-size: 1.1rem;
            font-weight: 600;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.8rem;
            font-weight: bold;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .stat-label {{
            font-size: 0.8rem;
            opacity: 0.9;
            margin: 0;
            font-weight: 500;
        }}
        
        .keyword-list {{
            max-height: 350px;
            overflow-y: auto;
            background: rgba(248, 249, 250, 0.8);
            border-radius: 10px;
            padding: 15px;
        }}
        
        .keyword-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 15px;
            background: white;
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            border: 1px solid #e9ecef;
        }}
        
        .keyword-item:hover {{
            background: var(--primary-color);
            color: white;
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .keyword-name {{
            font-weight: 600;
            color: #495057;
        }}
        
        .keyword-item:hover .keyword-name {{
            color: white;
        }}
        
        .keyword-freq {{
            background: var(--primary-color);
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .keyword-item:hover .keyword-freq {{
            background: rgba(255,255,255,0.3);
        }}
        
        .control-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .control-btn {{
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .btn-primary {{
            background: var(--primary-color);
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #5a67d8;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #545b62;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
        }}
        
        .info-panel {{
            position: absolute;
            top: 20px;
            right: 20px;
            width: 350px;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
            transform: translateX(100%);
            transition: transform 0.4s ease;
            z-index: 1000;
            border: 1px solid rgba(255,255,255,0.5);
        }}
        
        .info-panel.show {{
            transform: translateX(0);
        }}
        
        .close-btn {{
            position: absolute;
            top: 15px;
            right: 20px;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6c757d;
            transition: all 0.3s ease;
        }}
        
        .close-btn:hover {{
            color: var(--danger-color);
            transform: scale(1.2);
        }}
        
        .legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            font-size: 0.85rem;
            border: 1px solid rgba(255,255,255,0.5);
        }}
        
        .legend-title {{
            font-weight: bold;
            margin-bottom: 12px;
            color: #495057;
            font-size: 0.9rem;
        }}
        
        .legend-items {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .info-section {{
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .info-section:last-child {{
            border-bottom: none;
            margin-bottom: 0;
        }}
        
        .info-section h5 {{
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
        }}
        
        .info-section h5 i {{
            margin-right: 8px;
            color: var(--primary-color);
        }}
        
        .info-section ul {{
            margin: 0;
            padding-left: 0;
            list-style: none;
        }}
        
        .info-section li {{
            margin-bottom: 8px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 0.85rem;
        }}
        
        .loading {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.95);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
        }}
        
        .spinner {{
            width: 60px;
            height: 60px;
            border: 6px solid #e9ecef;
            border-top: 6px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--primary-color);
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #5a67d8;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .dashboard-container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: 300px;
            }}
            
            .info-panel {{
                width: calc(100% - 40px);
                top: 10px;
                right: 20px;
            }}
        }}
    </style>
</head>

<body>
    <!-- Loading screen -->
    <div id="loading" class="loading">
        <div class="spinner"></div>
        <p style="margin-top: 20px; font-weight: 600; color: #495057;">Loading Semantic Network...</p>
    </div>

    <div class="dashboard-container">
        <!-- Left sidebar -->
        <div class="sidebar">
            <!-- Search section -->
            <div class="control-section">
                <h3><i class="fas fa-search"></i>Search Keywords</h3>
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="Search keywords (e.g., artificial intelligence, user)">
                    <i class="fas fa-search"></i>
                </div>
            </div>

            <!-- Layout selection -->
            <div class="control-section">
                <h3><i class="fas fa-project-diagram"></i>Network Layout</h3>
                <div class="layout-selector">
                    <select id="layout-select">
                        <option value="cose-bilkent">🌟 Force-directed (Best)</option>
                        <option value="circle">⭕ Circular Layout</option>
                        <option value="grid">🔲 Grid Layout</option>
                        <option value="breadthfirst">🌳 Hierarchical</option>
                        <option value="concentric">🎯 Concentric</option>
                        <option value="cola">🍃 Cola Layout</option>
                    </select>
                </div>
            </div>

            <!-- AI Method filters -->
            <div class="control-section">
                <h3><i class="fas fa-brain"></i>AI Methods</h3>
                <div class="filter-group">
                    <div id="ai-method-filters" class="filter-options">
                        <!-- Dynamically generated -->
                    </div>
                </div>
            </div>

            <!-- Design Task filters -->
            <div class="control-section">
                <h3><i class="fas fa-tasks"></i>Design Phases</h3>
                <div class="filter-group">
                    <div id="design-task-filters" class="filter-options">
                        <!-- Dynamically generated -->
                    </div>
                </div>
            </div>

            <!-- Control buttons -->
            <div class="control-section">
                <div class="control-buttons">
                    <button id="reset-btn" class="control-btn btn-secondary">
                        <i class="fas fa-undo"></i> Reset All
                    </button>
                    <button id="fit-btn" class="control-btn btn-primary">
                        <i class="fas fa-expand-arrows-alt"></i> Fit View
                    </button>
                </div>
            </div>

            <!-- Statistics panel -->
            <div class="stats-panel">
                <h4><i class="fas fa-chart-bar"></i> Network Statistics</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <p class="stat-value" id="total-nodes">198</p>
                        <p class="stat-label">Total Keywords</p>
                    </div>
                    <div class="stat-item">
                        <p class="stat-value" id="total-edges">160</p>
                        <p class="stat-label">Connections</p>
                    </div>
                    <div class="stat-item">
                        <p class="stat-value" id="visible-nodes">0</p>
                        <p class="stat-label">Currently Visible</p>
                    </div>
                    <div class="stat-item">
                        <p class="stat-value" id="selected-nodes">0</p>
                        <p class="stat-label">Selected</p>
                    </div>
                </div>
            </div>

            <!-- Top keywords list -->
            <div class="control-section">
                <h3><i class="fas fa-list"></i>Top Keywords</h3>
                <div id="keyword-list" class="keyword-list">
                    <!-- Dynamically generated -->
                </div>
            </div>
        </div>

        <!-- Main content -->
        <div class="main-content">
            <!-- Header -->
            <div class="header">
                <h1>🔗 AI Design Research Semantic Network</h1>
                <p>Explore 198 keywords and their 160 co-occurrence relationships</p>
            </div>

            <!-- Cytoscape.js network -->
            <div id="cy"></div>

            <!-- Info panel (hidden by default) -->
            <div id="info-panel" class="info-panel">
                <button class="close-btn" onclick="hideInfoPanel()">&times;</button>
                <div id="info-content">
                    <div style="text-align: center; color: #6c757d; padding: 40px 20px;">
                        <i class="fas fa-mouse-pointer" style="font-size: 2rem; margin-bottom: 15px;"></i>
                        <h4>Click on a keyword</h4>
                        <p>to explore its connections and see detailed information</p>
                    </div>
                </div>
            </div>

            <!-- Legend -->
            <div class="legend">
                <div class="legend-title">🎨 AI Methods</div>
                <div class="legend-items" id="legend-items">
                    <!-- Dynamically generated -->
                </div>
            </div>
        </div>
    </div>

    <!-- Embedded Data (No CORS issues!) -->
    <script>
        // Network data embedded directly in HTML
        window.NETWORK_DATA = {json.dumps(network_data, indent=8)};
        
        window.METADATA = {json.dumps(metadata, indent=8)};
    </script>

    <!-- Network Dashboard Controller -->
    <script>
        class NetworkDashboard {{
            constructor() {{
                this.cy = null;
                this.networkData = window.NETWORK_DATA;
                this.metadata = window.METADATA;
                this.selectedNode = null;
                
                this.init();
            }}

            init() {{
                console.log('🚀 Initializing Network Dashboard...');
                
                try {{
                    // Initialize Cytoscape.js
                    this.initCytoscape();
                    
                    // Initialize UI
                    this.initUI();
                    
                    // Setup event listeners
                    this.setupEventListeners();
                    
                    // Update initial statistics
                    this.updateStats();
                    
                    console.log('✅ Dashboard initialization complete');
                    
                }} catch (error) {{
                    console.error('❌ Initialization failed:', error);
                    alert('Failed to initialize dashboard. Please refresh the page.');
                }} finally {{
                    // Hide loading screen
                    setTimeout(() => {{
                        document.getElementById('loading').style.display = 'none';
                    }}, 500);
                }}
            }}

            initCytoscape() {{
                console.log('🕸️ Initializing Cytoscape.js...');
                
                this.cy = cytoscape({{
                    container: document.getElementById('cy'),
                    elements: this.networkData.elements,
                    style: this.networkData.style,
                    layout: {{
                        name: 'cose-bilkent',
                        quality: 'default',
                        nodeRepulsion: 8000,
                        nodeOverlap: 20,
                        idealEdgeLength: 100,
                        edgeElasticity: 0.45,
                        nestingFactor: 0.1,
                        gravity: 0.8,
                        numIter: 2500,
                        tile: true,
                        animate: 'end',
                        animationEasing: 'ease-out',
                        animationDuration: 2000,
                        randomize: false
                    }},
                    minZoom: 0.1,
                    maxZoom: 3,
                    wheelSensitivity: 0.3
                }});

                console.log('✅ Cytoscape.js initialized');
            }}

            initUI() {{
                console.log('🎨 Initializing UI...');
                
                this.createAIMethodFilters();
                this.createDesignTaskFilters();
                this.createKeywordList();
                this.createLegend();
                
                console.log('✅ UI initialized');
            }}

            createAIMethodFilters() {{
                const container = document.getElementById('ai-method-filters');
                const colors = this.metadata.colors;
                
                this.metadata.ai_methods.forEach(method => {{
                    const div = document.createElement('div');
                    div.className = 'filter-option';
                    
                    div.innerHTML = `
                        <input type="checkbox" id="ai-${{method}}" checked>
                        <label for="ai-${{method}}">${{method}}</label>
                        <div class="color-indicator" style="background-color: ${{colors[method]}}"></div>
                    `;
                    
                    container.appendChild(div);
                }});
            }}

            createDesignTaskFilters() {{
                const container = document.getElementById('design-task-filters');
                const tasks = this.metadata.design_tasks;
                
                tasks.forEach(task => {{
                    const div = document.createElement('div');
                    div.className = 'filter-option';
                    
                    div.innerHTML = `
                        <input type="checkbox" id="task-${{task}}" checked>
                        <label for="task-${{task}}">${{task}}</label>
                    `;
                    
                    container.appendChild(div);
                }});
            }}

            createKeywordList() {{
                const container = document.getElementById('keyword-list');
                
                // Sort by frequency
                const sortedNodes = this.networkData.elements.nodes
                    .sort((a, b) => b.data.frequency - a.data.frequency)
                    .slice(0, 25); // Top 25
                
                sortedNodes.forEach(node => {{
                    const div = document.createElement('div');
                    div.className = 'keyword-item';
                    div.setAttribute('data-keyword', node.data.id);
                    
                    div.innerHTML = `
                        <span class="keyword-name">${{node.data.label}}</span>
                        <span class="keyword-freq">${{node.data.frequency}}</span>
                    `;
                    
                    div.addEventListener('click', () => this.focusOnKeyword(node.data.id));
                    
                    container.appendChild(div);
                }});
            }}

            createLegend() {{
                const container = document.getElementById('legend-items');
                const colors = this.metadata.colors;
                
                Object.entries(colors).forEach(([method, color]) => {{
                    const div = document.createElement('div');
                    div.className = 'legend-item';
                    
                    div.innerHTML = `
                        <div class="color-indicator" style="background-color: ${{color}}"></div>
                        <span>${{method}}</span>
                    `;
                    
                    container.appendChild(div);
                }});
            }}

            setupEventListeners() {{
                console.log('🎧 Setting up event listeners...');
                
                // Cytoscape.js events
                this.cy.on('tap', 'node', (evt) => {{
                    const node = evt.target;
                    this.selectNode(node);
                }});
                
                this.cy.on('tap', (evt) => {{
                    if (evt.target === this.cy) {{
                        this.deselectAll();
                    }}
                }});
                
                // Search functionality
                const searchInput = document.getElementById('search-input');
                searchInput.addEventListener('input', (e) => {{
                    this.searchKeywords(e.target.value);
                }});
                
                // Layout change
                const layoutSelect = document.getElementById('layout-select');
                layoutSelect.addEventListener('change', (e) => {{
                    this.changeLayout(e.target.value);
                }});
                
                // Filter events
                this.setupFilterEvents();
                
                // Control buttons
                document.getElementById('reset-btn').addEventListener('click', () => this.resetView());
                document.getElementById('fit-btn').addEventListener('click', () => this.cy.fit());
                
                console.log('✅ Event listeners setup complete');
            }}

            setupFilterEvents() {{
                // AI Method filters
                this.metadata.ai_methods.forEach(method => {{
                    const checkbox = document.getElementById(`ai-${{method}}`);
                    checkbox.addEventListener('change', () => this.applyFilters());
                }});
                
                // Design Task filters
                this.metadata.design_tasks.forEach(task => {{
                    const checkbox = document.getElementById(`task-${{task}}`);
                    checkbox.addEventListener('change', () => this.applyFilters());
                }});
            }}

            selectNode(node) {{
                // Clear previous selection
                this.cy.elements().removeClass('highlighted faded');
                
                // Select new node
                this.selectedNode = node;
                node.addClass('highlighted');
                
                // Highlight neighbor nodes
                const neighbors = node.neighborhood();
                neighbors.addClass('highlighted');
                
                // Fade other nodes
                this.cy.elements().difference(neighbors.union(node)).addClass('faded');
                
                // Show info panel
                this.showInfoPanel(node);
                
                // Update statistics
                this.updateStats();
            }}

            deselectAll() {{
                this.cy.elements().removeClass('highlighted faded');
                this.selectedNode = null;
                this.hideInfoPanel();
                this.updateStats();
            }}

            showInfoPanel(node) {{
                const panel = document.getElementById('info-panel');
                const content = document.getElementById('info-content');
                
                const data = node.data();
                const neighbors = node.neighborhood('node');
                const neighborNames = neighbors.map(n => n.data('label')).slice(0, 12).join(', ');
                
                content.innerHTML = `
                    <h3 style="color: ${{data.color}}; margin-bottom: 20px; text-align: center;">
                        <i class="fas fa-key"></i> ${{data.label}}
                    </h3>
                    <div class="info-section">
                        <h5><i class="fas fa-chart-bar"></i> Basic Information</h5>
                        <ul>
                            <li><strong>Frequency:</strong> ${{data.frequency}} occurrences</li>
                            <li><strong>Connections:</strong> ${{data.degree}} keywords</li>
                            <li><strong>AI Method:</strong> ${{data.ai_method}}</li>
                            <li><strong>Design Phase:</strong> ${{data.design_task}}</li>
                        </ul>
                    </div>
                    <div class="info-section">
                        <h5><i class="fas fa-network-wired"></i> Network Centrality</h5>
                        <ul>
                            <li><strong>Betweenness:</strong> ${{data.betweenness_centrality.toFixed(3)}}</li>
                            <li><strong>Closeness:</strong> ${{data.closeness_centrality.toFixed(3)}}</li>
                            <li><strong>Eigenvector:</strong> ${{data.eigenvector_centrality.toFixed(3)}}</li>
                        </ul>
                    </div>
                    <div class="info-section">
                        <h5><i class="fas fa-link"></i> Connected Keywords</h5>
                        <p style="font-size: 0.85rem; line-height: 1.5; color: #6c757d; background: #f8f9fa; padding: 10px; border-radius: 6px;">
                            ${{neighborNames}}${{neighbors.length > 12 ? ' and more...' : ''}}
                        </p>
                    </div>
                `;
                
                panel.classList.add('show');
            }}

            hideInfoPanel() {{
                document.getElementById('info-panel').classList.remove('show');
            }}

            searchKeywords(query) {{
                if (!query.trim()) {{
                    this.cy.elements().removeClass('highlighted faded');
                    return;
                }}
                
                const matchingNodes = this.cy.nodes().filter(node => {{
                    return node.data('label').toLowerCase().includes(query.toLowerCase());
                }});
                
                if (matchingNodes.length > 0) {{
                    this.cy.elements().addClass('faded');
                    matchingNodes.removeClass('faded').addClass('highlighted');
                    
                    // Focus on first matching node
                    if (matchingNodes.length === 1) {{
                        this.selectNode(matchingNodes.first());
                    }}
                    
                    this.cy.animate({{
                        fit: {{
                            eles: matchingNodes,
                            padding: 100
                        }}
                    }}, {{
                        duration: 1200
                    }});
                }}
            }}

            focusOnKeyword(keyword) {{
                const node = this.cy.getElementById(keyword);
                if (node.length > 0) {{
                    this.selectNode(node);
                    this.cy.animate({{
                        fit: {{
                            eles: node,
                            padding: 150
                        }}
                    }}, {{
                        duration: 1200
                    }});
                }}
            }}

            applyFilters() {{
                console.log('🔍 Applying filters...');
                
                // Selected AI Methods
                const selectedMethods = [];
                this.metadata.ai_methods.forEach(method => {{
                    const checkbox = document.getElementById(`ai-${{method}}`);
                    if (checkbox && checkbox.checked) {{
                        selectedMethods.push(method);
                    }}
                }});
                
                // Selected Design Tasks
                const selectedTasks = [];
                this.metadata.design_tasks.forEach(task => {{
                    const checkbox = document.getElementById(`task-${{task}}`);
                    if (checkbox && checkbox.checked) {{
                        selectedTasks.push(task);
                    }}
                }});
                
                // Filter nodes
                this.cy.nodes().forEach(node => {{
                    const aiMethod = node.data('ai_method');
                    const designTask = node.data('design_task');
                    
                    const show = selectedMethods.includes(aiMethod) && selectedTasks.includes(designTask);
                    
                    if (show) {{
                        node.style('display', 'element');
                    }} else {{
                        node.style('display', 'none');
                    }}
                }});
                
                // Filter edges
                this.cy.edges().forEach(edge => {{
                    const source = edge.source();
                    const target = edge.target();
                    
                    if (source.style('display') !== 'none' && target.style('display') !== 'none') {{
                        edge.style('display', 'element');
                    }} else {{
                        edge.style('display', 'none');
                    }}
                }});
                
                // Update statistics
                this.updateStats();
                
                console.log('✅ Filters applied');
            }}

            changeLayout(layoutName) {{
                console.log(`🔄 Changing layout: ${{layoutName}}`);
                
                let layoutOptions = {{ name: layoutName, animate: true, animationDuration: 2000 }};
                
                // Layout-specific optimized options
                switch(layoutName) {{
                    case 'cose-bilkent':
                        layoutOptions = {{
                            name: 'cose-bilkent',
                            quality: 'default',
                            nodeRepulsion: 8000,
                            idealEdgeLength: 100,
                            animate: 'end',
                            animationDuration: 2000
                        }};
                        break;
                    case 'circle':
                        layoutOptions.radius = Math.min(400, window.innerWidth * 0.3);
                        break;
                    case 'grid':
                        layoutOptions.padding = 30;
                        layoutOptions.spacingFactor = 1.2;
                        break;
                    case 'breadthfirst':
                        layoutOptions.directed = false;
                        layoutOptions.spacingFactor = 2;
                        break;
                    case 'concentric':
                        layoutOptions.concentric = node => node.data('frequency');
                        layoutOptions.levelWidth = () => 3;
                        layoutOptions.minNodeSpacing = 50;
                        break;
                }}
                
                this.cy.layout(layoutOptions).run();
            }}

            resetView() {{
                console.log('🔄 Resetting view...');
                
                // Check all filters
                this.metadata.ai_methods.forEach(method => {{
                    const checkbox = document.getElementById(`ai-${{method}}`);
                    if (checkbox) checkbox.checked = true;
                }});
                this.metadata.design_tasks.forEach(task => {{
                    const checkbox = document.getElementById(`task-${{task}}`);
                    if (checkbox) checkbox.checked = true;
                }});
                
                // Clear search
                document.getElementById('search-input').value = '';
                
                // Deselect all
                this.deselectAll();
                
                // Apply filters
                this.applyFilters();
                
                // Fit view
                setTimeout(() => {{
                    this.cy.fit();
                }}, 500);
                
                console.log('✅ View reset complete');
            }}

            updateStats() {{
                const visibleNodes = this.cy.nodes().filter(node => node.style('display') !== 'none');
                const visibleEdges = this.cy.edges().filter(edge => edge.style('display') !== 'none');
                const selectedCount = this.selectedNode ? 1 : 0;
                
                document.getElementById('visible-nodes').textContent = visibleNodes.length;
                document.getElementById('selected-nodes').textContent = selectedCount;
            }}
        }}

        // Global functions
        function hideInfoPanel() {{
            document.getElementById('info-panel').classList.remove('show');
        }}

        // Initialize dashboard when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {{
            console.log('📱 DOM loaded, initializing dashboard...');
            window.dashboard = new NetworkDashboard();
        }});
    </script>
</body>
</html>"""
    
    # 출력 파일 저장
    output_file = '/Users/outcode.jongmokim/Documents/paper_review_with_llm/output/semantic_network_analysis/interactive/self_contained_english_dashboard.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 자체 완성형 영어 대시보드 생성 완료!")
    print(f"📁 파일 위치: {output_file}")
    print(f"📊 포함된 데이터: {len(network_data['elements']['nodes'])}개 노드, {len(network_data['elements']['edges'])}개 엣지")
    print("\n🚀 사용법: 브라우저에서 HTML 파일을 직접 열어보세요!")

if __name__ == "__main__":
    create_self_contained_dashboard()