"""
PDF 논문 자동 분류 시스템
Papers 폴더의 PDF 파일들을 체계적으로 분석하여 7개 분류 기준에 따라 분류
Claude API를 활용한 PhD급 전문가 수준의 분석 수행
"""

import os
import sys
import json
import subprocess
import pdfplumber
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import time
from datetime import datetime
import re
import argparse
import shutil

# 상위 경로 추가
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


class PDFAnalyzer:
    """PDF 논문 자동 분류 분석기"""
    
    def __init__(self, papers_folder: str = None, output_folder: str = None):
        """
        PDF 분석기 초기화
        
        Args:
            papers_folder: PDF 파일들이 있는 폴더 경로
            output_folder: 결과 CSV 파일들을 저장할 폴더 경로
        """
        # 기본 경로 설정
        if papers_folder is None:
            # scripts 폴더에서 상위로 2번 올라가서 Papers 폴더
            papers_folder = str(Path(__file__).parent.parent.parent / "Papers")
        
        if output_folder is None:
            output_folder = str(Path(__file__).parent.parent / "results" / "pdf_analysis")
        
        self.papers_folder = Path(papers_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # 진행 상태 파일 경로
        self.progress_file = self.output_folder / "progress.json"

        # Google Sheets 연결
        self.sheets_connector = GoogleSheetsConnector()

        # CodeBook 로드 (초기화 시점에는 로드하지 않음, connect_to_sheets 이후 호출)
        self.codebook = {}

        # Multiple이 있는 카테고리 맵 (Multiple 선택 시 구체적 요소 표시용)
        self.MULTIPLE_CATEGORIES = {
            "Design Discipline": "Multiple",
            "Data Modality": "Multimodal",
            "AI Assistance Types (Lee and Kim, 2025)": "Multiple"
        }

        # 분류 기준 (CodedPapers 시트에서 확인된 7개 항목)
        self.classification_categories = [
            "Design Discipline",
            "Data About",
            "Data Modality",
            "AI methods",
            "AI Assistance Types (Lee and Kim, 2025)",
            "Design Phase",
            "Design Practice/Task"
        ]
        
        # CodedPapers 시트의 전체 헤더 (14개)
        self.csv_headers = [
            "Article Title", "Author Full Names", "Source Title", "Publication Year", "DOI Link",
            "Design Discipline", "Data About", "Data Modality", "AI methods", 
            "AI Assistance Types (Lee and Kim, 2025)", "Design Phase", "Design Practice/Task",
            "Notes", "Questions"
        ]
        
        # 결과 저장용
        self.processing_log = []
        self.classification_results = []  # 분류명 결과
        self.reasoning_results = []       # 분류 근거
        self.reference_results = []       # 참고 원문
        
    def connect_to_sheets(self) -> bool:
        """Google Sheets API 연결"""
        print("🔗 Google Sheets 연결 중...")
        if not self.sheets_connector.connect():
            print("❌ Google Sheets 연결 실패")
            return False
        print("✅ Google Sheets 연결 성공")
        return True

    def load_progress(self) -> Dict:
        """
        진행 상태 로드 (progress.json)

        Returns:
            Dict: 진행 상태 딕셔너리
        """
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  progress.json 로드 실패: {e}")
                return self._create_empty_progress()
        return self._create_empty_progress()

    def _create_empty_progress(self) -> Dict:
        """빈 진행 상태 딕셔너리 생성"""
        return {
            "last_updated": None,
            "total_target": 0,
            "processed_count": 0,
            "failed_count": 0,
            "processed": [],
            "failed": {}
        }

    def save_progress(self, progress: Dict):
        """
        진행 상태 저장 (자동 백업 포함)

        Args:
            progress: 저장할 진행 상태 딕셔너리
        """
        try:
            # 1. 기존 파일이 있으면 백업
            if self.progress_file.exists():
                backup_file = self.progress_file.with_suffix('.json.backup')
                shutil.copy2(self.progress_file, backup_file)

            # 2. 타임스탬프 업데이트
            progress["last_updated"] = datetime.now().isoformat()

            # 3. 새 상태 저장
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️  progress.json 저장 실패: {e}")

    def mark_as_processed(self, pdf_filename: str):
        """
        PDF를 처리 완료 목록에 추가

        Args:
            pdf_filename: 처리 완료된 PDF 파일명
        """
        progress = self.load_progress()

        # processed 목록에 추가
        if pdf_filename not in progress["processed"]:
            progress["processed"].append(pdf_filename)
            progress["processed_count"] = len(progress["processed"])

        # failed에서 제거 (재시도 성공 시)
        if pdf_filename in progress["failed"]:
            del progress["failed"][pdf_filename]
            progress["failed_count"] = len(progress["failed"])

        self.save_progress(progress)

    def mark_as_failed(self, pdf_filename: str, error_msg: str):
        """
        PDF를 실패 목록에 추가

        ⚠️ DEPRECATED: 에러 즉시 중단 모드에서는 사용하지 않음
        (호환성 유지를 위해 메서드는 남겨둠)

        Args:
            pdf_filename: 실패한 PDF 파일명
            error_msg: 에러 메시지
        """
        progress = self.load_progress()

        if pdf_filename not in progress["failed"]:
            progress["failed"][pdf_filename] = {
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "retry_count": 0
            }
        else:
            # 재시도 카운트 증가
            progress["failed"][pdf_filename]["retry_count"] += 1
            progress["failed"][pdf_filename]["timestamp"] = datetime.now().isoformat()
            progress["failed"][pdf_filename]["error"] = error_msg

        progress["failed_count"] = len(progress["failed"])
        self.save_progress(progress)

    def load_codebook(self) -> Dict:
        """
        CodeBook CSV 파일에서 분류 기준 데이터 로드 (레이블 + 설명)

        Returns:
            Dict: CodeBook 분류 기준 데이터
                  각 카테고리는 [{'label': '...', 'description': '...'}, ...] 형식
        """
        try:
            # CodeBook 경로: coding_work/scripts -> paper_review_with_llm/source/CodeBook.csv
            codebook_path = Path(__file__).parent.parent.parent / "source" / "CodeBook.csv"

            if not codebook_path.exists():
                print(f"❌ CodeBook 파일을 찾을 수 없습니다: {codebook_path}")
                return {}

            print(f"📚 CodeBook 로드 중: {codebook_path}")

            # CSV 로드 (header=1: 첫 번째 행은 제목, 두 번째 행이 실제 헤더)
            df = pd.read_csv(codebook_path, encoding='utf-8-sig', header=1)

            # 각 분류 기준별 옵션 추출 (레이블 + 설명)
            codebook = {}

            # Helper function to extract label-description pairs
            def extract_with_description(label_col: str, desc_col: str) -> list:
                """레이블과 설명을 쌍으로 추출"""
                items = []
                if label_col in df.columns:
                    for idx, row in df.iterrows():
                        label = str(row[label_col]).strip() if pd.notna(row[label_col]) else ''
                        description = str(row[desc_col]).strip() if desc_col in df.columns and pd.notna(row[desc_col]) else ''

                        if label and label.lower() != 'nan':
                            items.append({
                                'label': label,
                                'description': description
                            })
                return items

            # AI methods 추출 (AI methods + Description)
            ai_methods = extract_with_description('AI methods', 'Description')
            if ai_methods:
                codebook['ai_methods'] = ai_methods
                print(f"   ✅ AI Methods: {len(ai_methods)}개 로드 (설명 포함)")

            # Design Discipline 추출 (Design Discipline + 다음 컬럼)
            design_disciplines = extract_with_description('Design Discipline', 'Discipline refers to where AI is applied for')
            if design_disciplines:
                codebook['design_disciplines'] = design_disciplines
                print(f"   ✅ Design Disciplines: {len(design_disciplines)}개 로드 (설명 포함)")

            # Data Modality 추출 (Data Modality + 다음 컬럼)
            data_modalities = extract_with_description('Data Modality', 'A distinct format or structure of input data- text, images, audio, video, or time series, each requiring different approaches for labeling and analysis.')
            if data_modalities:
                codebook['data_modalities'] = data_modalities
                print(f"   ✅ Data Modalities: {len(data_modalities)}개 로드 (설명 포함)")

            # Data About 추출
            data_about = extract_with_description('Data About (DATA SOURCE: sensor, design component(artifhact), natural language)', 'What the data inform')
            if data_about:
                codebook['data_about'] = data_about
                print(f"   ✅ Data About: {len(data_about)}개 로드 (설명 포함)")

            # AI Assistance Types 추출
            # CodeBook에서 컬럼명 찾기
            assistance_col = None
            assistance_desc_col = None
            for col in df.columns:
                if 'AI Assistance Types' in col:
                    assistance_col = col
                    # 다음 컬럼이 설명일 가능성
                    col_idx = df.columns.get_loc(col)
                    if col_idx + 1 < len(df.columns):
                        assistance_desc_col = df.columns[col_idx + 1]
                    break

            if assistance_col:
                assistance_types = extract_with_description(assistance_col, assistance_desc_col if assistance_desc_col else '')
                if assistance_types:
                    codebook['assistance_types'] = assistance_types
                    print(f"   ✅ AI Assistance Types: {len(assistance_types)}개 로드 (설명 포함)")

            # Design Phase 추출
            design_phase_col = 'Design Phase'
            design_phase_desc_col = None
            if design_phase_col in df.columns:
                col_idx = df.columns.get_loc(design_phase_col)
                if col_idx + 1 < len(df.columns):
                    design_phase_desc_col = df.columns[col_idx + 1]

            design_phases = extract_with_description(design_phase_col, design_phase_desc_col if design_phase_desc_col else '')
            if design_phases:
                codebook['design_phases'] = design_phases
                print(f"   ✅ Design Phases: {len(design_phases)}개 로드 (설명 포함)")

            # Design Practice/Task는 자유 형식이므로 옵션 없이 처리
            codebook['design_practice_task'] = []

            return codebook

        except Exception as e:
            print(f"❌ CodeBook 로드 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def extract_index_from_filename(self, filename: str) -> Optional[str]:
        """
        PDF 파일명에서 Index 번호 추출

        Args:
            filename: PDF 파일명 (예: "80_Deep learning for design.pdf")

        Returns:
            Optional[str]: Index 번호 또는 None
        """
        # 파일명 패턴: {Index}_{Title}.pdf
        match = re.match(r'^(\d+)_', filename)
        if match:
            return match.group(1)
        return None

    def get_included_papers_from_sheets(self) -> Set[str]:
        """
        Google Sheets에서 Inclusion='Y' AND Assigned_to='J' 논문의 Index 목록 가져오기

        Returns:
            Set[str]: Index 번호 집합
        """
        try:
            print("📥 Google Sheets에서 필터링된 논문 목록 가져오는 중...")

            # "3rd Screening" 시트 접근
            sheet = self.sheets_connector.get_sheet("3rd Screening")
            all_values = sheet.get_all_values()

            if len(all_values) < 2:
                print("❌ 시트에 데이터가 없습니다.")
                return set()

            # DataFrame 생성
            headers = all_values[0]
            data = all_values[1:]
            df = pd.DataFrame(data, columns=headers)

            print(f"   총 논문 수: {len(df)}개")

            # Inclusion='Y' AND Assigned_to='J' 필터링
            # Column name: "Inclusion (Y/N/Q/R) for 2nd screening"
            inclusion_col = 'Inclusion (Y/N/Q/R) for 2nd screening'

            if inclusion_col not in df.columns:
                print(f"❌ '{inclusion_col}' 컬럼을 찾을 수 없습니다.")
                print(f"   사용 가능한 컬럼: {list(df.columns)}")
                return set()

            filtered_df = df[
                (df[inclusion_col].str.upper() == 'Y') &
                (df['Assigned_to'].str.upper() == 'J')
            ]

            print(f"   ✅ Inclusion='Y' & Assigned_to='J': {len(filtered_df)}개")

            # Index 컬럼 추출
            if 'Index' not in filtered_df.columns:
                print("❌ Index 컬럼을 찾을 수 없습니다.")
                return set()

            indices = set(str(idx).strip() for idx in filtered_df['Index'] if str(idx).strip())
            print(f"   ✅ Index 목록: {len(indices)}개")

            return indices

        except Exception as e:
            print(f"❌ Google Sheets 필터링 실패: {str(e)}")
            return set()

    def get_pdf_files(self, included_indices: Set[str] = None) -> List[Path]:
        """
        Papers 폴더에서 필터링된 PDF 파일 목록 가져오기

        Args:
            included_indices: 포함할 Index 번호 집합 (None이면 전체)

        Returns:
            List[Path]: 필터링된 PDF 파일 경로 리스트
        """
        if not self.papers_folder.exists():
            print(f"❌ Papers 폴더를 찾을 수 없습니다: {self.papers_folder}")
            return []

        # 전체 PDF 파일 목록
        all_pdf_files = list(self.papers_folder.glob("*.pdf"))
        print(f"📁 Papers 폴더 전체 PDF: {len(all_pdf_files)}개")

        # 필터링이 없으면 전체 반환
        if included_indices is None:
            print("   ℹ️  필터링 없이 전체 PDF 처리")
            for i, pdf_file in enumerate(all_pdf_files, 1):
                print(f"   {i}. {pdf_file.name}")
            return all_pdf_files

        # Index 기반 필터링
        filtered_pdf_files = []
        skipped_count = 0

        for pdf_file in all_pdf_files:
            # 파일명에서 Index 추출
            index = self.extract_index_from_filename(pdf_file.name)

            if index and index in included_indices:
                filtered_pdf_files.append(pdf_file)
            else:
                skipped_count += 1

        print(f"   ✅ 필터링된 PDF: {len(filtered_pdf_files)}개")
        print(f"   ⏭️  제외된 PDF: {skipped_count}개")

        # 필터링된 파일 목록 출력
        for i, pdf_file in enumerate(filtered_pdf_files, 1):
            index = self.extract_index_from_filename(pdf_file.name)
            print(f"   {i}. [{index}] {pdf_file.name}")

        return filtered_pdf_files
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """
        PDF 파일의 전체 텍스트 추출
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            str: 추출된 전체 텍스트
        """
        try:
            print(f"📖 PDF 텍스트 추출 중: {pdf_path.name}")
            
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"   총 페이지 수: {total_pages}")
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content.append(f"=== Page {i+1} ===\n{page_text}")
                    else:
                        text_content.append(f"=== Page {i+1} ===\n[텍스트 없음]")
            
            full_text = "\n\n".join(text_content)

            # Clean null bytes and other problematic characters that cause subprocess errors
            full_text = full_text.replace('\x00', '')  # Remove null bytes

            print(f"✅ 텍스트 추출 완료: {len(full_text):,} 문자, {total_pages} 페이지")

            # 빈 문서 체크
            if not full_text.strip():
                raise RuntimeError(f"PDF에서 텍스트를 추출할 수 없음 (빈 문서): {pdf_path.name}")

            return full_text

        except Exception as e:
            error_msg = f"PDF 텍스트 추출 실패 ({pdf_path.name}): {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e
    
    def call_claude_api(self, prompt: str, max_retries: int = 3) -> str:
        """
        Claude CLI API 호출 (재시도 로직 포함, 원본 응답 반환)

        Args:
            prompt: Claude에게 보낼 프롬프트
            max_retries: API 호출 재시도 횟수

        Returns:
            str: Claude 원본 응답 (JSON 문자열)

        Raises:
            RuntimeError: Rate limit 또는 복구 불가능한 에러
            TimeoutError: 모든 재시도 후 타임아웃
        """
        for attempt in range(max_retries):
            try:
                print(f"🤖 Claude API 호출 중... (시도 {attempt + 1}/{max_retries})")

                # Claude CLI 호출
                result = subprocess.run(
                    ['claude', '--model', 'sonnet', '-p', '--output-format', 'json', prompt],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5분 타임아웃
                )

                # 성공
                if result.returncode == 0:
                    response = result.stdout.strip()
                    print(f"✅ Claude API 호출 성공")
                    return response

                # 에러 발생 - 에러 타입 분류
                stderr = result.stderr.lower()

                # Rate Limit 감지 - 재시도 하지 않음
                if "429" in stderr or "rate_limit" in stderr:
                    print(f"🚫 Rate limit 감지 - 즉시 실패")
                    raise RuntimeError(f"Rate limit exceeded: {result.stderr}")

                # Service Overload - 재시도 가능
                if "overloaded" in stderr or "529" in stderr:
                    if attempt < max_retries - 1:
                        wait_time = 30 * (attempt + 1)
                        print(f"⏳ Service overload 감지, {wait_time}초 대기 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"Service overloaded (모든 재시도 실패): {result.stderr}")

                # 기타 에러 - 재시도 안 함
                raise RuntimeError(f"Claude CLI 실행 실패 (exit code {result.returncode}): {result.stderr}")

            except subprocess.TimeoutExpired:
                # Timeout - 재시도 가능
                if attempt < max_retries - 1:
                    print(f"⏳ Timeout 발생, 재시도 {attempt + 2}/{max_retries}...")
                    continue
                else:
                    raise TimeoutError(f"Claude CLI 타임아웃 (모든 재시도 실패)")

        # 모든 재시도 실패
        raise RuntimeError("모든 API 호출 시도 실패")

    def save_raw_response(self, pdf_filename: str, category: str, claude_response: str,
                         parsing_success: bool, parsing_error: str = None,
                         parsing_methods_tried: List[str] = None):
        """
        Claude 원본 응답을 txt 파일로 저장

        Args:
            pdf_filename: PDF 파일명
            category: 분류 카테고리
            claude_response: Claude 원본 응답
            parsing_success: 파싱 성공 여부
            parsing_error: 파싱 에러 메시지
            parsing_methods_tried: 시도한 파싱 방법 리스트
        """
        try:
            # raw_responses 폴더 생성
            raw_folder = self.output_folder / "raw_responses"
            raw_folder.mkdir(parents=True, exist_ok=True)

            # Index 추출
            index = self.extract_index_from_filename(pdf_filename)
            if not index:
                index = "unknown"

            # 안전한 카테고리 이름 (파일명에 사용 가능하도록)
            safe_category = category.replace("/", "_").replace(" ", "_").replace("(", "").replace(")", "")

            # 파일명
            txt_file = raw_folder / f"{index}_{safe_category}.txt"
            metadata_file = raw_folder / f"{index}_{safe_category}_metadata.json"

            # 1. 원본 응답 txt로 저장
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(claude_response)

            # 2. 메타데이터 JSON 저장
            metadata = {
                "pdf_file": pdf_filename,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "parsing_success": parsing_success,
                "parsing_methods_tried": parsing_methods_tried or [],
                "parsing_error": parsing_error,
                "raw_response_file": txt_file.name
            }

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"💾 Raw response 저장: {txt_file.name}")

        except Exception as e:
            print(f"⚠️  Raw response 저장 실패: {str(e)}")

    def parse_json_response(self, claude_raw_response: str) -> Dict:
        """
        Claude 응답을 여러 방법으로 파싱 시도

        Args:
            claude_raw_response: Claude 원본 응답

        Returns:
            Dict: 파싱된 JSON 객체

        Raises:
            ValueError: 모든 파싱 방법 실패 시
        """
        parsing_methods_tried = []
        last_error = None

        # Claude CLI JSON 메타데이터 파싱
        try:
            response_metadata = json.loads(claude_raw_response)
            if 'result' in response_metadata:
                claude_answer = response_metadata['result']
            else:
                raise ValueError("Claude 응답에 'result' 필드가 없음")
        except Exception as e:
            raise ValueError(f"Claude CLI 응답 메타데이터 파싱 실패: {str(e)}")

        print(f"🔍 Claude 원본 답변: {claude_answer[:200]}...")

        # 여러 패턴으로 JSON 추출
        json_str = None

        # 패턴 1: ```json {...} ``` (non-greedy를 greedy로 변경하여 전체 JSON 추출)
        json_match = re.search(r'```json\s*(\{.*\})\s*```', claude_answer, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print("✅ 패턴 1: ```json``` 블록에서 JSON 발견")
        else:
            # 패턴 2: { ... } 직접 매칭
            brace_match = re.search(r'\{[^{}]*"category"[^{}]*"classification"[^{}]*"reasoning"[^{}]*"reference_text"[^{}]*\}', claude_answer, re.DOTALL)
            if brace_match:
                json_str = brace_match.group(0)
                print("✅ 패턴 2: 중괄호 블록에서 JSON 발견")
            else:
                # 패턴 3: 부분 JSON 재구성
                category_match = re.search(r'"category":\s*"([^"]*)"', claude_answer)
                classification_match = re.search(r'"classification":\s*"([^"]*)"', claude_answer)
                reasoning_match = re.search(r'"reasoning":\s*"([^"]*)"', claude_answer)
                reference_match = re.search(r'"reference_text":\s*"([^"]*)"', claude_answer)

                if category_match and classification_match:
                    json_str = f'{{"category": "{category_match.group(1)}", "classification": "{classification_match.group(1)}", "reasoning": "{reasoning_match.group(1) if reasoning_match else "분류 근거 없음"}", "reference_text": "{reference_match.group(1) if reference_match else "참고 텍스트 없음"}"}}'
                    print("✅ 패턴 3: 부분 매칭으로 JSON 재구성")

        if not json_str:
            raise ValueError("모든 패턴에서 JSON을 찾을 수 없음")

        # JSON 정리 및 파싱 시도

        # 방법 1: 기본 정리
        parsing_methods_tried.append("method1_basic")
        try:
            clean_json = json_str
            # 스마트 따옴표 정규화
            clean_json = clean_json.replace('"', '"').replace('"', '"')
            clean_json = clean_json.replace(''', "'").replace(''', "'")
            # 제어 문자 제거
            clean_json = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', clean_json)
            clean_json = clean_json.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            # 공백 정리
            clean_json = re.sub(r'\s+', ' ', clean_json)

            print(f"🔧 정리된 JSON (첫 300자): {clean_json[:300]}...")
            answer_json = json.loads(clean_json)
            print(f"✅ Method 1 성공: 기본 정리")
            return answer_json

        except json.JSONDecodeError as e:
            last_error = str(e)
            print(f"❌ Method 1 실패: {str(e)}")

        # 방법 2: Aggressive cleaning (non-ASCII 제거)
        parsing_methods_tried.append("method2_aggressive")
        try:
            aggressive_json = clean_json.encode('ascii', 'ignore').decode('ascii')
            answer_json = json.loads(aggressive_json)
            print(f"✅ Method 2 성공: Aggressive cleaning")
            return answer_json

        except json.JSONDecodeError as e:
            last_error = str(e)
            print(f"❌ Method 2 실패: {str(e)}")

        # 방법 3: 더 공격적인 정리 (특수문자 완전 제거)
        parsing_methods_tried.append("method3_ultra_aggressive")
        try:
            ultra_clean = re.sub(r'[^\x20-\x7E]', '', json_str)  # 출력 가능한 ASCII만
            ultra_clean = ultra_clean.replace('"', '"').replace('"', '"')
            ultra_clean = re.sub(r'\s+', ' ', ultra_clean)
            answer_json = json.loads(ultra_clean)
            print(f"✅ Method 3 성공: Ultra aggressive cleaning")
            return answer_json

        except json.JSONDecodeError as e:
            last_error = str(e)
            print(f"❌ Method 3 실패: {str(e)}")

        # 모든 방법 실패
        raise ValueError(f"JSON 파싱 실패 (모든 방법 실패): {last_error}")

    def validate_classification(self, result: Dict, allowed_options: List[str], category: str) -> str:
        """
        분류 결과가 CodeBook 옵션에 있는지 검증

        Args:
            result: 분류 결과 딕셔너리
            allowed_options: 허용된 옵션 리스트
            category: 분류 카테고리명

        Returns:
            str: 검증된 분류값 (필요시 보정됨)
        """
        classification = result.get("classification", "")

        if not allowed_options:
            # 자유 형식 카테고리 (예: Design Practice/Task)
            return classification

        # Multiple/Multimodal 유연 검증 (Multiple [...]로 시작하면 허용)
        if category in self.MULTIPLE_CATEGORIES:
            multiple_keyword = self.MULTIPLE_CATEGORIES[category]
            if classification.startswith(multiple_keyword):
                print(f"   ℹ️  {multiple_keyword} 선택 감지: {classification}")
                return classification  # 그대로 통과

        if classification in allowed_options:
            # 정확히 일치
            return classification

        # 불일치 발견
        print(f"   ⚠️  경고: 잘못된 분류값 발견")
        print(f"      입력: '{classification}'")
        print(f"      허용: {allowed_options[:3]}..." if len(allowed_options) > 3 else f"      허용: {allowed_options}")

        # Fuzzy matching으로 가장 유사한 옵션 찾기
        from difflib import get_close_matches
        matches = get_close_matches(classification, allowed_options, n=1, cutoff=0.6)
        if matches:
            print(f"   🔄 자동 보정: '{matches[0]}'")
            return matches[0]

        # 보정 실패
        print(f"   ❌ 자동 보정 실패, 첫 번째 옵션 사용: '{allowed_options[0]}'")
        return allowed_options[0]

    def classify_single_category(self, pdf_text: str, category: str, pdf_filename: str, codebook: Dict = None) -> Dict[str, str]:
        """
        단일 분류 기준에 대한 분석 수행

        Args:
            pdf_text: PDF에서 추출된 텍스트
            category: 분류 기준 (예: "Design Discipline")
            pdf_filename: PDF 파일명
            codebook: CodeBook 분류 기준 데이터

        Returns:
            Dict: 분류 결과
        """
        print(f"🎯 분류 수행: {category}")

        # 전체 PDF 텍스트 사용 (제한 없음)
        analysis_text = pdf_text

        # CodeBook에서 카테고리별 옵션 동적으로 가져오기
        if codebook:
            def extract_enum_options(items: list) -> List[str]:
                """레이블만 추출 (enum용)"""
                if not items:
                    return []

                enum_list = []
                for item in items:
                    if isinstance(item, dict):
                        label = item.get('label', '')
                        if label:
                            enum_list.append(label)
                    elif isinstance(item, str):
                        enum_list.append(item)

                return enum_list

            def format_options_as_enum(items: list) -> str:
                """Enum 형태로 포맷팅"""
                if not items:
                    return ""

                formatted_lines = []
                formatted_lines.append("AVAILABLE OPTIONS (choose EXACTLY one):")
                for i, item in enumerate(items, 1):
                    if isinstance(item, dict):
                        label = item.get('label', '')
                        formatted_lines.append(f'{i}. "{label}"')
                    else:
                        formatted_lines.append(f'{i}. "{item}"')

                return "\n".join(formatted_lines)

            # Enum 옵션 추출 (검증용)
            category_enum_map = {
                "Design Discipline": extract_enum_options(codebook.get('design_disciplines', [])),
                "Data About": extract_enum_options(codebook.get('data_about', [])),
                "Data Modality": extract_enum_options(codebook.get('data_modalities', [])),
                "AI methods": extract_enum_options(codebook.get('ai_methods', [])),
                "AI Assistance Types (Lee and Kim, 2025)": extract_enum_options(codebook.get('assistance_types', [])),
                "Design Phase": extract_enum_options(codebook.get('design_phases', [])),
                "Design Practice/Task": []  # 자유 형식
            }
            allowed_options = category_enum_map.get(category, [])

            # 프롬프트용 포맷팅
            category_options_map = {
                "Design Discipline": format_options_as_enum(codebook.get('design_disciplines', [])),
                "Data About": format_options_as_enum(codebook.get('data_about', [])),
                "Data Modality": format_options_as_enum(codebook.get('data_modalities', [])),
                "AI methods": format_options_as_enum(codebook.get('ai_methods', [])),
                "AI Assistance Types (Lee and Kim, 2025)": format_options_as_enum(codebook.get('assistance_types', [])),
                "Design Phase": format_options_as_enum(codebook.get('design_phases', [])),
                "Design Practice/Task": "Analyze the paper and identify the specific design practice or task being addressed (e.g., User research, Prototyping, Testing, Ideation, etc.)"
            }
            options = category_options_map.get(category, "Please analyze and classify appropriately")
        else:
            # Fallback: 하드코딩된 옵션 (CodeBook 로드 실패 시)
            print("⚠️  CodeBook 데이터 없음, 기본 옵션 사용")
            fallback_enum_map = {
                "Design Discipline": ["Industrial Design/Engineering design/Product design", "Service Design/System Design/Business design", "UI/UX Design", "Multiple"],
                "Data About": ["Perception", "Physiology", "Behavior", "Product", "Synthetic", "Demographic", "Environments"],
                "Data Modality": ["Text", "Image", "Audio", "Video", "Time Series", "Multimodal"],
                "AI methods": ["Traditional ML (shallow models)", "Deep models in CV", "Deep models in NLP", "Gen AI", "Large Gen AI", "Reinforcement learning", "Exploratory data analysis"],
                "AI Assistance Types (Lee and Kim, 2025)": ["Design generation", "Prediction", "Decision making (Validation, evaluation)", "Coordination", "Sense making", "Multiple"],
                "Design Phase": ["Discovery", "Define", "Develop", "Delivery"],
                "Design Practice/Task": []
            }
            allowed_options = fallback_enum_map.get(category, [])

            # 프롬프트용 포맷팅
            category_options = {
                "Design Discipline": '\n'.join([f'{i}. "{opt}"' for i, opt in enumerate(fallback_enum_map["Design Discipline"], 1)]),
                "Data About": '\n'.join([f'{i}. "{opt}"' for i, opt in enumerate(fallback_enum_map["Data About"], 1)]),
                "Data Modality": '\n'.join([f'{i}. "{opt}"' for i, opt in enumerate(fallback_enum_map["Data Modality"], 1)]),
                "AI methods": '\n'.join([f'{i}. "{opt}"' for i, opt in enumerate(fallback_enum_map["AI methods"], 1)]),
                "AI Assistance Types (Lee and Kim, 2025)": '\n'.join([f'{i}. "{opt}"' for i, opt in enumerate(fallback_enum_map["AI Assistance Types (Lee and Kim, 2025)"], 1)]),
                "Design Phase": '\n'.join([f'{i}. "{opt}"' for i, opt in enumerate(fallback_enum_map["Design Phase"], 1)]),
                "Design Practice/Task": "Analyze the paper and identify the specific design practice or task being addressed (e.g., User research, Prototyping, Testing, Ideation, etc.)"
            }
            options = category_options.get(category, "Please analyze and classify appropriately")
        
        # PhD급 전문가 프롬프트 생성 (Structured Output 강화)
        if category == "Design Practice/Task":
            # 자유 형식 카테고리
            prompt = f"""You're an expert Ph.D level researcher doing systematic literature review. Analyze this paper for "{category}" classification. /ultrathink

Paper text: {analysis_text}

Task: {options}

JSON OUTPUT SCHEMA (STRICT):
{{
  "category": "{category}",
  "classification": <describe the specific design practice or task>,
  "reasoning": <string, min 10 chars>,
  "reference_text": <EXACT sentence(s) from paper text, min 20 chars>
}}

CRITICAL:
- For "reference_text": Copy exact sentences from paper text above (do not paraphrase)

Output ONLY the JSON object. No markdown, no explanations, no other text."""
        else:
            # Enum 카테고리 (엄격한 제약)

            # Multiple SPECIAL RULE 생성 (해당 카테고리만)
            special_rule = ""
            if category in self.MULTIPLE_CATEGORIES and allowed_options:
                multiple_keyword = self.MULTIPLE_CATEGORIES[category]
                # Multiple을 제외한 다른 옵션들
                other_options = [opt for opt in allowed_options if opt != multiple_keyword]

                if len(other_options) >= 2:
                    special_rule = f"""
SPECIAL RULE for "{multiple_keyword}":
- If you select "{multiple_keyword}", you MUST specify which options are combined
- Format: "{multiple_keyword} [Option1, Option2, ...]"
- Example: "{multiple_keyword} [{other_options[0]}, {other_options[1]}]"
- Only list the specific options that apply (minimum 2)
"""

            prompt = f"""You're an expert Ph.D level researcher doing systematic literature review. Analyze this paper for "{category}" classification. /ultrathink

Paper text: {analysis_text}

CLASSIFICATION RULES:
1. You MUST select EXACTLY ONE option from the list below
2. DO NOT modify, combine, or paraphrase the option text
3. Copy the EXACT text character-by-character from the list

{options}{special_rule}

JSON OUTPUT SCHEMA (STRICT):
{{
  "category": "{category}",
  "classification": <MUST be EXACT text from options above>,
  "reasoning": <string, min 10 chars>,
  "reference_text": <EXACT sentence(s) from paper text, min 20 chars>
}}

CRITICAL:
- For "classification": Copy EXACT text from options list above
- For "reference_text": Copy exact sentences from paper text above (do not paraphrase)

Output ONLY the JSON object. No markdown, no explanations, no other text."""

        # Claude API 호출 (원본 응답 받기)
        try:
            claude_raw_response = self.call_claude_api(prompt)
        except (RuntimeError, TimeoutError) as e:
            # API 호출 실패 - raw 저장 없이 에러
            print(f"❌ Claude API 호출 실패: {str(e)}")
            raise

        # Raw response 저장 (파싱 전)
        parsing_success = False
        parsing_error = None
        parsing_methods_tried = []
        result = None

        # JSON 파싱 시도 (여러 방법)
        try:
            result = self.parse_json_response(claude_raw_response)
            parsing_success = True
            parsing_methods_tried = ["parse_json_response"]
            print(f"✅ JSON 파싱 성공")

        except ValueError as e:
            # 모든 파싱 방법 실패
            parsing_success = False
            parsing_error = str(e)
            parsing_methods_tried = ["method1_basic", "method2_aggressive", "method3_ultra_aggressive"]
            print(f"❌ 모든 파싱 방법 실패: {str(e)}")

            # Raw 저장 후 에러 raise
            self.save_raw_response(
                pdf_filename=pdf_filename,
                category=category,
                claude_response=claude_raw_response,
                parsing_success=parsing_success,
                parsing_error=parsing_error,
                parsing_methods_tried=parsing_methods_tried
            )
            raise

        # 파싱 성공 - Raw 저장
        self.save_raw_response(
            pdf_filename=pdf_filename,
            category=category,
            claude_response=claude_raw_response,
            parsing_success=parsing_success,
            parsing_error=parsing_error,
            parsing_methods_tried=parsing_methods_tried
        )

        # 결과 검증 및 정리
        classification = result.get("classification", "UNKNOWN")

        # 검증 로직 적용 (enum 옵션이 있는 경우)
        if allowed_options:
            classification = self.validate_classification(result, allowed_options, category)
            result["classification"] = classification  # 보정된 값으로 업데이트

        reasoning = result.get("reasoning", "분류 근거 없음")
        reference_text = result.get("reference_text", "")

        print(f"✅ {category} 분류 완료:")
        print(f"   분류: {classification}")
        print(f"   근거: {reasoning[:100]}..." if len(reasoning) > 100 else f"   근거: {reasoning}")
        print(f"   원문: {reference_text[:100]}..." if len(reference_text) > 100 else f"   원문: {reference_text}")

        return {
            "category": category,
            "classification": classification,
            "reasoning": reasoning,
            "reference_text": reference_text
        }
    
    def analyze_single_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        단일 PDF 파일에 대한 전체 분석 수행 (에러 발생 시 즉시 예외)

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            Dict: 분석 결과

        Raises:
            RuntimeError: PDF 처리 실패 시 (텍스트 추출, Claude API 등)
        """
        print(f"\n📄 PDF 분석 시작: {pdf_path.name}")
        print("=" * 60)

        # PDF 텍스트 추출 (실패 시 예외 발생)
        pdf_text = self.extract_pdf_text(pdf_path)

        # 각 분류 기준별로 분석 수행 (실패 시 예외 발생)
        classifications = []
        for i, category in enumerate(self.classification_categories, 1):
            print(f"\n[{i}/{len(self.classification_categories)}] {category} 분석 중...")

            result = self.classify_single_category(pdf_text, category, pdf_path.name, codebook=self.codebook)
            classifications.append(result)

            # API 호출 간 대기
            time.sleep(2)

        # 결과 패키징
        analysis_result = {
            "pdf_file": pdf_path.name,
            "success": True,
            "error": None,
            "classifications": classifications,
            "pdf_text_length": len(pdf_text)
        }

        # 즉시 저장: CSV에 추가 + 진행 상태 업데이트
        self._add_to_csv_data(pdf_path.name, classifications)
        self._save_single_result()
        self.mark_as_processed(pdf_path.name)

        return analysis_result
    
    def _save_single_result(self):
        """
        현재 처리한 1개 PDF 결과를 CSV에 저장 (Index 기준 덮어쓰기)

        Logic:
        1. 기존 CSV 파일 읽기
        2. Index 기준으로 중복 체크
        3. 중복이면 해당 행 업데이트, 아니면 추가
        4. 전체 DataFrame 저장 (덮어쓰기)
        """
        if not self.classification_results:
            return

        try:
            # 마지막 결과만 추출
            last_classification = self.classification_results[-1]
            last_reasoning = self.reasoning_results[-1]
            last_reference = self.reference_results[-1]

            # 3개 CSV 파일별로 Upsert 수행
            csv_files = [
                ("pdf_classifications.csv", last_classification),
                ("pdf_reasoning.csv", last_reasoning),
                ("pdf_references.csv", last_reference)
            ]

            for csv_filename, new_data in csv_files:
                file_path = self.output_folder / csv_filename

                # 1. 기존 CSV 읽기 (없으면 빈 DataFrame)
                if file_path.exists():
                    existing_df = pd.read_csv(file_path, encoding='utf-8')
                else:
                    existing_df = pd.DataFrame()

                # 2. 새 데이터 DataFrame 생성
                new_df = pd.DataFrame([new_data])

                # 3. Index 기준 중복 체크
                pdf_index = new_data.get("Index", "")

                if not existing_df.empty and "Index" in existing_df.columns:
                    # Index 값을 문자열로 변환하여 비교
                    existing_df["Index"] = existing_df["Index"].astype(str)
                    mask = existing_df["Index"] == str(pdf_index)

                    if mask.any():
                        # 중복 발견: 해당 행 업데이트 (덮어쓰기)
                        existing_df.loc[mask] = new_df.iloc[0].values
                        result_df = existing_df
                        print(f"   ℹ️  {csv_filename}: 기존 데이터 덮어쓰기 (Index: {pdf_index})")
                    else:
                        # 중복 없음: 새 행 추가
                        result_df = pd.concat([existing_df, new_df], ignore_index=True)
                        print(f"   ✅ {csv_filename}: 새 데이터 추가 (Index: {pdf_index})")
                else:
                    # CSV 파일이 비어있거나 처음 생성
                    result_df = new_df
                    print(f"   ✅ {csv_filename}: 새 파일 생성 (Index: {pdf_index})")

                # 4. 전체 DataFrame 저장 (덮어쓰기)
                result_df.to_csv(file_path, index=False, encoding='utf-8')

        except Exception as e:
            print(f"⚠️  즉시 저장 실패: {e}")
            import traceback
            traceback.print_exc()

    def save_results_to_csv(self) -> Tuple[str, str, str]:
        """
        분석 결과를 3개 CSV 파일로 누적 저장
        
        Returns:
            Tuple[str, str, str]: 저장된 3개 CSV 파일 경로
        """
        # 고정된 파일명 (누적 저장)
        classifications_file = self.output_folder / "pdf_classifications.csv"
        reasoning_file = self.output_folder / "pdf_reasoning.csv"
        reference_file = self.output_folder / "pdf_references.csv"
        
        # 1. 분류명 CSV (누적)
        if self.classification_results:
            df_classifications = pd.DataFrame(self.classification_results)
            # 기존 파일이 있으면 append, 없으면 새로 생성
            if classifications_file.exists():
                existing_df = pd.read_csv(classifications_file, encoding='utf-8')
                combined_df = pd.concat([existing_df, df_classifications], ignore_index=True)
                combined_df.to_csv(classifications_file, index=False, encoding='utf-8')
                print(f"📄 분류명 CSV 누적 저장: {len(df_classifications)}행 추가 → 총 {len(combined_df)}행")
            else:
                df_classifications.to_csv(classifications_file, index=False, encoding='utf-8')
                print(f"📄 분류명 CSV 새로 생성: {len(df_classifications)}행")
        
        # 2. 분류 근거 CSV (누적)
        if self.reasoning_results:
            df_reasoning = pd.DataFrame(self.reasoning_results)
            if reasoning_file.exists():
                existing_df = pd.read_csv(reasoning_file, encoding='utf-8')
                combined_df = pd.concat([existing_df, df_reasoning], ignore_index=True)
                combined_df.to_csv(reasoning_file, index=False, encoding='utf-8')
                print(f"📄 분류 근거 CSV 누적 저장: {len(df_reasoning)}행 추가 → 총 {len(combined_df)}행")
            else:
                df_reasoning.to_csv(reasoning_file, index=False, encoding='utf-8')
                print(f"📄 분류 근거 CSV 새로 생성: {len(df_reasoning)}행")
        
        # 3. 참고 원문 CSV (누적)
        if self.reference_results:
            df_reference = pd.DataFrame(self.reference_results)
            if reference_file.exists():
                existing_df = pd.read_csv(reference_file, encoding='utf-8')
                combined_df = pd.concat([existing_df, df_reference], ignore_index=True)
                combined_df.to_csv(reference_file, index=False, encoding='utf-8')
                print(f"📄 참고 원문 CSV 누적 저장: {len(df_reference)}행 추가 → 총 {len(combined_df)}행")
            else:
                df_reference.to_csv(reference_file, index=False, encoding='utf-8')
                print(f"📄 참고 원문 CSV 새로 생성: {len(df_reference)}행")
        
        return str(classifications_file), str(reasoning_file), str(reference_file)
    
    def process_all_pdfs(self, use_filtering: bool = True, resume: bool = False, retry_failed: bool = False, limit: int = None) -> Dict[str, Any]:
        """
        모든 PDF 파일 처리

        Args:
            use_filtering: Inclusion='Y' & Assigned_to='J' 필터링 사용 여부
            resume: 이어서 실행 (이미 처리된 PDF 건너뛰기)
            retry_failed: 실패한 PDF만 재시도
            limit: 처리할 최대 PDF 개수 (None이면 전체 처리)

        Returns:
            Dict: 처리 결과 통계
        """
        print("=" * 60)
        print("🚀 PDF 논문 자동 분류 시스템 시작")
        print("=" * 60)

        # 1. CodeBook 로드
        print("\n📚 CodeBook 로드 중...")
        self.codebook = self.load_codebook()
        if not self.codebook:
            print("⚠️  CodeBook 로드 실패, 기본 옵션 사용")

        # 2. 필터링된 논문 Index 목록 가져오기
        included_indices = None
        if use_filtering:
            print("\n🔍 필터링 활성화: Inclusion='Y' & Assigned_to='J'")
            included_indices = self.get_included_papers_from_sheets()
            if not included_indices:
                print("⚠️  필터링된 논문이 없습니다.")
                return {"error": "필터링된 논문 없음"}
        else:
            print("\n⚠️  필터링 비활성화: 전체 PDF 처리")

        # 3. PDF 파일 목록 가져오기 (필터링 적용)
        pdf_files = self.get_pdf_files(included_indices)
        if not pdf_files:
            return {"error": "PDF 파일 없음"}

        # 4. Resume 또는 Retry 모드 처리
        progress = self.load_progress()
        original_count = len(pdf_files)

        if resume:
            # 이미 처리된 파일 제외
            processed_names = set(progress["processed"])
            pdf_files = [f for f in pdf_files if f.name not in processed_names]
            print(f"\n🔄 Resume 모드: {len(processed_names)}개 건너뛰기, {len(pdf_files)}개 처리 예정")

        elif retry_failed:
            # 실패한 파일만 재처리
            failed_names = set(progress["failed"].keys())
            pdf_files = [f for f in pdf_files if f.name in failed_names]
            print(f"\n🔁 Retry 모드: {len(pdf_files)}개 실패 파일 재시도")

        else:
            # 새로 시작: 진행 상태 초기화
            progress = self._create_empty_progress()
            progress["total_target"] = len(pdf_files)
            self.save_progress(progress)
            print(f"\n🆕 새로 시작: 진행 상태 초기화 완료")

        # 5. Limit 적용 (Resume/Retry 모드 후 적용)
        if limit is not None and limit > 0:
            pdf_files = pdf_files[:limit]
            print(f"\n🔢 처리 개수 제한: 최대 {limit}개")

        # 처리 통계
        stats = {
            "total_pdfs": len(pdf_files),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "total_classifications": 0,
            "results": []
        }

        print(f"\n🎯 처리 대상: {len(pdf_files)}개 PDF 파일")
        print(f"📋 분류 기준: {len(self.classification_categories)}개")
        print(f"🤖 예상 Claude 호출 횟수: {len(pdf_files) * len(self.classification_categories)}회")
        print()

        # 각 PDF 파일 처리 (에러 발생 시 즉시 중단)
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n🔄 [{i}/{len(pdf_files)}] 처리 중: {pdf_file.name}")

            try:
                result = self.analyze_single_pdf(pdf_file)
                stats["results"].append(result)
                stats["processed"] += 1
                stats["successful"] += 1
                stats["total_classifications"] += len(result["classifications"])
                # analyze_single_pdf()에서 이미 저장함 (즉시 저장)

            except Exception as e:
                # 에러 발생 시 즉시 중단
                print(f"\n{'=' * 60}")
                print(f"🛑 프로세스 중단: 에러 발생")
                print(f"{'=' * 60}")
                print(f"📄 실패한 PDF: {pdf_file.name}")
                print(f"❌ 에러 원인: {str(e)}")
                print(f"\n📊 중단 시점 통계:")
                print(f"   ✅ 성공: {stats['successful']}개")
                print(f"   ❌ 실패: 1개 ({pdf_file.name})")
                print(f"   📋 완료된 분류: {stats['total_classifications']}개")
                print(f"\n💾 완료된 {stats['successful']}개 PDF는 저장됨")
                print(f"🔄 다음 실행 시 {pdf_file.name}부터 자동 재개")

                # 에러 정보와 함께 즉시 반환
                return {
                    "error": str(e),
                    "failed_pdf": pdf_file.name,
                    "successful": stats["successful"],
                    "failed": 1,
                    "total_pdfs": len(pdf_files)
                }

        # 최종 결과 출력
        print("\n" + "=" * 60)
        print("📊 처리 결과 통계")
        print("=" * 60)
        print(f"총 대상 PDF: {stats['total_pdfs']}개")
        print(f"처리 시도: {stats['processed']}개")
        print(f"✅ 성공: {stats['successful']}개")
        print(f"❌ 실패: {stats['failed']}개")
        print(f"📋 총 분류 수행: {stats['total_classifications']}개")

        # 전체 진행 상황 요약
        final_progress = self.load_progress()
        if final_progress["total_target"] > 0:
            print(f"\n📈 전체 진행 상황:")
            print(f"   완료: {final_progress['processed_count']}/{final_progress['total_target']}개 ({final_progress['processed_count']/final_progress['total_target']*100:.1f}%)")
            print(f"   실패: {final_progress['failed_count']}개")

        return stats
    
    def _add_to_csv_data(self, pdf_filename: str, classifications: List[Dict]):
        """CSV 데이터에 결과 추가"""
        # Index 추출
        index = self.extract_index_from_filename(pdf_filename)

        # 기본 행 데이터 생성 (15개 컬럼: Index 추가!)
        base_row = {
            "Index": index,  # Index 컬럼 추가!
            "Article Title": pdf_filename.replace('.pdf', ''),
            "Author Full Names": "",
            "Source Title": "",
            "Publication Year": "",
            "DOI Link": "",
            "Design Discipline": "",
            "Data About": "",
            "Data Modality": "",
            "AI methods": "",
            "AI Assistance Types (Lee and Kim, 2025)": "",
            "Design Phase": "",
            "Design Practice/Task": "",
            "Notes": f"Analyzed by PDF Analyzer on {datetime.now().strftime('%Y-%m-%d')}",
            "Questions": ""
        }
        
        # 분류 결과로 업데이트
        for classification in classifications:
            category = classification["category"] 
            value = classification["classification"]
            
            if category in base_row:
                base_row[category] = value
        
        # 3개 CSV용 데이터에 추가
        self.classification_results.append(base_row.copy())
        
        # 근거 데이터
        reasoning_row = base_row.copy()
        for classification in classifications:
            category = classification["category"]
            reasoning = classification["reasoning"]
            if category in reasoning_row:
                reasoning_row[category] = reasoning
        self.reasoning_results.append(reasoning_row)
        
        # 참고 원문 데이터
        reference_row = base_row.copy()
        for classification in classifications:
            category = classification["category"] 
            reference = classification["reference_text"]
            if category in reference_row:
                reference_row[category] = reference
        self.reference_results.append(reference_row)


def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description='PDF 논문 자동 분류 시스템 (기본: 자동으로 이어서 실행)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python3 pdf_analyzer.py 5                       # 5개 처리 (자동 이어서 실행)
  python3 pdf_analyzer.py 5                       # 다시 실행 → 다음 5개 처리
  python3 pdf_analyzer.py 10                      # 다시 실행 → 다음 10개 처리
  python3 pdf_analyzer.py 20 --reset              # 진행 상태 초기화 후 처음부터 20개
  python3 pdf_analyzer.py 3 --retry-failed        # 실패한 것 중 3개만 재시도
  nohup python3 pdf_analyzer.py 10 &              # 백그라운드로 10개 처리
        """
    )
    parser.add_argument('count', type=int,
                       help='처리할 PDF 개수 (필수)')
    parser.add_argument('--reset', action='store_true',
                       help='진행 상태 초기화 후 처음부터 시작')
    parser.add_argument('--retry-failed', action='store_true',
                       help='실패한 PDF만 재시도')
    args = parser.parse_args()

    print("🚀 PDF 논문 자동 분류 시스템 시작\n")

    # PDF 분석기 초기화
    analyzer = PDFAnalyzer()

    # Reset 모드: progress.json 삭제
    if args.reset:
        if analyzer.progress_file.exists():
            analyzer.progress_file.unlink()
            backup_file = analyzer.progress_file.with_suffix('.json.backup')
            if backup_file.exists():
                backup_file.unlink()
            print("✅ 진행 상태 초기화 완료 (progress.json 삭제)\n")
        else:
            print("ℹ️  진행 상태 파일이 없습니다.\n")

    # Google Sheets 연결 확인
    if not analyzer.connect_to_sheets():
        print("❌ Google Sheets 연결 실패로 인한 중단")
        return False

    # 모든 PDF 파일 처리 (기본: resume 모드)
    results = analyzer.process_all_pdfs(
        use_filtering=True,
        resume=not args.reset,  # reset이 아니면 항상 resume
        retry_failed=args.retry_failed,
        limit=args.count
    )

    if "error" in results:
        print(f"❌ 처리 실패: {results['error']}")
        return False

    if results["successful"] > 0:
        print(f"\n🎉 완료! {results['successful']}개 PDF 파일 분석 성공")
        return True
    else:
        print("❌ 처리된 PDF 파일이 없습니다.")
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n📋 문제해결 체크리스트:")
        print("1. Papers 폴더에 PDF 파일 존재 확인")
        print("2. Google Sheets API 연결 확인")
        print("3. Claude CLI 설치 및 인증 확인")
        print("4. 네트워크 연결 상태 확인")