# Paper Review with LLM - Project Documentation

## 프로젝트 개요
논문 리뷰 자동화를 위한 Python 스크립트 모음입니다. 데이터 분석 및 시각화를 통해 논문 연구 생태계를 체계적으로 탐색하는 워크플로우를 제공합니다.

## 파일 구조
```
paper_review_with_llm/
├── source/                              # 소스 데이터
│   ├── PaperList.csv                   # 원본 논문 리스트 (511개)
│   ├── Result.csv                      # 이미 분석된 논문들 (34개, 실제 33개)
│   ├── Result_2.csv                    # 확장된 분석 결과 (93편)
│   └── CodeBook.csv                    # 코딩 기준서
│
├── analysis_work/                       # 📈 데이터 분석 워크플로우
│   ├── scripts/                        # 분석 관련 스크립트 (13개)
│   │   ├── improved_nlp_analysis.py    # 7단계: 데이터 정규화 및 인사이트 분석
│   │   ├── topic_modeling_analysis.py  # 8단계: BERTopic 토픽 모델링 분석
│   │   ├── create_dashboard_data.py    # 9단계: 인터랙티브 대시보드 데이터 생성
│   │   ├── create_self_contained_dashboard.py # 10단계: Self-contained 대시보드
│   │   ├── semantic_network_builder.py # 11단계: Semantic Network 구축
│   │   ├── semantic_network_visualizer.py # 12단계: Network 시각화
│   │   ├── network_insights_analyzer.py # 13단계: Network 인사이트 분석
│   │   ├── keyword_extraction_analysis.py # 키워드 추출 분석
│   │   ├── nlp_analysis_workflow.py    # NLP 워크플로우 통합
│   │   ├── convert_to_cytoscape_json.py # Cytoscape JSON 변환
│   │   ├── analyze_gantt_colors.js     # Gantt 차트 색상 분석 (JavaScript)
│   │   ├── package.json               # Node.js 의존성
│   │   └── node_modules/              # Node.js 모듈들
│   └── results/                        # 분석 결과물
│       ├── nlp_analysis_improved/      # 데이터 정규화 및 갭 분석 결과
│       ├── topic_modeling_analysis/    # 토픽 모델링 분석 결과
│       ├── semantic_network_analysis/  # Semantic Network 분석 결과
│       ├── dashboard_data.json         # 대시보드용 JSON 데이터 (85KB)
│       ├── interactive_topic_dashboard_en.html # 영어 인터랙티브 대시보드 (38KB)
│       ├── project_gantt_chart.html    # 프로젝트 Gantt 차트
│       ├── project_gantt_chart_custom.html # 커스텀 Gantt 차트
│       └── nlp_analysis/              # 기존 NLP 분석 결과
│
├── coding_work/                        # 🔧 논문 분류 자동화 워크플로우
│   ├── scripts/                        # 분류 관련 스크립트 (7개)
│   │   ├── google_sheets_connector.py  # Google Sheets API 연결 모듈
│   │   ├── paper_tracking.py           # 논문 추적 (Inclusion='Y' → Mark='M')
│   │   ├── pdf_title_fixer.py          # PDF 파일명 자동 정리
│   │   ├── pdf_upload_checker.py       # PDF 업로드 상태 자동 마킹 ⭐
│   │   ├── pdf_analyzer.py             # PDF 내용 분석 및 Claude 매칭
│   │   ├── debug_single_pdf.py         # PDF 단건 디버깅
│   │   └── analyze_sheets_structure.py # Google Sheets 구조 분석
│   ├── credentials/                    # Google API 인증 파일 (gitignore)
│   ├── logs/                          # 로그 파일
│   └── results/                       # 처리 결과물
│       └── pdf_analysis/              # PDF 분석 결과
│
├── Papers/                             # 논문 파일들 (100+)
├── checked_papers/                     # 체크 완료된 논문 보관
├── ai_evolution_diagram/              # AI 진화 다이어그램
├── venv/                              # Python 가상환경
├── requirements.txt                   # Python 의존성 (통합)
├── research_report.md                 # AI 방법론 진화 분석 에세이
└── CLAUDE.md                          # 이 문서 (README.md와 동일)
```

