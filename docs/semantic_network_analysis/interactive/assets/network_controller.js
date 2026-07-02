// AI Design Research 시맨틱 네트워크 대시보드 컨트롤러
// Cytoscape.js 기반 인터랙티브 네트워크 시각화

class NetworkDashboard {
    constructor() {
        this.cy = null;
        this.networkData = null;
        this.metadata = null;
        this.originalData = null;
        this.filteredNodes = new Set();
        this.selectedNode = null;
        
        this.init();
    }

    async init() {
        console.log('🚀 네트워크 대시보드 초기화 시작...');
        
        try {
            // 데이터 로드
            await this.loadData();
            
            // Cytoscape.js 초기화
            this.initCytoscape();
            
            // UI 초기화
            this.initUI();
            
            // 이벤트 리스너 설정
            this.setupEventListeners();
            
            // 초기 통계 업데이트
            this.updateStats();
            
            console.log('✅ 대시보드 초기화 완료');
            
        } catch (error) {
            console.error('❌ 초기화 실패:', error);
            alert('네트워크 데이터 로드에 실패했습니다. 페이지를 새로고침해주세요.');
        } finally {
            // 로딩 화면 제거
            document.getElementById('loading').style.display = 'none';
        }
    }

    async loadData() {
        console.log('📊 데이터 로딩 중...');
        
        // 네트워크 데이터 로드
        const networkResponse = await fetch('data/network_data.json');
        this.networkData = await networkResponse.json();
        this.originalData = JSON.parse(JSON.stringify(this.networkData)); // 깊은 복사
        
        // 메타데이터 로드
        const metadataResponse = await fetch('data/metadata.json');
        this.metadata = await metadataResponse.json();
        
        console.log(`✅ 데이터 로드 완료: ${this.networkData.elements.nodes.length}개 노드, ${this.networkData.elements.edges.length}개 엣지`);
    }

    initCytoscape() {
        console.log('🕸️ Cytoscape.js 초기화 중...');
        
        this.cy = cytoscape({
            container: document.getElementById('cy'),
            elements: this.networkData.elements,
            style: this.networkData.style,
            layout: {
                name: 'cose',
                quality: 'default',
                nodeRepulsion: 4500,
                nodeOverlap: 10,
                idealEdgeLength: 50,
                edgeElasticity: 0.45,
                nestingFactor: 0.1,
                gravity: 0.25,
                numIter: 2500,
                tile: true,
                animate: 'end',
                animationEasing: 'ease-out',
                animationDuration: 1000,
                randomize: false
            },
            minZoom: 0.2,
            maxZoom: 5,
            wheelSensitivity: 0.2
        });

        console.log('✅ Cytoscape.js 초기화 완료');
    }

    initUI() {
        console.log('🎨 UI 초기화 중...');
        
        // AI Method 필터 생성
        this.createAIMethodFilters();
        
        // Design Task 필터 생성  
        this.createDesignTaskFilters();
        
        // 키워드 리스트 생성
        this.createKeywordList();
        
        // 범례 생성
        this.createLegend();
        
        console.log('✅ UI 초기화 완료');
    }

    createAIMethodFilters() {
        const container = document.getElementById('ai-method-filters');
        const colors = this.metadata.colors;
        
        this.metadata.ai_methods.forEach(method => {
            const div = document.createElement('div');
            div.className = 'filter-option';
            
            div.innerHTML = `
                <input type="checkbox" id="ai-${method}" checked>
                <label for="ai-${method}">${method}</label>
                <div class="color-indicator" style="background-color: ${colors[method]}"></div>
            `;
            
            container.appendChild(div);
        });
    }

    createDesignTaskFilters() {
        const container = document.getElementById('design-task-filters');
        const tasks = this.metadata.design_tasks;
        
        tasks.forEach(task => {
            const div = document.createElement('div');
            div.className = 'filter-option';
            
            div.innerHTML = `
                <input type="checkbox" id="task-${task}" checked>
                <label for="task-${task}">${task}</label>
            `;
            
            container.appendChild(div);
        });
    }

    createKeywordList() {
        const container = document.getElementById('keyword-list');
        
        // 빈도순으로 정렬
        const sortedNodes = this.networkData.elements.nodes
            .sort((a, b) => b.data.frequency - a.data.frequency)
            .slice(0, 20); // 상위 20개만
        
        sortedNodes.forEach(node => {
            const div = document.createElement('div');
            div.className = 'keyword-item';
            div.setAttribute('data-keyword', node.data.id);
            
            div.innerHTML = `
                <span class="keyword-name">${node.data.label}</span>
                <span class="keyword-freq">${node.data.frequency}</span>
            `;
            
            div.addEventListener('click', () => this.focusOnKeyword(node.data.id));
            
            container.appendChild(div);
        });
    }

