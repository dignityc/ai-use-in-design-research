"""
Google Sheets CodedPapers_2 시트의 셀 코멘트 누락 현황 조사
7개 분류 컬럼 (Design Discipline ~ Design Practice/Task)의 805개 셀 스캔
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import time
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


class CommentChecker:
    """셀 코멘트 누락 체커"""

    def __init__(self, sheet_name: str = "CodedPapers_2"):
        """
        초기화

        Args:
            sheet_name: 확인할 시트 이름
        """
        self.sheet_name = sheet_name
        self.connector = GoogleSheetsConnector()

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
            "total_cells": 0,
            "with_comment": 0,
            "without_comment": 0,
            "missing_list": []  # [(Index, Column, Row, Col)]
        }

    def check_missing_comments(self, sample_only: bool = False) -> pd.DataFrame:
        """
        Google Sheets에서 누락된 코멘트 확인 (gspread 방식)

        Args:
            sample_only: True이면 처음 10개 논문만 확인

        Returns:
            pd.DataFrame: 누락된 셀 목록
        """
        print("=" * 70)
        print("🔍 Google Sheets 셀 코멘트 누락 현황 조사")
        print("=" * 70)
        print()

        # 1. Google Sheets 연결
        print("🔗 Google Sheets 연결 중...")
        if not self.connector.connect():
            print("❌ Google Sheets 연결 실패")
            return pd.DataFrame()

        print("   ✅ 연결 성공")

        # 2. 시트 가져오기
        try:
            sheet = self.connector.get_sheet(self.sheet_name)
            print(f"   ✅ 시트 발견: '{self.sheet_name}'")
        except Exception as e:
            print(f"❌ 시트를 찾을 수 없습니다: {e}")
            return pd.DataFrame()

        # 3. 헤더 및 데이터 가져오기
        print("\n📥 시트 데이터 로드 중...")
        all_values = sheet.get_all_values()

        if len(all_values) <= 1:
            print("   ⚠️  시트가 비어있습니다.")
            return pd.DataFrame()

        headers = all_values[0]
        data_rows = all_values[1:]

        print(f"   ✅ 데이터 행: {len(data_rows)}개")

        # 4. Index 컬럼 및 분류 컬럼 인덱스 찾기
        try:
            index_col_idx = headers.index("Index")
        except ValueError:
            print("   ⚠️  Index 컬럼을 찾을 수 없습니다.")
            return pd.DataFrame()

        # 분류 컬럼 인덱스 매핑
        column_indices = {}
        for col in self.classification_columns:
            try:
                column_indices[col] = headers.index(col) + 1  # 1-based index for gspread
            except ValueError:
                print(f"   ⚠️  '{col}' 컬럼을 찾을 수 없습니다.")

        print(f"   ✅ 분류 컬럼: {len(column_indices)}개 발견")

        # 5. 샘플 모드 처리
        if sample_only:
            data_rows = data_rows[:10]
            print(f"\n🔔 샘플 모드: 처음 10개 논문만 확인")

        # 6. 각 셀의 코멘트 확인
        print(f"\n📝 셀 코멘트 스캔 중... (총 {len(data_rows)} × {len(column_indices)} = {len(data_rows) * len(column_indices)}개 셀)")
        print("   ⚠️  API 제한으로 0.5초씩 대기 (시간 소요 예상)")

        self.stats["total_cells"] = len(data_rows) * len(column_indices)

        for row_idx, row in enumerate(data_rows, start=2):  # 2부터 시작 (1=헤더)
            # Index 값
            if len(row) <= index_col_idx or not row[index_col_idx]:
                continue

            index_value = str(row[index_col_idx]).strip()

            # 각 분류 컬럼 확인
            for col_name, col_num in column_indices.items():
                try:
                    # 셀 주소 (A1 notation)
                    cell_address = self._get_cell_address(row_idx, col_num)

                    # 코멘트 확인 (get_note 메서드 사용)
                    note = sheet.get_note(cell_address)

                    if note:
                        self.stats["with_comment"] += 1
                    else:
                        self.stats["without_comment"] += 1
                        self.stats["missing_list"].append({
                            "Index": index_value,
                            "Column": col_name,
                            "Row": row_idx,
                            "Col": col_num,
                            "Cell": cell_address
                        })

                    # 진행 상황 출력
                    total_checked = self.stats["with_comment"] + self.stats["without_comment"]
                    if total_checked % 50 == 0:
                        print(f"   [{total_checked}/{self.stats['total_cells']}] 확인 중... (코멘트 있음: {self.stats['with_comment']}, 없음: {self.stats['without_comment']})")

                    # API 호출 제한 (1초 대기 - 분당 60회 제한)
                    time.sleep(1)

                except Exception as e:
                    print(f"   ⚠️  에러 (Index={index_value}, {col_name}): {e}")

        # 7. 결과 출력
        print("\n" + "=" * 70)
        print("📊 조사 결과")
        print("=" * 70)
        print(f"총 셀 개수: {self.stats['total_cells']}개 ({len(data_rows)}개 논문 × {len(column_indices)}개 컬럼)")
        print(f"코멘트 있음: {self.stats['with_comment']}개 ({self.stats['with_comment'] / self.stats['total_cells'] * 100:.1f}%)")
        print(f"코멘트 없음: {self.stats['without_comment']}개 ({self.stats['without_comment'] / self.stats['total_cells'] * 100:.1f}%)")

        # 8. 누락된 셀 샘플 출력
        if self.stats["missing_list"]:
            print(f"\n⚠️  누락된 셀 샘플 (처음 20개):")
            for i, missing in enumerate(self.stats["missing_list"][:20], 1):
                print(f"   {i}. Index={missing['Index']}, 컬럼={missing['Column']}, 셀={missing['Cell']}")

            if len(self.stats["missing_list"]) > 20:
                print(f"   ... (총 {len(self.stats['missing_list'])}개)")
        else:
            print(f"\n✅ 모든 셀에 코멘트가 있습니다!")

        # 9. DataFrame으로 변환
        missing_df = pd.DataFrame(self.stats["missing_list"])

        return missing_df

    def _get_cell_address(self, row: int, col: int) -> str:
        """
        행/열 번호를 A1 notation으로 변환

        Args:
            row: 행 번호 (1-based)
            col: 열 번호 (1-based)

        Returns:
            str: A1 notation (예: "G2", "M10")
        """
        # 열 번호를 알파벳으로 변환
        col_letter = ""
        temp = col
        while temp > 0:
            temp -= 1
            col_letter = chr(65 + (temp % 26)) + col_letter
            temp //= 26

        return f"{col_letter}{row}"

    def save_results(self, missing_df: pd.DataFrame) -> str:
        """
        결과를 CSV 파일로 저장

        Args:
            missing_df: 누락된 셀 목록 DataFrame

        Returns:
            str: 저장된 파일 경로
        """
        # 결과 폴더
        results_folder = Path(__file__).parent.parent / "results"
        results_folder.mkdir(exist_ok=True)

        # 파일명
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"missing_comments_{timestamp}.csv"
        filepath = results_folder / filename

        # CSV 저장
        if not missing_df.empty:
            missing_df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"\n💾 결과 저장: {filepath}")
            print(f"   - {len(missing_df)}개 누락 셀 정보")
        else:
            # 빈 DataFrame이면 통계만 저장
            stats_df = pd.DataFrame([{
                "total_cells": self.stats["total_cells"],
                "with_comment": self.stats["with_comment"],
                "without_comment": self.stats["without_comment"]
            }])
            stats_df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"\n💾 통계 저장: {filepath}")

        return str(filepath)


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="Google Sheets 셀 코멘트 누락 현황 조사"
    )
    parser.add_argument(
        "--sample-only",
        action="store_true",
        help="처음 10개 논문만 확인 (빠른 테스트용)"
    )

    args = parser.parse_args()

    checker = CommentChecker()

    try:
        # 누락 현황 조사
        missing_df = checker.check_missing_comments(sample_only=args.sample_only)

        # 결과 저장
        if missing_df is not None:
            checker.save_results(missing_df)

        print("\n" + "=" * 70)
        print("🎉 조사 완료!")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
