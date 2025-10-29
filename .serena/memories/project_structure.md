# 프로젝트 구조 및 주요 컴포넌트

## 디렉토리 구조
```
paper_review_with_llm/
├── source/                              # 📊 원본 데이터
│   ├── PaperList.csv                   # 511개 논문 리스트
│   ├── Result_2.csv                    # 93개 분석 완료 논문 (메인)
│   └── CodeBook.csv                    # 코딩 기준서
│
├── analysis_work/                       # 📈 NLP 분석 워크플로우
│   ├── scripts/ (10개)                 # Python 분석 스크립트
│   └── results/                        # 분석 결과물
│       ├── nlp_analysis_improved/      # 7단계: 데이터 정규화
│       ├── topic_modeling_analysis/    # 8단계: 토픽 모델링
│       ├── semantic_network_analysis/  # 11-13단계: 네트워크 분석
│       └── *.html                      # 인터랙티브 대시보드
│
├── coding_work/                        # 🔧 Google Sheets 자동화
│   ├── scripts/                        # API 연동 스크립트
│   ├── credentials/                    # Google API 인증 (gitignore)
│   └── results/                        # PDF 분석 결과
│
├── Papers/                             # 📁 논문 PDF 파일들
├── checked_papers/                     # ✅ 검토 완료 논문들
└── venv/                              # 🐍 Python 가상환경
```

## 핵심 컴포넌트

### 분석워크 주요 클래스
1. **DataNormalizer** (`improved_nlp_analysis.py`)
   - AI Methods와 Design Tasks 정규화 (50+ → 4-5개 카테고리)
   - 연구 갭 분석 및 구체적 연구 아이디어 제안

2. **ImprovedNLPWorkflow** (`improved_nlp_analysis.py`)
   - 7단계 분석 파이프라인 통합 관리
   - 데이터 로드 → 정규화 → 분석 → 시각화 → 리포트

3. **SemanticNetworkBuilder** (`semantic_network_builder.py`)
   - 키워드 기반 논문 클러스터링
   - 네트워크 노드/엣지 생성

4. **ImprovedVisualizer** (각 분석 스크립트)
   - Plotly 기반 인터랙티브 시각화
   - 시계열 트렌드, 매트릭스, 네트워크 차트

### 코딩워크 주요 클래스
1. **GoogleSheetsConnector** (`google_sheets_connector.py`)
   - 서비스 계정 기반 Google Sheets API 연동
   - 900개 논문 × 18개 컬럼 데이터 관리
   - 배치 업데이트 및 API 할당량 관리

## 데이터 플로우

### 분석워크 플로우 (7-13단계)
```
source/Result_2.csv (93개 논문)
    ↓
7. improved_nlp_analysis.py → 데이터 정규화
    ↓
8. topic_modeling_analysis.py → BERTopic 토픽 모델링 (9개 토픽)
    ↓
9. create_dashboard_data.py → JSON 데이터 생성 (85KB)
    ↓
10. create_self_contained_dashboard.py → HTML 대시보드 (38KB)
    ↓
11-13. semantic_network_*.py → 네트워크 분석 및 시각화
```

### 코딩워크 플로우
```
Google Sheets (900개 논문) ←→ GoogleSheetsConnector
    ↓
논문 분류 상태 업데이트 (Y/N/Q)
    ↓
카테고리 분류 (ENGINEERING/PRODUCT/UI.UX/SERVICE)
```

## 주요 결과물

### 대시보드 시스템
- **interactive_topic_dashboard_en.html**: 메인 대시보드 (38KB)
- **self_contained_english_dashboard.html**: 네트워크 대시보드
- 기술스택: HTML5 + Bootstrap 5 + Plotly.js + JavaScript ES6

### 데이터 정규화 성과
- **Data Modality**: 22개 → 5개 (78% 간소화)
- **Design Practice**: 6개 → 4개 (Others 제거)
- **AI Methods**: Traditional ML, Deep Learning, Generative AI 중심

### 핵심 인사이트
- **AI 방법론 진화**: Deep Learning 급감, Generative AI 급증 (2023년 전환점)
- **토픽 발견**: 9개 주요 연구 토픽 (BERTopic 분석)
- **연구 갭**: Method × Task 조합에서 빈 영역 식별