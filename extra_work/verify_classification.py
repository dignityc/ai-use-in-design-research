"""
AI 서비스 분류 결과 검증 스크립트

Perplexity API를 이용하여 One-by-One으로 분류 결과를 검증합니다.
OpenAI GPT-4를 이용하여 Perplexity 응답에서 모달리티를 추출합니다.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from openai import OpenAI

# 같은 디렉토리의 perplexity_search 모듈 임포트
from perplexity_search import perplexity_search, extract_answer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 파일 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFICATION_FILE = os.path.join(SCRIPT_DIR, "ai_services_classification.json")
PROGRESS_FILE = os.path.join(SCRIPT_DIR, "verification_progress.json")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "verification_results.json")


def load_classification_data() -> Dict[str, Any]:
    """분류 JSON 파일 로드"""
    with open(CLASSIFICATION_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_progress(progress: Dict[str, Any]):
    """진행 상황 저장 (중간 저장용)"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def load_progress() -> Optional[Dict[str, Any]]:
    """이전 진행 상황 로드"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_results(results: List[Dict[str, Any]]):
    """최종 검증 결과 저장"""
    output = {
        "verification_date": datetime.now().isoformat(),
        "total_verified": len(results),
        "results": results
    }
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    logger.info(f"검증 결과 저장됨: {RESULTS_FILE}")


def build_verification_query(service: Dict[str, Any]) -> str:
    """서비스 검증용 쿼리 생성"""
    name = service.get('name', 'Unknown')

    # 검증 쿼리: 서비스의 최신 AI 기능과 입출력 모달리티 확인
    query = f"{name} AI service features input output modalities capabilities December 2025"

    return query


def parse_modalities_with_gpt(response_text: str, service_name: str) -> Dict[str, Any]:
    """
    OpenAI GPT-4를 이용하여 Perplexity 응답에서 모달리티 정보 추출

    Args:
        response_text: Perplexity 검색 결과 텍스트
        service_name: AI 서비스 이름

    Returns:
        Dict with detected_modalities, evidence, is_multimodal
    """
    client = OpenAI()

    # 모달리티 분류 기준 설명
    modality_guide = """
모달리티 분류 기준:
- T2T (Text-to-Text): 텍스트 입력 → 텍스트 출력 (챗봇, LLM 대화, 글쓰기 등)
- T2I (Text-to-Image): 텍스트 입력 → 이미지 생성
- I2T (Image-to-Text): 이미지 입력 → 텍스트 출력 (이미지 분석, OCR, 비전)
- T2V (Text-to-Video): 텍스트 입력 → 비디오 생성
- V2T (Video-to-Text): 비디오 입력 → 텍스트 출력 (비디오 분석)
- T2A (Text-to-Audio): 텍스트 입력 → 음성/오디오 생성 (TTS)
- A2T (Audio-to-Text): 음성 입력 → 텍스트 출력 (STT, 음성 인식)
- T2C (Text-to-Code): 텍스트 입력 → 코드 생성
- T23D (Text-to-3D): 텍스트 입력 → 3D 모델 생성
- I2I (Image-to-Image): 이미지 입력 → 이미지 출력 (스타일 변환, 편집)
- I2V (Image-to-Video): 이미지 입력 → 비디오 생성
"""

    prompt = f"""다음은 "{service_name}" AI 서비스에 대한 최신 정보입니다.
이 정보를 바탕으로 서비스가 지원하는 입출력 모달리티를 분석해주세요.

{modality_guide}

=== 서비스 정보 ===
{response_text[:3000]}
==================

위 정보를 바탕으로 "{service_name}"이 지원하는 모달리티를 JSON 형식으로 출력하세요.
반드시 아래 형식을 따라주세요:

```json
{{
  "detected_modalities": ["T2T", "I2T", ...],
  "evidence": [
    "T2T: 텍스트 대화 기능 지원",
    "I2T: 이미지 분석 기능 지원"
  ],
  "confidence": "high/medium/low"
}}
```