## 📈 분석 워크플로우 (7-13단계)

### 7단계: 데이터 정규화 및 인사이트 분석
**파일**: `analysis_work/scripts/improved_nlp_analysis.py`
- **입력**: source/Result_2.csv (93개 논문 + Abstract)
- **핵심 기능**:
  1. **데이터 정규화**: AI Methods와 Design Tasks를 4-5개 메인 카테고리로 체계화
  2. **AI 방법론 진화 분석**: 2020-2025년 방법론 변화 트렌드
  3. **연구 갭 분석**: Method × Task 조합에서 빈 영역 식별
  4. **구체적 연구 아이디어 제안**: 빈 영역을 실행 가능한 연구 주제로 변환
- **출력**: analysis_work/results/nlp_analysis_improved/
- **실행**: `cd analysis_work/scripts && python improved_nlp_analysis.py`

### 8단계: 토픽 모델링 중심 분석
**파일**: `analysis_work/scripts/topic_modeling_analysis.py`
- **입력**: 정규화된 데이터 (93편 Abstract)
- **핵심 기능**:
  1. **BERTopic 토픽 모델링**: 도메인 정보 보존하며 9개 주요 토픽 발견
  2. **연도별 토픽 트렌드**: 연구자들의 관심 변화 추적
  3. **토픽 × AI Methods 관계**: 토픽별 주요 AI 기법 분석
  4. **토픽 × Design Practice 관계**: 토픽별 주요 디자인 단계 분석
- **출력**: analysis_work/results/topic_modeling_analysis/
- **실행**: `cd analysis_work/scripts && python topic_modeling_analysis.py`

### 9단계: 대시보드 데이터 준비 시스템
**파일**: `analysis_work/scripts/create_dashboard_data.py`
- **목적**: 토픽 분석 결과를 인터랙티브 웹 대시보드용 JSON 데이터로 변환
- **핵심 기능**:
  1. **다차원 데이터 정규화**: Data Modality, Design Practice 체계적 정리
  2. **4차원 시계열 트렌드**: Topics, AI Methods, Data Modality, Design Practice
  3. **3차원 관계 매트릭스**: Topics×AI Methods, Topics×Design Practice, AI Methods×Design Practice
  4. **논문 상세 정보**: 74개 논문의 완전한 메타데이터 + Abstract
- **출력**: analysis_work/results/dashboard_data.json
- **실행**: `cd analysis_work/scripts && python create_dashboard_data.py`

### 10단계: 인터랙티브 웹 대시보드 구축
**파일**: `analysis_work/scripts/create_self_contained_dashboard.py`
- **기술 스택**: HTML5, Bootstrap 5, Plotly.js, JavaScript ES6
- **핵심 특징**: 단일 HTML 파일 (38KB), 외부 의존성 최소화
- **출력**: analysis_work/results/interactive_topic_dashboard_en.html
- **실행**: `cd analysis_work/scripts && python create_self_contained_dashboard.py`

### 11단계: Semantic Network 구축
**파일**: `analysis_work/scripts/semantic_network_builder.py`
- **목적**: 논문 간 의미론적 관계 네트워크 구축
- **핵심 기능**: 키워드 기반 논문 클러스터링 및 관계 매핑
- **출력**: analysis_work/results/semantic_network_analysis/data/
- **실행**: `cd analysis_work/scripts && python semantic_network_builder.py`

### 12단계: Network 시각화
**파일**: `analysis_work/scripts/semantic_network_visualizer.py`
- **목적**: Semantic Network의 인터랙티브 시각화
- **기술 스택**: Cytoscape.js, D3.js
- **출력**: analysis_work/results/semantic_network_analysis/interactive/
- **실행**: `cd analysis_work/scripts && python semantic_network_visualizer.py`

### 13단계: Network 인사이트 분석
**파일**: `analysis_work/scripts/network_insights_analyzer.py`
- **목적**: 네트워크 구조 분석을 통한 연구 트렌드 인사이트 도출
- **핵심 기능**: 중심성 분석, 커뮤니티 탐지, 연구 갭 식별
- **출력**: analysis_work/results/semantic_network_analysis/insights/
- **실행**: `cd analysis_work/scripts && python network_insights_analyzer.py`

