"""
PDF 분석 결과를 Google Sheets에 업로드하는 스크립트
CodedPapers_2 시트에 Index 기준 Upsert + 셀 메모 첨부
"""

import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time

# 상위 경로 추가
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


class PDFDataUploader:
    """PDF 분석 결과 Google Sheets 업로더"""

    def __init__(self, sheet_name: str = "CodedPapers_2"):
        """
        초기화

        Args:
            sheet_name: 업로드할 시트 이름 (기본: CodedPapers_2)
        """
        self.sheet_name = sheet_name
        self.sheets_connector = GoogleSheetsConnector()

        # CSV 파일 경로 설정
        self.results_folder = Path(__file__).parent.parent / "results" / "pdf_analysis"
        self.classifications_file = self.results_folder / "pdf_classifications.csv"
        self.references_file = self.results_folder / "pdf_references.csv"

        # 분류 카테고리 컬럼명 (7개 - 셀 메모를 첨부할 대상)
        self.classification_columns = [
            "Design Discipline",
            "Data About",
            "Data Modality",
            "AI methods",
            "AI Assistance Types (Lee and Kim, 2025)",
            "Design Phase",
            "Design Practice/Task"
        ]

        # 헤더 컬럼 순서 (13개 - Notes, Questions 제거)
        self.header_columns = [
            "Index", "Article Title", "Author Full Names", "Source Title",
            "Publication Year", "DOI Link", "Design Discipline", "Data About",
            "Data Modality", "AI methods", "AI Assistance Types (Lee and Kim, 2025)",
            "Design Phase", "Design Practice/Task"
        ]

    def fetch_metadata_from_sheets(self, indices: List[str]) -> pd.DataFrame:
        """
        3rd Screening 시트에서 Index 기준으로 메타데이터 가져오기

        Args:
            indices: 가져올 Index 목록

        Returns:
            pd.DataFrame: Index, Article Title, Author Full Names, Source Title,
                         Publication Year, DOI Link 컬럼을 포함한 DataFrame
        """
        print("📥 3rd Screening 시트에서 메타데이터 로드 중...")

        try:
            # 3rd Screening 시트 가져오기
            sheet = self.sheets_connector.get_sheet("3rd Screening")
            all_values = sheet.get_all_values()

            if len(all_values) < 2:
                print("   ⚠️  3rd Screening 시트가 비어있습니다.")
                return pd.DataFrame()

            # 헤더와 데이터 분리
            headers = all_values[0]
            data_rows = all_values[1:]

            # DataFrame 생성
            df = pd.DataFrame(data_rows, columns=headers)

            # 필요한 컬럼만 선택
            required_columns = [
                "Index", "Article Title", "Author Full Names", "Source Title",
                "Publication Year", "DOI Link"
            ]

            # 컬럼 존재 확인
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"   ⚠️  경고: 다음 컬럼을 찾을 수 없습니다: {missing_columns}")
                # 없는 컬럼은 빈 값으로 채우기
                for col in missing_columns:
                    df[col] = ""

            # Index 필터링 (요청된 Index만)
            df['Index'] = df['Index'].astype(str).str.strip()
            filtered_df = df[df['Index'].isin(indices)][required_columns]

            print(f"   ✅ 메타데이터 로드 완료: {len(filtered_df)}개 논문")

            return filtered_df

        except Exception as e:
            print(f"   ❌ 메타데이터 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def load_csv_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        CSV 파일 로드 (분류값 + 참고 원문) + Google Sheets 메타데이터 병합

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (분류 데이터, 참고 원문 데이터)
        """
        print("📥 CSV 파일 로드 중...")

        # 1. 분류 데이터 로드
        if not self.classifications_file.exists():
            raise FileNotFoundError(f"분류 CSV 파일을 찾을 수 없습니다: {self.classifications_file}")

        classifications_df = pd.read_csv(self.classifications_file, encoding='utf-8')
        print(f"   ✅ 분류 데이터: {len(classifications_df)}개 논문")

        # 2. 참고 원문 로드
        if not self.references_file.exists():
            raise FileNotFoundError(f"참고 원문 CSV 파일을 찾을 수 없습니다: {self.references_file}")

        references_df = pd.read_csv(self.references_file, encoding='utf-8')
        print(f"   ✅ 참고 원문: {len(references_df)}개 논문")

        # 3. Index 일치 확인
        if not classifications_df['Index'].equals(references_df['Index']):
            print("⚠️  경고: 분류 데이터와 참고 원문의 Index가 일치하지 않습니다.")

        # 4. Google Sheets에서 메타데이터 가져오기
        indices = classifications_df['Index'].astype(str).str.strip().tolist()
        metadata_df = self.fetch_metadata_from_sheets(indices)

        # 5. 메타데이터와 분류 데이터 병합 (Index 기준)
        if not metadata_df.empty:
            print("🔗 메타데이터 병합 중...")

            # Index를 문자열로 변환하여 매칭
            classifications_df['Index'] = classifications_df['Index'].astype(str).str.strip()
            references_df['Index'] = references_df['Index'].astype(str).str.strip()
            metadata_df['Index'] = metadata_df['Index'].astype(str).str.strip()

            # 병합할 컬럼들 (Google Sheets의 정확한 데이터로 교체)
            metadata_columns = ["Article Title", "Author Full Names", "Source Title",
                               "Publication Year", "DOI Link"]

            # 기존 메타데이터 컬럼 제거
            classifications_df = classifications_df.drop(columns=metadata_columns, errors='ignore')
            references_df = references_df.drop(columns=metadata_columns, errors='ignore')

            # 메타데이터 병합 (left join)
            classifications_df = classifications_df.merge(
                metadata_df,
                on="Index",
                how="left"
            )

            references_df = references_df.merge(
                metadata_df,
                on="Index",
                how="left"
            )

            # 컬럼 순서 재정렬 (header_columns 순서대로)
            # 분류 데이터
            available_cols_class = [col for col in self.header_columns if col in classifications_df.columns]
            classifications_df = classifications_df[available_cols_class]

            # 참고 원문 데이터
            available_cols_ref = [col for col in self.header_columns if col in references_df.columns]
            references_df = references_df[available_cols_ref]

            print(f"   ✅ 메타데이터 병합 완료")
        else:
            print("   ⚠️  메타데이터를 가져오지 못했습니다. CSV 데이터만 사용합니다.")

        return classifications_df, references_df

    def find_or_create_sheet(self):
        """
        CodedPapers_2 시트 찾기 또는 생성 (헤더 확인 및 추가 포함)

        Returns:
            gspread.Worksheet: 시트 객체
        """
        try:
            # 시트 찾기
            sheet = self.sheets_connector.get_sheet(self.sheet_name)
            print(f"   ✅ 시트 발견: '{self.sheet_name}'")

            # 헤더 확인
            first_row = sheet.row_values(1) if sheet.row_count > 0 else []

            # 헤더가 없거나 잘못되어 있으면 추가
            if not first_row or first_row[0] != "Index":
                print(f"   ⚠️  헤더가 없습니다. 헤더를 추가합니다.")

                # 기존 데이터가 있으면 한 칸 아래로 밀기
                if first_row:
                    sheet.insert_row(self.header_columns, 1)
                    print(f"   ✅ 헤더 추가 완료 (기존 데이터는 2행부터 유지)")
                else:
                    # 빈 시트면 헤더만 추가
                    sheet.append_row(self.header_columns)
                    print(f"   ✅ 헤더 추가 완료")

                time.sleep(1)  # API 호출 제한

            return sheet

        except Exception as e:
            # 시트가 없으면 생성
            print(f"   ℹ️  시트가 없습니다. 새로 생성합니다: '{self.sheet_name}'")
            try:
                spreadsheet = self.sheets_connector.spreadsheet
                sheet = spreadsheet.add_worksheet(title=self.sheet_name, rows=1000, cols=20)

                # 헤더 추가
                sheet.append_row(self.header_columns)
                print(f"   ✅ 시트 생성 완료: '{self.sheet_name}'")
                time.sleep(1)  # API 호출 제한
                return sheet
            except Exception as create_error:
                print(f"❌ 시트 생성 실패: {create_error}")
                raise

    def get_existing_indices(self, sheet) -> Dict[str, int]:
        """
        시트에 있는 기존 Index 목록 및 행 번호 가져오기

        Args:
            sheet: 시트 객체

        Returns:
            Dict[str, int]: {Index: 행 번호} 매핑
        """
        print("🔍 기존 Index 목록 확인 중...")

        # 시트 전체 데이터 가져오기
        all_values = sheet.get_all_values()

        if len(all_values) <= 1:
            # 헤더만 있거나 빈 시트
            print("   ℹ️  시트가 비어있습니다. 모든 데이터를 새로 추가합니다.")
            return {}

        # 헤더와 데이터 분리
        headers = all_values[0]
        data_rows = all_values[1:]

        # Index 컬럼 찾기
        try:
            index_col_idx = headers.index("Index")
        except ValueError:
            print("   ⚠️  Index 컬럼을 찾을 수 없습니다. 헤더를 확인하세요.")
            return {}

        # Index → 행 번호 매핑 (행 번호는 2부터 시작: 1=헤더)
        existing_indices = {}
        for i, row in enumerate(data_rows, start=2):
            if len(row) > index_col_idx and row[index_col_idx]:
                index_value = str(row[index_col_idx]).strip()
                if index_value:
                    existing_indices[index_value] = i

        print(f"   ✅ 기존 Index: {len(existing_indices)}개 발견")
        return existing_indices

    def upsert_row_data(self, sheet, classifications_df: pd.DataFrame, existing_indices: Dict[str, int]) -> Dict[str, int]:
        """
        Index 기준 Upsert (Update or Insert)

        Args:
            sheet: 시트 객체
            classifications_df: 분류 데이터 DataFrame
            existing_indices: 기존 Index → 행 번호 매핑

        Returns:
            Dict[str, int]: 업데이트된 Index → 행 번호 매핑 (셀 메모 첨부용)
        """
        print(f"🔄 Index 기준 Upsert 중... (총 {len(classifications_df)}개)")

        updated_indices = {}  # Index → 행 번호 매핑

        for idx, row in classifications_df.iterrows():
            paper_index = str(row['Index']).strip()

            # 행 데이터 준비 (13개 컬럼 순서대로)
            row_data = [str(row.get(col, "")) for col in self.header_columns]

            if paper_index in existing_indices:
                # 기존 행 업데이트
                row_num = existing_indices[paper_index]

                # 범위 지정하여 업데이트 (A1 notation)
                range_name = f"A{row_num}:M{row_num}"  # 13개 컬럼 (A-M)
                sheet.update(values=[row_data], range_name=range_name)

                print(f"   [{idx+1}/{len(classifications_df)}] Index={paper_index} → 행 {row_num} 업데이트")
                updated_indices[paper_index] = row_num
            else:
                # 새 행 추가
                sheet.append_row(row_data)

                # 새로 추가된 행 번호 계산 (기존 행 개수 + 1)
                new_row_num = len(existing_indices) + idx + 2  # 2 = 헤더(1) + 0-based index 보정

                print(f"   [{idx+1}/{len(classifications_df)}] Index={paper_index} → 새 행 {new_row_num} 추가")
                updated_indices[paper_index] = new_row_num

            # API 호출 제한 (1초 대기)
            time.sleep(1)

        print(f"✅ Upsert 완료: {len(updated_indices)}개 행 처리")
        return updated_indices

    def attach_cell_notes(self, sheet, references_df: pd.DataFrame, updated_indices: Dict[str, int]):
        """
        셀 메모 첨부 (각 분류 카테고리 셀에 참고 원문 추가)

        Args:
            sheet: 시트 객체
            references_df: 참고 원문 DataFrame
            updated_indices: Index → 행 번호 매핑
        """
        print(f"📝 셀 메모 첨부 중...")

        # 헤더에서 각 분류 카테고리의 컬럼 인덱스 찾기
        header_row = sheet.row_values(1)
        column_indices = {}
        for col in self.classification_columns:
            try:
                column_indices[col] = header_row.index(col) + 1  # 1-based index
            except ValueError:
                print(f"   ⚠️  경고: '{col}' 컬럼을 찾을 수 없습니다.")

        # 총 메모 개수 계산
        total_notes = len(references_df) * len(self.classification_columns)
        note_count = 0

        for idx, row in references_df.iterrows():
            paper_index = str(row['Index']).strip()

            if paper_index not in updated_indices:
                print(f"   ⚠️  Index={paper_index} 행을 찾을 수 없습니다. 건너뜁니다.")
                continue

            row_num = updated_indices[paper_index]

            # 각 분류 카테고리별로 메모 첨부
            for category in self.classification_columns:
                if category not in column_indices:
                    continue

                col_num = column_indices[category]
                reference_text = str(row.get(category, "")).strip()

                # 참고 원문이 비어있지 않으면 메모 첨부
                if reference_text and reference_text.lower() not in ['nan', '', 'none']:
                    try:
                        # 셀 좌표 (A1 notation)
                        cell_label = sheet.cell(row_num, col_num).address

                        # 메모 첨부 (gspread의 update_note 메서드 사용)
                        sheet.update_note(cell_label, reference_text)

                        note_count += 1
                        if note_count % 10 == 0:
                            print(f"   [{note_count}/{total_notes}] 메모 첨부 중...")

                        # API 호출 제한 (0.5초 대기 - 메모는 빈번하므로 짧게)
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"   ⚠️  메모 첨부 실패 (Index={paper_index}, {category}): {e}")

        print(f"✅ 셀 메모 첨부 완료: {note_count}개 메모")

    def upload_to_sheets(self):
        """전체 업로드 프로세스 실행"""
        print("=" * 60)
        print("🚀 PDF 분석 결과 → Google Sheets 업로드 시작")
        print("=" * 60)

        # 1. Google Sheets 연결 (먼저 연결해야 메타데이터 가져오기 가능)
        print("\n🔗 Google Sheets 연결 중...")
        if not self.sheets_connector.connect():
            print("❌ Google Sheets 연결 실패")
            return False
        print(f"   ✅ 스프레드시트: 연결 성공")

        # 2. CSV 파일 로드 (메타데이터 병합 포함)
        print()
        classifications_df, references_df = self.load_csv_data()

        # 3. 시트 찾기 또는 생성
        print()
        sheet = self.find_or_create_sheet()

        # 4. 기존 Index 목록 가져오기
        existing_indices = self.get_existing_indices(sheet)

        # 5. Index 기준 Upsert
        print()
        updated_indices = self.upsert_row_data(sheet, classifications_df, existing_indices)

        # 6. 셀 메모 첨부
        print()
        self.attach_cell_notes(sheet, references_df, updated_indices)

        # 7. 최종 결과
        print("\n" + "=" * 60)
        print("📊 업로드 완료!")
        print("=" * 60)
        print(f"✅ 총 {len(updated_indices)}개 논문 업로드")
        print(f"   - 업데이트: {sum(1 for idx in updated_indices if idx in existing_indices)}개")
        print(f"   - 새로 추가: {sum(1 for idx in updated_indices if idx not in existing_indices)}개")
        print(f"📝 셀 메모: 7개 분류 카테고리 × {len(references_df)}개 논문")
        print(f"\n🌐 Google Sheets에서 '{self.sheet_name}' 시트를 확인하세요!")

        return True


def main():
    """메인 실행 함수"""
    uploader = PDFDataUploader(sheet_name="CodedPapers_2")

    try:
        success = uploader.upload_to_sheets()
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
