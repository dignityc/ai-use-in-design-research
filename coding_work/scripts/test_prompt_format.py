"""
프롬프트 포맷 테스트 스크립트
실제 Claude에게 전달되는 프롬프트 형식 확인
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from pdf_analyzer import PDFAnalyzer


def test_prompt_format():
    """프롬프트 형식 테스트"""

    print("=" * 80)
    print("🧪 프롬프트 형식 테스트")
    print("=" * 80)

    # PDF Analyzer 초기화
    analyzer = PDFAnalyzer()

    # Google Sheets 연결
    if not analyzer.connect_to_sheets():
        print("❌ Google Sheets 연결 실패")
        return False

    # CodeBook 로드
    print("\n📚 CodeBook 로드 중...")
    codebook = analyzer.load_codebook()

    if not codebook:
        print("❌ CodeBook 로드 실패")
        return False

    print("✅ CodeBook 로드 성공!\n")

    # AI methods 프롬프트 형식 확인
    print("=" * 80)
    print("📋 실제 프롬프트 예시: AI methods")
    print("=" * 80)

    # format_options_with_descriptions 함수 재현
    def format_options_with_descriptions(items: list) -> str:
        """레이블과 설명을 포맷팅"""
        if not items:
            return ""

        formatted_lines = []
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                label = item.get('label', '')
                description = item.get('description', '')
                if description:
                    formatted_lines.append(f"{i}. {label}: {description}")
                else:
                    formatted_lines.append(f"{i}. {label}")
            else:
                formatted_lines.append(f"{i}. {item}")

        return "\n".join(formatted_lines)

    # AI methods 옵션 생성
    ai_methods_options = format_options_with_descriptions(codebook.get('ai_methods', []))

    print("\n📝 Available options for AI methods:")
    print(ai_methods_options)

    print("\n" + "=" * 80)
    print("📋 실제 프롬프트 예시: Design Discipline")
    print("=" * 80)

    # Design Discipline 옵션 생성
    design_discipline_options = format_options_with_descriptions(codebook.get('design_disciplines', []))

    print("\n📝 Available options for Design Discipline:")
    print(design_discipline_options)

    print("\n" + "=" * 80)
    print("✅ 테스트 완료!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = test_prompt_format()

    if success:
        print("\n✅ 프롬프트 형식 확인 완료!")
        sys.exit(0)
    else:
        print("\n❌ 테스트 실패!")
        sys.exit(1)