## 🛠 기술 스택

### Python 라이브러리
- **BERTopic**: Transformer 기반 토픽 모델링
- **sentence-transformers**: Abstract 임베딩 생성 (all-MiniLM-L6-v2)
- **spaCy**: 텍스트 전처리 및 표제어 추출
- **KeyBERT**: 키워드 추출 (미래 확장용)
- **scikit-learn**: 전통적 ML 분석
- **matplotlib/seaborn**: 정적 시각화
- **plotly**: 인터랙티브 시각화
- **pandas**: 데이터 처리 및 조작
- **networkx**: 네트워크 분석
- **cytoscape**: 네트워크 시각화

### 데이터 처리 전략
1. **도메인 정보 보존**: design, method, approach 등 연구 핵심 용어 유지
2. **의미있는 토큰 보존**: AI, UI 같은 2-3글자 중요 용어 보존
3. **체계적 정규화**: 50+ 세분화 카테고리를 4-5개 메인 그룹으로 통합
4. **다층 관계 분석**: 시간축, AI 기법, 디자인 단계 3차원 교차 분석

## 🚀 실행 순서

### 📈 분석워크 실행 (7-13단계)
```bash
# 가상환경 활성화
source venv/bin/activate

# 분석워크 디렉토리로 이동
cd analysis_work/scripts

# 7-10단계: NLP 분석 및 대시보드 시스템
python improved_nlp_analysis.py                 # 7단계: 데이터 정규화 및 인사이트
python topic_modeling_analysis.py               # 8단계: BERTopic 토픽 모델링
python create_dashboard_data.py                 # 9단계: 대시보드 데이터 생성
python create_self_contained_dashboard.py       # 10단계: 인터랙티브 대시보드 생성

# 11-13단계: Semantic Network 분석 시스템
python semantic_network_builder.py              # 11단계: Semantic Network 구축
python semantic_network_visualizer.py           # 12단계: Network 시각화  
python network_insights_analyzer.py             # 13단계: Network 인사이트 분석
```

### 🌐 결과물 확인
```bash
# 대시보드 서버 실행
cd ../results && python3 -m http.server 8000 --bind 127.0.0.1

# 브라우저에서 대시보드 접속
# http://127.0.0.1:8000/interactive_topic_dashboard_en.html
```

### 🔧 라이브러리 설치 (필요시)
```bash
# Python 라이브러리 설치
pip install bertopic sentence-transformers spacy matplotlib seaborn plotly pandas networkx cytoscape

# spaCy 모델 다운로드
python -m spacy download en_core_web_sm

# Node.js 라이브러리 설치 (Gantt 차트용)
cd analysis_work/scripts && npm install
```

## 📊 주요 인사이트 및 발견

### AI 방법론 진화 (2020-2025)
- **Deep Learning**: 50% → 21.1% (28.9%p 급감)
- **Generative AI**: 0% → 23.7% (23.7%p 급증) - 2023년 전환점
- **Traditional ML**: 여전히 주류 (51편/93편)

### 발견된 주요 토픽 (BERTopic 분석)
1. **Interaction + User + Technology** (18편) - Gen AI 중심
2. **Design + Case + Research** (10편) - Traditional ML 중심  
3. **Emotion + Emotional + Recognition** (9편) - Deep Learning 중심
4. **Product + Customer + Review** (9편) - Traditional ML, Define 단계 중심

### 데이터 정규화 성과
- **Data Modality**: 22개 → 5개 카테고리 (78% 간소화)
  - Text: 32편, Image: 19편, Time Series: 12편, Multimodal: 11편, Audio: 8편
- **Design Practice**: 6개 → 4개 카테고리 (Others 완전 제거)
  - Develop: 58편, Define: 13편, Discovery: 2편, Delivery: 1편

