# Reference Text Verification System

PDF 분석 결과의 reference text가 실제로 원문에 존재하는지 검증하는 시스템입니다.

## 🎯 목적

PDF 분석 시 Claude가 생성한 reference text가:
- ✅ **실제로 PDF에 존재하는지** 확인
- ⚠️ **Hallucination (환각)** 감지
- 🔍 **Paraphrase (의역)** 감지
- 📄 **정확한 페이지 번호** 추적

## 🚀 빠른 시작

### 1. 단일 논문 검증
```bash
cd coding_work/scripts

# 논문 167번의 "AI methods" 카테고리만 검증
python3 verify_reference_texts.py --index "167" --category "AI methods"
```

### 2. 여러 논문 검증
```bash
# 논문 167, 108, 172번의 모든 카테고리 검증
python3 verify_reference_texts.py --index "167,108,172"
```

### 3. 전체 검증 (54개 논문 × 7개 카테고리 = 378개 작업)
```bash
# 병렬 처리 (5개 workers)
python3 verify_reference_texts.py --workers 5
```

### 4. Dry Run (실제 실행 없이 작업 목록만 확인)
```bash
python3 verify_reference_texts.py --dry-run
```

## 📋 명령줄 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--index` | 검증할 논문 Index (쉼표 구분) | `--index "167,108,172"` |
| `--category` | 단일 카테고리만 검증 | `--category "AI methods"` |
| `--workers` | 병렬 처리 워커 수 (기본: 5) | `--workers 10` |
| `--chunk-size` | 페이지 청크 크기 (기본: 2) | `--chunk-size 4` |
| `--dry-run` | 실제 실행 없이 목록만 표시 | `--dry-run` |

## 📊 검증 카테고리 (7개)

1. Design Discipline
2. Data About
3. Data Modality
4. AI methods
5. AI Assistance Types (Lee and Kim, 2025)
6. Design Phase
7. Design Practice/Task

## 🔍 작동 원리

### 2-Page Chunking 방식

```
논문 (18페이지)
├─ 청크 1 (페이지 1-2) → Claude CLI 검증 → found=False
├─ 청크 2 (페이지 3-4) → Claude CLI 검증 → found=False
├─ 청크 3 (페이지 5-6) → Claude CLI 검증 → found=True ✅ → 중단!
└─ 청크 4-9 (검사 안 함, Early Exit)
```

**장점**:
- ✅ 정확한 페이지 번호 추적
- ✅ 찾으면 즉시 중단 (시간/비용 절약)
- ✅ 토큰 제한 회피 (전체 PDF를 한 번에 넣지 않음)

### 검증 결과 타입

| Match Type | 설명 | 신뢰도 |
|------------|------|--------|
| **EXACT** | 완전 일치 | 90-100% |
| **FUZZY** | 약간의 변형 (띄어쓰기, 구두점) | 60-89% |
| **SEMANTIC** | 의미는 같지만 표현 다름 | 40-59% |
| **NONE** | 찾을 수 없음 | 0-39% |

### Issue 타입

| Issue Type | 설명 | 조치 필요 |
|------------|------|----------|
| **NONE** | 문제 없음 | ❌ 없음 |
| **PARAPHRASE** | 의역/요약된 텍스트 | ⚠️ 확인 권장 |
| **HALLUCINATION** | 원문에 없는 내용 | ✅ **반드시 수정** |
| **OCR_ERROR** | PDF 텍스트 추출 오류 | ⚠️ 수동 확인 |

## 📁 출력 파일

### 1. 검증 결과 CSV
```
coding_work/results/reference_verification_[timestamp].csv
```

**컬럼**:
- `Index`: 논문 번호
- `Article_Title`: 논문 제목
- `Category`: 검증한 카테고리
- `Found`: Y/N (찾았는지 여부)
- `Page_Numbers`: 찾은 페이지 번호
- `Match_Confidence`: 신뢰도 (0-100)
- `Verification_Method`: EXACT/FUZZY/SEMANTIC/NONE
- `Issue_Type`: NONE/PARAPHRASE/HALLUCINATION/OCR_ERROR
- `Full_Reference_Text`: 전체 reference text
- `Notes`: Claude의 상세 설명
- `Timestamp`: 검증 시각

### 2. 진행 상황 JSON
```
coding_work/results/reference_verification_progress_[timestamp].json
```

## 📈 예상 소요 시간