주의:
1. 정보에 명시적으로 언급된 기능만 포함
2. 추측하지 말 것
3. evidence에는 각 모달리티의 근거를 명시
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI service analyst. Extract input/output modalities from the given information. Be precise and only include explicitly mentioned capabilities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        # JSON 추출
        import re
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', answer, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
            detected = result.get('detected_modalities', [])
            return {
                'detected_modalities': detected,
                'evidence': result.get('evidence', []),
                'confidence': result.get('confidence', 'medium'),
                'is_multimodal': len(detected) > 1
            }

        # JSON 블록 없이 직접 파싱 시도
        brace_match = re.search(r'\{[^{}]*"detected_modalities"[^{}]*\}', answer, re.DOTALL)
        if brace_match:
            result = json.loads(brace_match.group(0))
            detected = result.get('detected_modalities', [])
            return {
                'detected_modalities': detected,
                'evidence': result.get('evidence', []),
                'confidence': result.get('confidence', 'medium'),
                'is_multimodal': len(detected) > 1
            }

        logger.warning(f"GPT 응답에서 JSON 추출 실패: {answer[:200]}")
        return {
            'detected_modalities': [],
            'evidence': ['GPT 응답 파싱 실패'],
            'confidence': 'low',
            'is_multimodal': False,
            'raw_response': answer
        }

    except Exception as e:
        logger.error(f"GPT API 호출 실패: {str(e)}")
        return {
            'detected_modalities': [],
            'evidence': [f'GPT API 오류: {str(e)}'],
            'confidence': 'low',
            'is_multimodal': False
        }


def parse_modalities_from_response(response_text: str, service_name: str) -> Dict[str, Any]:
    """
    Perplexity 응답에서 모달리티 정보 추출
    OpenAI GPT-4를 사용하여 정확한 분석 수행

    Returns:
        Dict with detected_modalities and evidence
    """
    # OpenAI API 키 확인
    if os.getenv("OPENAI_API_KEY"):
        return parse_modalities_with_gpt(response_text, service_name)

    # Fallback: 휴리스틱 분석 (API 키 없을 때)
    logger.warning("OPENAI_API_KEY 없음 - 휴리스틱 분석 사용")
    return _parse_modalities_heuristic(response_text, service_name)


def _parse_modalities_heuristic(response_text: str, service_name: str) -> Dict[str, Any]:
    """
    휴리스틱 기반 모달리티 분석 (Fallback)
    """
    response_lower = response_text.lower()

    detected = []
    evidence = []

    # 텍스트 관련
    if any(kw in response_lower for kw in ['text generation', 'chatbot', 'llm', 'text-to-text', 'conversation', 'writing']):
        detected.append('T2T')
        evidence.append('Text generation/LLM detected')

    # 이미지 생성
    if any(kw in response_lower for kw in ['image generation', 'text-to-image', 'generate image', 'create image', 'dall-e', 'midjourney-style']):
        detected.append('T2I')
        evidence.append('Image generation detected')

    # 이미지 분석
    if any(kw in response_lower for kw in ['image analysis', 'image-to-text', 'vision', 'image recognition', 'analyze image', 'visual understanding']):
        detected.append('I2T')
        evidence.append('Image analysis detected')

    # 비디오 생성
    if any(kw in response_lower for kw in ['video generation', 'text-to-video', 'generate video', 'create video']):
        detected.append('T2V')
        evidence.append('Video generation detected')

    # 오디오/음성 생성
    if any(kw in response_lower for kw in ['text-to-speech', 'voice generation', 'audio generation', 'tts', 'speech synthesis']):
        detected.append('T2A')
        evidence.append('Audio/Speech generation detected')

    # 음성 인식
    if any(kw in response_lower for kw in ['speech-to-text', 'voice recognition', 'transcription', 'stt', 'audio-to-text', 'voice input']):
        detected.append('A2T')
        evidence.append('Speech recognition detected')

    # 코드 생성
    if any(kw in response_lower for kw in ['code generation', 'text-to-code', 'coding assistant', 'code completion', 'programming']):
        detected.append('T2C')
        evidence.append('Code generation detected')

    # 3D 생성
    if any(kw in response_lower for kw in ['3d generation', 'text-to-3d', '3d model', '3d content']):
        detected.append('T23D')
        evidence.append('3D generation detected')

    # 비디오 분석
    if any(kw in response_lower for kw in ['video analysis', 'video-to-text', 'analyze video', 'video understanding']):
        detected.append('V2T')
        evidence.append('Video analysis detected')

    return {
        'detected_modalities': list(set(detected)),
        'evidence': evidence,
        'is_multimodal': len(detected) > 1
    }