### 핵심 통찰
- **2023년 Gen AI 전환점**: 2022년 1편 → 2024년 9편으로 급성장
- **Text 데이터 압도적 우세**: 전체 논문의 43.2% (32편)
- **Develop 단계 집중**: 전체 논문의 78.4% (58편)
- **AI Methods × Design Practice**: Traditional ML이 Develop 집중, Gen AI는 균형 분포

## 🎯 달성된 주요 성과
1. **완전한 메타데이터**: 93편 논문에 Abstract 추가 완료 → 74편 유효 토픽 분류
2. **체계적 데이터 정규화**: 복잡한 카테고리를 핵심 그룹으로 간소화
3. **9개 주요 토픽 발견**: BERTopic으로 연구 생태계 체계화
4. **3차원 관계 분석**: Topics×AI Methods×Design Practice 교차 분석 완성
5. **인터랙티브 웹 대시보드**: 단일 HTML 파일(38KB)로 모든 분석 결과 탐색 가능
6. **국제 공유 가능**: 영어 기반 학술 발표용 대시보드 완성
7. **Semantic Network 분석**: 논문 간 의미론적 관계 네트워크 구축 및 시각화

**결과**: **워크플로우별로 체계화된 연구 생태계 전체를 탐색할 수 있는 완전한 인터랙티브 분석 시스템** 구축 완료!

## 🔧 코딩워크 (논문 분류 자동화)

### 개요
Google Sheets API를 통한 논문 분류 작업 자동화 시스템입니다. 900개 논문이 포함된 "Coding & screening works" 스프레드시트와 연동하여 논문 분류 작업을 효율화합니다.

### 데이터베이스 현황
- **스프레드시트**: "Coding & screening works"
- **시트**: "1st Screening results (track record)" (총 5개 시트 중 1개)
- **데이터 규모**: **900개 논문** × **18개 컬럼**
- **분류 상태**: 525개 분류 완료 (58.3%), 375개 미분류 (41.7%)

### 주요 컬럼 구조
| 컬럼명 | 데이터 수 | 용도 |
|--------|----------|------|
| **Rank** | 900개 | 논문 순위 |
| **Article Title** | 900개 | 논문 제목 |
| **Author Full Names** | 900개 | 저자명 |
| **Publication Year** | 900개 | 출판연도 (2020-2025) |
| **Abstract** | 900개 | 논문 초록 (분류 핵심 데이터) |
| **Design_Score** | 900개 | 디자인 관련도 점수 (0-1) |
| **AI_Score** | 900개 | AI 관련도 점수 (0-1) |
| **Overall_Score** | 900개 | 종합 점수 |
| **Inclusion (Y/N/Q)** | 900개 | **분류 상태** (Y/N/YES) |
| **ENGINEERING.PRODUCT/UI.UX/SERVICE** | 525개 | **카테고리 분류** |

### 기술 스택
- **Google Sheets API**: 서비스 계정 인증 방식
- **gspread**: Python Google Sheets 클라이언트
- **pandas**: 데이터 처리 및 조작

### 실행 방법

#### 1. 환경 설정
```bash
# 가상환경 활성화
source venv/bin/activate

# 라이브러리 설치 (이미 requirements.txt에 포함됨)
pip install -r requirements.txt
```

#### 2. Google Sheets API 설정
1. Google Cloud Console에서 서비스 계정 생성
2. JSON 키를 `coding_work/credentials/` 폴더에 저장
3. 스프레드시트에 서비스 계정 이메일 편집 권한 부여

#### 3. 연결 테스트
```bash
python coding_work/scripts/test_connection.py
```

#### 4. 기본 사용법
```python
from coding_work.scripts.google_sheets_connector import GoogleSheetsConnector

# 연결 생성
connector = GoogleSheetsConnector(
    credentials_path='coding_work/credentials/service_account.json',
    spreadsheet_id='1MgMKl7b8y5hPScQZJQ5y8y-J_UY1qalgVnQEFOucbBM'
)

# API 연결
if connector.connect():
    # 원시 데이터 읽기
    sheet = connector.get_sheet()
    all_values = sheet.get_all_values()
    
    # 논문 분류 상태 업데이트
    connector.update_paper_status('1', 'CLASSIFIED')
```

