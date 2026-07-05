"""
Perplexity Sonar API를 이용한 실시간 웹 검색 도구

원본: ask-engine/app/graph/InDepth_processor/core_tools/perplexity_tools.py
단순화: LangGraph/LangFuse 의존성 제거, standalone 버전
"""

import os
import asyncio
from typing import Dict, Any, List
import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


async def _single_perplexity_search(query: str, search_recency_filter: str = None) -> Dict[str, Any]:
    """
    단일 쿼리에 대한 Perplexity 검색 수행.

    Args:
        query: 검색할 쿼리 문자열
        search_recency_filter: 검색 결과 시간 범위 필터 (optional)

    Returns:
        Dict[str, Any]: 검색 결과를 담은 딕셔너리
    """

    try:
        # 환경변수에서 API 키 가져오기
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("PERPLEXITY_API_KEY 환경변수가 설정되지 않았습니다.")
            return {
                "__results__": {
                    "search_query": query,
                    "answer": "Perplexity API 키가 설정되지 않아 검색을 수행할 수 없습니다.",
                    "success": False,
                    "error_message": "PERPLEXITY_API_KEY 환경변수가 설정되지 않았습니다."
                }
            }

        # Perplexity API용 AsyncOpenAI 클라이언트 설정
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )

        # Perplexity Sonar 모델로 검색 요청
        # 참고: Perplexity API는 OpenAI SDK 호환이지만 일부 파라미터가 다름
        messages = [
            {
                "role": "system",
                "content": "Your role is to search for relevant source information based on the user's question and generate and extract data by describing it in detail. Do not perform analysis work. To support subsequent analysis work, find as many relevant sources as possible and answer clearly and in great detail with the information extracted from each source. Also, explore 2-3 sources that are expected to contain the most relevant information in detail and answer with detailed information. Include the sources."
            },
            {
                "role": "user",
                "content": query
            }
        ]

        # search_recency_filter를 쿼리에 포함 (API 파라미터 대신)
        if search_recency_filter:
            time_hint = {
                "day": "in the last 24 hours",
                "week": "in the last week",
                "month": "in the last month",
                "year": "in the last year"
            }.get(search_recency_filter, "")
            if time_hint:
                messages[1]["content"] = f"{query} (Focus on information {time_hint})"

        response = await client.chat.completions.create(
            model="sonar-pro",
            messages=messages,
            max_tokens=2000
        )

        # 응답에서 답변 추출
        answer = response.choices[0].message.content

        # 원본 응답을 딕셔너리로 변환
        raw_response = response.model_dump() if hasattr(response, 'model_dump') else dict(response)

        logger.info(f"Perplexity 검색 성공: {query[:50]}...")

        return {
            "__results__": {
                "search_query": query,
                "raw_response": raw_response,  # 전체 원본 응답 (답변 및 인용 포함)
                "success": True
            }
        }

    except Exception as e:
        error_message = f"Perplexity 검색 중 오류 발생: {str(e)}"
        logger.error(error_message)

        return {
            "__results__": {
                "search_query": query,
                "success": False,
                "error_message": error_message
            }
        }