def compare_classifications(
    current: Dict[str, Any],
    detected: Dict[str, Any]
) -> Dict[str, Any]:
    """
    현재 분류와 검출된 모달리티 비교

    Returns:
        Dict with match status and details
    """
    current_class = current.get('classification')
    current_modalities = current.get('modalities') or []

    detected_modalities = detected.get('detected_modalities', [])

    # 비교 결과
    result = {
        'current_classification': current_class,
        'current_modalities': current_modalities,
        'detected_modalities': detected_modalities,
        'match_status': 'unknown'
    }

    # 분류 비교
    if current_class == 'MULTI':
        # MULTI인 경우: 검출된 모달리티와 현재 모달리티 비교
        current_set = set(current_modalities)
        detected_set = set(detected_modalities)

        if detected_set.issubset(current_set):
            result['match_status'] = 'match'
            result['note'] = '검출된 모달리티가 현재 분류에 포함됨'
        elif detected_set & current_set:  # 교집합이 있으면
            result['match_status'] = 'partial'
            result['missing_in_current'] = list(detected_set - current_set)
            result['extra_in_current'] = list(current_set - detected_set)
            result['note'] = '일부 모달리티 불일치'
        else:
            result['match_status'] = 'mismatch'
            result['note'] = '모달리티 완전 불일치'
    else:
        # 단일 분류인 경우
        if current_class in detected_modalities:
            if len(detected_modalities) > 1 and current_class != 'MULTI':
                result['match_status'] = 'needs_upgrade'
                result['note'] = f'현재 {current_class}이지만 MULTI로 업그레이드 필요할 수 있음'
            else:
                result['match_status'] = 'match'
                result['note'] = '분류 일치'
        elif detected_modalities:
            result['match_status'] = 'mismatch'
            result['note'] = f'현재 {current_class}이지만 {detected_modalities} 검출됨'
        else:
            result['match_status'] = 'no_detection'
            result['note'] = '모달리티 검출 실패 - 수동 확인 필요'

    return result


async def verify_single_service(
    service: Dict[str, Any],
    delay: float = 1.0
) -> Dict[str, Any]:
    """
    단일 서비스 검증 (One-by-One)

    Args:
        service: 서비스 정보 딕셔너리
        delay: API 호출 후 딜레이 (초)

    Returns:
        검증 결과 딕셔너리
    """
    service_id = service.get('id')
    service_name = service.get('name')

    logger.info(f"[{service_id}] {service_name} 검증 시작...")

    # 미분류 서비스 스킵
    if not service.get('is_classified', False):
        logger.info(f"[{service_id}] {service_name} - 미분류 상태, 스킵")
        return {
            'id': service_id,
            'name': service_name,
            'status': 'skipped',
            'reason': '미분류 서비스'
        }

    # 검색 쿼리 생성
    query = build_verification_query(service)

    try:
        # Perplexity 검색 실행
        result = await perplexity_search(
            queries=[query],
            search_recency_filter="month"  # 최근 1개월 데이터
        )

        # 답변 추출
        answer = extract_answer(result)

        # 모달리티 분석
        detected = parse_modalities_from_response(answer, service_name)

        # 분류 비교
        comparison = compare_classifications(service, detected)

        verification_result = {
            'id': service_id,
            'name': service_name,
            'status': 'verified',
            'query': query,
            'perplexity_response': answer[:1000] + '...' if len(answer) > 1000 else answer,
            'detected': detected,
            'comparison': comparison,
            'verified_at': datetime.now().isoformat()
        }

        # 결과 요약 출력
        match_status = comparison.get('match_status', 'unknown')
        status_emoji = {
            'match': '✅',
            'partial': '⚠️',
            'mismatch': '❌',
            'needs_upgrade': '🔄',
            'no_detection': '❓'
        }.get(match_status, '❓')

        logger.info(f"[{service_id}] {service_name} {status_emoji} {match_status}: {comparison.get('note', '')}")

        # 딜레이 (rate limiting)
        await asyncio.sleep(delay)

        return verification_result

    except Exception as e:
        logger.error(f"[{service_id}] {service_name} 검증 실패: {str(e)}")
        return {
            'id': service_id,
            'name': service_name,
            'status': 'error',
            'error': str(e),
            'verified_at': datetime.now().isoformat()
        }