### 주요 기능
- `GoogleSheetsConnector.connect()`: Google Sheets API 연결
- `GoogleSheetsConnector.get_sheet()`: 시트 객체 가져오기
- `GoogleSheetsConnector.update_paper_status()`: 논문 분류 상태 업데이트
- `GoogleSheetsConnector.add_new_row()`: 새 행 추가
- 로깅 시스템: `coding_work/logs/google_sheets.log`

### 보안 설정
- `coding_work/credentials/` 폴더는 `.gitignore`에 포함됨
- 서비스 계정 키는 최소 권한으로 설정 권장
- **Credentials 경로**: `gen-lang-client-0444199460-38266703559b.json` 파일명이 하드코딩됨
- **Spreadsheet ID**: `1MgMKl7b8y5hPScQZJQ5y8y-J_UY1qalgVnQEFOucbBM` 하드코딩됨
- 환경변수 없이도 기본 설정으로 바로 실행 가능

### 코딩워크 스크립트 상세 설명

#### 1. paper_tracking.py - 논문 추적 시스템
**목적**: Google Sheets에서 논문 진행 상황 추적 (2단계 필터링)
- **단계 1**: `Inclusion='Y'` 논문 필터링
- **단계 2**: `Mark='M'` (내가 담당) 논문 필터링
- **기능**:
  - 각 단계별 통계 및 진행 상황 리포트 생성
  - `3rd Screening` 시트 데이터 자동 조회
  - 필터링 결과 DataFrame 반환
- **실행**: `python coding_work/scripts/paper_tracking.py`

#### 2. pdf_title_fixer.py - PDF 파일명 자동 정리
**목적**: PDF 파일명을 `{index}_{title}` 형식으로 정리
- **데이터 소스**: `3rd Screening` 시트 (189개 논문)
- **필터링**: 모든 논문 대상 (Inclusion 필터링 제거)
- **매칭 방식**: Claude AI CLI를 통한 지능적 PDF 내용 분석
  - PDF 텍스트 추출 (pdfplumber 사용)
  - Claude CLI JSON 응답 파싱
  - 3번 재시도 로직 포함
- **결과**: `26_Deep learning for engineering design.pdf` 형식
- **주의**: PDF 파일명만 정리하고 Google Sheets 업데이트는 하지 않음
- **실행**: `cd coding_work/scripts && python3 pdf_title_fixer.py`

#### 3. pdf_upload_checker.py - PDF 업로드 상태 자동 마킹 ⭐
**목적**: Papers 폴더의 PDF 파일을 스캔하여 Google Sheets의 `pdf_upload` 컬럼에 'Y' 자동 기록
- **데이터 소스**: `3rd Screening` 시트
- **매칭 방식**: 파일명 패턴 기반 Index 추출 (`{Index}_{Title}.pdf` → `{Index}`)
- **핵심 기능**:
  - Papers 폴더의 모든 PDF 자동 스캔
  - 파일명에서 Index 자동 추출 (정규식 매칭)
  - Google Sheets의 Index 컬럼과 대조
  - 매칭되는 행의 `pdf_upload` 컬럼에 'Y' 업데이트
  - 여러 컬럼명 자동 인식 (pdf_upload, PDF_Upload, PDF_uploaded 등)
- **안전 기능**:
  - `--dry-run`: 시뮬레이션만 (실제 업데이트 안 함)
  - `--test-index`: 특정 Index만 테스트 (디버깅용)
  - API 호출 제한 고려 (1초 대기)
  - 처리 결과 CSV 자동 저장
- **실행**:
  - 시뮬레이션: `python3 pdf_upload_checker.py --dry-run`
  - 특정 테스트: `python3 pdf_upload_checker.py --test-index "101" --dry-run`
  - 실제 실행: `python3 pdf_upload_checker.py`
- **결과**: `coding_work/results/pdf_upload_check_results_[timestamp].csv`

#### 4. pdf_analyzer.py - PDF 논문 자동 분류 시스템 ⭐⭐⭐
**목적**: PDF 내용을 7개 분류 기준에 따라 자동 분류 (Claude API 활용)

