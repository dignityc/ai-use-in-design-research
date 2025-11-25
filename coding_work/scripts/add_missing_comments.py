"""
Google Sheets CodedPapers_2 시트의 누락된 셀 코멘트 추가
Excel 파일에서 코멘트를 가져와 누락된 셀에만 추가 (Skip 방식)
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
import time
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector
from excel_to_dataframe import ExcelDataLoader
from check_missing_comments import CommentChecker


class MissingCommentAdder:
    """누락된 셀 코멘트 추가기"""

    def __init__(
        self,
        excel_path: str,
        sheet_name: str = "CodedPapers_2",
        dry_run: bool = False,
        limit: int = None
    ):
        """
        초기화

        Args:
            excel_path: Excel 파일 경로
            sheet_name: Google Sheets 시트 이름
            dry_run: True이면 시뮬레이션만
            limit: 처리할 셀 개수 제한
        """
        self.excel_path = Path(excel_path)
        self.sheet_name = sheet_name
        self.dry_run = dry_run
        self.limit = limit

        # 연결
        self.connector = GoogleSheetsConnector()
        self.excel_loader = ExcelDataLoader(self.excel_path)
        self.comment_checker = CommentChecker(sheet_name)

        # 7개 분류 컬럼
        self.classification_columns = [
            "Design Discipline",
            "Data About",
            "Data Modality",
            "AI methods",
            "AI Assistance Types (Lee and Kim, 2025)",
            "Design Phase",
            "Design Practice/Task"
        ]

        # 통계
        self.stats = {
            "total_missing": 0,
            "added": 0,
            "skipped": 0,
            "failed": 0
        }

    def load_excel_comments(self) -> Dict[Tuple[str, str], str]:
        """
        Excel 파일에서 코멘트 로드

        Returns:
            Dict[Tuple[str, str], str]: {(Index, Column): comment_text}
        """
        print("📥 Excel 파일에서 코멘트 로드 중...")

        try:
            _, comments_df = self.excel_loader.load_excel_with_comments()

            # {(Index, Column): comment_text} 매핑 생성
            excel_comments = {}

            for _, row in comments_df.iterrows():
                index_value = str(row['Index']).strip()

                for col in self.classification_columns:
                    comment_text = str(row.get(col, "")).strip()

                    if comment_text and comment_text.lower() not in ['nan', '', 'none']:
                        excel_comments[(index_value, col)] = comment_text

            print(f"   ✅ Excel 코멘트: {len(excel_comments)}개 로드")

            return excel_comments

        except Exception as e:
            print(f"❌ Excel 코멘트 로드 실패: {e}")
            return {}

    def add_missing_comments(self):
        """누락된 셀 코멘트 추가 (Skip 방식)"""
        print("=" * 70)
        print("🚀 누락된 셀 코멘트 추가 (Skip 방식)")
        print("=" * 70)
        print()

        if self.dry_run:
            print("🔔 [DRY RUN 모드] 시뮬레이션만 실행합니다.")
        if self.limit:
            print(f"🔔 [제한 모드] 최대 {self.limit}개 셀만 처리합니다.")

        print()

        # 1. Excel 코멘트 로드
        excel_comments = self.load_excel_comments()

        if not excel_comments:
            print("❌ Excel 코멘트를 로드할 수 없습니다.")
            return False

        # 2. Google Sheets 연결
        print("\n🔗 Google Sheets 연결 중...")
        if not self.connector.connect():
            print("❌ Google Sheets 연결 실패")
            return False

        print("   ✅ 연결 성공")

        # 3. 시트 가져오기
        try:
            sheet = self.connector.get_sheet(self.sheet_name)
            print(f"   ✅ 시트 발견: '{self.sheet_name}'")
        except Exception as e:
            print(f"❌ 시트를 찾을 수 없습니다: {e}")
            return False

        # 4. 누락된 셀 확인
        print(f"\n🔍 누락된 셀 확인 중...")
        print("   ⚠️  시간이 소요됩니다 (805개 셀 스캔)...")

        missing_df = self.comment_checker.check_missing_comments(sample_only=False)

        if missing_df.empty:
            print("\n✅ 모든 셀에 코멘트가 이미 있습니다!")
            return True

        self.stats["total_missing"] = len(missing_df)

        # 5. limit 처리
        if self.limit:
            missing_df = missing_df.head(self.limit)
            print(f"\n🔔 제한 모드: {len(missing_df)}개 셀만 처리")

        # 6. 누락된 셀에 코멘트 추가
        print(f"\n📝 코멘트 추가 중... (총 {len(missing_df)}개)")

        for idx, row in missing_df.iterrows():
            index_value = str(row['Index']).strip()
            col_name = row['Column']
            cell_address = row['Cell']

            # Excel에서 코멘트 가져오기
            comment_text = excel_comments.get((index_value, col_name))

            if not comment_text:
                print(f"   ⚠️  [{idx+1}/{len(missing_df)}] Index={index_value}, {col_name} → Excel 코멘트 없음, 건너뛰기")
                self.stats["skipped"] += 1
                continue

            if self.dry_run:
                # Dry Run: 로그만 출력
                print(f"   [DRY RUN] [{idx+1}/{len(missing_df)}] Index={index_value}, {col_name} → 코멘트 추가 예정")
                self.stats["added"] += 1
            else:
                # 실제 추가
                try:
                    sheet.update_note(cell_address, comment_text)
                    print(f"   ✅ [{idx+1}/{len(missing_df)}] Index={index_value}, {col_name} → 코멘트 추가 (셀 {cell_address})")
                    self.stats["added"] += 1

                    # API 호출 제한 (1초 대기 - 분당 60회 제한)
                    time.sleep(1)

                except Exception as e:
                    print(f"   ❌ [{idx+1}/{len(missing_df)}] Index={index_value}, {col_name} → 실패: {e}")
                    self.stats["failed"] += 1

        # 7. 최종 결과
        print("\n" + "=" * 70)
        print("📊 코멘트 추가 결과")
        print("=" * 70)
        print(f"누락된 셀: {self.stats['total_missing']}개")
        print(f"추가된 코멘트: {self.stats['added']}개")
        print(f"건너뛴 셀: {self.stats['skipped']}개 (Excel 코멘트 없음)")
        print(f"실패한 셀: {self.stats['failed']}개")

        if self.dry_run:
            print("\n🔔 [DRY RUN] 시뮬레이션 완료. 실제 데이터는 변경되지 않았습니다.")
            print("   실제 추가를 하려면 --dry-run 플래그를 제거하세요.")
        else:
            print(f"\n🌐 Google Sheets에서 '{self.sheet_name}' 시트를 확인하세요!")

        # 8. 결과 저장
        self._save_results(missing_df)

        return True

    def _save_results(self, missing_df: pd.DataFrame):
        """
        결과를 CSV 파일로 저장

        Args:
            missing_df: 처리한 셀 목록 DataFrame
        """
        results_folder = Path(__file__).parent.parent / "results"
        results_folder.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comment_addition_results_{timestamp}.csv"
        filepath = results_folder / filename

        # 결과 추가
        result_df = missing_df.copy()
        result_df['Status'] = 'Added' if not self.dry_run else 'DryRun'

        result_df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"\n💾 결과 저장: {filepath}")


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="Google Sheets 누락된 셀 코멘트 추가 (Skip 방식)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="시뮬레이션 모드 (실제 추가 안 함)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="처리할 셀 개수 제한 (예: --limit 5)"
    )
    parser.add_argument(
        "--excel-path",
        type=str,
        default=None,
        help="Excel 파일 경로"
    )

    args = parser.parse_args()

    # Excel 파일 경로
    if args.excel_path:
        excel_path = Path(args.excel_path)
    else:
        excel_path = Path(__file__).parent.parent / "Coding & screening works-integrated.xlsx"

    # 코멘트 추가기 생성
    adder = MissingCommentAdder(
        excel_path=excel_path,
        sheet_name="CodedPapers_2",
        dry_run=args.dry_run,
        limit=args.limit
    )

    try:
        success = adder.add_missing_comments()

        if success:
            print("\n🎉 모든 작업 완료!")
            return True
        else:
            print("\n❌ 작업 실패")
            return False

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
