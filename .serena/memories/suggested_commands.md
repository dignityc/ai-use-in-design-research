# 추천 명령어 모음

## 프로젝트 설정

### 가상환경 및 의존성
```bash
# 가상환경 활성화
source venv/bin/activate

# 라이브러리 설치
pip install -r requirements.txt

# spaCy 모델 다운로드
python -m spacy download en_core_web_sm
```

## 분석워크 실행 (7-13단계)

### 디렉토리 이동
```bash
cd analysis_work/scripts
```

### NLP 분석 파이프라인 (7-10단계)
```bash
python improved_nlp_analysis.py                 # 7단계: 데이터 정규화 및 인사이트
python topic_modeling_analysis.py               # 8단계: BERTopic 토픽 모델링
python create_dashboard_data.py                 # 9단계: 대시보드 데이터 생성
python create_self_contained_dashboard.py       # 10단계: 인터랙티브 대시보드 생성
```

### 시맨틱 네트워크 분석 (11-13단계)
```bash
python semantic_network_builder.py              # 11단계: Semantic Network 구축
python semantic_network_visualizer.py           # 12단계: Network 시각화  
python network_insights_analyzer.py             # 13단계: Network 인사이트 분석
```

## 코딩워크 실행

### Google Sheets 연동
```bash
cd coding_work/scripts

# 연결 테스트
python test_connection.py

# 논문 분류 작업
GOOGLE_SHEETS_CREDENTIALS_PATH="../credentials/gen-lang-client-0444199460-38266703559b.json" python paper_tracking.py
```

## 결과물 확인

### 대시보드 서버 실행
```bash
cd analysis_work/results
python3 -m http.server 8000 --bind 127.0.0.1

# 브라우저 접속: http://127.0.0.1:8000/interactive_topic_dashboard_en.html
```

### 대시보드 직접 열기 (macOS)
```bash
open analysis_work/results/interactive_topic_dashboard_en.html
open analysis_work/results/semantic_network_analysis/interactive/self_contained_english_dashboard.html
```

## 개발 명령어

### 프로젝트 구조 확인
```bash
tree -I 'venv|__pycache__|*.pyc|node_modules' -a
```

### Git 작업
```bash
git status
git add .
git commit -m "분석 워크플로우 업데이트"
```

## Node.js 관련 (Gantt 차트)
```bash
cd analysis_work/scripts
npm install
node analyze_gantt_colors.js
```

## 시스템별 명령어 (macOS)

### 파일 찾기
```bash
find . -name "*.py" -type f
find . -name "*.csv" -type f
```

### 텍스트 검색
```bash
grep -r "keyword" analysis_work/scripts/
rg "pattern" --type py
```

### 디렉토리 탐색
```bash
ls -la
ls -la analysis_work/results/