async def run_verification(
    start_index: int = 0,
    limit: Optional[int] = None,
    delay: float = 1.0
):
    """
    전체 검증 실행 (One-by-One 이터레이션)

    Args:
        start_index: 시작 인덱스 (이어하기용)
        limit: 처리할 최대 서비스 수 (None이면 전체)
        delay: 서비스 간 딜레이 (초)
    """
    # API 키 확인
    if not os.getenv("PERPLEXITY_API_KEY"):
        logger.error("PERPLEXITY_API_KEY 환경변수가 설정되지 않았습니다.")
        logger.error("export PERPLEXITY_API_KEY='your-api-key' 명령으로 설정하세요.")
        return

    # 데이터 로드
    data = load_classification_data()
    services = data.get('services', [])

    # 이전 진행 상황 로드
    progress = load_progress() or {
        'last_verified_index': -1,
        'results': []
    }

    # 시작 인덱스 결정
    actual_start = max(start_index, progress.get('last_verified_index', -1) + 1)

    # 처리할 서비스 목록
    end_index = len(services) if limit is None else min(actual_start + limit, len(services))
    services_to_verify = services[actual_start:end_index]

    logger.info(f"=" * 60)
    logger.info(f"AI 서비스 분류 검증 시작")
    logger.info(f"전체 서비스: {len(services)}개")
    logger.info(f"검증 대상: {actual_start}번 ~ {end_index-1}번 ({len(services_to_verify)}개)")
    logger.info(f"=" * 60)

    results = progress.get('results', [])

    for i, service in enumerate(services_to_verify):
        current_index = actual_start + i

        # 진행 상황 출력
        logger.info(f"\n[진행] {current_index + 1}/{len(services)} ({(current_index + 1) / len(services) * 100:.1f}%)")

        # 검증 실행
        result = await verify_single_service(service, delay)
        results.append(result)

        # 진행 상황 저장
        progress['last_verified_index'] = current_index
        progress['results'] = results
        save_progress(progress)

    # 최종 결과 저장
    save_results(results)

    # 요약 출력
    logger.info(f"\n" + "=" * 60)
    logger.info(f"검증 완료 요약")
    logger.info(f"=" * 60)

    status_counts = {}
    match_counts = {}

    for r in results:
        status = r.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

        if status == 'verified':
            match = r.get('comparison', {}).get('match_status', 'unknown')
            match_counts[match] = match_counts.get(match, 0) + 1

    logger.info(f"처리 상태:")
    for status, count in status_counts.items():
        logger.info(f"  - {status}: {count}개")

    logger.info(f"\n일치 상태 (verified 중):")
    for match, count in match_counts.items():
        emoji = {'match': '✅', 'partial': '⚠️', 'mismatch': '❌', 'needs_upgrade': '🔄', 'no_detection': '❓'}.get(match, '❓')
        logger.info(f"  - {emoji} {match}: {count}개")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='AI 서비스 분류 검증')
    parser.add_argument('--start', type=int, default=0, help='시작 인덱스')
    parser.add_argument('--limit', type=int, default=None, help='처리할 최대 서비스 수')
    parser.add_argument('--delay', type=float, default=1.0, help='서비스 간 딜레이 (초)')
    parser.add_argument('--reset', action='store_true', help='진행 상황 초기화')

    args = parser.parse_args()

    # 진행 상황 초기화
    if args.reset and os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        logger.info("진행 상황 초기화됨")

    # 검증 실행
    asyncio.run(run_verification(
        start_index=args.start,
        limit=args.limit,
        delay=args.delay
    ))


if __name__ == "__main__":
    main()
