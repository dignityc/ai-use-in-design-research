# Paper Review with LLM - Project Documentation

## 프로젝트 개요
논문 리뷰 자동화를 위한 Python 스크립트 모음입니다. 단계별 필터링을 통해 특정 조건에 맞는 논문들을 추출하는 체계적인 워크플로우를 제공합니다.

## 파일 구조
```
paper_review_with_llm/
├── input/                          # 입력 데이터
│   ├── PaperList.csv              # 원본 논문 리스트 (511개)
│   ├── Result.csv                 # 이미 분석된 논문들 (34개, 실제 33개)
│   └── CodeBook.csv               # 코딩 기준서
├── output/                         # 출력 결과
│   ├── step1_filtered_inclusion_y.csv        # 1단계: Inclusion Y (192개)
│   ├── step2_final_filtered_list.csv         # 2단계: Result 중복 제거 (159개)
│   ├── step3_service_ui_design_papers.csv    # 3단계: 서비스/UI 디자인 (112개)
│   ├── step3_service_ui_design_papers_improved.csv  # 3단계 개선: 정밀 필터링 (53개)
│   ├── step4_category_only_papers.csv        # 4단계: 카테고리 기반만 (31개)
│   ├── classified_papers.csv                 # 5단계: AI 자동 분류 결과
│   ├── dashboard_data.json                   # 9단계: 대시보드용 JSON 데이터 (85KB)
│   ├── interactive_topic_dashboard_en.html   # 10단계: 영어 인터랙티브 대시보드 (38KB)
│   ├── nlp_analysis_improved/                # 7단계: 데이터 정규화 및 갭 분석 결과
│   │   ├── data/normalized_data.csv
│   │   ├── visualizations/ai_evolution_story.png
│   │   └── reports/final_insights.md
│   └── topic_modeling_analysis/              # 8단계: 토픽 모델링 분석 결과
│       ├── data/papers_with_topics.csv      # 토픽 배정된 74개 논문 데이터
│       ├── data/topic_info.csv              # BERTopic 토픽 정보
│       ├── data/topic_labels.json           # 의미있는 토픽 라벨
│       ├── visualizations/topic_trends_timeline.png
│       └── topic_analysis_report.md         # 토픽 분석 종합 리포트
├── scripts/                        # Python 스크립트
│   ├── filter_inclusion_y.py      # 1단계: Inclusion Y 필터링
│   ├── filter_missing_from_result.py  # 2단계: Result에 없는 논문 필터링
│   ├── filter_service_ui_design.py    # 3단계: 서비스/UI 디자인 논문 필터링
│   ├── filter_service_ui_design_improved.py  # 3단계 개선: 정밀 키워드 필터링
│   ├── filter_category_only.py    # 4단계: 카테고리 기반만 필터링
│   ├── paper_classifier.py        # 5단계: AI 기반 자동 분류 시스템
│   ├── add_abstracts_to_result2.py     # 6단계: Abstract 추가 시스템
│   ├── improved_nlp_analysis.py   # 7단계: 데이터 정규화 및 인사이트 분석
│   ├── topic_modeling_analysis.py # 8단계: BERTopic 토픽 모델링 분석
│   └── create_dashboard_data.py   # 9단계: 인터랙티브 대시보드 데이터 생성
├── Papers/                         # 논문 파일들
├── venv/                          # Python 가상환경
└── CLAUDE.md                      # 이 문서
```

## 데이터 처리 워크플로우

### 1단계: Inclusion Y 필터링
**파일**: `scripts/filter_inclusion_y.py`
- **입력**: input/PaperList.csv (511개 논문)
- **필터링 조건**: "Inclusion (Y/N/Q/R) for 2nd screening" 컬럼이 'Y'
- **출력**: output/step1_filtered_inclusion_y.csv (192개 논문)
- **실행**: `python scripts/filter_inclusion_y.py`

### 2단계: Result.csv 중복 제거
**파일**: `scripts/filter_missing_from_result.py`
- **입력**: output/step1_filtered_inclusion_y.csv (192개)
- **필터링 조건**: input/Result.csv에 없는 논문들만 선택
- **출력**: output/step2_final_filtered_list.csv (159개 논문)
- **검증**: Result.csv의 33개 논문이 모두 필터링된 리스트에 포함되어 있음 확인
- **실행**: `python scripts/filter_missing_from_result.py`

