"""
Excel 파일과 Google Sheets의 상세 비교 분석
1. 인덱스 불일치 (제거/추가된 페이퍼)
2. 셀 수정 비교 (컬럼별 값 차이)
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


def normalize_value(val):
    """값을 비교 가능한 형태로 정규화"""
    if pd.isna(val) or val is None:
        return ""
    val = str(val).strip()
    # 숫자 정규화 (100.0 -> 100)
    try:
        if '.' in val and float(val) == int(float(val)):
            return str(int(float(val)))
    except:
        pass
    return val


def main():
    print("=" * 70)
    print("🔍 Excel vs Google Sheets 상세 비교 분석")
    print("=" * 70)
    print()

    # 1. Excel 파일 로드
    print("📥 Excel 파일 로드 중...")
    excel_path = Path(__file__).parent.parent / "Coding & screening works-2.xlsx"

    try:
        excel_df = pd.read_excel(excel_path)
        excel_df['Index'] = excel_df['Index'].astype(str).str.strip()
        print(f"   ✅ Excel 로드 완료: {len(excel_df)}행, {len(excel_df.columns)}열")
        print(f"   📋 컬럼: {list(excel_df.columns)}")
    except Exception as e:
        print(f"❌ Excel 로드 실패: {e}")
        return

    # 2. Google Sheets 로드
    print("\n📥 Google Sheets 로드 중...")
    connector = GoogleSheetsConnector()

    if not connector.connect():
        print("❌ Google Sheets 연결 실패")
        return

    try:
        sheet = connector.get_sheet("CodedPapers_2")
        all_values = sheet.get_all_values()

        if len(all_values) <= 1:
            print("   ⚠️ Google Sheets가 비어있습니다.")
            return

        headers = all_values[0]
        data_rows = all_values[1:]
        sheets_df = pd.DataFrame(data_rows, columns=headers)
        sheets_df['Index'] = sheets_df['Index'].astype(str).str.strip()

        # 빈 행 제거
        sheets_df = sheets_df[sheets_df['Index'] != '']

        print(f"   ✅ Google Sheets 로드 완료: {len(sheets_df)}행, {len(sheets_df.columns)}열")
        print(f"   📋 컬럼: {list(sheets_df.columns)}")

    except Exception as e:
        print(f"❌ Google Sheets 로드 실패: {e}")
        return

    # 3. 인덱스 비교
    print("\n" + "=" * 70)
    print("📊 1. 인덱스 불일치 분석")
    print("=" * 70)

    excel_indices = set(excel_df['Index'].tolist())
    sheets_indices = set(sheets_df['Index'].tolist())

    # Excel에만 있는 Index (Sheets에서 제거됨)
    excel_only = excel_indices - sheets_indices
    print(f"\n❌ Excel에만 있는 Index (Sheets에서 제거됨): {len(excel_only)}개")
    if excel_only:
        sorted_indices = sorted(excel_only, key=lambda x: int(x) if x.isdigit() else 0)
        for idx in sorted_indices:
            row = excel_df[excel_df['Index'] == idx].iloc[0]
            title = row.get('Article Title', 'N/A')[:50]
            print(f"   • Index {idx}: {title}...")

    # Sheets에만 있는 Index (Excel에는 없음)
    sheets_only = sheets_indices - excel_indices
    print(f"\n➕ Sheets에만 있는 Index (Excel에는 없음): {len(sheets_only)}개")
    if sheets_only:
        sorted_indices = sorted(sheets_only, key=lambda x: int(x) if x.isdigit() else 0)
        for idx in sorted_indices:
            row = sheets_df[sheets_df['Index'] == idx].iloc[0]
            title = row.get('Article Title', 'N/A')[:50]
            print(f"   • Index {idx}: {title}...")

    # 공통 Index
    common_indices = excel_indices & sheets_indices
    print(f"\n✅ 공통 Index: {len(common_indices)}개")

    # 4. 셀 수정 비교
    print("\n" + "=" * 70)
    print("📊 2. 셀 수정 비교 (공통 Index 기준)")
    print("=" * 70)

    # 비교할 컬럼 (공통 컬럼만)
    common_columns = [c for c in excel_df.columns if c in sheets_df.columns and c != 'Index']
    print(f"\n비교 대상 컬럼: {len(common_columns)}개")

    modifications = []
    modified_indices = set()

    for idx in sorted(common_indices, key=lambda x: int(x) if x.isdigit() else 0):
        excel_row = excel_df[excel_df['Index'] == idx].iloc[0]
        sheets_row = sheets_df[sheets_df['Index'] == idx].iloc[0]

        row_mods = []
        for col in common_columns:
            excel_val = normalize_value(excel_row.get(col, ""))
            sheets_val = normalize_value(sheets_row.get(col, ""))

            if excel_val != sheets_val:
                row_mods.append({
                    'column': col,
                    'excel': excel_val,
                    'sheets': sheets_val
                })

        if row_mods:
            modified_indices.add(idx)
            modifications.append({
                'index': idx,
                'title': str(excel_row.get('Article Title', 'N/A'))[:40],
                'changes': row_mods
            })

    print(f"\n수정된 행: {len(modified_indices)}개")
    print(f"총 수정된 셀: {sum(len(m['changes']) for m in modifications)}개")

    if modifications:
        print("\n--- 수정 내역 상세 ---")
        for mod in modifications:
            print(f"\n📝 Index {mod['index']}: {mod['title']}...")
            for change in mod['changes']:
                print(f"   • {change['column']}:")
                excel_preview = change['excel'][:60] if change['excel'] else "(빈값)"
                sheets_preview = change['sheets'][:60] if change['sheets'] else "(빈값)"
                print(f"      Excel:  {excel_preview}")
                print(f"      Sheets: {sheets_preview}")

    # 5. 컬럼별 수정 통계
    print("\n" + "=" * 70)
    print("📊 3. 컬럼별 수정 통계")
    print("=" * 70)

    column_stats = {}
    for mod in modifications:
        for change in mod['changes']:
            col = change['column']
            column_stats[col] = column_stats.get(col, 0) + 1

    if column_stats:
        sorted_stats = sorted(column_stats.items(), key=lambda x: x[1], reverse=True)
        for col, count in sorted_stats:
            print(f"   {col}: {count}건")
    else:
        print("   수정된 셀이 없습니다.")

    print("\n" + "=" * 70)
    print("✅ 비교 분석 완료!")
    print("=" * 70)


if __name__ == "__main__":
    main()
