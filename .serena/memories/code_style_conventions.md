# 코드 스타일 및 컨벤션

## 전반적 스타일

### 네이밍 컨벤션
- **클래스명**: PascalCase (예: `GoogleSheetsConnector`, `ImprovedNLPWorkflow`)
- **메소드/함수명**: snake_case (예: `get_paper_list`, `run_improved_analysis`)
- **변수명**: snake_case (예: `credentials_path`, `spreadsheet_id`)
- **상수명**: UPPER_CASE (예: `SPREADSHEET_ID`)

### 문서화 스타일
- **Docstring**: Google 스타일의 한국어 docstring 사용
```python
def connect(self) -> bool:
    """
    Google Sheets API에 연결
    
    Returns:
        bool: 연결 성공 여부
    """
```

### 타입 힌트
- **메소드 시그니처**: 타입 힌트 적극 사용
- **리턴 타입**: 명시적 반환 타입 지정
- **파라미터**: typing 모듈 활용 (List, Dict, Any 등)

## 클래스 설계 패턴

### 초기화 패턴
```python
def __init__(self, credentials_path: str = None, spreadsheet_id: str = None):
    # 기본값 설정 (환경변수 → 하드코딩된 기본값 순)
    default_credentials_path = str(Path(__file__).parent.parent / 'credentials' / '...')
    self.credentials_path = credentials_path or os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH') or default_credentials_path
```

### 로깅 패턴
- **로거 설정**: 각 클래스마다 전용 로거 생성
- **로그 레벨**: INFO 레벨로 주요 작업 추적
- **파일 + 콘솔**: 이중 출력 핸들러 사용

### 에러 처리 패턴
```python
try:
    # 주요 로직
    self.logger.info("작업 완료 메시지")
    return True
except Exception as e:
    self.logger.error(f"작업 실패: {str(e)}")
    return False
```

## 파일 구조 컨벤션

### 디렉토리 구조
- **scripts/**: 실행 가능한 Python 스크립트
- **results/**: 분석 결과물 저장
- **data/**: 중간 처리 데이터
- **visualizations/**: 시각화 결과물
- **reports/**: 텍스트 기반 리포트

### 파일 명명
- **분석 스크립트**: `{단계명}_analysis.py` (예: `improved_nlp_analysis.py`)
- **결과 파일**: `{분석명}_{결과타입}.{확장자}` (예: `topic_trends_timeline.png`)
- **설정 파일**: 루트에 `requirements.txt`, `CLAUDE.md` 배치

## 다국어 사용 패턴
- **변수명/함수명**: 영어 사용
- **Docstring/주석**: 한국어 사용  
- **로그 메시지**: 한국어 사용
- **결과물 파일명**: 영어 사용 (국제 공유 고려)