### 3단계: 서비스/UI 디자인 논문 추출
**파일**: `scripts/filter_service_ui_design.py`
- **입력**: output/step2_final_filtered_list.csv (159개)
- **필터링 조건**: 
  - 카테고리 기반: SERVICE, UI.UX, UI/UX, UI.UX, SERVICE
  - 키워드 기반: user interface, UX, service design, HCI 등
- **출력**: output/step3_service_ui_design_papers.csv (112개 논문)
- **실행**: `python scripts/filter_service_ui_design.py`

### 3단계 개선: 정밀 필터링
**파일**: `scripts/filter_service_ui_design_improved.py`
- **개선점**: 정규식을 활용한 정확한 단어 매칭, 엄격한 키워드 조건
- **출력**: output/step3_service_ui_design_papers_improved.csv (53개 논문)

### 4단계: 카테고리 기반만 필터링
**파일**: `scripts/filter_category_only.py`
- **입력**: output/step2_final_filtered_list.csv (159개)
- **필터링 조건**: 카테고리 컬럼에서 SERVICE, UI.UX, UI/UX, UI.UX, SERVICE만
- **출력**: output/step4_category_only_papers.csv (31개 논문)
- **실행**: `python scripts/filter_category_only.py`

### 5단계: AI 기반 자동 분류 시스템 ⭐ 신규 추가
**파일**: `scripts/paper_classifier.py`
- **입력**: output/step4_category_only_papers.csv (31개 논문의 Abstract)
- **처리 방식**: Claude CLI를 통한 배치 자동 분류
- **분류 기준**: input/CodeBook.csv의 카테고리 체계
- **출력**: output/classified_papers.csv (Result.csv와 동일 구조)
- **실행**: `python scripts/paper_classifier.py`

#### 분류 카테고리:
1. **Design Discipline**: Industrial/Engineering, Service/System/Business, UI/UX, Multiple (구성 요소 명시)
2. **Data About**: Perception, Physiological, Behavioral-based, Product-based, Generated, Demographic, Environmental
3. **Data Modality**: Text, Image, Audio, Video, Time Series, Multimodal (구성 요소 명시)
4. **AI methods**: Traditional ML, Deep models, Gen AI, Reinforcement learning, Exploratory data analysis (구체적 모델명 포함)
5. **AI Assistance Types**: Design generation, Prediction, Decision making, Coordination, Multiple (구성 요소 명시), Sense making
6. **Design Practice/Task**: Discovery, Define, Develop, Delivery

#### 핵심 특징:
- **Abstract 기반 분류**: PDF 대신 구조화된 Abstract 데이터 활용
- **Claude CLI 통합**: subprocess를 통한 Claude CLI 호출
- **배치 처리**: 31개 논문 자동 순차 처리
- **구체적 명시**: Multiple/Multimodal의 경우 구성 요소를 괄호 안에 명시
- **핵심 인용문 추출**: Abstract에서 중요 구문을 Notes로 추출

## 데이터 검증 결과

### 전체 진행 상황
```
input/PaperList.csv (511개)
    ↓ Inclusion Y 필터링
output/step1_filtered_inclusion_y.csv (192개)
    ↓ Result.csv 중복 제거
output/step2_final_filtered_list.csv (159개)
    ↓ 서비스/UI 디자인 필터링
├── step3_service_ui_design_papers.csv (112개)     # 포괄적 필터링
├── step3_service_ui_design_papers_improved.csv (53개)  # 정밀 필터링
└── step4_category_only_papers.csv (31개)          # 카테고리만
    ↓ AI 자동 분류
output/classified_papers.csv                        # CodeBook 기준 분류 결과
```

### 카테고리별 분포 (step4 최종 결과)
- UI.UX: 24개
- SERVICE: 4개
- UI/UX: 2개
- UI.UX, SERVICE: 1개

## 사용된 기술

### Python 라이브러리
- **pandas**: CSV 파일 처리 및 데이터 조작
- **re**: 정규식을 활용한 정밀 텍스트 매칭 및 JSON 파싱
- **subprocess**: Claude CLI 호출 및 외부 프로세스 실행
- **json**: Claude 응답의 JSON 구조 파싱
- **set operations**: 중복 제거 및 교집합/차집합 연산

### 필터링 전략
1. **정확한 매칭**: 카테고리 컬럼의 값을 정확히 매칭
2. **키워드 검색**: 제목, 초록, 노트에서 관련 키워드 탐지
3. **정규식 활용**: 단어 경계(\b)를 활용한 정확한 단어 매칭
4. **다층 검증**: 카테고리와 키워드 기반 결과를 결합하여 포괄적 추출
5. **AI 기반 분류**: Claude CLI를 통한 CodeBook 기준 자동 분류
6. **구체적 명시**: Multiple/Multimodal 카테고리의 구성 요소 상세 기술

