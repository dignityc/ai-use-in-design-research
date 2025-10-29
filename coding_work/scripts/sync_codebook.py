"""
CodeBook Synchronization Script
구글 시트의 CodeBook을 로컬 source/CodeBook.csv로 동기화
"""

import os
import sys
import csv
from pathlib import Path
from datetime import datetime
import pandas as pd

# google_sheets_connector 임포트를 위한 경로 설정
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


class CodeBookSynchronizer:
    """Google Sheets CodeBook을 로컬 CSV로 동기화하는 클래스"""

    def __init__(self, credentials_path: str = None, output_path: str = None):
        """
        CodeBook Synchronizer 초기화

        Args:
            credentials_path: Google Sheets API 인증 파일 경로
            output_path: 출력 CSV 파일 경로
        """
        # 기본 경로 설정
        if credentials_path is None:
            credentials_path = str(Path(__file__).parent.parent / "credentials" / "gen-lang-client-0444199460-38266703559b.json")

        if output_path is None:
            # scripts 폴더에서 상위로 2번 올라가서 source 폴더
            output_path = str(Path(__file__).parent.parent.parent / "source" / "CodeBook.csv")

        self.credentials_path = credentials_path
        self.output_path = Path(output_path)
        self.sheet_name = "CodeBook"

        # Google Sheets Connector 초기화
        self.connector = GoogleSheetsConnector(
            credentials_path=credentials_path,
            spreadsheet_id='1MgMKl7b8y5hPScQZJQ5y8y-J_UY1qalgVnQEFOucbBM'
        )

    def connect_to_sheets(self) -> bool:
        """Google Sheets 연결"""
        if not self.connector.connect():
            print("❌ Google Sheets 연결 실패")
            return False
        print("✅ Google Sheets 연결 성공")
        return True

    def download_codebook(self) -> pd.DataFrame:
        """
        Google Sheets에서 CodeBook 시트 다운로드

        Returns:
            DataFrame: CodeBook 데이터
        """
        print(f"📥 '{self.sheet_name}' 시트 다운로드 중...")

        try:
            # CodeBook 시트 데이터 가져오기
            sheet = self.connector.get_sheet(self.sheet_name)
            all_values = sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                print(f"❌ '{self.sheet_name}' 시트가 비어있거나 데이터가 부족합니다.")
                return pd.DataFrame()

            # DataFrame 생성 (첫 번째 행을 헤더로 사용)
            headers = all_values[0]
            data = all_values[1:]
            df = pd.DataFrame(data, columns=headers)

            print(f"✅ {len(df)}개 행, {len(df.columns)}개 컬럼 다운로드 완료")
            print(f"📋 컬럼: {list(df.columns)}")

            return df

        except Exception as e:
            print(f"❌ CodeBook 다운로드 실패: {str(e)}")
            return pd.DataFrame()

    def save_to_csv(self, df: pd.DataFrame) -> bool:
        """
        DataFrame을 CSV 파일로 저장

        Args:
            df: 저장할 DataFrame

        Returns:
            bool: 성공 여부
        """
        if df.empty:
            print("❌ 저장할 데이터가 없습니다.")
            return False

        try:
            # 출력 디렉토리 생성 (없는 경우)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # 기존 파일이 있으면 백업 생성
            if self.output_path.exists():
                backup_path = self.output_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                print(f"💾 기존 파일 백업: {backup_path.name}")
                import shutil
                shutil.copy(self.output_path, backup_path)

            # CSV로 저장
            df.to_csv(self.output_path, index=False, encoding='utf-8-sig')
            print(f"✅ CodeBook 저장 완료: {self.output_path}")
            print(f"   파일 크기: {self.output_path.stat().st_size:,} bytes")

            return True

        except Exception as e:
            print(f"❌ CSV 저장 실패: {str(e)}")
            return False

    def print_summary(self, df: pd.DataFrame):
        """CodeBook 내용 요약 출력"""
        if df.empty:
            return

        print("\n" + "=" * 60)
        print("📊 CodeBook 요약")
        print("=" * 60)

        # 기본 정보
        print(f"총 행 수: {len(df)}")
        print(f"총 컬럼 수: {len(df.columns)}")

        # 주요 컬럼별 데이터 개수
        print("\n📋 주요 분류 기준:")

        # AI methods 컬럼 찾기
        ai_methods_col = None
        for col in df.columns:
            if 'ai method' in col.lower():
                ai_methods_col = col
                break

        if ai_methods_col:
            ai_methods = df[ai_methods_col].dropna()
            ai_methods = [str(m).strip() for m in ai_methods if str(m).strip() and str(m).strip().lower() != 'nan']
            print(f"   AI Methods: {len(ai_methods)}개")
            if ai_methods:
                print(f"      예시: {', '.join(ai_methods[:3])}")

        # Data Modality 컬럼 찾기
        data_modality_col = None
        for col in df.columns:
            if 'data modality' in col.lower():
                data_modality_col = col
                break

        if data_modality_col:
            data_modalities = df[data_modality_col].dropna()
            data_modalities = [str(m).strip() for m in data_modalities if str(m).strip() and str(m).strip().lower() != 'nan']
            print(f"   Data Modality: {len(data_modalities)}개")
            if data_modalities:
                print(f"      예시: {', '.join(data_modalities[:3])}")

        # Design Practice/Task 컬럼 찾기
        design_practice_col = None
        for col in df.columns:
            if 'design practice' in col.lower() or 'design task' in col.lower():
                design_practice_col = col
                break

        if design_practice_col:
            design_practices = df[design_practice_col].dropna()
            design_practices = [str(p).strip() for p in design_practices if str(p).strip() and str(p).strip().lower() != 'nan']
            print(f"   Design Practice/Task: {len(design_practices)}개")
            if design_practices:
                print(f"      예시: {', '.join(design_practices[:3])}")

        print("\n✅ 동기화 완료: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60 + "\n")

    def sync(self) -> bool:
        """
        전체 동기화 프로세스 실행

        Returns:
            bool: 성공 여부
        """
        print("\n" + "=" * 60)
        print("🔄 CodeBook 동기화 시작")
        print("=" * 60 + "\n")

        # 1. Google Sheets 연결
        if not self.connect_to_sheets():
            return False

        # 2. CodeBook 다운로드
        df = self.download_codebook()
        if df.empty:
            return False

        # 3. CSV로 저장
        if not self.save_to_csv(df):
            return False

        # 4. 요약 출력
        self.print_summary(df)

        return True


def main():
    """메인 함수"""
    synchronizer = CodeBookSynchronizer()
    success = synchronizer.sync()

    if success:
        print("✅ CodeBook 동기화 성공!")
        sys.exit(0)
    else:
        print("❌ CodeBook 동기화 실패!")
        sys.exit(1)


if __name__ == "__main__":
    main()
