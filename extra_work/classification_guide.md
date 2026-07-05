# AI Services Classification Guide

AI 서비스 분류 작업을 위한 가이드 문서입니다.

## 분류 기준 (Categories)

| ID | Name | 설명 | 예시 |
|----|------|------|------|
| T2T | Text-to-Text | 텍스트 → 텍스트 (LLM, 챗봇) | ChatGPT, Claude |
| T2I | Text-to-Image | 텍스트 → 이미지 생성 | DALL-E, Midjourney |
| T2V | Text-to-Video | 텍스트 → 비디오 생성 | Kling, Runway |
| T2A | Text-to-Audio | 텍스트 → 오디오 (음성, 음악) | Whisper, Jukebox |
| T2C | Text-to-Code | 텍스트 → 코드 생성 | Cursor, Copilot |
| T23D | Text-to-3D | 텍스트 → 3D 모델 생성 | Dreamfusion |
| T2S | Text-to-Science | 텍스트 → 과학적 결과물 | Galactica |
| I2T | Image-to-Text | 이미지 → 텍스트 (캡셔닝, 분석) | Flamingo |
| A2T | Audio-to-Text | 오디오 → 텍스트 (STT) | Whisper |
| V2T | Video-to-Text | 비디오 → 텍스트 | - |
| MULTI | Multimodal | 여러 모달리티 지원 | Gemini, GPT-4V |
| OTHER | Other | 기타 특수 목적 | - |

---

## ⚠️ 핵심 원칙: One-by-One 이터레이션

> **중요**: 분류 작업은 반드시 **서비스 하나씩 순차적으로** 진행합니다.
> 여러 서비스를 한꺼번에 검색하고 일괄 업데이트하는 방식은 금지합니다.

### 왜 One-by-One인가?

| 일괄 처리 (❌) | One-by-One (✅) |
|---------------|-----------------|
| 빠르지만 부정확 | 느리지만 정확 |
| 세분화 판단 어려움 | 동적 세분화 가능 |
| 중간 발견 놓침 | 발견 즉시 반영 |
| 컨텍스트 손실 | 컨텍스트 유지 |

### 이터레이션 흐름

```
┌─────────────────────────────────────────────────────────┐
│  1. 서비스 하나 선택                                      │
│           ↓                                              │
│  2. 웹 검색으로 조사 (WebSearch)                          │
│           ↓                                              │
│  3. 분류 결정 + 세분화 필요 여부 판단                      │
│           ↓                                              │
│  4. JSON 즉시 업데이트 (Edit)                             │
│           ↓                                              │
│  5. 세분화 필요시 → 새 서비스 추가 후 다시 3번으로         │
│           ↓                                              │
│  6. 다음 서비스로 → 1번으로 돌아감                        │
└─────────────────────────────────────────────────────────┘
```

### 금지 사항

- ❌ 여러 서비스 병렬 검색 후 일괄 Write
- ❌ 검색 결과 모아두고 나중에 정리
- ❌ 세분화 판단 미루기

### 권장 사항

- ✅ 서비스 하나 검색 → 즉시 Edit으로 업데이트
- ✅ 검색 중 새 AI 기능 발견 → 즉시 세분화 결정
- ✅ 불확실하면 `is_classified: false`로 남기고 다음으로

---

## 분류 절차 (One-by-One)

### Step 1: 서비스 하나 선택
- 미분류(`is_classified: false`) 서비스 중 하나 선택
- 명확한 서비스부터 시작 권장

### Step 2: 웹 검색으로 조사
```
WebSearch: "[서비스명] AI features capabilities 2024"
```
1. 서비스 공식 웹사이트/문서 확인
2. 핵심 AI 기능 파악
3. 입출력 모달리티 확인
4. **세분화 필요한 하위 서비스 있는지 확인**

### Step 3: 분류 결정
- **단일 모달리티**: 해당 카테고리 ID 기입
- **복수 모달리티**: `MULTI` + `modalities` 배열에 지원 모달리티 나열
- **세분화 필요**: 하위 서비스 목록 작성

