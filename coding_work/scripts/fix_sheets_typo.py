"""
Google Sheets 컬럼명 오타 수정 스크립트
'Assinged_to' → 'Assigned_to' 수정
"""

import sys
from pathlib import Path

# google_sheets_connector 임포트를 위한 경로 설정
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


def fix_column_typo():
    """3rd Screening 시트의 컬럼명 오타 수정"""

    print("🔧 Google Sheets 컬럼명 오타 수정 시작")
    print("=" * 60)

    # Google Sheets 연결
    connector = GoogleSheetsConnector()

    print("📞 Google Sheets 연결 중...")
    if not connector.connect():
        print("❌ Google Sheets 연결 실패")
        return False

    print("✅ Google Sheets 연결 성공")

    try:
        # 3rd Screening 시트 가져오기
        sheet = connector.get_sheet("3rd Screening")

        # 헤더(첫 번째 행) 가져오기
        headers = sheet.row_values(1)

        print(f"\n📋 현재 헤더: {len(headers)}개 컬럼")
        print(f"   처음 10개: {headers[:10]}")

        # 'Assinged_to' 컬럼 찾기
        typo_col_index = None
        for i, header in enumerate(headers, 1):
            if header == 'Assinged_to':
                typo_col_index = i
                print(f"\n🎯 오타 발견!")
                print(f"   컬럼 번호: {i}")
                print(f"   현재 이름: '{header}'")
                break

        if typo_col_index is None:
            print("\n⚠️  'Assinged_to' 컬럼을 찾을 수 없습니다.")
            print("   이미 수정되었거나, 다른 이름일 수 있습니다.")

            # 'Assigned_to' 확인
            if 'Assigned_to' in headers:
                print("   ✅ 'Assigned_to' 컬럼은 이미 존재합니다.")

            return False

        # 컬럼명 수정
        print(f"\n🔄 컬럼명 수정 중...")
        print(f"   'Assinged_to' → 'Assigned_to'")

        connector.update_cell(
            sheet_name="3rd Screening",
            row=1,
            col=typo_col_index,
            value='Assigned_to'
        )

        print("✅ 컬럼명 수정 완료!")

        # 검증
        updated_headers = sheet.row_values(1)
        if updated_headers[typo_col_index - 1] == 'Assigned_to':
            print("\n✅ 검증 성공: 컬럼명이 'Assigned_to'로 정상 변경되었습니다.")
            return True
        else:
            print("\n❌ 검증 실패: 변경이 제대로 반영되지 않았습니다.")
            return False

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📝 Google Sheets 오타 수정 도구")
    print("   대상: 3rd Screening 시트")
    print("   변경: 'Assinged_to' → 'Assigned_to'")
    print("=" * 60 + "\n")

    success = fix_column_typo()

    if success:
        print("\n🎉 모든 작업이 완료되었습니다!")
        print("\n📋 다음 단계:")
        print("   1. 코드는 이미 수정되었습니다.")
        print("   2. Google Sheets도 수정되었습니다.")
        print("   3. 이제 paper_inclusion_evaluator.py를 실행할 수 있습니다.")
    else:
        print("\n⚠️  작업이 완료되지 않았습니다.")
        print("   Google Sheets를 수동으로 확인해주세요.")