**핵심 기능**:
1. **자동 분류**: 54개 PDF 논문을 7개 기준으로 자동 분류
   - Design Discipline, Data About, Data Modality
   - AI methods, AI Assistance Types, Design Phase, Design Practice/Task
2. **CodeBook 연동**: Google Sheets CodeBook에서 분류 기준 동적 로드
3. **Extended Thinking**: 모든 분류에 `/ultrathink` 적용 (32K 토큰 사고 예산)
4. **Resume & Retry 시스템**: 중단된 작업 이어서 실행 또는 실패한 PDF만 재시도
5. **Index 기반 중복 방지**: 같은 PDF를 여러 번 분석해도 CSV에 1행만 유지
6. **즉시 저장**: 각 PDF 처리 후 즉시 CSV 저장 (중단 시 손실 없음)
7. **자동 백업**: progress.json 수정 시 자동 백업 생성

**데이터 흐름**:
```
Google Sheets (3rd Screening)
  → Inclusion='Y' & Assigned_to='J' 필터링 (54개)
  → PDF 파일 Index 매칭
  → PDF 전문 텍스트 추출
  → Claude API 분류 (7개 카테고리 × 54개 = 378회 호출)
  → CSV 즉시 저장 (Index 기준 Upsert)
  → progress.json 업데이트
```