### Step 4: JSON 즉시 업데이트 (Edit 사용)
```json
{
  "is_classified": true,
  "classification": "T2T",           // 또는 "MULTI"
  "modalities": null,                // MULTI인 경우 ["T2T", "T2I", "I2T"]
  "source": "https://...",           // 참고한 URL
  "reasoning": "텍스트 입력으로 텍스트 응답 생성하는 LLM 서비스"
}
```

### Step 5: 세분화 처리 (필요시)
- 발견한 하위 서비스를 JSON에 추가
- 각 하위 서비스에 대해 Step 2부터 다시 진행

### Step 6: 다음 서비스로
- metadata의 `classified_count` 업데이트
- Step 1로 돌아가 다음 미분류 서비스 선택

---

## 서비스 세분화 규칙

플랫폼 내에 **독립적으로 분류 가능한 AI 기능**이 있으면 분리합니다.

### 세분화가 필요한 경우
- 플랫폼 내 AI 기능이 **서로 다른 모달리티**를 가질 때
- 예: Adobe → `Adobe Firefly` (T2I), `Adobe Podcast` (A2T)

### 세분화하지 않는 경우
- AI 기능이 **단일 목적**일 때
- 예: Midjourney는 T2I만 하므로 분리 불필요

### 세분화 시 처리 방법

1. **새 서비스 추가**
```json
{
  "id": [새 ID],
  "name": "[플랫폼명] - [기능명]",
  "parent_service": "[원래 플랫폼명]",
  ...
}
```

2. **원래 서비스 처리**
   - 플랫폼 자체에 AI 기능이 없으면 → 삭제 또는 `classification: null` 유지
   - 플랫폼 자체도 AI 기능이 있으면 → 별도 분류

3. **metadata 업데이트**
```json
"total_services": [새 총 개수],
"classified_count": [분류 완료 개수],
"unclassified_count": [미분류 개수]
```

---

## 분류 예시

### 예시 1: 단일 모달리티 (Midjourney)
```json
{
  "name": "Midjourney",
  "is_classified": true,
  "classification": "T2I",
  "modalities": null,
  "source": "https://midjourney.com",
  "reasoning": "텍스트 프롬프트로 이미지를 생성하는 AI 서비스"
}
```

### 예시 2: Multimodal (Gemini)
```json
{
  "name": "Gemini",
  "is_classified": true,
  "classification": "MULTI",
  "modalities": ["T2T", "T2I", "I2T", "T2C"],
  "source": "https://gemini.google.com",
  "reasoning": "텍스트 대화, 이미지 생성, 이미지 분석, 코드 생성 등 다중 모달리티 지원"
}
```

### 예시 3: 플랫폼 세분화 (Adobe)
```json
// Adobe Firefly
{
  "name": "Adobe Firefly",
  "parent_service": "Adobe",
  "is_classified": true,
  "classification": "T2I",
  "source": "https://firefly.adobe.com",
  "reasoning": "텍스트 프롬프트로 이미지 생성 및 편집"
}

// Adobe Podcast (추가 발견 시)
{
  "name": "Adobe Podcast",
  "parent_service": "Adobe",
  "is_classified": true,
  "classification": "A2T",
  "source": "https://podcast.adobe.com",
  "reasoning": "오디오 녹음을 텍스트로 변환 및 편집"
}
```

---

## 분류 우선순위

1. **명확한 서비스 먼저**: Midjourney, DALL-E 등
2. **플랫폼 서비스**: Figma, Miro, Notion 등 (조사 후 세분화 결정)
3. **Uncategorized**: 정보가 부족한 서비스

---

## 주의사항

- [ ] 분류 근거(`reasoning`)는 반드시 작성
- [ ] 출처(`source`)는 공식 문서/웹사이트 우선
- [ ] 불확실한 경우 `is_classified: false` 유지하고 `note`에 메모
- [ ] 서비스가 종료되었거나 찾을 수 없으면 `note: "서비스 종료/확인 불가"` 기록

