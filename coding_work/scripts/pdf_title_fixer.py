"""
PDF Title Fixer Script
paper_tracking.py에서 Mark='M'으로 필터링된 논문 제목을 사용해서
Papers 폴더의 PDF 파일명을 정확한 논문 제목으로 변경하는 스크립트
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd
import pdfplumber
import time

# paper_tracking.py 모듈 임포트를 위한 경로 설정
sys.path.append(str(Path(__file__).parent))
from paper_tracking import PaperTracker


class PDFTitleFixer:
    """PDF 제목 픽싱 클래스"""
    
    def __init__(self, papers_folder: str = None, credentials_path: str = None):
        """
        PDF Title Fixer 초기화
        
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
        
        # Paper Tracker 초기화 (기본 설정 사용)
        self.tracker = PaperTracker()
        
        # 처리 결과 저장용
        self.processing_log = []
        
    def connect_to_sheets(self) -> bool:
        """Google Sheets 연결"""
        if not self.tracker.connect():
            print("❌ Google Sheets 연결 실패")
            return False
        print("✅ Google Sheets 연결 성공")
        return True
    
    def get_all_paper_data(self) -> List[Dict[str, str]]:
        """
        3rd Screening 시트의 모든 논문 데이터 가져오기 (Index와 Title 포함)
        
        Returns:
            List[Dict]: [{"index": "1", "title": "논문제목"}, ...] 형식의 리스트
        """
        print("📋 3rd Screening 시트의 모든 논문 데이터 추출 중...")
        
        try:
            # 모든 논문 데이터 가져오기
            all_papers = self.tracker.get_all_papers()
            
            if all_papers.empty:
                print("❌ 3rd Screening 시트에서 논문을 찾을 수 없습니다.")
                return []
            
            print(f"✅ 3rd Screening 시트에서 {len(all_papers)}개 논문 발견")
            
            # Index와 Article Title 컬럼 확인
            if 'Index' not in all_papers.columns:
                print("❌ 'Index' 컬럼을 찾을 수 없습니다.")
                print(f"📋 사용 가능한 컬럼: {list(all_papers.columns)[:5]}...")
                return []
            
            if 'Article Title' not in all_papers.columns:
                print("❌ 'Article Title' 컬럼을 찾을 수 없습니다.")
                print(f"📋 사용 가능한 컬럼: {list(all_papers.columns)[:5]}...")
                return []
            
            # Index와 Title 데이터 추출
            paper_data = []
            for _, row in all_papers.iterrows():
                index = str(row['Index']).strip()
                title = str(row['Article Title']).strip()
                
                if index and title:  # 빈 값 제거
                    paper_data.append({
                        "index": index,
                        "title": title
                    })
            
            print(f"📝 유효한 논문 데이터 {len(paper_data)}개 추출")
            return paper_data
                
        except Exception as e:
            print(f"❌ 논문 데이터 추출 실패: {str(e)}")
            return []
    
    def get_assigned_m_paper_data(self) -> List[Dict[str, str]]:
        """
        3rd Screening 시트에서 Assigned_to='M'인 논문 데이터만 가져오기

        Returns:
            List[Dict]: [{"index": "1", "title": "논문제목"}, ...] 형식의 리스트
        """
        print("📋 Assigned_to='M' 논문 데이터 추출 중...")
        
        try:
            # 모든 논문 데이터 가져오기
            all_papers = self.tracker.get_all_papers()
            
            if all_papers.empty:
                print("❌ 3rd Screening 시트에서 논문을 찾을 수 없습니다.")
                return []
            
            print(f"✅ 3rd Screening 시트에서 {len(all_papers)}개 논문 발견")
            
            # 필수 컬럼 확인
            required_columns = ['Index', 'Article Title', 'Assigned_to']
            for col in required_columns:
                if col not in all_papers.columns:
                    print(f"❌ '{col}' 컬럼을 찾을 수 없습니다.")
                    print(f"📋 사용 가능한 컬럼: {list(all_papers.columns)}")
                    return []
            
            # Assigned_to='M' 필터링
            m_assigned_papers = all_papers[all_papers['Assigned_to'].str.upper() == 'M']
            print(f"🎯 Assigned_to='M' 논문: {len(m_assigned_papers)}개 발견")
            
            # Index와 Title 데이터 추출
            paper_data = []
            for _, row in m_assigned_papers.iterrows():
                index = str(row['Index']).strip()
                title = str(row['Article Title']).strip()
                
                if index and title:  # 빈 값 제거
                    paper_data.append({
                        "index": index,
                        "title": title
                    })
            
            print(f"📝 유효한 Assigned_to='M' 논문 데이터 {len(paper_data)}개 추출")
            return paper_data
                
        except Exception as e:
            print(f"❌ 논문 데이터 추출 실패: {str(e)}")
            return []

    def get_uploaded_indices(self) -> set:
        """
        Google Sheets에서 PDF_uploaded='Y'인 Index 리스트 가져오기

        Returns:
            set: {'23', '101', '148', ...} 형태의 Index 집합
        """
        try:
            print("🔍 Google Sheets에서 업로드 완료된 Index 조회 중...")

            sheet = self.tracker.connector.get_sheet('3rd Screening')
            all_values = sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                print("❌ 시트 데이터를 읽을 수 없습니다.")
                return set()

            headers = all_values[0]

            # Index와 PDF_uploaded 컬럼 위치 찾기
            try:
                index_col_idx = headers.index('Index')
            except ValueError:
                print("❌ 'Index' 컬럼을 찾을 수 없습니다.")
                return set()

            # PDF_uploaded 컬럼 찾기 (여러 변형 지원)
            pdf_upload_col_idx = None
            possible_names = [
                'pdf_upload', 'PDF_Upload', 'PDF Upload', 'pdf upload',
                'PDF_uploaded', 'pdf_uploaded', 'PDF uploaded'
            ]

            for col_name in possible_names:
                if col_name in headers:
                    pdf_upload_col_idx = headers.index(col_name)
                    break

            if pdf_upload_col_idx is None:
                print("❌ 'PDF_uploaded' 컬럼을 찾을 수 없습니다.")
                return set()

            # PDF_uploaded='Y'인 Index만 추출
            uploaded_indices = set()
            for row in all_values[1:]:
                if len(row) > max(index_col_idx, pdf_upload_col_idx):
                    if row[pdf_upload_col_idx].upper() == 'Y':
                        index = row[index_col_idx].strip()
                        if index:
                            uploaded_indices.add(index)

            print(f"✅ 업로드 완료된 논문: {len(uploaded_indices)}개")
            if uploaded_indices:
                sample_indices = sorted(list(uploaded_indices)[:5], key=lambda x: int(x) if x.isdigit() else 0)
                print(f"   샘플: {sample_indices}...")

            return uploaded_indices

        except Exception as e:
            print(f"❌ 업로드 Index 조회 실패: {str(e)}")
            return set()

    def get_pdf_files(self, skip_uploaded: bool = True) -> List[Path]:
        """
        Papers 폴더에서 처리할 PDF 파일 목록 가져오기

        Args:
            skip_uploaded: True면 이미 업로드된(PDF_uploaded='Y') 파일 제외

        Returns:
            List[Path]: 처리할 PDF 파일 경로 리스트
        """
        if not self.papers_folder.exists():
            print(f"❌ Papers 폴더를 찾을 수 없습니다: {self.papers_folder}")
            return []

        # 전체 PDF 파일 목록
        all_pdf_files = list(self.papers_folder.glob("*.pdf"))
        print(f"📁 Papers 폴더에서 {len(all_pdf_files)}개 PDF 파일 발견")

        # skip_uploaded가 False면 전체 반환
        if not skip_uploaded:
            print("⚠️  skip_uploaded=False: 모든 파일 처리")
            return all_pdf_files

        # Google Sheets에서 이미 업로드된 Index 리스트 가져오기
        uploaded_indices = self.get_uploaded_indices()

        # PDF 파일 필터링
        unprocessed_files = []
        skipped_files = []

        for pdf_file in all_pdf_files:
            # 파일명에서 Index 추출 시도 (패턴: {Index}_Title.pdf)
            match = re.match(r'^(\d+)_', pdf_file.name)
            if match:
                index = match.group(1)
                if index in uploaded_indices:
                    skipped_files.append(pdf_file.name)
                    continue  # 이미 처리된 파일 skip

            unprocessed_files.append(pdf_file)

        # 결과 출력
        print(f"⏭️  이미 처리됨 (skip): {len(skipped_files)}개")
        if skipped_files and len(skipped_files) <= 5:
            for filename in skipped_files[:5]:
                print(f"     - {filename[:60]}...")
        elif skipped_files:
            print(f"     - {skipped_files[0][:60]}...")
            print(f"     ... (총 {len(skipped_files)}개)")

        print(f"🎯 처리 대상: {len(unprocessed_files)}개")
        if unprocessed_files:
            for i, pdf_file in enumerate(unprocessed_files[:3], 1):
                print(f"     {i}. {pdf_file.name[:60]}...")
            if len(unprocessed_files) > 3:
                print(f"     ... 외 {len(unprocessed_files) - 3}개")

        return unprocessed_files
    
    def extract_pdf_text(self, pdf_path: Path, max_pages: int = 3) -> str:
        """
        PDF 파일의 첫 N페이지 텍스트 추출
        
        Args:
            pdf_path: PDF 파일 경로
            max_pages: 읽을 최대 페이지 수
            
        Returns:
            str: 추출된 텍스트
        """
        try:
            print(f"📖 PDF 텍스트 추출 중: {pdf_path.name} (첫 {max_pages}페이지)")
            
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                # 첫 N페이지 또는 전체 페이지 중 적은 것
                pages_to_read = min(max_pages, len(pdf.pages))
                
                for i in range(pages_to_read):
                    page = pdf.pages[i]
                    page_text = page.extract_text()
                    
                    if page_text:
                        text_content.append(f"=== Page {i+1} ===\n{page_text}")
                    else:
                        text_content.append(f"=== Page {i+1} ===\n[텍스트 없음]")
            
            full_text = "\n\n".join(text_content)
            
            # 텍스트 길이 제한 (Claude 입력 최적화)
            if len(full_text) > 5000:
                full_text = full_text[:5000] + "\n[텍스트 길이 제한으로 인한 잘림...]"
            
            print(f"✅ 텍스트 추출 완료: {len(full_text)} 문자")
            return full_text
            
        except Exception as e:
            print(f"❌ PDF 텍스트 추출 실패 ({pdf_path.name}): {str(e)}")
            return ""
    
    def match_with_claude(self, pdf_text: str, paper_data: List[Dict[str, str]], max_retries: int = 3) -> Optional[Dict[str, str]]:
        """
        Claude CLI를 사용해서 PDF 텍스트와 매칭되는 논문 찾기
        
        Args:
            pdf_text: PDF에서 추출된 텍스트
            paper_data: [{"index": "1", "title": "제목"}, ...] 형식의 논문 데이터
            max_retries: 최대 재시도 횟수
            
        Returns:
            Optional[Dict]: {"index": "1", "title": "매칭된 제목"} 또는 None
        """
        print("🤖 Claude로 논문 매칭 중...")
        
        # Claude에게 줄 프롬프트 생성 (Index 포함)
        paper_list = []
        for paper in paper_data:
            paper_list.append(f"{paper['index']:>3}. {paper['title']}")
        
        prompt = f"""이 PDF의 제목을 아래 리스트에서 찾아주세요.

PDF 텍스트:
{pdf_text[:1000]}

논문 리스트 (Index. Title):
{chr(10).join(paper_list)}

위 리스트에서 PDF와 가장 관련 있는 논문을 하나 선택해주세요. 
정확히 일치하지 않아도 가장 유사한 것을 찾아주세요.

Respond ONLY with valid JSON. No explanations, no insights, no other text:

{{
  "matched_index": "선택한 논문의 Index",
  "matched_title": "선택한 논문의 제목"
}}"""

        # 재시도 로직
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 재시도 {attempt}/{max_retries-1} (10초 대기 후)")
                    time.sleep(10)  # 10초 대기
                
                print(f"📞 Claude CLI 호출 중... (시도 {attempt + 1}/{max_retries})")
                
                # Claude CLI 호출 (JSON 형식 응답 강제)
                result = subprocess.run(
                    ['claude', '--model', 'sonnet', '-p', '--output-format', 'json', prompt], 
                    capture_output=True, 
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    print(f"❌ Claude CLI 실행 실패 (시도 {attempt + 1}): {result.stderr}")
                    if attempt < max_retries - 1:
                        continue
                    return None
                
                response = result.stdout.strip()
                print(f"🤖 Claude 응답: {response}")
                
                # Claude CLI JSON 메타데이터 파싱
                try:
                    response_metadata = json.loads(response)
                    
                    # 실제 Claude 답변은 'result' 필드에 있음
                    if 'result' in response_metadata:
                        claude_answer = response_metadata['result']
                        
                        # Claude 답변에서 JSON 추출 (여러 패턴 시도)
                        import re
                        json_str = None
                        
                        # 패턴 1: ```json {...} ```
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', claude_answer, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            # 패턴 2: 단순 {...} 패턴
                            alt_match = re.search(r'\{[^{}]*"matched_index"[^{}]*\}', claude_answer)
                            if alt_match:
                                json_str = alt_match.group(0)
                        
                        if json_str:
                            try:
                                answer_json = json.loads(json_str)
                                matched_index = answer_json.get('matched_index')
                                matched_title = answer_json.get('matched_title')
                                
                                if matched_index and matched_title:
                                    result_dict = {
                                        "index": matched_index,
                                        "title": matched_title
                                    }
                                    print(f"✅ 매칭 성공: [{matched_index}] {matched_title[:50]}...")
                                    return result_dict
                                else:
                                    print(f"❌ 매칭된 논문이 없음 (시도 {attempt + 1})")
                                    if attempt < max_retries - 1:
                                        continue
                                    return None
                                
                            except json.JSONDecodeError as e:
                                print(f"❌ Claude 답변 내 JSON 파싱 실패 (시도 {attempt + 1}): {e}")
                                if attempt < max_retries - 1:
                                    continue
                                return None
                        else:
                            print(f"❌ Claude 답변에서 JSON 형식을 찾을 수 없음 (시도 {attempt + 1})")
                            if attempt < max_retries - 1:
                                continue
                            return None
                    else:
                        print(f"❌ Claude 응답에 'result' 필드가 없음 (시도 {attempt + 1})")
                        if attempt < max_retries - 1:
                            continue
                        return None
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Claude 메타데이터 JSON 파싱 실패 (시도 {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        continue
                    return None
                    
            except subprocess.TimeoutExpired:
                print(f"❌ Claude CLI 타임아웃 (시도 {attempt + 1})")
                if attempt < max_retries - 1:
                    continue
                return None
            except Exception as e:
                print(f"❌ Claude CLI 호출 실패 (시도 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    continue
                return None
        
        print(f"❌ {max_retries}번 시도 후 모두 실패")
        return None
    
    def sanitize_filename(self, title: str, max_length: int = 200) -> str:
        """
        논문 제목을 안전한 파일명으로 변환
        
        Args:
            title: 원본 논문 제목
            max_length: 최대 파일명 길이
            
        Returns:
            str: 안전한 파일명
        """
        # 특수문자 제거 및 치환
        # Windows/macOS/Linux에서 사용할 수 없는 문자들: \/:*?"<>|
        safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
        
        # 연속된 공백을 하나로 통합
        safe_title = re.sub(r'\s+', ' ', safe_title)
        
        # 양 끝 공백 제거
        safe_title = safe_title.strip()
        
        # 공백을 언더스코어로 변경 (선택사항)
        # safe_title = safe_title.replace(' ', '_')
        
        # 길이 제한
        if len(safe_title) > max_length:
            safe_title = safe_title[:max_length].strip()
            # 마지막 단어가 잘렸을 수 있으므로 마지막 공백까지 제거
            last_space = safe_title.rfind(' ')
            if last_space > max_length - 20:  # 너무 많이 자르지 않도록
                safe_title = safe_title[:last_space]
        
        return safe_title
    
    def rename_pdf_file(self, old_path: Path, matched_paper: Dict[str, str], dry_run: bool = False) -> bool:
        """
        PDF 파일 이름 변경 (Index_Title 형식으로)
        
        Args:
            old_path: 기존 PDF 파일 경로
            matched_paper: {"index": "1", "title": "제목"} 형식의 매칭된 논문 정보
            dry_run: True면 실제 변경하지 않고 시뮬레이션만
            
        Returns:
            bool: 성공 여부
        """
        try:
            # Index_Title 형식의 파일명 생성
            index = matched_paper["index"]
            title = matched_paper["title"]
            safe_title = self.sanitize_filename(title)
            new_filename = f"{index}_{safe_title}"
            new_path = old_path.parent / f"{new_filename}.pdf"
            
            print(f"📝 파일명 변경:")
            print(f"   이전: {old_path.name}")
            print(f"   이후: {new_path.name}")
            
            if dry_run:
                print("   [DRY-RUN] 실제 변경하지 않음")
                return True
            
            # 파일명 변경 (덮어쓰기)
            old_path.rename(new_path)
            print("   ✅ 파일명 변경 완료")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 파일명 변경 실패: {str(e)}")
            return False
    
    def process_all_pdfs(self, dry_run: bool = False, debug: bool = False) -> Dict:
        """
        모든 PDF 파일 처리
        
        Args:
            dry_run: True면 실제 변경하지 않고 시뮬레이션만
            
        Returns:
            Dict: 처리 결과 통계
        """
        print("=" * 60)
        print("🔧 PDF Title Fixer 시작")
        print("=" * 60)
        
        # Google Sheets 연결
        if not self.connect_to_sheets():
            return {"error": "Google Sheets 연결 실패"}
        
        # 3rd Screening 시트의 모든 논문 데이터 가져오기
        paper_data = self.get_all_paper_data()
        if not paper_data:
            return {"error": "3rd Screening 시트에 논문 데이터 없음"}
        
        # PDF 파일 목록 가져오기
        pdf_files = self.get_pdf_files()
        if not pdf_files:
            return {"error": "PDF 파일 없음"}
        
        # 처리 통계
        stats = {
            "total_pdfs": len(pdf_files),
            "total_papers": len(paper_data),
            "processed": 0,
            "matched": 0,
            "renamed": 0,
            "failed": 0,
            "results": []
        }
        
        print(f"\n🎯 처리 대상:")
        print(f"   PDF 파일: {len(pdf_files)}개")
        print(f"   3rd Screening 논문: {len(paper_data)}개")
        print(f"   모드: {'DRY-RUN' if dry_run else 'LIVE'}")
        print()
        
        # 각 PDF 파일 처리
        files_to_process = pdf_files
        for i, pdf_file in enumerate(files_to_process, 1):
            print(f"📄 [{i}/{len(files_to_process)}] 처리 중: {pdf_file.name}")
            
            result = {
                "pdf_file": pdf_file.name,
                "matched_index": None,
                "matched_title": None,
                "success": False,
                "error": None
            }
            
            try:
                # 1. PDF 텍스트 추출
                pdf_text = self.extract_pdf_text(pdf_file)
                if not pdf_text.strip():
                    result["error"] = "텍스트 추출 실패"
                    stats["failed"] += 1
                    stats["results"].append(result)
                    print("❌ 텍스트 추출 실패, 다음 파일로 이동\n")
                    continue
                
                # 2. Claude로 논문 매칭
                matched_paper = self.match_with_claude(pdf_text, paper_data)
                if not matched_paper:
                    result["error"] = "논문 매칭 실패"
                    stats["failed"] += 1
                    stats["results"].append(result)
                    print("❌ 논문 매칭 실패, 다음 파일로 이동\n")
                    continue
                
                stats["matched"] += 1
                result["matched_index"] = matched_paper["index"]
                result["matched_title"] = matched_paper["title"]
                
                # 3. 파일명 변경
                if self.rename_pdf_file(pdf_file, matched_paper, dry_run):
                    stats["renamed"] += 1
                    result["success"] = True
                else:
                    result["error"] = "파일명 변경 실패"
                
                stats["results"].append(result)
                print("✅ 처리 완료")
                
                # 다음 파일 처리 전 10초 대기
                if i < len(files_to_process):  # 마지막 파일이 아닌 경우에만 대기
                    print("⏳ 10초 대기 중...")
                    time.sleep(10)
                print()
                
            except Exception as e:
                result["error"] = str(e)
                stats["failed"] += 1
                stats["results"].append(result)
                print(f"❌ 처리 실패: {str(e)}")
                
                # 실패한 경우에도 10초 대기
                if i < len(files_to_process):
                    print("⏳ 10초 대기 중...")
                    time.sleep(10)
                print()
            
            stats["processed"] += 1
        
        # 최종 결과 출력
        print("=" * 60)
        print("📊 처리 결과")
        print("=" * 60)
        print(f"전체 PDF: {stats['total_pdfs']}개")
        print(f"처리 완료: {stats['processed']}개")
        print(f"매칭 성공: {stats['matched']}개")
        print(f"파일명 변경: {stats['renamed']}개")
        print(f"처리 실패: {stats['failed']}개")
        
        if dry_run:
            print("\n⚠️  DRY-RUN 모드: 실제 파일은 변경되지 않았습니다.")
        
        return stats


def main():
    """메인 실행 함수"""
    print("🚀 PDF Title Fixer 시작\n")
    
    # PDF Title Fixer 초기화
    fixer = PDFTitleFixer()
    
    # 바로 실제 실행
    print("🔧 PDF 파일명 변경 시작...")
    results = fixer.process_all_pdfs(dry_run=False)
    
    if "error" in results:
        print(f"❌ 실행 실패: {results['error']}")
        return False
    
    if results["renamed"] > 0:
        print(f"\n🎉 완료! {results['renamed']}개 파일명이 변경되었습니다.")
        
        # 성공한 결과들 출력
        for result in results["results"]:
            if result["success"]:
                print(f"   ✅ {result['pdf_file']} → [{result['matched_index']}] {result['matched_title'][:50]}...")
        
        return True
    else:
        print("❌ 변경된 파일이 없습니다.")
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n📋 문제 해결 체크리스트:")
        print("1. Google Sheets API 연결 확인")
        print("2. Papers 폴더에 PDF 파일 존재 확인")
        print("3. '3rd Screening' 시트에 논문이 존재하는지 확인")
        print("4. Claude CLI 설치 및 작동 확인")