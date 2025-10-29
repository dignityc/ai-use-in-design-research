# PDF 논문 자동 분류 시스템 - Scripts 가이드

## 🎯 시스템 개요

이 폴더는 **PDF 논문 자동 분류 시스템**의 핵심 스크립트들을 포함하고 있습니다. Google Sheets API와 Claude API를 활용하여 논문을 체계적으로 분류하고, Systematic Literature Review를 자동화합니다.

### 주요 기능
- **PDF 전문 분석**: Papers 폴더의 PDF 파일들을 전체 텍스트 추출
- **7개 분류 기준**: Design Discipline, Data About, Data Modality, AI methods, AI Assistance Types, Design Phase, Design Practice/Task
- **PhD급 분석**: Claude API를 활용한 전문가 수준의 분류 수행
- **3개 CSV 출력**: 분류명, 분류근거, 참고원문을 각각 저장
- **Google Sheets 연동**: CodeBook과 CodedPapers 시트와 연동

### 워크플로우
```
Papers/*.pdf → PDF 분석 → Claude API (7회 호출) → 3개 CSV 파일
     ↓              ↓                    ↓              ↓
  8개 논문    전체 텍스트 추출      PhD급 분류      누적 저장
```

---

## 📚 스크립트 상세 가이드

### 🔧 **인프라 스크립트**

#### `google_sheets_connector.py` - Google Sheets API 연결
**목적**: Google Sheets와의 모든 통신을 담당하는 기반 모듈

**주요 기능**:
- 서비스 계정 인증 (`gen-lang-client-0444199460-38266703559b.json`)
- CRUD 연산 (읽기, 쓰기, 업데이트, 추가)
- 배치 업데이트 및 API 요청 제한 관리
- 로깅 시스템 (`logs/google_sheets.log`)

**사용법**:
```python
from google_sheets_connector import GoogleSheetsConnector
connector = GoogleSheetsConnector()
if connector.connect():
    data = connector.get_paper_list("CodedPapers")
```

**의존성**: `gspread`, `google.oauth2.service_account`

---

#### `analyze_sheets_structure.py` - 시트 구조 분석
**목적**: CodeBook과 CodedPapers 시트의 구조를 분석하여 분류 기준 확인

**주요 기능**:
- CodeBook 시트에서 6개 분류 기준 추출
- CodedPapers 시트에서 14개 컬럼 헤더 확인  
- 분류 관련 컬럼 7개 자동 식별
- JSON 분석 리포트 생성 (`results/sheets_structure_analysis.json`)

**실행법**:
```bash
python analyze_sheets_structure.py
```

**출력**: 
- 콘솔: 시트 구조 요약 정보
- 파일: `../results/sheets_structure_analysis.json`

---

### 🎯 **메인 분석 시스템**

#### `pdf_analyzer.py` - PDF 논문 자동 분류 시스템 ⭐
**목적**: 시스템의 핵심! Papers 폴더의 PDF들을 체계적으로 분류

**주요 기능**:
- **PDF 전체 텍스트 추출** (`pdfplumber` 사용, 제한 없음)
- **7개 분류 기준별 개별 분석**:
  1. Design Discipline (UX Design, Service Design, Product Design, Interaction Design)
  2. Data About (User behavior, preferences, emotions, Design process)
  3. Data Modality (Text, Image, Video, Audio, Sensor data, Multimodal)
  4. AI methods (ML, Deep Learning, NLP, Computer Vision, Generative AI)
  5. AI Assistance Types (Augmentation, Automation, Recommendation, Generation)
  6. Design Phase (Discovery, Define, Develop, Deliver)
  7. Design Practice/Task (User research, Prototyping, Testing, Ideation)

- **Claude API 통합**:
  - PhD급 전문가 프롬프트 (`claude -p --output-format json`)
  - 생각모드 활용으로 신중한 분석
  - 3회 재시도 + 강화된 JSON 파싱
  - 원문 그대로 인용 강제

- **3개 CSV 누적 저장**:
  - `pdf_classifications.csv`: 분류 결과만
  - `pdf_reasoning.csv`: 분류 근거만  
  - `pdf_references.csv`: 참고 원문만

**실행법**:
```bash
python pdf_analyzer.py
```

**예상 소요시간**: 8개 PDF × 7개 분류 × 평균 15초 = **약 30-45분**

**출력 위치**: `../results/pdf_analysis/`

**클래스 구조**:
```python
PDFAnalyzer
├── connect_to_sheets()      # Google Sheets 연결
├── get_pdf_files()          # PDF 파일 목록 가져오기
├── extract_pdf_text()       # 전체 PDF 텍스트 추출
├── call_claude_api()        # Claude CLI 호출 (3회 재시도)
├── classify_single_category() # 단일 분류 수행
├── analyze_single_pdf()     # PDF당 7개 분류 수행
├── save_results_to_csv()    # 3개 CSV 누적 저장
└── process_all_pdfs()       # 전체 워크플로우 실행
```

---

### 📋 **지원 도구들**

#### `paper_tracking.py` - 논문 진행 상황 추적
**목적**: Google Sheets에서 논문 처리 상황을 체계적으로 추적

**주요 기능**:
- 2단계 필터링: `Inclusion='Y'` → `Mark='M'` 
- 논문 처리 통계 및 진행 상황 리포트 생성
- 단계별 통계 분석

**사용 시트**: `"2nd Screening (rescreening needed)"`

**실행법**:
```python
from paper_tracking import PaperTracker
tracker = PaperTracker()
if tracker.connect():
    papers = tracker.get_marked_papers()
```

---

#### `pdf_title_fixer.py` - PDF 파일명 정리
**목적**: Papers 폴더의 PDF 파일명을 정확한 논문 제목으로 변경