---

# 📋 작업 이력

## 2025-12-04 전체 재분류 작업

### 작업 개요
- **방법**: One-by-One 이터레이션 (서비스별 WebSearch → 즉시 Edit)
- **기준 연도**: 2025년 최신 기능 반영
- **작업 시간**: 38개 서비스 전체 검토

### 최종 결과

| 항목 | 수치 |
|------|------|
| 총 서비스 | 38개 |
| 분류 완료 | 37개 (97.4%) |
| 미분류 | 1개 |

### 분류별 현황

| 분류 | 서비스 수 | 서비스 목록 |
|------|----------|------------|
| **MULTI** | 24개 | Gemini, Deepseek, ChatGPT, NotebookLM, Apple Intelligence, Granola, Copilot, Grok, Perplexity, Claude, Miro AI, Whimsical AI, Figma AI, Adobe Firefly, Midjourney, Canva Magic Studio, VIZcom, Kling, Notion AI, Slack AI, AI Studio, Replit AI, Cursor, Stitch, UX Pilot |
| **T2T** | 7개 | Grammarly, Craft, Confluence AI, Monday.com AI, Power Automate AI, Malirang, LLMs (General) |
| **T2C** | 2개 | Claude Code, String |
| **T2I** | 1개 | DALL-E |
| **OTHER** | 1개 | Basecamp |
| **미분류** | 1개 | CX Agents (특정 서비스 아님) |

### One-by-One 이터레이션 주요 발견

| 서비스 | 변경 전 | 변경 후 | 발견 내용 |
|--------|---------|---------|-----------|
| **Perplexity** | T2T | MULTI (5개) | 2025년 이미지/비디오 생성, 음성 입력 추가 |
| **Midjourney** | T2I | MULTI (2개) | 2025년 6월 V1 Video Model 출시 |
| **Claude** | MULTI (3개) | MULTI (5개) | 2025년 5월 Voice Mode 출시 |
| **Kling** | T2V | MULTI (3개) | 2025년 12월 O1 통합 모델 출시 |
| **Notion AI** | T2T | MULTI (3개) | 시스템 오디오 전사, 이미지 분석 추가 |
| **Cursor** | T2C | MULTI (2개) | Browser Agent 스크린샷 분석 |
| **Replit AI** | T2C | MULTI (2개) | 2025년 8월 AI 이미지 생성 추가 |
| **Stitch** | T2I | MULTI (3개) | Google Stitch (I/O 2025) 확인 |
| **UX Pilot** | T2I | MULTI (3개) | Predictive Heatmap, 코드 내보내기 |

### 미분류/정보 제한 서비스

| 서비스 | 상태 | 비고 |
|--------|------|------|
| CX Agents | 미분류 | 특정 서비스 아님, CX AI Agents 일반 카테고리 |
| Malirang | 분류됨 (T2T) | Wings 한국 기업용 AI, 상세 정보 제한적 |
| AI Studio | 분류됨 (MULTI) | Google AI Studio로 추정, Azure일 수 있음 |

### 추가된 모달리티 (분류 체계 확장)

| ID | Name | 설명 | 사용 서비스 |
|----|------|------|------------|
| I2I | Image-to-Image | 이미지 변환 (스케치→렌더링) | VIZcom, Stitch |
| I2V | Image-to-Video | 이미지→비디오 | Kling |

### 교훈 및 인사이트

1. **2025년 AI 트렌드**: 대부분의 서비스가 멀티모달로 진화 중
2. **Voice Mode 확산**: Claude, Perplexity 등 음성 기능 대폭 추가
3. **비디오 생성 대중화**: Midjourney, Perplexity도 비디오 생성 지원
4. **코딩 도구 진화**: Cursor, Replit 등 이미지 분석/생성 기능 추가
5. **One-by-One 효과**: 일괄 분류 대비 8개 이상 서비스에서 새 기능 발견

