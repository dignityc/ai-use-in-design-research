"""
Excel 파일의 CodedPapers_2 데이터를 Google Sheets에 업로드
Skip 방식: 기존 Index는 절대 덮어쓰지 않고, 새로운 Index만 추가
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from typing import Dict, List, Set
import time
from datetime import datetime

# 상위 경로 추가
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector
from excel_to_dataframe import ExcelDataLoader


class ExcelToSheetsUploader:
    """Excel → Google Sheets Skip 방식 업로더"""

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
            sheet_name: 업로드할 Google Sheets 시트 이름
            dry_run: True이면 시뮬레이션만 (실제 업로드 안 함)
            limit: 처리할 논문 개수 제한 (None이면 전체)
        """
        self.excel_path = Path(excel_path)
        self.sheet_name = sheet_name
        self.dry_run = dry_run
        self.limit = limit

        # Google Sheets 연결
        self.sheets_connector = GoogleSheetsConnector()

        # Excel 데이터 로더
        self.excel_loader = ExcelDataLoader(self.excel_path)

        # 분류 컬럼 (7개)
        self.classification_columns = [
            "Design Discipline",
            "Data About",
            "Data Modality",
            "AI methods",
            "AI Assistance Types (Lee and Kim, 2025)",
            "Design Phase",
            "Design Practice/Task"
        ]

        # 헤더 컬럼 (13개)
        self.header_columns = [
            "Index", "Article Title", "Author Full Names", "Source Title",
            "Publication Year", "DOI Link", "Design Discipline", "Data About",
            "Data Modality", "AI methods", "AI Assistance Types (Lee and Kim, 2025)",
            "Design Phase", "Design Practice/Task"
        ]

        # 통계
        self.stats = {
            "total": 0,
            "skipped": 0,
            "added": 0,
            "comments_attached": 0
        }

    def get_existing_indices(self, sheet) -> Set[str]:
        """
        Google Sheets에 이미 있는 Index 목록 가져오기

        Args:
            sheet: 시트 객체

        Returns:
            Set[str]: 기존 Index 집합
        """
        print("🔍 Google Sheets 기존 Index 확인 중...")

        all_values = sheet.get_all_values()

        if len(all_values) <= 1:
            print("   ℹ️  시트가 비어있습니다. 모든 데이터를 새로 추가합니다.")
            return set()

        # 헤더와 데이터 분리
        headers = all_values[0]
        data_rows = all_values[1:]

        # Index 컬럼 찾기
        try:
            index_col_idx = headers.index("Index")
        except ValueError:
            print("   ⚠️  Index 컬럼을 찾을 수 없습니다.")
            return set()

        # Index 집합 생성
        existing_indices = set()
        for row in data_rows:
            if len(row) > index_col_idx and row[index_col_idx]:
                index_value = str(row[index_col_idx]).strip()
                if index_value:
                    existing_indices.add(index_value)

        print(f"   ✅ 기존 Index: {len(existing_indices)}개 발견")

        # 샘플 출력 (처음 10개)
        if existing_indices:
            sample_indices = sorted(existing_indices)[:10]
            print(f"   📋 샘플 Index: {', '.join(sample_indices)}...")

        return existing_indices

    def skip_based_upload(
        self,
        sheet,
        values_df: pd.DataFrame,
        comments_df: pd.DataFrame,
        existing_indices: Set[str]
    ) -> Dict[str, int]:
        """
        Skip 방식 업로드: 기존 Index는 건너뛰고, 새로운 Index만 추가

        Args:
            sheet: 시트 객체
            values_df: 셀 값 DataFrame
            comments_df: 코멘트 DataFrame
            existing_indices: 기존 Index 집합

        Returns:
            Dict[str, int]: 추가된 Index → 행 번호 매핑
        """
        print(f"\n📤 Skip 방식 업로드 시작...")

        if self.dry_run:
            print("   🔔 [DRY RUN] 시뮬레이션 모드 (실제 업로드 안 함)")

        added_indices = {}  # Index → 행 번호
        current_max_row = len(sheet.get_all_values())  # 현재 최대 행 번호

        # limit 처리
        if self.limit:
            values_df = values_df.head(self.limit)
            comments_df = comments_df.head(self.limit)
            print(f"   🔔 처리 개수 제한: {self.limit}개만 처리")

        self.stats["total"] = len(values_df)

        for idx, row in values_df.iterrows():
            paper_index = str(row['Index']).strip()

            # ⭐ Skip 로직: 기존에 있으면 완전히 건너뛰기
            if paper_index in existing_indices:
                print(f"   ⏭️  [{idx+1}/{len(values_df)}] Index={paper_index} → 이미 존재, 건너뛰기")
                self.stats["skipped"] += 1
                continue

            # 새로운 Index만 추가
            row_data = [str(row.get(col, "")) for col in self.header_columns]

            if self.dry_run:
                # Dry Run: 로그만 출력
                print(f"   [DRY RUN] [{idx+1}/{len(values_df)}] Index={paper_index} → 추가 예정")
                current_max_row += 1
                added_indices[paper_index] = current_max_row
                self.stats["added"] += 1
            else:
                # 실제 추가
                try:
                    sheet.append_row(row_data)
                    current_max_row += 1
                    added_indices[paper_index] = current_max_row

                    print(f"   ➕ [{idx+1}/{len(values_df)}] Index={paper_index} → 행 {current_max_row} 추가")
                    self.stats["added"] += 1

                    # API 호출 제한 (1초 대기)
                    time.sleep(1)

                except Exception as e:
                    print(f"   ❌ Index={paper_index} 추가 실패: {e}")

        print(f"\n✅ Skip 방식 업로드 완료")
        print(f"   - 총 처리: {self.stats['total']}개")
        print(f"   - 건너뛴 논문: {self.stats['skipped']}개 (기존 Index)")
        print(f"   - 추가된 논문: {self.stats['added']}개 (새로운 Index)")

        return added_indices

    def attach_cell_notes(
        self,
        sheet,
        comments_df: pd.DataFrame,
        added_indices: Dict[str, int]
    ):
        """
        셀 메모 첨부 (새로 추가된 논문만)

        Args:
            sheet: 시트 객체
            comments_df: 코멘트 DataFrame
            added_indices: 추가된 Index → 행 번호 매핑
        """
        if not added_indices:
            print("\n📝 셀 메모 첨부: 추가된 논문이 없습니다.")
            return

        print(f"\n📝 셀 메모 첨부 중... (새로 추가된 {len(added_indices)}개 논문)")

        if self.dry_run:
            print("   🔔 [DRY RUN] 시뮬레이션 모드 (실제 첨부 안 함)")

        # 헤더에서 각 분류 컬럼의 인덱스 찾기
        header_row = sheet.row_values(1)
        column_indices = {}
        for col in self.classification_columns:
            try:
                column_indices[col] = header_row.index(col) + 1  # 1-based index
            except ValueError:
                print(f"   ⚠️  '{col}' 컬럼을 찾을 수 없습니다.")

        # 추가된 논문만 필터링
        comments_df_filtered = comments_df[comments_df['Index'].isin(added_indices.keys())]

        total_notes = len(comments_df_filtered) * len(self.classification_columns)
        note_count = 0

        for idx, row in comments_df_filtered.iterrows():
            paper_index = str(row['Index']).strip()
            row_num = added_indices[paper_index]

            # 각 분류 컬럼별로 메모 첨부
            for category in self.classification_columns:
                if category not in column_indices:
                    continue

                col_num = column_indices[category]
                comment_text = str(row.get(category, "")).strip()

                # 코멘트가 비어있지 않으면 첨부
                if comment_text and comment_text.lower() not in ['nan', '', 'none']:
                    if self.dry_run:
                        # Dry Run: 로그만
                        note_count += 1
                        if note_count % 20 == 0:
                            print(f"   [DRY RUN] [{note_count}/{total_notes}] 메모 첨부 예정...")
                    else:
                        # 실제 첨부
                        try:
                            cell_label = sheet.cell(row_num, col_num).address
                            sheet.update_note(cell_label, comment_text)

                            note_count += 1
                            if note_count % 20 == 0:
                                print(f"   [{note_count}/{total_notes}] 메모 첨부 중...")

                            # API 호출 제한 (0.5초 대기)
                            time.sleep(0.5)

                        except Exception as e:
                            print(f"   ⚠️  메모 첨부 실패 (Index={paper_index}, {category}): {e}")

        self.stats["comments_attached"] = note_count
        print(f"\n✅ 셀 메모 첨부 완료: {note_count}개 메모")

    def upload(self):
        """전체 업로드 프로세스 실행"""
        print("=" * 70)
        print("🚀 Excel → Google Sheets 업로드 (Skip 방식)")
        print("=" * 70)

        if self.dry_run:
            print("🔔 [DRY RUN 모드] 시뮬레이션만 실행합니다. 실제 업로드는 하지 않습니다.")
        if self.limit:
            print(f"🔔 [제한 모드] 처음 {self.limit}개 논문만 처리합니다.")

        print()

        # 1. Excel 파일 로드
        print("📥 Excel 파일 로드 중...")
        try:
            values_df, comments_df = self.excel_loader.load_excel_with_comments()
        except Exception as e:
            print(f"❌ Excel 파일 로드 실패: {e}")
            return False

        # 2. Google Sheets 연결
        print("\n🔗 Google Sheets 연결 중...")
        if not self.sheets_connector.connect():
            print("❌ Google Sheets 연결 실패")
            return False
        print("   ✅ 연결 성공")

        # 3. 시트 가져오기
        try:
            sheet = self.sheets_connector.get_sheet(self.sheet_name)
            print(f"   ✅ 시트 발견: '{self.sheet_name}'")
        except Exception as e:
            print(f"❌ 시트를 찾을 수 없습니다: {e}")
            return False

        # 4. 기존 Index 목록 가져오기
        print()
        existing_indices = self.get_existing_indices(sheet)

        # 5. Skip 방식 업로드 (새로운 Index만 추가)
        added_indices = self.skip_based_upload(sheet, values_df, comments_df, existing_indices)

        # 6. 셀 메모 첨부 (새로 추가된 논문만)
        self.attach_cell_notes(sheet, comments_df, added_indices)

        # 7. 최종 결과
        print("\n" + "=" * 70)
        print("📊 업로드 결과")
        print("=" * 70)
        print(f"✅ Excel 데이터: {self.stats['total']}개 논문")
        print(f"✅ Google Sheets 기존: {len(existing_indices)}개 논문")
        print(f"⏭️  건너뛴 논문: {self.stats['skipped']}개 (기존 Index - 덮어쓰기 금지!)")
        print(f"➕ 추가된 논문: {self.stats['added']}개 (새로운 Index)")
        print(f"📝 첨부된 셀 메모: {self.stats['comments_attached']}개")

        if self.dry_run:
            print("\n🔔 [DRY RUN] 시뮬레이션 완료. 실제 데이터는 변경되지 않았습니다.")
            print("   실제 업로드를 하려면 --dry-run 플래그를 제거하세요.")
        else:
            print(f"\n🌐 Google Sheets에서 '{self.sheet_name}' 시트를 확인하세요!")

        return True


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="Excel 파일의 CodedPapers_2 데이터를 Google Sheets에 업로드 (Skip 방식)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="시뮬레이션 모드 (실제 업로드 안 함)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="처리할 논문 개수 제한 (예: --limit 5)"
    )
    parser.add_argument(
        "--excel-path",
        type=str,
        default=None,
        help="Excel 파일 경로 (기본: coding_work/Coding & screening works-integrated.xlsx)"
    )

    args = parser.parse_args()

    # Excel 파일 경로
    if args.excel_path:
        excel_path = Path(args.excel_path)
    else:
        excel_path = Path(__file__).parent.parent / "Coding & screening works-integrated.xlsx"

    # 업로더 생성
    uploader = ExcelToSheetsUploader(
        excel_path=excel_path,
        sheet_name="CodedPapers_2",
        dry_run=args.dry_run,
        limit=args.limit
    )

    try:
        success = uploader.upload()

        if success:
            print("\n🎉 모든 작업 완료!")
            return True
        else:
            print("\n❌ 업로드 실패")
            return False

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