**주요 기능**:
- PDF 텍스트 추출 (처음 3페이지)
- Claude API로 제목 매칭 수행
- 안전한 파일명 생성 (특수문자 제거, 길이 제한)
- 중복 파일명 자동 처리

**워크플로우**:
```
Papers/*.pdf → 텍스트 추출 → Claude 매칭 → 파일명 변경
```

**실행법**:
```bash
python pdf_title_fixer.py
```

**처리 과정**:
1. Mark='J' 논문 제목 리스트 가져오기
2. 각 PDF 텍스트 추출
3. Claude로 제목 매칭 (확신도 0.8 이상)
4. 안전한 파일명으로 변경

---

#### `debug_single_pdf.py` - 디버그 도구
**목적**: 단일 PDF 파일로 시스템 테스트 및 디버깅

**주요 기능**:
- 첫 번째 PDF 파일만 처리
- 상세한 디버그 출력
- 분류 결과 요약 표시
- CSV 파일 생성 테스트

**실행법**:
```bash
python debug_single_pdf.py
```

---

## 🚀 실행 가이드

### 1. **환경 설정**
```bash
# 필수 라이브러리 설치
pip install -r ../../requirements.txt

# 주요 의존성
pip install gspread google-auth pdfplumber pandas
```

### 2. **인증 설정**
- Google Sheets API 서비스 계정 키: `../credentials/gen-lang-client-0444199460-38266703559b.json`
- Claude CLI 인증 확인: `claude --help`

### 3. **실행 순서** (권장)
```bash
# 1. 구조 분석 (1회만)
python analyze_sheets_structure.py

# 2. PDF 파일명 정리 (선택사항)
python pdf_title_fixer.py

# 3. 메인 분석 실행
python pdf_analyzer.py

# 4. 결과 확인
ls -la ../results/pdf_analysis/
```

---

## 📊 출력 파일 설명

### CSV 파일 구조 (14개 컬럼)
```csv
Article Title, Author Full Names, Source Title, Publication Year, DOI Link,
Design Discipline, Data About, Data Modality, AI methods, 
AI Assistance Types (Lee and Kim, 2025), Design Phase, Design Practice/Task,
Notes, Questions
```

### 주요 출력 위치
```
coding_work/
├── results/
│   ├── pdf_analysis/           # PDF 분석 결과
│   │   ├── pdf_classifications.csv
│   │   ├── pdf_reasoning.csv
│   │   └── pdf_references.csv
│   └── sheets_structure_analysis.json
└── logs/
    └── google_sheets.log       # API 호출 로그
```

---

## 🔗 워크플로우 연결

### 데이터 흐름도
```
Google Sheets (CodeBook/CodedPapers)
         ↓
    구조 분석 ←→ PDF 분석기 ←→ Papers/*.pdf
         ↓           ↓              ↓
   분류 기준     Claude API     PDF 텍스트
         ↓           ↓              ↓
    JSON 리포트  PhD급 분석     3개 CSV
```

### 스크립트 간 의존성
```
google_sheets_connector.py (기반)
    ↓
├── analyze_sheets_structure.py (설정)
├── paper_tracking.py (추적)
├── pdf_title_fixer.py (파일명)
└── pdf_analyzer.py (메인) ← debug_single_pdf.py
```

---

## 🔧 문제해결

### 자주 발생하는 문제

1. **Google Sheets 연결 실패**
   ```
   해결: credentials 파일 경로 확인
   위치: ../credentials/gen-lang-client-0444199460-38266703559b.json
   ```

2. **Claude API 오류**
   ```bash
   # Claude CLI 상태 확인
   claude --help
   
   # 인증 재설정
   claude auth login
   ```

3. **PDF 읽기 실패**
   ```
   해결: pdfplumber 재설치
   pip install --upgrade pdfplumber
   ```

4. **JSON 파싱 오류**
   ```
   해결: 이미 3단계 대응 시스템 구현됨
   - 패턴 매칭 → 직접 파싱 → 수동 재구성
   ```

### 로그 확인
```bash
# Google Sheets API 로그
tail -f ../logs/google_sheets.log

# PDF 분석 진행 상황
python pdf_analyzer.py | tee analysis.log
```

---

## 📈 성능 최적화

### 현재 최적화 상태
- ✅ PDF 전체 텍스트 분석 (제한 없음)
- ✅ Claude API 3회 재시도 + 2-5초 대기
- ✅ 강화된 JSON 파싱 (3단계 대응)
- ✅ 누적 CSV 저장 (중복 방지)
- ✅ API 요청 제한 준수 (1초 대기)

### 예상 비용 (Claude API)
- 8개 PDF × 7개 분류 = 56회 API 호출
- 추정 비용: $3-5 (논문 길이에 따라 변동)

---

## 🎯 향후 확장 가능성

1. **다른 LLM 모델 지원** (GPT-4, Gemini 등)
2. **병렬 처리** (멀티스레딩으로 속도 향상)
3. **웹 인터페이스** (Streamlit/Flask 기반)
4. **실시간 모니터링** (분류 진행 상황 대시보드)
5. **품질 평가 시스템** (분류 일관성 검증)

---

## 📞 지원

문제가 발생하면 다음 체크리스트를 확인하세요:
1. [ ] Google Sheets API 크레덴셜 유효성
2. [ ] Claude CLI 인증 상태  
3. [ ] Papers 폴더에 PDF 파일 존재
4. [ ] 네트워크 연결 상태
5. [ ] 필수 Python 라이브러리 설치

**마지막 업데이트**: 2025-08-31
**시스템 버전**: v1.0 - PDF 자동 분류 시스템