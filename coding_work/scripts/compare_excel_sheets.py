"""
Excel 파일과 Google Sheets의 Index 비교
어떤 Index가 추가되어야 하고, 어떤 Index가 건너뛰어야 하는지 확인
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from excel_to_dataframe import ExcelDataLoader
from google_sheets_connector import GoogleSheetsConnector


def compare_excel_and_sheets():
    """Excel과 Google Sheets의 Index 비교"""
    print("=" * 70)
    print("🔍 Excel vs Google Sheets Index 비교")
    print("=" * 70)
    print()

    # 1. Excel 파일 로드
    print("📥 Excel 파일 로드 중...")
    excel_path = Path(__file__).parent.parent / "Coding & screening works-integrated.xlsx"
    loader = ExcelDataLoader(excel_path)

    try:
        values_df, _ = loader.load_excel_with_comments()
        excel_indices = set(values_df['Index'].astype(str).str.strip())
        print(f"   ✅ Excel Index: {len(excel_indices)}개")
    except Exception as e:
        print(f"❌ Excel 로드 실패: {e}")
        return False

    # 2. Google Sheets 로드
    print("\n📥 Google Sheets 로드 중...")
    connector = GoogleSheetsConnector()

    if not connector.connect():
        print("❌ Google Sheets 연결 실패")
        return False

    try:
        sheet = connector.get_sheet("CodedPapers_2")
        all_values = sheet.get_all_values()

        if len(all_values) <= 1:
            print("   ℹ️  Google Sheets가 비어있습니다.")
            sheets_indices = set()
        else:
            headers = all_values[0]
            data_rows = all_values[1:]
            index_col_idx = headers.index("Index")

            sheets_indices = set()
            for row in data_rows:
                if len(row) > index_col_idx and row[index_col_idx]:
                    sheets_indices.add(str(row[index_col_idx]).strip())

        print(f"   ✅ Google Sheets Index: {len(sheets_indices)}개")

    except Exception as e:
        print(f"❌ Google Sheets 로드 실패: {e}")
        return False

    # 3. 비교 분석
    print("\n" + "=" * 70)
    print("📊 비교 결과")
    print("=" * 70)

    # 3.1 교집합 (이미 존재하는 Index - 건너뛸 대상)
    common = excel_indices & sheets_indices
    print(f"\n✅ Excel과 Google Sheets 공통 Index: {len(common)}개")
    if common:
        common_sorted = sorted(common, key=lambda x: int(x) if x.isdigit() else 0)
        print(f"   📋 샘플 (처음 20개): {', '.join(common_sorted[:20])}")
        if len(common) > 20:
            print(f"   ... (총 {len(common)}개)")

    # 3.2 Excel에만 있는 Index (추가할 대상)
    excel_only = excel_indices - sheets_indices
    print(f"\n➕ Excel에만 있는 Index (추가 대상): {len(excel_only)}개")
    if excel_only:
        excel_only_sorted = sorted(excel_only, key=lambda x: int(x) if x.isdigit() else 0)
        print(f"   📋 목록: {', '.join(excel_only_sorted)}")
    else:
        print("   ℹ️  Excel의 모든 Index가 Google Sheets에 이미 존재합니다.")

    # 3.3 Google Sheets에만 있는 Index (Excel에는 없음)
    sheets_only = sheets_indices - excel_indices
    print(f"\n⚠️  Google Sheets에만 있는 Index (Excel에는 없음): {len(sheets_only)}개")
    if sheets_only:
        sheets_only_sorted = sorted(sheets_only, key=lambda x: int(x) if x.isdigit() else 0)
        print(f"   📋 목록: {', '.join(sheets_only_sorted)}")
    else:
        print("   ✅ Google Sheets의 모든 Index가 Excel에 존재합니다.")

    # 4. 최종 예측
    print("\n" + "=" * 70)
    print("📈 업로드 예측")
    print("=" * 70)
    print(f"Excel 논문 총 개수: {len(excel_indices)}개")
    print(f"Google Sheets 기존: {len(sheets_indices)}개")
    print(f"건너뛸 논문 (이미 존재): {len(common)}개")
    print(f"추가할 논문 (새로운 Index): {len(excel_only)}개")

    if len(common) == len(excel_indices):
        print("\n🔔 모든 Excel 논문이 Google Sheets에 이미 존재합니다!")
        print("   → Skip 방식으로 업로드하면 아무것도 추가되지 않습니다.")
    elif len(excel_only) > 0:
        print(f"\n🔔 Skip 방식으로 업로드하면 {len(excel_only)}개 논문이 추가됩니다.")
    else:
        print("\n✅ Excel과 Google Sheets가 완전히 일치합니다.")

    print("\n" + "=" * 70)

    return True


def main():
    """메인 실행 함수"""
    try:
        success = compare_excel_and_sheets()

        if success:
            print("🎉 비교 완료!")
        else:
            print("❌ 비교 실패")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