## 실행 순서
```bash
# 가상환경 활성화
source venv/bin/activate

# 1단계: Inclusion Y 필터링
python scripts/filter_inclusion_y.py

# 2단계: Result.csv 중복 제거  
python scripts/filter_missing_from_result.py

# 3단계: 서비스/UI 디자인 논문 추출 (선택)
python scripts/filter_service_ui_design.py          # 포괄적
python scripts/filter_service_ui_design_improved.py # 정밀
python scripts/filter_category_only.py              # 카테고리만

# 4단계: AI 기반 자동 분류 (신규)
python scripts/paper_classifier.py                  # Claude CLI 활용
```

## 주요 특징

### 데이터 무결성 보장
- Result.csv의 모든 유효한 논문(33개)이 필터링된 리스트에 포함되어 있음을 검증
- NaN 값 처리를 통한 데이터 품질 관리

### 체계적 프로젝트 구조
- **input/**: 입력 데이터 분리로 원본 보호
- **output/**: 단계별 결과 파일 체계적 명명
- **scripts/**: 실행 스크립트 독립적 관리

### 다양한 필터링 옵션
- **포괄적(112개)**: 키워드 기반 확장으로 누락 최소화
- **정밀(53개)**: 정규식 활용으로 정확성 향상
- **카테고리만(31개)**: 가장 신뢰할 수 있는 명시적 분류
- **AI 자동 분류**: Claude CLI를 통한 CodeBook 기준 체계적 분류

### 재현 가능한 워크플로우
- 각 단계별 독립적인 스크립트로 구성
- 중간 결과 파일 저장으로 단계별 검증 가능
- 명확한 입력/출력 경로로 추적 용이

## 향후 확장 가능성
- 다른 논문 카테고리별 필터링 스크립트 추가
- ~~자동화된 키워드 추출 및 분류 시스템~~ ✅ **완료** (Claude CLI 기반)
- ~~논문 내용 분석을 위한 NLP 파이프라인 구축~~ ✅ **완료** (BERTopic 기반)
- 실시간 필터링 및 모니터링 대시보드
- 배치 처리 성능 최적화 (병렬 처리)
- 다양한 LLM 모델과의 연동 (GPT, Gemini 등)
- 분류 품질 평가 및 피드백 시스템

---

## ⭐ 신규 추가: Abstract 기반 인사이트 도출 시스템

### 6단계: Abstract에 추가
**파일**: `scripts/add_abstracts_to_result2.py`
- **목적**: Result_2.csv에 Abstract 컬럼 추가
- **입력**: input/Result_2.csv (Abstract 없음), input/PaperList.csv (Abstract 있음)
- **처리**: Article Title 기준 1:1 매칭
- **출력**: 완전한 메타데이터를 포함한 Result_2.csv (93편)
- **성공률**: 100% (93/93개 논문 매칭 완료)

### 7단계: 데이터 정규화 및 인사이트 분석 ⭐ 최신 추가
**파일**: `scripts/improved_nlp_analysis.py`
- **입력**: input/Result_2.csv (93개 논문 + Abstract)
- **핵심 기능**:
  1. **데이터 정규화**: AI Methods와 Design Tasks를 4-5개 메인 카테고리로 체계화
  2. **AI 방법론 진화 분석**: 2020-2025년 방법론 변화 트렌드
  3. **연구 갭 분석**: Method × Task 조합에서 빈 영역 식별
  4. **구체적 연구 아이디어 제안**: 빈 영역을 실행 가능한 연구 주제로 변환

**주요 발견점**:
- **Deep Learning**: 50% → 21.1% (28.9%p 급감)
- **Generative AI**: 0% → 23.7% (23.7%p 급증) - 2023년 전환점
- **Traditional ML**: 여전히 주류 (51편/93편)

### 8단계: 토픽 모델링 중심 분석 ⭐ 최신 추가
**파일**: `scripts/topic_modeling_analysis.py`
- **입력**: 정규화된 데이터 (93편 Abstract)
- **핵심 기능**:
  1. **BERTopic 토픽 모델링**: 도메인 정보 보존하며 9개 주요 토픽 발견
  2. **연도별 토픽 트렌드**: 연구자들의 관심 변화 추적
  3. **토픽 × AI Methods 관계**: 토픽별 주요 AI 기법 분석
  4. **토픽 × Design Practice 관계**: 토픽별 주요 디자인 단계 분석

**발견된 주요 토픽**:
1. **Interaction + User + Technology** (18편) - Gen AI 중심
2. **Design + Case + Research** (10편) - Traditional ML 중심  
3. **Emotion + Emotional + Recognition** (9편) - Deep Learning 중심
4. **Product + Customer + Review** (9편) - Traditional ML, Define 단계 중심

**핵심 인사이트**:
- 모든 주요 토픽이 2022-2024년 급성장
- "Interaction + User + Technology"가 압도적 관심사
- Gen AI는 주로 인터랙션 토픽에서 활용
- 감정 인식은 딥러닝 전용 영역

---

## 🚀 최신 추가: 인터랙티브 대시보드 시스템 ⭐ 완전 신규

### 9단계: 대시보드 데이터 준비 시스템
**파일**: `scripts/create_dashboard_data.py`
- **목적**: 토픽 분석 결과를 인터랙티브 웹 대시보드용 JSON 데이터로 변환
- **핵심 기능**:
  1. **다차원 데이터 정규화**: Data Modality, Design Practice 체계적 정리
  2. **4차원 시계열 트렌드**: Topics, AI Methods, Data Modality, Design Practice
  3. **3차원 관계 매트릭스**: Topics×AI Methods, Topics×Design Practice, AI Methods×Design Practice
  4. **논문 상세 정보**: 74개 논문의 완전한 메타데이터 + Abstract

**데이터 정규화 성과**:
- **Data Modality**: 22개 → 5개 카테고리 (78% 간소화)
  - Text: 32편, Image: 19편, Time Series: 12편, Multimodal: 11편, Audio: 8편
  - 멀티모달 조합 분해 (예: Text+Audio → Text+1, Audio+1)
- **Design Practice**: 6개 → 4개 카테고리 (Others 완전 제거)
  - Develop: 58편, Define: 13편, Discovery: 2편, Delivery: 1편

### 10단계: 인터랙티브 웹 대시보드 구축 ⭐ 완전 신규
**파일**: `output/interactive_topic_dashboard_en.html` (영어 버전)
- **기술 스택**: HTML5, Bootstrap 5, Plotly.js, JavaScript ES6
- **핵심 특징**: 단일 HTML 파일 (38KB), 외부 의존성 최소화

**주요 기능**:
1. **토픽 개요**: 인터랙티브 파이 차트 + 토픽별 키워드 정보
2. **다차원 시계열 트렌드**: 4개 탭 전환 (Topics, AI Methods, Data Modality, Design Practice)
3. **3차원 관계 분석**: 
   - Topics × AI Methods 히트맵
   - Topics × Design Practice 히트맵  
   - AI Methods × Design Practice 히트맵 ⭐ 신규
4. **논문 검색 시스템**: 실시간 검색, 다중 필터, 페이지네이션 (10개씩)
5. **상호작용 인사이트**: 각 섹션별 맞춤형 해석 가이드

**사용자 경험**:
- **완전 반응형**: 모바일/태블릿/데스크톱 최적화
- **실시간 상호작용**: 토픽 클릭시 모든 관련 정보 동기화
- **검색 하이라이트**: 키워드 강조 표시
- **직관적 네비게이션**: 섹션 간 부드러운 스크롤

**새로운 인사이트 발견**:
- **AI Methods × Design Practice**: Traditional ML이 Develop 집중 (33편), Gen AI는 균형 분포
- **2023년 Gen AI 전환점**: 2022년 1편 → 2024년 9편으로 급성장
- **Text 데이터 압도적 우세**: 전체 논문의 43.2% (32편)
- **Develop 단계 집중**: 전체 논문의 78.4% (58편)

### 🌐 접속 정보
```bash
# 로컬 서버 실행
cd output && python3 -m http.server 8000 --bind 127.0.0.1

# 브라우저 접속
http://127.0.0.1:8000/interactive_topic_dashboard_en.html
```

## 🛠 고급 NLP 기술 스택

### 사용된 라이브러리
- **BERTopic**: Transformer 기반 토픽 모델링
- **sentence-transformers**: Abstract 임베딩 생성 (all-MiniLM-L6-v2)
- **spaCy**: 텍스트 전처리 및 표제어 추출
- **KeyBERT**: 키워드 추출 (미래 확장용)
- **scikit-learn**: 전통적 ML 분석
- **matplotlib/seaborn**: 정적 시각화
- **plotly**: 인터랙티브 시각화 (필요시)

### 데이터 처리 전략
1. **도메인 정보 보존**: design, method, approach 등 연구 핵심 용어 유지
2. **의미있는 토큰 보존**: AI, UI 같은 2-3글자 중요 용어 보존
3. **체계적 정규화**: 50+ 세분화 카테고리를 4-5개 메인 그룹으로 통합
4. **다층 관계 분석**: 시간축, AI 기법, 디자인 단계 3차원 교차 분석

## 📊 최종 출력 구조
```
output/
├── nlp_analysis_improved/           # 데이터 정규화 및 갭 분석
│   ├── data/
│   │   ├── normalized_data.csv      # 정규화된 마스터 데이터
│   │   └── research_gaps.csv        # 연구 갭 분석 결과
│   ├── visualizations/
│   │   ├── ai_evolution_story.png   # AI 방법론 5년 변화
│   │   └── research_gap_matrix.png  # Method × Task 갭 매트릭스
│   └── reports/
│       └── final_insights.md        # 종합 인사이트 리포트
├── topic_modeling_analysis/         # 토픽 모델링 중심 분석
│   ├── data/
│   │   ├── papers_with_topics.csv   # 토픽 배정된 논문 데이터
│   │   ├── topic_info.csv           # BERTopic 토픽 정보
│   │   └── topic_labels.json        # 의미있는 토픽 라벨
│   ├── visualizations/
│   │   ├── topic_trends_timeline.png      # 연도별 토픽 변화
│   │   ├── topic_ai_methods_matrix.png    # 토픽 × AI Method
│   │   └── topic_design_practice_matrix.png # 토픽 × Design Practice  
│   └── topic_analysis_report.md     # 토픽 분석 종합 리포트
└── [기존 단계별 결과 파일들...]
```

## 🚀 최신 실행 순서 (전체 10단계)
```bash
# 가상환경 활성화
source venv/bin/activate

# 1-5단계: 기존 논문 필터링 및 분류 시스템
python scripts/filter_inclusion_y.py                    # 1단계: Inclusion Y 필터링
python scripts/filter_missing_from_result.py            # 2단계: Result 중복 제거
python scripts/filter_service_ui_design.py              # 3단계: 서비스/UI 디자인 (선택)
python scripts/filter_category_only.py                  # 4단계: 카테고리 기반
python scripts/paper_classifier.py                      # 5단계: AI 자동 분류

# 6-8단계: NLP 분석 시스템
python scripts/add_abstracts_to_result2.py              # 6단계: Abstract 추가
python scripts/improved_nlp_analysis.py                 # 7단계: 데이터 정규화 및 인사이트
python scripts/topic_modeling_analysis.py               # 8단계: BERTopic 토픽 모델링

# 9-10단계: 인터랙티브 대시보드 시스템 ⭐ 신규
python scripts/create_dashboard_data.py                 # 9단계: 대시보드 데이터 생성
cd output && python3 -m http.server 8000 --bind 127.0.0.1  # 10단계: 웹 서버 실행

# 브라우저에서 대시보드 접속
# http://127.0.0.1:8000/interactive_topic_dashboard_en.html

# [필요시] 라이브러리 설치
pip install bertopic sentence-transformers spacy matplotlib seaborn plotly pandas
python -m spacy download en_core_web_sm
```

## 🎯 달성된 주요 성과
1. **완전한 메타데이터**: 93편 논문에 Abstract 추가 완료 → 74편 유효 토픽 분류
2. **체계적 데이터 정규화**: 
   - Data Modality: 22개 → 5개 카테고리 (78% 간소화)
   - Design Practice: 6개 → 4개 카테고리 (Others 완전 제거)
3. **핵심 인사이트 발견**: 
   - "2023년 Gen AI 전환점": 2022년 1편 → 2024년 9편 급성장
   - "Develop 단계 압도적 집중": 전체 논문의 78.4% (58편)
   - "Text 데이터 주류": 전체 논문의 43.2% (32편)
4. **9개 주요 토픽 발견**: BERTopic으로 연구 생태계 체계화
   - "Interaction + User + Technology" (18편) - 최대 토픽
5. **3차원 관계 분석**: Topics×AI Methods×Design Practice 교차 분석 완성
6. **인터랙티브 웹 대시보드**: 단일 HTML 파일(38KB)로 모든 분석 결과 탐색 가능
7. **국제 공유 가능**: 영어 기반 학술 발표용 대시보드 완성

**결과**: 단순 논문 필터링에서 **연구 생태계 전체를 탐색할 수 있는 완전한 인터랙티브 분석 시스템**으로 진화 완료! 🚀