### 단일 논문 (7개 카테고리)
- **평균 페이지**: 15페이지
- **청크 수**: 7-8개
- **예상 시간**: 5-10분 (early exit 시 더 빠름)

### 전체 검증 (54개 논문 × 7 = 378개 작업)
- **순차 처리**: 약 30-60시간
- **병렬 처리 (5 workers)**: 약 6-12시간
- **병렬 처리 (10 workers)**: 약 3-6시간

## 💡 사용 예시

### 예시 1: 빠른 품질 체크 (3개 논문 샘플)
```bash
# 무작위로 3개 논문만 검증
python3 verify_reference_texts.py --index "167,108,172"
```

### 예시 2: 특정 카테고리만 전체 검증
```bash
# "AI methods"만 전체 54개 논문 검증
python3 verify_reference_texts.py --category "AI methods" --workers 5
```

### 예시 3: 전체 검증 (백그라운드)
```bash
# nohup으로 백그라운드 실행
nohup python3 verify_reference_texts.py --workers 10 > ../logs/verification_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# 진행 상황 확인
tail -f ../logs/verification_*.log
```

## 🔧 결과 분석

### 1. 전체 통계 확인
```python
import pandas as pd

df = pd.read_csv('coding_work/results/reference_verification_[timestamp].csv')

# 발견율
print(f"Found: {len(df[df['Found'] == 'Y'])}/{len(df)} ({len(df[df['Found'] == 'Y'])/len(df)*100:.1f}%)")

# 문제 있는 케이스
issues = df[df['Issue_Type'].isin(['HALLUCINATION', 'PARAPHRASE'])]
print(f"Issues: {len(issues)}")
```

### 2. Hallucination 찾기
```python
# Hallucination (환각) 케이스만 필터링
hallucinations = df[df['Issue_Type'] == 'HALLUCINATION']

for _, row in hallucinations.iterrows():
    print(f"Paper {row['Index']}, {row['Category']}")
    print(f"  Reference: {row['Reference_Text_Preview']}")
    print(f"  Issue: {row['Notes']}")
    print()
```

### 3. 카테고리별 정확도
```python
# 카테고리별 통계
category_stats = df.groupby('Category').agg({
    'Found': lambda x: (x == 'Y').sum(),
    'Match_Confidence': 'mean'
})
print(category_stats)
```

## ⚠️ 주의사항

1. **Claude CLI 인증 필요**: `claude setup-token` 실행 필요
2. **비용**: 378개 작업 × 약 $0.05 = **$15-20** 예상
3. **시간**: 병렬 처리해도 수 시간 소요
4. **네트워크**: 안정적인 인터넷 연결 필요

## 🐛 문제 해결

### 문제 1: "Claude CLI not found"
```bash
# Claude CLI 설치 확인
which claude

# 설치 안 되어 있으면
npm install -g @anthropic-ai/claude-cli
```

### 문제 2: "Authentication failed"
```bash
# 토큰 설정
claude setup-token
```

### 문제 3: 너무 느림
```bash
# Worker 수 늘리기
python3 verify_reference_texts.py --workers 10
```

### 문제 4: JSON parse error
- Claude CLI 버전 확인: `claude --version`
- 최신 버전으로 업데이트

## 📝 결과 해석 가이드

### ✅ 정상 케이스
```csv
Found,Match_Confidence,Verification_Method,Issue_Type
Y,95,EXACT,NONE
```
→ **조치 불필요**

### ⚠️ 주의 케이스
```csv
Found,Match_Confidence,Verification_Method,Issue_Type
Y,65,FUZZY,PARAPHRASE
```
→ **원문 확인 권장** (의역되었을 가능성)

### ❌ 문제 케이스
```csv
Found,Match_Confidence,Verification_Method,Issue_Type
N,0,NONE,HALLUCINATION
```
→ **즉시 수정 필요** (환각, 원문에 없는 내용)

## 🚀 다음 단계

1. **샘플 검증** (3-5개 논문)
   ```bash
   python3 verify_reference_texts.py --index "167,108,172" --workers 3
   ```

2. **결과 분석** → Hallucination 비율 확인

3. **전체 검증 결정**
   - Hallucination 비율 < 5% → 전체 검증 불필요
   - Hallucination 비율 > 5% → 전체 검증 권장

4. **문제 있는 논문 재분석**
   ```bash
   # pdf_analyzer.py로 문제 있는 논문 다시 분석
   ```

---

**Created**: 2025-11-07
**Author**: Auto-generated
**Version**: 1.0