    createLegend() {
        const container = document.getElementById('legend-items');
        const colors = this.metadata.colors;
        
        Object.entries(colors).forEach(([method, color]) => {
            const div = document.createElement('div');
            div.className = 'legend-item';
            
            div.innerHTML = `
                <div class="color-indicator" style="background-color: ${color}"></div>
                <span style="font-size: 0.8rem;">${method}</span>
            `;
            
            container.appendChild(div);
        });
    }

    setupEventListeners() {
        console.log('🎧 이벤트 리스너 설정 중...');
        
        // Cytoscape.js 이벤트
        this.cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            this.selectNode(node);
        });
        
        this.cy.on('tap', (evt) => {
            if (evt.target === this.cy) {
                this.deselectAll();
            }
        });
        
        // 검색 기능
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', (e) => {
            this.searchKeywords(e.target.value);
        });
        
        // 레이아웃 변경
        const layoutSelect = document.getElementById('layout-select');
        layoutSelect.addEventListener('change', (e) => {
            this.changeLayout(e.target.value);
        });
        
        // 필터 이벤트
        this.setupFilterEvents();
        
        // 컨트롤 버튼
        document.getElementById('reset-btn').addEventListener('click', () => this.resetView());
        document.getElementById('fit-btn').addEventListener('click', () => this.cy.fit());
        
        console.log('✅ 이벤트 리스너 설정 완료');
    }

    setupFilterEvents() {
        // AI Method 필터
        this.metadata.ai_methods.forEach(method => {
            const checkbox = document.getElementById(`ai-${method}`);
            checkbox.addEventListener('change', () => this.applyFilters());
        });
        
        // Design Task 필터
        this.metadata.design_tasks.forEach(task => {
            const checkbox = document.getElementById(`task-${task}`);
            checkbox.addEventListener('change', () => this.applyFilters());
        });
    }

    selectNode(node) {
        // 이전 선택 해제
        this.cy.elements().removeClass('highlighted faded');
        
        // 새 노드 선택
        this.selectedNode = node;
        node.addClass('highlighted');
        
        // 이웃 노드들 강조
        const neighbors = node.neighborhood();
        neighbors.addClass('highlighted');
        
        // 나머지 노드들 흐리게
        this.cy.elements().difference(neighbors.union(node)).addClass('faded');
        
        // 정보 패널 표시
        this.showInfoPanel(node);
        
        // 통계 업데이트
        this.updateStats();
    }

    deselectAll() {
        this.cy.elements().removeClass('highlighted faded');
        this.selectedNode = null;
        this.hideInfoPanel();
        this.updateStats();
    }

    showInfoPanel(node) {
        const panel = document.getElementById('info-panel');
        const content = document.getElementById('info-content');
        
        const data = node.data();
        const neighbors = node.neighborhood('node');
        const neighborNames = neighbors.map(n => n.data('label')).slice(0, 10).join(', ');
        
        content.innerHTML = `
            <h3 style="color: ${data.color}; margin-bottom: 15px;">
                <i class="fas fa-key"></i> ${data.label}
            </h3>
            <div class="info-section">
                <h5><i class="fas fa-chart-bar"></i> 기본 정보</h5>
                <ul>
                    <li><strong>출현 빈도:</strong> ${data.frequency}회</li>
                    <li><strong>연결 수:</strong> ${data.degree}개</li>
                    <li><strong>AI 방법론:</strong> ${data.ai_method}</li>
                    <li><strong>디자인 단계:</strong> ${data.design_task}</li>
                </ul>
            </div>
            <div class="info-section">
                <h5><i class="fas fa-network-wired"></i> 중심성 지표</h5>
                <ul>
                    <li><strong>매개 중심성:</strong> ${data.betweenness_centrality.toFixed(3)}</li>
                    <li><strong>근접 중심성:</strong> ${data.closeness_centrality.toFixed(3)}</li>
                    <li><strong>고유벡터 중심성:</strong> ${data.eigenvector_centrality.toFixed(3)}</li>
                </ul>
            </div>
            <div class="info-section">
                <h5><i class="fas fa-link"></i> 연결된 키워드</h5>
                <p style="font-size: 0.85rem; line-height: 1.4; color: #6c757d;">
                    ${neighborNames}${neighbors.length > 10 ? '...' : ''}
                </p>
            </div>
        `;
        
        panel.classList.add('show');
    }

    hideInfoPanel() {
        document.getElementById('info-panel').classList.remove('show');
    }

    searchKeywords(query) {
        if (!query.trim()) {
            this.cy.elements().removeClass('highlighted faded');
            return;
        }
        
        const matchingNodes = this.cy.nodes().filter(node => {
            return node.data('label').toLowerCase().includes(query.toLowerCase());
        });
        
        if (matchingNodes.length > 0) {
            this.cy.elements().addClass('faded');
            matchingNodes.removeClass('faded').addClass('highlighted');
            
            // 첫 번째 매칭 노드로 이동
            this.cy.animate({
                fit: {
                    eles: matchingNodes.first(),
                    padding: 100
                }
            }, {
                duration: 1000
            });
        }
    }

    focusOnKeyword(keyword) {
        const node = this.cy.getElementById(keyword);
        if (node.length > 0) {
            this.selectNode(node);
            this.cy.animate({
                fit: {
                    eles: node,
                    padding: 150
                }
            }, {
                duration: 1000
            });
        }
    }

    applyFilters() {
        console.log('🔍 필터 적용 중...');
        
        // 선택된 AI Methods
        const selectedMethods = [];
        this.metadata.ai_methods.forEach(method => {
            const checkbox = document.getElementById(`ai-${method}`);
            if (checkbox.checked) {
                selectedMethods.push(method);
            }
        });
        
        // 선택된 Design Tasks
        const selectedTasks = [];
        this.metadata.design_tasks.forEach(task => {
            const checkbox = document.getElementById(`task-${task}`);
            if (checkbox.checked) {
                selectedTasks.push(task);
            }
        });
        
        // 노드 필터링
        this.cy.nodes().forEach(node => {
            const aiMethod = node.data('ai_method');
            const designTask = node.data('design_task');
            
            const show = selectedMethods.includes(aiMethod) && selectedTasks.includes(designTask);
            
            if (show) {
                node.style('display', 'element');
            } else {
                node.style('display', 'none');
            }
        });
        
        // 엣지 필터링 (보이는 노드들 간의 엣지만 표시)
        this.cy.edges().forEach(edge => {
            const source = edge.source();
            const target = edge.target();
            
            if (source.style('display') !== 'none' && target.style('display') !== 'none') {
                edge.style('display', 'element');
            } else {
                edge.style('display', 'none');
            }
        });
        
        // 통계 업데이트
        this.updateStats();
        
        console.log('✅필터 적용 완료');
    }

    changeLayout(layoutName) {
        console.log(`🔄 레이아웃 변경: ${layoutName}`);
        
        let layoutOptions = { name: layoutName, animate: true, animationDuration: 1500 };
        
        // 레이아웃별 세부 옵션
        switch(layoutName) {
            case 'cose':
                layoutOptions = {
                    name: 'cose',
                    quality: 'default',
                    nodeRepulsion: 4500,
                    idealEdgeLength: 50,
                    animate: 'end',
                    animationDuration: 1500
                };
                break;
            case 'circle':
                layoutOptions.radius = 300;
                break;
            case 'grid':
                layoutOptions.padding = 50;
                break;
            case 'breadthfirst':
                layoutOptions.directed = false;
                layoutOptions.spacingFactor = 1.5;
                break;
            case 'concentric':
                layoutOptions.concentric = node => node.data('frequency');
                layoutOptions.levelWidth = () => 2;
                break;
        }
        
        this.cy.layout(layoutOptions).run();
    }

    resetView() {
        console.log('🔄 뷰 초기화 중...');
        
        // 모든 필터 체크
        this.metadata.ai_methods.forEach(method => {
            document.getElementById(`ai-${method}`).checked = true;
        });
        this.metadata.design_tasks.forEach(task => {
            document.getElementById(`task-${task}`).checked = true;
        });
        
        // 검색 초기화
        document.getElementById('search-input').value = '';
        
        // 선택 해제
        this.deselectAll();
        
        // 필터 적용
        this.applyFilters();
        
        // 뷰 맞춤
        this.cy.fit();
        
        console.log('✅ 뷰 초기화 완료');
    }

    updateStats() {
        const visibleNodes = this.cy.nodes().filter(node => node.style('display') !== 'none');
        const visibleEdges = this.cy.edges().filter(edge => edge.style('display') !== 'none');
        const selectedCount = this.selectedNode ? 1 : 0;
        
        document.getElementById('total-nodes').textContent = this.networkData.elements.nodes.length;
        document.getElementById('total-edges').textContent = this.networkData.elements.edges.length;
        document.getElementById('visible-nodes').textContent = visibleNodes.length;
        document.getElementById('selected-nodes').textContent = selectedCount;
    }
}

// 전역 함수들
function hideInfoPanel() {
    document.getElementById('info-panel').classList.remove('show');
}

// 페이지 로드 시 대시보드 초기화
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 DOM 로드 완료, 대시보드 초기화 시작...');
    window.dashboard = new NetworkDashboard();
});