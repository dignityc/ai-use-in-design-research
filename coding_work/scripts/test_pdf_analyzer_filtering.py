"""
PDF Analyzer 필터링 테스트 스크립트
수정된 pdf_analyzer.py의 필터링 및 CodeBook 로드 기능 검증
"""

import sys
from pathlib import Path

# pdf_analyzer 임포트
sys.path.append(str(Path(__file__).parent))
from pdf_analyzer import PDFAnalyzer


def test_filtering_and_codebook():
    """필터링 및 CodeBook 로드 테스트"""

    print("=" * 80)
    print("🧪 PDF Analyzer 필터링 & CodeBook 테스트")
    print("=" * 80)

    # PDF Analyzer 초기화
    analyzer = PDFAnalyzer()

    # 1. Google Sheets 연결
    print("\n[1/4] Google Sheets 연결 테스트")
    print("-" * 80)
    if not analyzer.connect_to_sheets():
        print("❌ Google Sheets 연결 실패")
        return False

    # 2. CodeBook 로드 테스트
    print("\n[2/4] CodeBook 로드 테스트")
    print("-" * 80)
    codebook = analyzer.load_codebook()

    if codebook:
        print("✅ CodeBook 로드 성공!")
        print("\n📚 CodeBook 내용:")
        for key, values in codebook.items():
            if values:  # 빈 리스트가 아닌 경우만
                print(f"\n   {key}:")
                for i, value in enumerate(values[:5], 1):  # 처음 5개만 출력
                    print(f"      {i}. {value}")
                if len(values) > 5:
                    print(f"      ... (총 {len(values)}개)")
    else:
        print("❌ CodeBook 로드 실패")
        return False

    # 3. 필터링된 논문 Index 목록 가져오기
    print("\n[3/4] Google Sheets 필터링 테스트 (Inclusion='Y' & Assigned_to='J')")
    print("-" * 80)
    included_indices = analyzer.get_included_papers_from_sheets()

    if included_indices:
        print(f"✅ 필터링된 Index: {len(included_indices)}개")
        print(f"\n📋 Index 목록 (처음 20개):")
        sorted_indices = sorted(included_indices, key=lambda x: int(x))
        for i, idx in enumerate(sorted_indices[:20], 1):
            print(f"   {i}. Index: {idx}")
        if len(included_indices) > 20:
            print(f"   ... (총 {len(included_indices)}개)")
    else:
        print("❌ 필터링된 논문이 없습니다.")
        return False

    # 4. 필터링된 PDF 파일 목록 가져오기
    print("\n[4/4] 필터링된 PDF 파일 목록 테스트")
    print("-" * 80)
    filtered_pdf_files = analyzer.get_pdf_files(included_indices)

    if filtered_pdf_files:
        print(f"✅ 필터링된 PDF 파일: {len(filtered_pdf_files)}개")
        print(f"\n📄 PDF 파일 목록 (처음 10개):")
        for i, pdf_file in enumerate(filtered_pdf_files[:10], 1):
            index = analyzer.extract_index_from_filename(pdf_file.name)
            print(f"   {i}. [{index}] {pdf_file.name}")
        if len(filtered_pdf_files) > 10:
            print(f"   ... (총 {len(filtered_pdf_files)}개)")
    else:
        print("⚠️  필터링된 PDF 파일이 없습니다.")
        print("   (Index가 매칭되는 PDF 파일이 Papers 폴더에 없을 수 있습니다)")

    # 5. Index 추출 테스트
    print("\n[5/5] Index 추출 테스트")
    print("-" * 80)
    test_filenames = [
        "80_Deep learning for design.pdf",
        "101_Customer requirements extraction.pdf",
        "NoIndex_SomeFile.pdf",
        "123.pdf"
    ]

    for filename in test_filenames:
        index = analyzer.extract_index_from_filename(filename)
        if index:
            print(f"   ✅ '{filename}' → Index: {index}")
        else:
            print(f"   ❌ '{filename}' → Index 추출 실패")

    # 최종 결과
    print("\n" + "=" * 80)
    print("🎉 테스트 완료!")
    print("=" * 80)
    print(f"✅ Google Sheets 연결: 성공")
    print(f"✅ CodeBook 로드: {len(codebook)}개 카테고리")
    print(f"✅ 필터링된 Index: {len(included_indices)}개")
    print(f"✅ 필터링된 PDF 파일: {len(filtered_pdf_files)}개")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = test_filtering_and_codebook()

    if success:
        print("\n✅ 모든 테스트 통과!")
        sys.exit(0)
    else:
        print("\n❌ 테스트 실패!")
        sys.exit(1)
