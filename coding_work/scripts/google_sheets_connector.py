"""
Google Sheets API 연결 모듈
논문 리스트 가져오기 및 분류 결과 업데이트를 위한 클래스 구현
"""

import gspread
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2.service_account import Credentials
import pandas as pd
import logging
import time
from typing import Optional, Dict, List, Any
import os
from pathlib import Path


class GoogleSheetsConnector:
    """Google Sheets API를 통한 스프레드시트 연결 및 데이터 관리"""
    
    def __init__(self, credentials_path: str = None, spreadsheet_id: str = None):
        """
        Google Sheets 연결 초기화
        
        Args:
            credentials_path: 서비스 계정 JSON 키 파일 경로
            spreadsheet_id: 구글 스프레드시트 ID
        """
        # 기본 경로 설정 (스크립트 폴더 기준)
        default_credentials_path = str(Path(__file__).parent.parent / 'credentials' / 'gen-lang-client-0444199460-38266703559b.json')
        default_spreadsheet_id = '1MgMKl7b8y5hPScQZJQ5y8y-J_UY1qalgVnQEFOucbBM'
        
        self.credentials_path = credentials_path or os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH') or default_credentials_path
        self.spreadsheet_id = spreadsheet_id or os.getenv('SPREADSHEET_ID') or default_spreadsheet_id
        
        # 로깅 설정
        self.logger = self._setup_logging()
        
        # 클라이언트 및 스프레드시트 객체
        self.client = None
        self.spreadsheet = None
        
        # API 요청 제한을 위한 설정
        self.request_delay = 1.0  # 요청 간 대기시간 (초)
        
    def _setup_logging(self) -> logging.Logger:
        """로깅 시스템 설정"""
        logger = logging.getLogger('GoogleSheetsConnector')
        logger.setLevel(logging.INFO)
        
        # 로그 디렉토리 확인/생성
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 파일 핸들러 설정
        if not logger.handlers:
            handler = logging.FileHandler(log_dir / 'google_sheets.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # 콘솔 출력도 추가
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def connect(self) -> bool:
        """
        Google Sheets API에 연결
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            if not self.credentials_path or not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {self.credentials_path}")
            
            if not self.spreadsheet_id:
                raise ValueError("스프레드시트 ID가 설정되지 않았습니다")
            
            # 서비스 계정 인증
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=scope
            )
            
            # 클라이언트 생성 및 스프레드시트 열기
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            self.logger.info("Google Sheets API 연결 성공")
            return True
            
        except Exception as e:
            self.logger.error(f"Google Sheets API 연결 실패: {str(e)}")
            return False
    
    def get_sheet(self, sheet_name: str = None):
        """
        특정 시트 가져오기
        
        Args:
            sheet_name: 시트 이름 (None이면 첫 번째 시트)
            
        Returns:
            gspread.Worksheet: 시트 객체
        """
        if not self.spreadsheet:
            raise ConnectionError("먼저 connect() 메서드를 호출해주세요")
        
        try:
            if sheet_name:
                return self.spreadsheet.worksheet(sheet_name)
            else:
                return self.spreadsheet.sheet1
        except Exception as e:
            self.logger.error(f"시트 가져오기 실패: {str(e)}")
            raise
    
    def get_paper_list(self, sheet_name: str = None) -> pd.DataFrame:
        """
        스프레드시트에서 논문 리스트 가져오기
        
        Args:
            sheet_name: 시트 이름
            
        Returns:
            pd.DataFrame: 논문 리스트 데이터프레임
        """
        try:
            sheet = self.get_sheet(sheet_name)
            
            # 모든 레코드를 딕셔너리 리스트로 가져오기
            records = sheet.get_all_records()
            
            if not records:
                self.logger.warning("스프레드시트가 비어있습니다")
                return pd.DataFrame()
            
            # DataFrame으로 변환
            df = pd.DataFrame(records)
            
            self.logger.info(f"논문 리스트 로드 완료: {len(df)}개 항목")
            
            # API 호출 제한을 위한 대기
            time.sleep(self.request_delay)
            
            return df
            
        except Exception as e:
            self.logger.error(f"논문 리스트 가져오기 실패: {str(e)}")
            raise
    
    def update_cell(self, sheet_name: str, row: int, col: int, value: Any) -> bool:
        """
        특정 셀 업데이트
        
        Args:
            sheet_name: 시트 이름
            row: 행 번호 (1부터 시작)
            col: 열 번호 (1부터 시작)
            value: 업데이트할 값
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            sheet = self.get_sheet(sheet_name)
            sheet.update_cell(row, col, value)
            
            self.logger.info(f"셀 업데이트 완료: ({row}, {col}) = {value}")
            
            # API 호출 제한을 위한 대기
            time.sleep(self.request_delay)
            
            return True
            
        except Exception as e:
            self.logger.error(f"셀 업데이트 실패: {str(e)}")
            return False
    
    
    def batch_update(self, sheet_name: str, updates: List[Dict], range_name: str = None) -> bool:
        """
        배치 업데이트
        
        Args:
            sheet_name: 시트 이름
            updates: 업데이트할 데이터 리스트
            range_name: 업데이트할 범위 (A1 notation)
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            sheet = self.get_sheet(sheet_name)
            
            if range_name:
                # 범위 지정 업데이트
                sheet.update(range_name, updates)
            else:
                # 개별 셀 업데이트
                for update in updates:
                    row = update.get('row')
                    col = update.get('col')
                    value = update.get('value')
                    
                    if row and col and value is not None:
                        sheet.update_cell(row, col, value)
                        time.sleep(self.request_delay)
            
            self.logger.info(f"배치 업데이트 완료: {len(updates)}개 항목")
            return True
            
        except Exception as e:
            self.logger.error(f"배치 업데이트 실패: {str(e)}")
            return False
    
    def add_new_row(self, sheet_name: str, row_data: List[Any]) -> bool:
        """
        새 행 추가
        
        Args:
            sheet_name: 시트 이름
            row_data: 추가할 행 데이터 리스트
            
        Returns:
            bool: 추가 성공 여부
        """
        try:
            sheet = self.get_sheet(sheet_name)
            sheet.append_row(row_data)
            
            self.logger.info(f"새 행 추가 완료: {row_data}")
            
            # API 호출 제한을 위한 대기
            time.sleep(self.request_delay)
            
            return True
            
        except Exception as e:
            self.logger.error(f"새 행 추가 실패: {str(e)}")
            return False
    
    def validate_sheet_structure(self, sheet_name: str = None, required_columns: List[str] = None) -> bool:
        """
        시트 구조 검증
        
        Args:
            sheet_name: 시트 이름
            required_columns: 필수 컬럼 리스트
            
        Returns:
            bool: 구조가 유효한지 여부
        """
        try:
            df = self.get_paper_list(sheet_name)
            
            if df.empty:
                self.logger.warning("시트가 비어있습니다")
                return False
            
            if required_columns:
                missing_columns = set(required_columns) - set(df.columns)
                if missing_columns:
                    self.logger.error(f"필수 컬럼이 누락되었습니다: {missing_columns}")
                    return False
            
            self.logger.info("시트 구조 검증 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"시트 구조 검증 실패: {str(e)}")
            return False


def create_sample_config():
    """샘플 설정 파일 생성"""
    config_content = """
# Google Sheets API 설정
GOOGLE_SHEETS_CREDENTIALS_PATH=coding_work/credentials/service_account.json
SPREADSHEET_ID=your_spreadsheet_id_here

# 시트 이름 설정 (선택사항)
SHEET_NAME=PaperList

# 필수 컬럼 설정
REQUIRED_COLUMNS=ID,Title,Authors,Status
    """
    
    config_path = Path(__file__).parent / 'config.env'
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content.strip())
    
    print(f"샘플 설정 파일이 생성되었습니다: {config_path}")


if __name__ == "__main__":
    # 설정 파일 생성
    create_sample_config()