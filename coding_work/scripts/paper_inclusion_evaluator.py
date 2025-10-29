"""
Paper Inclusion Evaluator
3rd Screening 시트에서 Assinged_to='J' 논문들을 자동으로 평가하여
Inclusion 컬럼에 'Y' 기록하는 스크립트

평가 기준: "AI-based study for Design (Plus, empirical studies)"
"""

import os
import sys
import json
import subprocess
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
import pdfplumber

# paper_tracking.py 모듈 임포트를 위한 경로 설정
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


class PaperInclusionEvaluator:
    """논문 Inclusion 자동 평가 클래스"""

    def __init__(self, papers_folder: str = None, credentials_path: str = None):
        """
        Paper Inclusion Evaluator 초기화

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

        # CodeBook 로드
        self.codebook = self.load_codebook()

    def load_codebook(self) -> Dict:
        """
        source/CodeBook.csv에서 분류 기준 로드

        Returns:
            Dict: CodeBook 데이터
        """
        codebook_path = Path(__file__).parent.parent.parent / "source" / "CodeBook.csv"

        try:
            # CodeBook CSV는 1행(제목), 2행(헤더), 3행부터 데이터이므로 header=1 사용
            df = pd.read_csv(codebook_path, encoding='utf-8-sig', header=1)

            # AI methods 추출 (컬럼 인덱스 6)
            ai_methods_col = 'AI methods'
            ai_methods = []
            if ai_methods_col in df.columns:
                ai_methods = df[ai_methods_col].dropna().tolist()
                ai_methods = [str(m).strip() for m in ai_methods if str(m).strip() and str(m).lower() not in ['nan', '']]

            # Design Disciplines 추출 (컬럼 인덱스 0)
            design_disciplines_col = 'Design Discipline'
            design_disciplines = []
            if design_disciplines_col in df.columns:
                design_disciplines = df[design_disciplines_col].dropna().tolist()
                design_disciplines = [str(d).strip() for d in design_disciplines if str(d).strip() and str(d).lower() not in ['nan', '']]

            # Design Phases 추출 (컬럼 인덱스 10)
            design_phases_col = 'Design Phase'
            design_phases = []
            if design_phases_col in df.columns:
                design_phases = df[design_phases_col].dropna().tolist()
                design_phases = [str(p).strip() for p in design_phases if str(p).strip() and str(p).lower() not in ['nan', '']]

            # AI Assistance Types 추출 (컬럼 인덱스 8)
            assistance_types_col = 'AI Assistance Types (Lee and Kim, 2025)'
            assistance_types = []
            if assistance_types_col in df.columns:
                assistance_types = df[assistance_types_col].dropna().tolist()
                assistance_types = [str(a).strip() for a in assistance_types if str(a).strip() and str(a).lower() not in ['nan', '']]

            print(f"📚 CodeBook 로드 완료:")
            print(f"   AI Methods: {len(ai_methods)}개")
            print(f"   Design Disciplines: {len(design_disciplines)}개")
            print(f"   Design Phases: {len(design_phases)}개")
            print(f"   Assistance Types: {len(assistance_types)}개")

            return {
                "ai_methods": ai_methods,
                "design_disciplines": design_disciplines,
                "design_phases": design_phases,
                "assistance_types": assistance_types
            }

        except Exception as e:
            print(f"⚠️  CodeBook 로드 실패 (기본값 사용): {str(e)}")
            # 로드 실패 시 기본값 반환
            return {
                "ai_methods": ["CNN", "GPT", "Random Forest", "Reinforcement Learning", "GAN", "LSTM"],
                "design_disciplines": ["product design", "service design", "UI/UX", "engineering design"],
                "design_phases": ["Discovery", "Define", "Develop", "Delivery"],
                "assistance_types": ["Design generation", "Prediction", "Decision making", "Coordination"]
            }

    def connect_to_sheets(self) -> bool:
        """Google Sheets 연결"""
        if not self.connector.connect():
            print("❌ Google Sheets 연결 실패")
            return False
        print("✅ Google Sheets 연결 성공")
        return True

    def get_assigned_j_papers(self) -> pd.DataFrame:
        """
        3rd Screening 시트에서 Assigned_to='J'인 논문 데이터 가져오기

        Returns:
            DataFrame: Assigned_to='J'인 논문들
        """
        print("📋 Assigned_to='J' 논문 데이터 추출 중...")

        try:
            # 모든 논문 데이터 가져오기
            sheet = self.connector.get_sheet(self.sheet_name)
            all_values = sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                print("❌ 3rd Screening 시트에서 데이터를 찾을 수 없습니다.")
                return pd.DataFrame()

            # DataFrame 생성 (첫 번째 행을 헤더로 사용)
            headers = all_values[0]
            data = all_values[1:]
            df = pd.DataFrame(data, columns=headers)

            print(f"✅ 3rd Screening 시트에서 {len(df)}개 논문 발견")

            # 필수 컬럼 확인
            required_columns = ['Index', 'Article Title', 'Assigned_to']
            for col in required_columns:
                if col not in df.columns:
                    print(f"❌ '{col}' 컬럼을 찾을 수 없습니다.")
                    print(f"📋 사용 가능한 컬럼: {list(df.columns)[:10]}...")
                    return pd.DataFrame()

            # Inclusion 컬럼 찾기 (여러 변형 지원)
            inclusion_col = None
            possible_inclusion_names = [
                'Inclusion', 'inclusion', 'INCLUSION',
                'Inclusion (Y/N/Q)', 'Inclusion (Y/N/Q/R)',
                'Inclusion (Y/N/Q/R) for 2nd screening'
            ]

            for col_name in possible_inclusion_names:
                if col_name in df.columns:
                    inclusion_col = col_name
                    break

            # 부분 매치 시도
            if inclusion_col is None:
                for col_name in df.columns:
                    if 'inclusion' in col_name.lower():
                        inclusion_col = col_name
                        break

            if inclusion_col is None:
                print("⚠️  Inclusion 컬럼을 찾을 수 없습니다. 업데이트가 제한될 수 있습니다.")
            else:
                print(f"✅ Inclusion 컬럼 발견: '{inclusion_col}'")

            # Note 컬럼 확인 (정확한 이름 사용)
            notes_col = 'Note' if 'Note' in df.columns else None

            if notes_col is None:
                print("⚠️  'Note' 컬럼을 찾을 수 없습니다. 판단 결과 기록이 제한될 수 있습니다.")
            else:
                print(f"✅ Note 컬럼 발견: '{notes_col}'")

            # Assigned_to='J' 필터링
            j_assigned_papers = df[df['Assigned_to'].str.upper() == 'J'].copy()
            print(f"🎯 Assigned_to='J' 논문: {len(j_assigned_papers)}개 발견")

            # 🚫 [임시 비활성화] 이미 Inclusion이 'Y' 또는 'N'인 논문 제외 (빈 값만 처리)
            # if inclusion_col:
            #     before_count = len(j_assigned_papers)
            #     # Inclusion이 비어있거나 공백인 것만 처리
            #     j_assigned_papers = j_assigned_papers[
            #         (j_assigned_papers[inclusion_col].str.strip() == '') |
            #         (j_assigned_papers[inclusion_col].isna())
            #     ].copy()
            #     excluded_count = before_count - len(j_assigned_papers)
            #     if excluded_count > 0:
            #         print(f"⏭️  이미 Inclusion 평가된 논문 {excluded_count}개 제외")
            #     print(f"✅ 처리 대상: {len(j_assigned_papers)}개 (Inclusion 미평가만)")
            print(f"⚠️  [주의] Inclusion skip 로직 비활성화 - 모든 논문 재평가")

            # 컬럼 이름 저장
            if inclusion_col:
                j_assigned_papers['_inclusion_col_name'] = inclusion_col
            if notes_col:
                j_assigned_papers['_notes_col_name'] = notes_col

            return j_assigned_papers

        except Exception as e:
            print(f"❌ 논문 데이터 추출 실패: {str(e)}")
            return pd.DataFrame()

    def find_pdf_by_index(self, index: str) -> Optional[Path]:
        """
        Index로 PDF 파일 찾기

        Args:
            index: 논문 Index (예: "101")

        Returns:
            Path: 찾은 PDF 경로 또는 None
        """
        # Papers/{index}_*.pdf 패턴 매칭
        pattern = f"{index}_*.pdf"
        matching_files = list(self.papers_folder.glob(pattern))

        if matching_files:
            return matching_files[0]

        return None

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
            if len(full_text) > 8000:
                full_text = full_text[:8000] + "\n[텍스트 길이 제한으로 인한 잘림...]"

            print(f"✅ 텍스트 추출 완료: {len(full_text)} 문자")
            return full_text

        except Exception as e:
            print(f"❌ PDF 텍스트 추출 실패 ({pdf_path.name}): {str(e)}")
            return ""

    def evaluate_with_claude(self, pdf_text: str, title: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Claude CLI를 사용해서 논문이 Inclusion 기준에 부합하는지 평가

        Args:
            pdf_text: PDF에서 추출된 텍스트
            title: 논문 제목
            max_retries: 최대 재시도 횟수

        Returns:
            Optional[Dict]: 평가 결과 또는 None
        """
        print("🤖 Claude로 논문 평가 중...")

        # CodeBook에서 AI methods와 Design disciplines 가져오기
        ai_methods_examples = ", ".join(self.codebook["ai_methods"][:6]) if self.codebook["ai_methods"] else "CNN, GPT, Random Forest, GAN"
        design_disciplines_list = ", ".join(self.codebook["design_disciplines"][:5]) if self.codebook["design_disciplines"] else "product design, service design, UI/UX, engineering design"
        assistance_types = ", ".join(self.codebook["assistance_types"][:4]) if self.codebook["assistance_types"] else "Design generation, Prediction, Decision making"

        prompt = f"""Evaluate if this paper meets the inclusion criteria:
"AI-based study that SUPPORTS design tasks or processes (directly or indirectly) (Plus, empirical studies)"

Paper Title: {title}

Paper Content (First 3 pages):
{pdf_text[:3000]}

Evaluation Criteria:
1. **AI must perform or support design tasks or processes (directly or indirectly)**

   ✅ INCLUDE (AI supports design tasks/processes):
   - AI generates UI layouts, visual designs, or product forms (direct)
   - AI optimizes design parameters or configurations (direct)
   - AI recommends design alternatives or solutions (direct)
   - AI automates design processes (e.g., code generation, prototyping) (direct)
   - AI assists designers in real-time design decisions (direct)
   - AI analyzes user data to inform design decisions (indirect)
   - AI predicts user preferences or behavior to guide design (indirect)
   - AI evaluates or assesses design quality/performance (indirect)
   - AI extracts design requirements from user feedback/data (indirect)
   - AI provides design insights, recommendations, or decision support (indirect)

   ❌ EXCLUDE (AI NOT related to design support):
   - Papers about "design of AI systems" only (e.g., neural network architecture design without design application)
   - Pure AI research that mentions design applications only theoretically without actual application
   - AI systems where design is completely unrelated to the AI's purpose

2. **MUST have a SPECIFIC AI/ML method explicitly mentioned**
   - Recognized AI methods from CodeBook: {ai_methods_examples}, etc.
   - Generic terms like "AI" or "machine learning" alone are NOT sufficient
   - If no specific AI method is found, decision MUST be "N"

3. **Design task or process must be the PRIMARY output or application**
   - Design can include: {design_disciplines_list}, interaction design
   - Common AI assistance types: {assistance_types}
   - The AI's role should be to produce, optimize, evaluate, or inform design creation (directly or indirectly)

4. Preferably includes empirical study/evaluation (not strictly required)

CRITICAL: Ask yourself - "Does the AI create, generate, optimize, evaluate, or inform design outputs or processes?"
If YES (whether directly or indirectly through insights, analysis, or recommendations), then consider "Y".
If NO (AI is completely unrelated to design support), then decision = "N".

Respond ONLY with valid JSON. No explanations, no insights, no other text:

{{
  "decision": "Y" or "N",
  "reason": "Brief 1-2 sentence explanation. Clearly state how AI supports design tasks/processes (directly or indirectly).",
  "ai_method_found": "SPECIFIC name of AI method (e.g., {ai_methods_examples}) or 'None' if not found",
  "design_task": "Design task or process that AI supports (e.g., 'UI layout generation', 'user preference analysis for design', 'design quality evaluation') or 'None'",
  "has_empirical_study": true or false
}}"""

        # 재시도 로직
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 재시도 {attempt}/{max_retries-1} (10초 대기 후)")
                    time.sleep(10)

                print(f"📞 Claude CLI 호출 중... (시도 {attempt + 1}/{max_retries})")

                # Claude CLI 호출 (JSON 형식 응답 강제)
                result = subprocess.run(
                    ['claude', '--model', 'sonnet', '-p', '--output-format', 'json', prompt],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode != 0:
                    print(f"❌ Claude CLI 실행 실패 (시도 {attempt + 1}): {result.stderr}")
                    if attempt < max_retries - 1:
                        continue
                    return None

                response = result.stdout.strip()

                # Claude CLI JSON 메타데이터 파싱
                try:
                    response_metadata = json.loads(response)

                    # 실제 Claude 답변은 'result' 필드에 있음
                    if 'result' in response_metadata:
                        claude_answer = response_metadata['result']

                        # Claude 답변에서 JSON 추출
                        import re
                        json_str = None

                        # 패턴 1: ```json {...} ```
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', claude_answer, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            # 패턴 2: 단순 {...} 패턴
                            alt_match = re.search(r'\{[^{}]*"decision"[^{}]*\}', claude_answer, re.DOTALL)
                            if alt_match:
                                json_str = alt_match.group(0)
                            else:
                                # 패턴 3: 전체 답변이 JSON인 경우
                                try:
                                    test_parse = json.loads(claude_answer)
                                    if 'decision' in test_parse:
                                        json_str = claude_answer
                                except:
                                    pass

                        if json_str:
                            try:
                                evaluation = json.loads(json_str)
                                decision = evaluation.get('decision')
                                reason = evaluation.get('reason', '')
                                ai_method = evaluation.get('ai_method_found', 'None')
                                design_task = evaluation.get('design_task', 'None')
                                has_empirical = evaluation.get('has_empirical_study', False)

                                if decision in ['Y', 'N']:
                                    result_dict = {
                                        "decision": decision,
                                        "reason": reason,
                                        "ai_method_found": ai_method,
                                        "design_task": design_task,
                                        "has_empirical_study": has_empirical
                                    }
                                    print(f"✅ 평가 완료: Decision={decision}")
                                    print(f"   이유: {reason[:100]}...")
                                    return result_dict
                                else:
                                    print(f"❌ 잘못된 decision 값: {decision}")
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
                            print(f"   답변: {claude_answer[:200]}...")
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

    def save_to_csv(self, output_path: str = None) -> str:
        """
        평가 결과를 CSV 파일로 저장

        Args:
            output_path: CSV 파일 경로 (None이면 기본 경로 사용)

        Returns:
            str: 저장된 파일 경로
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(Path(__file__).parent.parent / "results" / f"inclusion_evaluation_results_{timestamp}.csv")

        # 결과 디렉토리 생성
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # DataFrame 생성
        df = pd.DataFrame(self.results)

        # CSV 저장
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"📄 결과 CSV 저장: {output_path}")
        print(f"   총 {len(df)}개 논문 평가 결과 저장")

        return output_path

    def update_sheets_inclusion(self, index: str, inclusion_col_name: str, decision: str,
                               notes_col_name: str = None, evaluation_result: Dict = None,
                               dry_run: bool = False) -> bool:
        """
        Google Sheets의 Inclusion 컬럼에 'Y' 또는 'N' 업데이트 + Notes 컬럼에 AI 판단 결과 기록

        Args:
            index: 논문 Index
            inclusion_col_name: Inclusion 컬럼 이름
            decision: 'Y' 또는 'N'
            notes_col_name: Notes 컬럼 이름 (Optional)
            evaluation_result: AI 평가 결과 딕셔너리
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

            # Index 컬럼과 Inclusion 컬럼의 위치 찾기
            try:
                index_col_idx = headers.index('Index')
                inclusion_col_idx = headers.index(inclusion_col_name)
            except ValueError as e:
                print(f"❌ 컬럼을 찾을 수 없습니다: {e}")
                return False

            # Notes 컬럼 위치 찾기 (optional)
            notes_col_idx = None
            if notes_col_name:
                try:
                    notes_col_idx = headers.index(notes_col_name)
                except ValueError:
                    print(f"⚠️  Notes 컬럼을 찾을 수 없습니다: {notes_col_name}")

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
                print(f"   [DRY-RUN] Sheets 업데이트: Row={target_row}, Inclusion='{decision}'")
                if notes_col_idx is not None and evaluation_result:
                    notes_text = self._format_evaluation_notes(evaluation_result)
                    print(f"   [DRY-RUN] Notes 업데이트: {notes_text[:80]}...")
                return True

            # Inclusion 컬럼 업데이트 (컬럼 번호는 1부터 시작)
            self.connector.update_cell(
                sheet_name=self.sheet_name,
                row=target_row,
                col=inclusion_col_idx + 1,
                value=decision
            )
            print(f"   ✅ Inclusion 업데이트 완료: Index={index}, Row={target_row}, Decision={decision}")

            # Notes 컬럼 업데이트 (AI 판단 결과)
            if notes_col_idx is not None and evaluation_result:
                notes_text = self._format_evaluation_notes(evaluation_result)
                self.connector.update_cell(
                    sheet_name=self.sheet_name,
                    row=target_row,
                    col=notes_col_idx + 1,
                    value=notes_text
                )
                print(f"   ✅ Notes 업데이트 완료: {notes_text[:60]}...")

            return True

        except Exception as e:
            print(f"❌ Sheets 업데이트 실패 (Index={index}): {str(e)}")
            return False

    def _format_evaluation_notes(self, evaluation: Dict) -> str:
        """
        AI 평가 결과를 Notes 컬럼용 텍스트로 포맷팅

        Args:
            evaluation: AI 평가 결과 딕셔너리

        Returns:
            str: 포맷팅된 Notes 텍스트
        """
        notes_parts = []

        # AI Method
        ai_method = evaluation.get('ai_method_found', 'None')
        if ai_method and ai_method != 'None':
            notes_parts.append(f"AI Method: {ai_method}")

        # Design Task
        design_task = evaluation.get('design_task', 'None')
        if design_task and design_task != 'None':
            notes_parts.append(f"Design Task: {design_task}")

        # Reason
        reason = evaluation.get('reason', '')
        if reason:
            notes_parts.append(f"Reason: {reason}")

        # Empirical Study
        has_empirical = evaluation.get('has_empirical_study', False)
        notes_parts.append(f"Empirical: {'Yes' if has_empirical else 'No'}")

        return " | ".join(notes_parts)

    def process_all_papers(self, dry_run: bool = False, test_index: str = None) -> Dict:
        """
        모든 논문 처리

        Args:
            dry_run: True면 실제 변경하지 않고 시뮬레이션만
            test_index: 특정 Index만 테스트 (디버깅용)

        Returns:
            Dict: 처리 결과 통계
        """
        print("=" * 60)
        print("🔧 Paper Inclusion Evaluator 시작")
        print("=" * 60)

        # Google Sheets 연결
        if not self.connect_to_sheets():
            return {"error": "Google Sheets 연결 실패"}

        # Assigned_to='J' 논문 데이터 가져오기
        j_papers = self.get_assigned_j_papers()
        if j_papers.empty:
            return {"error": "Assigned_to='J' 논문 데이터 없음"}

        # Inclusion 컬럼 이름 확인
        inclusion_col_name = None
        if '_inclusion_col_name' in j_papers.columns:
            inclusion_col_name = j_papers['_inclusion_col_name'].iloc[0]

        # Notes 컬럼 이름 확인
        notes_col_name = None
        if '_notes_col_name' in j_papers.columns:
            notes_col_name = j_papers['_notes_col_name'].iloc[0]

        # Papers 폴더에 있는 PDF와 매칭되는 논문만 필터링
        print(f"\n📁 Papers 폴더 스캔 중...")
        available_pdf_indices = set()

        if self.papers_folder.exists():
            for pdf_path in self.papers_folder.glob("*.pdf"):
                # {Index}_*.pdf 패턴에서 Index 추출
                import re
                match = re.match(r'^(\d+)_', pdf_path.name)
                if match:
                    available_pdf_indices.add(match.group(1))

        print(f"✅ Papers 폴더에서 {len(available_pdf_indices)}개 PDF 발견")

        # PDF가 있는 논문만 필터링
        before_pdf_filter = len(j_papers)
        j_papers = j_papers[j_papers['Index'].astype(str).isin(available_pdf_indices)].copy()

        if len(j_papers) < before_pdf_filter:
            excluded = before_pdf_filter - len(j_papers)
            print(f"⏭️  PDF 없는 논문 {excluded}개 제외")

        print(f"✅ 최종 처리 대상: {len(j_papers)}개 (PDF 보유 + Inclusion 미평가)")

        # 테스트 모드인 경우 특정 Index만 필터링
        if test_index:
            j_papers = j_papers[j_papers['Index'] == test_index]
            if j_papers.empty:
                return {"error": f"Index={test_index}를 찾을 수 없습니다."}
            print(f"\n🧪 테스트 모드: Index={test_index}만 처리")

        # 처리 통계
        stats = {
            "total_papers": len(j_papers),
            "processed": 0,
            "pdf_found": 0,
            "pdf_not_found": 0,
            "decision_y": 0,
            "decision_n": 0,
            "sheets_updated": 0,
            "failed": 0
        }

        print(f"\n🎯 처리 시작:")
        print(f"   처리 대상 논문: {len(j_papers)}개")
        print(f"   모드: {'DRY-RUN' if dry_run else 'LIVE'}")
        print()

        # 각 논문 처리
        for i, (idx, row) in enumerate(j_papers.iterrows(), 1):
            index = str(row['Index']).strip()
            title = str(row['Article Title']).strip()

            print(f"📄 [{i}/{len(j_papers)}] Index={index} 처리 중")
            print(f"   제목: {title[:80]}...")

            result = {
                "index": index,
                "title": title,
                "assigned_to": row['Assigned_to'],
                "pdf_found": False,
                "decision": None,
                "reason": None,
                "ai_method_found": None,
                "design_task": None,
                "has_empirical_study": None,
                "sheets_updated": False,
                "error": None,
                "timestamp": datetime.now().isoformat()
            }

            try:
                # 1. PDF 찾기
                pdf_path = self.find_pdf_by_index(index)
                if not pdf_path:
                    result["error"] = "PDF 파일 없음"
                    stats["pdf_not_found"] += 1
                    self.results.append(result)
                    print("   ❌ PDF 파일을 찾을 수 없습니다.\n")
                    continue

                result["pdf_found"] = True
                stats["pdf_found"] += 1
                print(f"   ✅ PDF 발견: {pdf_path.name}")

                # 2. PDF 텍스트 추출
                pdf_text = self.extract_pdf_text(pdf_path)
                if not pdf_text.strip():
                    result["error"] = "텍스트 추출 실패"
                    stats["failed"] += 1
                    self.results.append(result)
                    print("   ❌ 텍스트 추출 실패\n")
                    continue

                # 3. Claude 평가
                evaluation = self.evaluate_with_claude(pdf_text, title)
                if not evaluation:
                    result["error"] = "Claude 평가 실패"
                    stats["failed"] += 1
                    self.results.append(result)
                    print("   ❌ Claude 평가 실패\n")
                    continue

                # 평가 결과 저장
                result["decision"] = evaluation["decision"]
                result["reason"] = evaluation["reason"]
                result["ai_method_found"] = evaluation["ai_method_found"]
                result["design_task"] = evaluation["design_task"]
                result["has_empirical_study"] = evaluation["has_empirical_study"]

                if evaluation["decision"] == "Y":
                    stats["decision_y"] += 1
                else:
                    stats["decision_n"] += 1

                # 4. Inclusion 컬럼이 있으면 Sheets 업데이트 (Y 또는 N + Notes)
                if inclusion_col_name:
                    if self.update_sheets_inclusion(
                        index=index,
                        inclusion_col_name=inclusion_col_name,
                        decision=evaluation["decision"],
                        notes_col_name=notes_col_name,
                        evaluation_result=evaluation,
                        dry_run=dry_run
                    ):
                        result["sheets_updated"] = True
                        stats["sheets_updated"] += 1

                self.results.append(result)
                print("   ✅ 처리 완료")

                # 다음 논문 처리 전 10초 대기 (마지막이 아닌 경우)
                if i < len(j_papers):
                    print("   ⏳ 10초 대기 중...")
                    time.sleep(10)
                print()

            except Exception as e:
                result["error"] = str(e)
                stats["failed"] += 1
                self.results.append(result)
                print(f"   ❌ 처리 실패: {str(e)}")

                # 실패한 경우에도 10초 대기
                if i < len(j_papers):
                    print("   ⏳ 10초 대기 중...")
                    time.sleep(10)
                print()

            stats["processed"] += 1

        # 최종 결과 출력
        print("=" * 60)
        print("📊 처리 결과")
        print("=" * 60)
        print(f"전체 논문: {stats['total_papers']}개")
        print(f"처리 완료: {stats['processed']}개")
        print(f"PDF 발견: {stats['pdf_found']}개")
        print(f"PDF 없음: {stats['pdf_not_found']}개")
        print(f"Decision=Y: {stats['decision_y']}개")
        print(f"Decision=N: {stats['decision_n']}개")
        print(f"Sheets 업데이트: {stats['sheets_updated']}개")
        print(f"처리 실패: {stats['failed']}개")

        if dry_run:
            print("\n⚠️  DRY-RUN 모드: 실제 Sheets는 변경되지 않았습니다.")

        return stats


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Paper Inclusion Evaluator')
    parser.add_argument('--dry-run', action='store_true', help='시뮬레이션만 (Sheets 업데이트 안 함)')
    parser.add_argument('--test-index', type=str, help='특정 Index만 테스트 (디버깅용)')
    parser.add_argument('--max-retries', type=int, default=3, help='Claude 재시도 횟수 (기본: 3)')

    args = parser.parse_args()

    print("🚀 Paper Inclusion Evaluator 시작\n")

    # Evaluator 초기화
    evaluator = PaperInclusionEvaluator()

    # 논문 처리
    if args.test_index:
        print(f"🧪 테스트 모드: Index={args.test_index}")

    results = evaluator.process_all_papers(
        dry_run=args.dry_run,
        test_index=args.test_index
    )

    if "error" in results:
        print(f"❌ 실행 실패: {results['error']}")
        return False

    # 결과 CSV 저장
    if evaluator.results:
        csv_path = evaluator.save_to_csv()
        print(f"\n📁 결과 파일: {csv_path}")

    # 최종 통계
    if results["decision_y"] > 0:
        print(f"\n🎉 완료! {results['decision_y']}개 논문이 Inclusion 기준을 충족했습니다.")
        if not args.dry_run:
            print(f"   Google Sheets에 {results['sheets_updated']}개 업데이트됨")
    else:
        print("\n📋 Inclusion 기준을 충족하는 논문이 없습니다.")

    return True


if __name__ == "__main__":
    success = main()

    if not success:
        print("\n📋 문제 해결 체크리스트:")
        print("1. Google Sheets API 연결 확인")
        print("2. Papers 폴더에 PDF 파일 존재 확인")
        print("3. '3rd Screening' 시트에 논문이 존재하는지 확인")
        print("4. Claude CLI 설치 및 작동 확인 (claude --version)")
