# 작업 완료 체크리스트

## 분석 작업 완료 시

### 1. 스크립트 실행 후 확인사항
```bash
# 결과 디렉토리 확인
ls -la analysis_work/results/
ls -la analysis_work/results/{해당_분석}/

# 로그 파일 확인 (에러 체크)
tail -20 coding_work/logs/google_sheets.log
```

### 2. 결과물 검증
- **CSV 파일**: pandas로 읽어서 데이터 무결성 확인
- **HTML 대시보드**: 브라우저에서 정상 렌더링 확인
- **PNG 시각화**: 이미지 뷰어에서 품질 확인

### 3. 대시보드 동작 테스트
```bash
# 로컬 서버 실행
cd analysis_work/results
python3 -m http.server 8000 --bind 127.0.0.1

# 브라우저에서 확인
# http://127.0.0.1:8000/interactive_topic_dashboard_en.html
```

## 코딩 작업 완료 시

### 1. Google Sheets 연결 확인
```bash
cd coding_work/scripts
python test_connection.py
```

### 2. API 할당량 확인
- 요청 제한: 1초당 1회 (self.request_delay = 1.0)
- 에러 로그에서 429 에러 확인

### 3. 데이터 무결성 검증
```python
# 스프레드시트 구조 검증
connector.validate_sheet_structure(required_columns=['Article Title', 'Abstract'])
```

## 공통 완료 작업

### 1. 파일 정리
```bash
# __pycache__ 정리
find . -name "__pycache__" -type d -exec rm -rf {} +

# 임시 파일 정리
find . -name "*.pyc" -delete
find . -name ".DS_Store" -delete
```

### 2. Git 작업 (필요시)
```bash
git status
git add analysis_work/results/
git commit -m "Add analysis results: [작업 설명]"
```

### 3. 메모리 및 리소스 정리
```bash
# 백그라운드 프로세스 확인
ps aux | grep python
pkill -f "http.server"
```

## 품질 확인 체크리스트

### ✅ 스크립트 실행 성공
- [ ] 에러 없이 완료
- [ ] 모든 결과 파일 생성됨
- [ ] 로그에 성공 메시지 확인

### ✅ 결과물 품질
- [ ] CSV: 컬럼 구조 올바름
- [ ] HTML: 브라우저 렌더링 정상
- [ ] PNG: 시각화 품질 양호

### ✅ 시스템 상태
- [ ] 가상환경 활성 상태
- [ ] 의존성 라이브러리 정상
- [ ] API 할당량 여유분 존재

## 문제 해결 가이드

### 메모리 부족 시
```bash
# Python 프로세스 메모리 사용량 확인
ps aux | grep python | awk '{print $2, $4, $11}'

# 대용량 데이터 처리 시 청크 단위로 처리
```

### API 할당량 초과 시
```python
# request_delay 늘리기
self.request_delay = 2.0  # 2초로 증가
```