**명령줄 옵션**:
```bash
# 처음 실행 (또는 일반 실행)
python3 pdf_analyzer.py

# 중단된 작업 이어서 실행 (31/54 완료 → 23개만 추가 처리)
python3 pdf_analyzer.py --resume

# 실패한 PDF만 재시도
python3 pdf_analyzer.py --retry-failed

# 진행 상태 초기화 후 새로 시작
python3 pdf_analyzer.py --reset

# 백그라운드 실행
nohup python3 pdf_analyzer.py --resume > ../logs/pdf_analyzer_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

**진행 상태 관리** (`progress.json`):
```json
{
  "last_updated": "2025-10-16T15:30:00",
  "total_target": 54,
  "processed_count": 31,
  "failed_count": 2,
  "processed": ["167_Optimizing HMI...", "108_Exploiting..."],
  "failed": {
    "172_Beyond Manual...": {
      "error": "embedded null byte",
      "timestamp": "2025-10-16T14:32:15",
      "retry_count": 1
    }
  }
}
```

**출력 CSV 구조** (Index 기준 중복 방지):
```csv
Index, Article Title, ..., Design Discipline, AI methods, ...
100, 100_Deep learning.pdf, ..., Engineering, Deep Learning, ...
101, 101_Customer requirements.pdf, ..., Product Design, Traditional ML, ...
```

**중복 방지 작동 방식**:
- **시나리오 1** (처음 처리): Index=100 → CSV에 1행 추가
- **시나리오 2** (재처리): Index=100 발견 → 기존 행 덮어쓰기 (중복 없음!)
- **시나리오 3** (새 논문): Index=101 → CSV에 1행 추가

**출력 파일**:
- `coding_work/results/pdf_analysis/pdf_classifications.csv` (분류 결과)
- `coding_work/results/pdf_analysis/pdf_reasoning.csv` (분류 근거)
- `coding_work/results/pdf_analysis/pdf_references.csv` (참고 원문)
- `coding_work/results/pdf_analysis/progress.json` (진행 상태)
- `coding_work/results/pdf_analysis/progress.json.backup` (자동 백업)

**주요 개선사항** (2025-10-16 업데이트):
- ✅ Resume 기능: 중단된 작업 이어서 실행 (처리된 PDF 건너뛰기)
- ✅ Retry 기능: 실패한 PDF만 선별적으로 재시도
- ✅ Index 기준 Upsert: 같은 PDF 재분석 시 자동 덮어쓰기 (중복 방지)
- ✅ 즉시 저장: 각 PDF 처리 후 즉시 CSV 업데이트 (중단 시 손실 없음)
- ✅ 자동 백업: progress.json 수정 전 항상 이전 상태 백업
- ✅ Null byte 에러 수정: PDF 텍스트에서 `\x00` 자동 제거

**실행**: `cd coding_work/scripts && python3 pdf_analyzer.py [--resume|--retry-failed|--reset]`

#### 5. debug_single_pdf.py - PDF 단건 디버깅
**목적**: 특정 PDF 파일 1개만 분석하여 문제 진단
- **기능**:
  - PDF 파일 단일 선택
  - 텍스트 추출 테스트
  - Claude 매칭 테스트
  - 상세 에러 로그 출력
- **실행**: `python coding_work/scripts/debug_single_pdf.py`

#### 6. analyze_sheets_structure.py - Sheets 구조 분석
**목적**: Google Sheets의 구조 및 데이터 현황 파악
- **출력**:
  - 전체 시트 목록
  - 각 시트의 컬럼 구조
  - 데이터 샘플 (첫 5행)
  - 통계 정보 (행/열 개수)
- **실행**: `python coding_work/scripts/analyze_sheets_structure.py`

#### 7. google_sheets_connector.py - Google Sheets API 연결
**역할**: 모든 스크립트의 기반 모듈
- **클래스**: `GoogleSheetsConnector`
- **주요 메서드**:
  - `connect()`: API 연결
  - `get_sheet(sheet_name)`: 특정 시트 가져오기
  - `get_paper_list()`: 논문 리스트 DataFrame 반환
  - `update_cell()`: 셀 업데이트
  - `batch_update()`: 배치 업데이트
  - `add_new_row()`: 새 행 추가
- **로깅**: `coding_work/logs/google_sheets.log`

### 활용 가능한 작업들
1. **미분류 논문 자동 분류** (375개)
2. **Abstract 기반 AI 자동 분류**
3. **점수 기반 우선순위 정리**
4. **분류 상태 업데이트 자동화**
5. **분류 결과 통계 및 리포팅**
6. **PDF 파일명 자동 정리** (Index 기반)
7. **PDF 업로드 상태 자동 마킹** (Papers 폴더 → Google Sheets 동기화) ⭐

## 📄 연구 리포트

### research_report.md - AI 방법론 진화 분석 에세이
**규모**: 19KB, 영어 학술 에세이 형식

**주요 내용**:
1. **Traditional Machine Learning 시대**:
   - 수치 입력 중심, 수동 Feature Engineering 필요
   - 전문가 의존도 높음, 제한적 응용 범위

2. **Deep Learning 혁명**:
   - End-to-End 학습, 자동 Feature 추출
   - 이미지/오디오 등 비정형 데이터 처리
   - 인간 해석 가능한 출력 (레이블, 텍스트)

3. **Generative AI & LLMs**:
   - 자연어 대화 인터페이스
   - 인간 소통 방식 그대로 사용 가능
   - 폭발적인 AI 도입 가속화

4. **디자인 분야 영향**:
   - Text-to-Image 모델 (DALL-E, Midjourney 등)
   - 디자이너 워크플로우 혁신
   - IBM/Oxford 조사: 57% "Gen AI가 가장 파괴적"

**결론**: AI는 "사람 언어"를 배워가며 접근성 향상 → 대중화 가속

**활용**: 학술 발표, 논문 Introduction, 연구 배경 설명

## 📁 기타 리소스

### checked_papers/
체크 및 검토가 완료된 논문 파일 보관 디렉토리

### ai_evolution_diagram/
AI 방법론 진화를 시각화한 다이어그램 및 차트

### Papers/
- 100개 이상의 PDF 논문 파일
- Index 기반 파일명: `{index}_{title}.pdf` 형식
- 지속적으로 추가 중

## 향후 확장 가능성
- 실시간 필터링 및 모니터링 대시보드
- 배치 처리 성능 최적화 (병렬 처리)
- 다양한 LLM 모델과의 연동 (GPT, Gemini 등)
- 분류 품질 평가 및 피드백 시스템
- 다국어 지원 및 다양한 학문 분야 확장

---

**최종 업데이트**: 2025년 10월 15일
**프로젝트 상태**: 분석 시스템 완성, 논문 분류 58.3% 진행, PDF 업로드 추적 시스템 추가
**문서 버전**: v2.1