---

# 🔍 검증 절차 (Perplexity 기반)

## 개요

분류 결과의 정확성을 검증하기 위해 Perplexity API를 활용한 One-by-One 검증 시스템을 구축했습니다.

## 검증 원칙

> **중요**: 검증도 분류와 마찬가지로 **서비스 하나씩 순차적으로** 진행합니다.

### 왜 자동 검증인가?

| 수동 검증 | 자동 검증 (Perplexity) |
|----------|----------------------|
| 시간 소요 큼 | 자동화로 효율적 |
| 주관적 판단 | 일관된 기준 적용 |
| 최신 정보 놓칠 수 있음 | 실시간 웹 검색 |
| 기록 어려움 | 결과 자동 저장 |

## 검증 흐름

```
┌─────────────────────────────────────────────────────────────┐
│  1. 분류된 서비스 하나 선택                                    │
│           ↓                                                  │
│  2. Perplexity로 최신 기능 검색                               │
│           ↓                                                  │
│  3. 응답에서 모달리티 자동 추출                                │
│           ↓                                                  │
│  4. 현재 분류와 비교                                          │
│           ↓                                                  │
│  5. 결과 저장 + 플래그 표시                                    │
│     ✅ match: 일치                                           │
│     ⚠️ partial: 부분 일치                                    │
│     ❌ mismatch: 불일치                                      │
│     🔄 needs_upgrade: MULTI로 업그레이드 필요                  │
│           ↓                                                  │
│  6. 다음 서비스로 → 1번으로 돌아감                             │
└─────────────────────────────────────────────────────────────┘
```

## 파일 구조

```
extra_work/
├── perplexity_search.py        # Perplexity 검색 모듈
├── verify_classification.py    # 검증 스크립트
├── verification_progress.json  # 진행 상황 (중간 저장)
└── verification_results.json   # 최종 검증 결과
```

## 실행 방법

### 1. 환경 설정

```bash
# Perplexity API 키 설정
export PERPLEXITY_API_KEY='your-api-key'

# 가상환경 활성화 (필요시)
source venv/bin/activate
```

### 2. 검증 실행

```bash
cd extra_work

# 전체 검증 (38개 서비스)
python verify_classification.py

# 처음 5개만 테스트
python verify_classification.py --limit 5

# 10번 인덱스부터 시작
python verify_classification.py --start 10

# 딜레이 2초로 설정 (rate limiting)
python verify_classification.py --delay 2.0

# 진행 상황 초기화 후 재시작
python verify_classification.py --reset
```

### 3. 결과 확인

검증 완료 후 `verification_results.json`에서 결과 확인:

```json
{
  "verification_date": "2025-12-04T...",
  "total_verified": 38,
  "results": [
    {
      "id": 1,
      "name": "Gemini",
      "status": "verified",
      "comparison": {
        "match_status": "match",
        "note": "검출된 모달리티가 현재 분류에 포함됨"
      }
    }
  ]
}
```

## 검증 결과 해석

| 상태 | 의미 | 조치 |
|------|------|------|
| ✅ match | 분류 정확 | 유지 |
| ⚠️ partial | 일부 불일치 | 수동 검토 권장 |
| ❌ mismatch | 완전 불일치 | 재분류 필요 |
| 🔄 needs_upgrade | MULTI 업그레이드 필요 | 모달리티 추가 |
| ❓ no_detection | 검출 실패 | 수동 확인 필요 |

## 비용 및 주의사항

- **API 호출**: 38개 서비스 × 1 쿼리 = 약 38 API 호출
- **Rate Limiting**: 기본 1초 딜레이 설정 (--delay로 조정)
- **중간 저장**: `verification_progress.json`에 자동 저장 → 중단 시 이어하기 가능
- **모달리티 검출**: 휴리스틱 기반이므로 100% 정확하지 않음 → 수동 검토 권장

---

*마지막 업데이트: 2025-12-04*
