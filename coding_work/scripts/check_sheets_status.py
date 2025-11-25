"""
Google Sheets CodedPapers_2 시트의 현재 상태 확인
기존 Index 목록 및 데이터 현황 파악
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


def check_sheets_status(sheet_name: str = "CodedPapers_2"):
    """
    Google Sheets 현황 확인

    Args:
        sheet_name: 확인할 시트 이름
    """
    print("=" * 70)
    print(f"🔍 Google Sheets '{sheet_name}' 시트 현황 확인")
    print("=" * 70)
    print()

    # Google Sheets 연결
    connector = GoogleSheetsConnector()

    print("🔗 Google Sheets 연결 중...")
    if not connector.connect():
        print("❌ Google Sheets 연결 실패")
        return False

    print("   ✅ 연결 성공")
    print()

    # 시트 가져오기
    try:
        sheet = connector.get_sheet(sheet_name)
        print(f"   ✅ 시트 발견: '{sheet_name}'")
    except Exception as e:
        print(f"❌ 시트를 찾을 수 없습니다: {e}")
        return False

    # 시트 데이터 가져오기
    print("\n📥 시트 데이터 로드 중...")
    all_values = sheet.get_all_values()

    if not all_values:
        print("   ℹ️  시트가 완전히 비어있습니다.")
        return True

    # 헤더와 데이터 분리
    headers = all_values[0]
    data_rows = all_values[1:]

    print(f"   ✅ 총 행 개수: {len(all_values)}개 (헤더 포함)")
    print(f"   ✅ 데이터 행 개수: {len(data_rows)}개")
    print(f"   ✅ 컬럼 개수: {len(headers)}개")

    # 헤더 출력
    print(f"\n📋 컬럼 목록:")
    for i, col in enumerate(headers, 1):
        print(f"   {i}. {col}")

    # Index 컬럼 찾기
    if "Index" not in headers:
        print("\n⚠️  Index 컬럼을 찾을 수 없습니다.")
        return False

    index_col_idx = headers.index("Index")

    # Index 목록 추출
    indices = []
    for row in data_rows:
        if len(row) > index_col_idx and row[index_col_idx]:
            index_value = str(row[index_col_idx]).strip()
            if index_value:
                indices.append(index_value)

    print(f"\n📊 Index 통계:")
    print(f"   - 총 Index 개수: {len(indices)}개")

    # 중복 확인
    unique_indices = set(indices)
    duplicate_count = len(indices) - len(unique_indices)

    if duplicate_count > 0:
        print(f"   ⚠️  중복된 Index: {duplicate_count}개 발견!")

        # 중복 Index 출력
        from collections import Counter
        counter = Counter(indices)
        duplicates = [idx for idx, count in counter.items() if count > 1]
        print(f"   ⚠️  중복 Index 목록: {', '.join(duplicates)}")
    else:
        print(f"   ✅ 모든 Index가 유니크함")

    # Index 샘플 출력 (처음 20개)
    print(f"\n📋 Index 목록 (처음 20개):")
    sample_indices = sorted(indices)[:20]
    for i, idx in enumerate(sample_indices, 1):
        print(f"   {i}. {idx}")

    if len(indices) > 20:
        print(f"   ... (총 {len(indices)}개)")

    # DataFrame으로 변환하여 기본 통계
    if data_rows:
        df = pd.DataFrame(data_rows, columns=headers)

        # Index 정렬하여 범위 확인
        if indices:
            sorted_indices = sorted([int(idx) for idx in indices if idx.isdigit()])
            if sorted_indices:
                print(f"\n📈 Index 범위:")
                print(f"   - 최소: {sorted_indices[0]}")
                print(f"   - 최대: {sorted_indices[-1]}")

                # 연속성 확인 (빠진 Index 찾기)
                missing = []
                for i in range(sorted_indices[0], sorted_indices[-1] + 1):
                    if i not in sorted_indices:
                        missing.append(i)

                if missing:
                    print(f"   ⚠️  빠진 Index: {len(missing)}개")
                    if len(missing) <= 20:
                        print(f"   ⚠️  빠진 Index 목록: {', '.join(map(str, missing))}")
                    else:
                        print(f"   ⚠️  빠진 Index 샘플 (처음 20개): {', '.join(map(str, missing[:20]))}")
                else:
                    print(f"   ✅ Index가 연속적임 ({sorted_indices[0]}-{sorted_indices[-1]})")

    print("\n" + "=" * 70)
    print("✅ 현황 확인 완료!")
    print("=" * 70)

    return True


def main():
    """메인 실행 함수"""
    try:
        success = check_sheets_status("CodedPapers_2")

        if success:
            print("\n🎉 확인 완료!")
        else:
            print("\n❌ 확인 실패")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
