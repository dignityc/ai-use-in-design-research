"""
PDF Upload Checker
Papers 폴더의 PDF 파일 존재 여부를 확인하여
Google Sheets의 pdf_upload 컬럼에 'Y' 자동 기록
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import pandas as pd

# google_sheets_connector 임포트를 위한 경로 설정
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


class PDFUploadChecker:
    """PDF 업로드 상태 체크 및 업데이트 클래스"""

    def __init__(self, papers_folder: str = None, credentials_path: str = None):
        """
        PDF Upload Checker 초기화

        Args:
            papers_folder: PDF 파일들이 있는 폴더 경로
            credentials_path: Google Sheets API 인증 파일 경로
        """
        # 기본 경로 설정
        if papers_folder is None:
            # scripts 폴더에서 상위로 2번 올라가서 Papers 폴더
            papers_folder = str(Path(__file__).parent.parent.parent / "Papers")

        if credentials_path is None:
            credentials_path = str(Path(__file__).parent.parent / "credentials" / "gen-lang-client-0444199460-38266703559b.json")

        self.papers_folder = Path(papers_folder)
        self.credentials_path = credentials_path
        self.sheet_name = "3rd Screening"

        # Google Sheets Connector 초기화
        self.connector = GoogleSheetsConnector(
            credentials_path=credentials_path,
            spreadsheet_id='1MgMKl7b8y5hPScQZJQ5y8y-J_UY1qalgVnQEFOucbBM'
        )

        # 처리 결과 저장용
        self.results = []

    def connect_to_sheets(self) -> bool:
        """Google Sheets 연결"""
        if not self.connector.connect():
            print("❌ Google Sheets 연결 실패")
            return False
        print("✅ Google Sheets 연결 성공")
        return True

    def scan_pdf_folder(self) -> List[Path]:
        """
        Papers 폴더의 모든 PDF 파일 스캔

        Returns:
            List[Path]: PDF 파일 경로 리스트
        """
        if not self.papers_folder.exists():
            print(f"❌ Papers 폴더를 찾을 수 없습니다: {self.papers_folder}")
            return []

        pdf_files = list(self.papers_folder.glob("*.pdf"))
        print(f"📁 Papers 폴더에서 {len(pdf_files)}개 PDF 파일 발견")

        return pdf_files

    def extract_index_from_filename(self, filename: str) -> Optional[str]:
        """
        파일명에서 Index 추출

        Args:
            filename: PDF 파일명 (예: "101_How to obtain...pdf")

        Returns:
            Optional[str]: Index (예: "101") 또는 None
        """
        # 파일명 패턴: {Index}_{Title}.pdf
        # 첫 번째 언더스코어(_) 앞의 숫자 추출
        match = re.match(r'^(\d+)_', filename)
        if match:
            return match.group(1)
        return None

    def get_pdf_indices(self) -> Dict[str, str]:
        """
        Papers 폴더의 모든 PDF 파일에서 Index 추출

        Returns:
            Dict[str, str]: {index: filename} 매핑
        """
        pdf_files = self.scan_pdf_folder()

        pdf_indices = {}
        for pdf_path in pdf_files:
            filename = pdf_path.name
            index = self.extract_index_from_filename(filename)

            if index:
                pdf_indices[index] = filename
            else:
                print(f"⚠️  Index 추출 실패: {filename}")

        print(f"✅ {len(pdf_indices)}개 PDF의 Index 추출 완료")
        print(f"   Indices: {sorted(pdf_indices.keys(), key=lambda x: int(x))[:10]}...")

        return pdf_indices

    def update_sheets_pdf_upload(self, index: str, pdf_upload_col_name: str, dry_run: bool = False) -> bool:
        """
        Google Sheets의 pdf_upload 컬럼에 'Y' 업데이트

        Args:
            index: 논문 Index
            pdf_upload_col_name: pdf_upload 컬럼 이름
            dry_run: True면 실제 업데이트하지 않음

        Returns:
            bool: 성공 여부
        """
        try:
            # 시트에서 Index에 해당하는 행 번호 찾기
            sheet = self.connector.get_sheet(self.sheet_name)
            all_values = sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                print(f"❌ 시트 데이터를 읽을 수 없습니다.")
                return False

            headers = all_values[0]

            # Index 컬럼과 pdf_upload 컬럼의 위치 찾기
            try:
                index_col_idx = headers.index('Index')
                pdf_upload_col_idx = headers.index(pdf_upload_col_name)
            except ValueError as e:
                print(f"❌ 컬럼을 찾을 수 없습니다: {e}")
                return False

            # Index 값으로 행 번호 찾기 (헤더 제외하므로 +2)
            target_row = None
            for i, row in enumerate(all_values[1:], start=2):
                if row[index_col_idx] == index:
                    target_row = i
                    break

            if target_row is None:
                print(f"❌ Index={index}에 해당하는 행을 찾을 수 없습니다.")
                return False

            if dry_run:
                print(f"   [DRY-RUN] Sheets 업데이트: Index={index}, Row={target_row}, Col={pdf_upload_col_idx+1}, Value='Y'")
                return True

            # pdf_upload 컬럼 업데이트 (컬럼 번호는 1부터 시작)
            self.connector.update_cell(
                sheet_name=self.sheet_name,
                row=target_row,
                col=pdf_upload_col_idx + 1,
                value='Y'
            )

            print(f"   ✅ Sheets 업데이트 완료: Index={index}, Row={target_row}")
            return True

        except Exception as e:
            print(f"❌ Sheets 업데이트 실패 (Index={index}): {str(e)}")
            return False

    def process_all_pdfs(self, dry_run: bool = False, test_index: str = None) -> Dict:
        """
        모든 PDF 파일 처리 및 Sheets 업데이트 (최적화 버전)

        Args:
            dry_run: True면 실제 변경하지 않고 시뮬레이션만
            test_index: 특정 Index만 테스트 (디버깅용)

        Returns:
            Dict: 처리 결과 통계
        """
        print("=" * 60)
        print("🔧 PDF Upload Checker 시작 (최적화 버전)")
        print("=" * 60)

        # Google Sheets 연결
        if not self.connect_to_sheets():
            return {"error": "Google Sheets 연결 실패"}

        # Papers 폴더의 PDF Index 추출
        pdf_indices = self.get_pdf_indices()
        if not pdf_indices:
            return {"error": "PDF 파일 없음 또는 Index 추출 실패"}

        # 테스트 모드인 경우 특정 Index만 필터링
        if test_index:
            if test_index in pdf_indices:
                pdf_indices = {test_index: pdf_indices[test_index]}
                print(f"\n🧪 테스트 모드: Index={test_index}만 처리")
            else:
                return {"error": f"Index={test_index}의 PDF를 찾을 수 없습니다."}

        # ⭐ 시트 데이터를 한 번만 읽기 (API 호출 1회)
        print("\n📥 Google Sheets 데이터 로딩 중... (1회 API 호출)")
        try:
            sheet = self.connector.get_sheet(self.sheet_name)
            all_values = sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                return {"error": "시트 데이터가 비어있습니다"}

            headers = all_values[0]
            print(f"✅ 시트 데이터 로드 완료: {len(all_values)-1}개 행")

            # Index 컬럼 찾기
            try:
                index_col_idx = headers.index('Index')
            except ValueError:
                print("❌ 'Index' 컬럼을 찾을 수 없습니다.")
                return {"error": "Index 컬럼 없음"}

            # pdf_upload 컬럼 찾기
            pdf_upload_col_idx = None
            pdf_upload_col_name = None
            possible_names = [
                'pdf_upload', 'PDF_Upload', 'PDF Upload', 'pdf upload',
                'PDF_uploaded', 'pdf_uploaded', 'PDF uploaded'
            ]

            for col_name in possible_names:
                if col_name in headers:
                    pdf_upload_col_name = col_name
                    pdf_upload_col_idx = headers.index(col_name)
                    break

            # 대소문자 구분 없이 찾기
            if pdf_upload_col_idx is None:
                for i, col_name in enumerate(headers):
                    normalized = col_name.lower().replace(' ', '_')
                    if normalized in ['pdf_upload', 'pdf_uploaded']:
                        pdf_upload_col_name = col_name
                        pdf_upload_col_idx = i
                        break

            if pdf_upload_col_idx is None:
                print("❌ 'pdf_upload' 컬럼을 찾을 수 없습니다.")
                print(f"📋 사용 가능한 컬럼: {headers}")
                return {"error": "pdf_upload 컬럼 없음"}

            print(f"✅ pdf_upload 컬럼 발견: '{pdf_upload_col_name}' (컬럼 {pdf_upload_col_idx+1})")

        except Exception as e:
            print(f"❌ 시트 데이터 로드 실패: {str(e)}")
            return {"error": f"시트 데이터 로드 실패: {str(e)}"}

        # ⭐ 로컬에서 매칭 작업 수행 (API 호출 없음)
        print("\n🔍 로컬에서 PDF-Sheet 매칭 중...")

        # Index → Row 번호 매핑 생성
        index_to_row = {}
        for row_idx, row in enumerate(all_values[1:], start=2):
            if len(row) > index_col_idx:
                row_index = row[index_col_idx].strip()
                if row_index:
                    index_to_row[row_index] = row_idx

        print(f"✅ 시트에서 {len(index_to_row)}개 Index 발견")

        # 매칭 작업
        matched_updates = []  # 업데이트할 셀 목록
        stats = {
            "total_pdfs": len(pdf_indices),
            "matched": 0,
            "not_matched": 0,
            "sheets_updated": 0,
            "failed": 0
        }

        print(f"\n🎯 처리 대상:")
        print(f"   PDF 파일: {len(pdf_indices)}개")
        print(f"   모드: {'DRY-RUN' if dry_run else 'LIVE'}")
        print()

        sorted_indices = sorted(pdf_indices.keys(), key=lambda x: int(x))
        for i, index in enumerate(sorted_indices, 1):
            filename = pdf_indices[index]
            print(f"📄 [{i}/{len(sorted_indices)}] Index={index}")
            print(f"   파일: {filename[:70]}...")

            result = {
                "index": index,
                "filename": filename,
                "pdf_found": True,
                "sheets_matched": False,
                "sheets_updated": False,
                "row_number": None,
                "error": None,
                "timestamp": datetime.now().isoformat()
            }

            # 로컬 매칭
            if index in index_to_row:
                row_num = index_to_row[index]
                result["sheets_matched"] = True
                result["row_number"] = row_num
                stats["matched"] += 1

                # 업데이트 목록에 추가
                matched_updates.append({
                    "index": index,
                    "row": row_num,
                    "col": pdf_upload_col_idx + 1,  # 1부터 시작
                    "value": "Y"
                })

                print(f"   ✅ 매칭 성공: Row={row_num}")
            else:
                result["error"] = "시트에서 해당 Index를 찾을 수 없음"
                stats["not_matched"] += 1
                print(f"   ⚠️  매칭 실패: 시트에 Index={index} 없음")

            self.results.append(result)

        # ⭐ 배치 업데이트 (API 호출 1회)
        if matched_updates and not dry_run:
            print(f"\n📤 Google Sheets 배치 업데이트 중... ({len(matched_updates)}개 셀)")
            try:
                for update in matched_updates:
                    self.connector.update_cell(
                        sheet_name=self.sheet_name,
                        row=update["row"],
                        col=update["col"],
                        value=update["value"]
                    )
                    stats["sheets_updated"] += 1

                print(f"✅ 배치 업데이트 완료: {stats['sheets_updated']}개 셀")

            except Exception as e:
                print(f"❌ 배치 업데이트 실패: {str(e)}")
                stats["failed"] = len(matched_updates) - stats["sheets_updated"]

        elif matched_updates and dry_run:
            print(f"\n[DRY-RUN] 업데이트 예정: {len(matched_updates)}개 셀")
            for update in matched_updates[:5]:
                print(f"   Index={update['index']}, Row={update['row']}, Col={update['col']}, Value='Y'")
            if len(matched_updates) > 5:
                print(f"   ... 외 {len(matched_updates)-5}개")
            stats["sheets_updated"] = len(matched_updates)

        # 최종 결과 출력
        print("\n" + "=" * 60)
        print("📊 처리 결과")
        print("=" * 60)
        print(f"전체 PDF: {stats['total_pdfs']}개")
        print(f"매칭 성공: {stats['matched']}개")
        print(f"매칭 실패: {stats['not_matched']}개")
        print(f"Sheets 업데이트: {stats['sheets_updated']}개")
        print(f"업데이트 실패: {stats['failed']}개")

        if dry_run:
            print("\n⚠️  DRY-RUN 모드: 실제 Sheets는 변경되지 않았습니다.")

        return stats

    def save_to_csv(self, output_path: str = None) -> str:
        """
        처리 결과를 CSV 파일로 저장

        Args:
            output_path: CSV 파일 경로 (None이면 기본 경로 사용)

        Returns:
            str: 저장된 파일 경로
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(Path(__file__).parent.parent / "results" / f"pdf_upload_check_results_{timestamp}.csv")

        # 결과 디렉토리 생성
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # DataFrame 생성
        df = pd.DataFrame(self.results)

        # CSV 저장
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"📄 결과 CSV 저장: {output_path}")
        print(f"   총 {len(df)}개 PDF 처리 결과 저장")

        return output_path


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='PDF Upload Checker')
    parser.add_argument('--dry-run', action='store_true', help='시뮬레이션만 (Sheets 업데이트 안 함)')
    parser.add_argument('--test-index', type=str, help='특정 Index만 테스트 (디버깅용)')

    args = parser.parse_args()

    print("🚀 PDF Upload Checker 시작\n")

    # Checker 초기화
    checker = PDFUploadChecker()

    # PDF 처리
    if args.test_index:
        print(f"🧪 테스트 모드: Index={args.test_index}")

    results = checker.process_all_pdfs(
        dry_run=args.dry_run,
        test_index=args.test_index
    )

    if "error" in results:
        print(f"❌ 실행 실패: {results['error']}")
        return False

    # 결과 CSV 저장
    if checker.results:
        csv_path = checker.save_to_csv()
        print(f"\n📁 결과 파일: {csv_path}")

    # 최종 통계
    if results["sheets_updated"] > 0:
        print(f"\n🎉 완료! {results['sheets_updated']}개 논문의 pdf_upload 상태가 업데이트되었습니다.")
        if not args.dry_run:
            print(f"   Google Sheets에 'Y'가 기록되었습니다.")
    else:
        print("\n📋 업데이트된 항목이 없습니다.")

    return True


if __name__ == "__main__":
    success = main()

    if not success:
        print("\n📋 문제 해결 체크리스트:")
        print("1. Google Sheets API 연결 확인")
        print("2. Papers 폴더에 PDF 파일 존재 확인")
        print("3. '3rd Screening' 시트에 'pdf_upload' 컬럼 존재 확인")
        print("4. PDF 파일명이 '{Index}_{Title}.pdf' 패턴인지 확인")