async def perplexity_search(
    queries: List[str],
    search_recency_filter: str = None
) -> Dict[str, Any]:
    """
    Perplexity Sonar 모델을 이용한 실시간 웹 검색 수행.
    쿼리 목록을 받아 동시에 처리.

    Args:
        queries: 검색할 쿼리 문자열 목록 (단일 쿼리는 ["쿼리"] 형식으로 입력)
        search_recency_filter: 검색 결과 시간 범위 필터 (optional)
            옵션: "day" (최근 1일), "week" (최근 1주), "month" (최근 1개월),
                  "year" (최근 1년), None (전체 기간, 기본값)

    Returns:
        Dict[str, Any] - 전체 검색 결과를 감싼 딕셔너리

        결과 구조:
        {
            "__results__": {
                "status": "success" | "error",
                "total_queries": int,
                "successful_queries": int,
                "failed_queries": int,
                "search_results": List[Dict] - 각 쿼리별 검색 결과 목록
                [
                    {
                        "search_query": str - 입력된 검색 쿼리,
                        "raw_response": Dict - 전체 원본 응답 (인용, 검색결과, 사용량 포함),
                        "success": bool - 검색 성공 여부,
                        "error_message": str - 오류 발생 시 오류 메시지 (optional)
                    },
                    ...
                ],
                "error": str - 전체 작업 실패 시 오류 메시지 (optional)
            }
        }

    Raises:
        ValueError: 쿼리 목록이 최대 허용 개수(5)를 초과할 때
        TypeError: queries가 리스트가 아닐 때
    """

    # 최대 동시 쿼리 처리 개수 (고정값)
    MAX_CONCURRENT_QUERIES = 5

    # 입력 타입 검증
    if not isinstance(queries, list):
        raise TypeError("queries는 문자열 리스트여야 합니다. 단일 쿼리는 ['쿼리'] 형식으로 입력하세요.")

    # 쿼리 개수 제한 확인
    if len(queries) > MAX_CONCURRENT_QUERIES:
        raise ValueError(
            f"쿼리 개수({len(queries)})가 최대 허용 개수({MAX_CONCURRENT_QUERIES})를 초과했습니다. "
            f"쿼리를 분할하여 여러 번 호출하세요."
        )

    # 빈 목록 확인
    if len(queries) == 0:
        logger.warning("빈 쿼리 목록이 전달되었습니다.")
        return {
            "__results__": {
                "status": "success",
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "search_results": []
            }
        }

    logger.info(f"동시 쿼리 검색 시작: {len(queries)}개 쿼리 (최대 {MAX_CONCURRENT_QUERIES}개)")

    # 모든 쿼리 동시 실행
    tasks = [
        _single_perplexity_search(query, search_recency_filter)
        for query in queries
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 예외 처리된 결과를 정상 결과로 변환하고 통계 수집
    processed_results = []
    successful_count = 0
    failed_count = 0

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            error_result = {
                "search_query": queries[i],
                "success": False,
                "error_message": f"쿼리 실행 중 예외 발생: {str(result)}"
            }
            processed_results.append(error_result)
            failed_count += 1
            logger.error(f"쿼리 '{queries[i]}' 실행 실패: {str(result)}")
        else:
            # 기존 결과에서 __results__ 래핑 제거하고 내용만 추출
            if isinstance(result, dict) and "__results__" in result:
                inner_result = result["__results__"]
                processed_results.append(inner_result)
                if inner_result.get("success", False):
                    successful_count += 1
                else:
                    failed_count += 1
            else:
                processed_results.append(result)
                successful_count += 1

    logger.info(f"쿼리 검색 완료: {successful_count}개 성공, {failed_count}개 실패")

    # 전체 결과를 표준 __results__ 구조로 래핑
    return {
        "__results__": {
            "status": "success",
            "total_queries": len(queries),
            "successful_queries": successful_count,
            "failed_queries": failed_count,
            "search_results": processed_results
        }
    }


def extract_answer(result: Dict[str, Any]) -> str:
    """
    Perplexity 검색 결과에서 답변 텍스트만 추출하는 헬퍼 함수.

    Args:
        result: perplexity_search() 또는 _single_perplexity_search()의 반환값

    Returns:
        str: 추출된 답변 텍스트, 실패 시 에러 메시지
    """
    try:
        if "__results__" in result:
            results = result["__results__"]

            # 단일 결과인 경우
            if "raw_response" in results:
                return results["raw_response"]["choices"][0]["message"]["content"]

            # 다중 결과인 경우 (search_results 배열)
            if "search_results" in results:
                answers = []
                for sr in results["search_results"]:
                    if sr.get("success") and "raw_response" in sr:
                        answer = sr["raw_response"]["choices"][0]["message"]["content"]
                        answers.append(f"[{sr['search_query']}]\n{answer}")
                    elif "error_message" in sr:
                        answers.append(f"[{sr['search_query']}] 오류: {sr['error_message']}")
                return "\n\n---\n\n".join(answers)

        return "결과를 추출할 수 없습니다."
    except Exception as e:
        return f"답변 추출 중 오류: {str(e)}"


if __name__ == "__main__":
    """
    단독 실행 테스트용 메인 블록
    """
    import json

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def test_perplexity_search():
        """테스트 함수"""
        print("=" * 60)
        print("Perplexity Search Tool Test")
        print("=" * 60)

        # API 키 확인
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if api_key:
            print(f"PERPLEXITY_API_KEY 설정됨 (길이: {len(api_key)})")
        else:
            print("PERPLEXITY_API_KEY 미설정")
            print("   export PERPLEXITY_API_KEY='your-api-key' 명령으로 설정하세요")
            return

        print("\n" + "-" * 60)

        # 단일 쿼리 테스트
        print("단일 쿼리 테스트")
        test_query = ["What are the main AI features of Claude in 2025?"]

        print(f"쿼리: {test_query[0]}")

        try:
            import time
            start_time = time.time()

            results = await perplexity_search(
                queries=test_query,
                search_recency_filter="month"
            )

            end_time = time.time()
            elapsed_time = end_time - start_time

            print(f"\n처리 시간: {elapsed_time:.2f}s")

            # 결과 구조 확인
            if "__results__" in results:
                result_data = results["__results__"]
                print(f"결과 수: {result_data.get('total_queries', 0)}")
                print(f"성공: {result_data.get('successful_queries', 0)}")
                print(f"실패: {result_data.get('failed_queries', 0)}")

                # 답변 추출
                answer = extract_answer(results)
                print(f"\n답변 (처음 500자):\n{answer[:500]}...")

        except Exception as e:
            print(f"테스트 실패: {str(e)}")

        print("\n" + "=" * 60)
        print("테스트 완료!")

    # 비동기 함수 실행
    asyncio.run(test_perplexity_search())
