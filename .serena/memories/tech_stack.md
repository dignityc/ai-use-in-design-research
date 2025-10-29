# 기술 스택 및 의존성

## 핵심 Python 라이브러리

### NLP & ML 분석
- **BERTopic (0.15.0)**: Transformer 기반 토픽 모델링
- **sentence-transformers (2.2.2)**: Abstract 임베딩 생성 (all-MiniLM-L6-v2)
- **KeyBERT (0.8.3)**: 키워드 추출
- **spaCy (≥3.4.0)**: 텍스트 전처리 및 표제어 추출
- **scikit-learn (≥1.0.0)**: 전통적 ML 분석
- **umap-learn (≥0.5.3)**: 차원 축소
- **hdbscan (≥0.8.29)**: 클러스터링

### 시각화 & 네트워크
- **plotly (≥5.11.0)**: 인터랙티브 시각화 (대시보드 메인)
- **matplotlib (≥3.5.0)**: 정적 시각화
- **seaborn (≥0.11.0)**: 통계 시각화
- **networkx (≥2.8.0)**: 네트워크 분석 및 시각화

### 데이터 처리
- **pandas (≥1.4.0)**: 데이터프레임 조작
- **numpy (≥1.21.0)**: 수치 연산

### Google Sheets 연동
- **gspread (≥5.7.0)**: Python Google Sheets 클라이언트
- **google-auth (≥2.16.0)**: 서비스 계정 인증
- **google-auth-oauthlib (≥0.8.0)**: OAuth 인증
- **google-auth-httplib2 (≥0.1.0)**: HTTP 클라이언트

### 고급 기능 (선택적)
- **transformers (≥4.21.0)**: 고급 토픽 모델링용
- **torch (≥1.12.0)**: 딥러닝 백엔드

## 웹 기술 스택
- **HTML5 + Bootstrap 5**: 대시보드 UI
- **Plotly.js**: 클라이언트사이드 시각화
- **JavaScript ES6**: 인터랙티브 기능
- **Cytoscape.js**: 네트워크 시각화

## 시스템 요구사항
- **Python 3.8+**: 메인 런타임
- **spaCy 모델**: en_core_web_sm (영어 NLP)
- **Node.js**: Gantt 차트 분석용 (선택적)