#!/usr/bin/env python3
"""
표본검사 기반 코딩 결과 검증 시스템 (간소화 버전)

5개 무작위 논문을 선택하여 2단계 검증:
1. CodeBook Enum 검증
2. Claude CLI + PDF 파일 검증
"""

import os
import sys
import random
import json
import subprocess
import re
import pandas as pd
import pdfplumber
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent.parent
PAPERS_DIR = PROJECT_ROOT / "Papers"
RESULTS_DIR = PROJECT_ROOT / "coding_work" / "results" / "pdf_analysis"
CODEBOOK_PATH = PROJECT_ROOT / "source" / "CodeBook.csv"
OUTPUT_DIR = PROJECT_ROOT / "coding_work" / "results"

# CSV 파일 경로
CLASSIFICATIONS_CSV = RESULTS_DIR / "pdf_classifications.csv"
REASONING_CSV = RESULTS_DIR / "pdf_reasoning.csv"
REFERENCES_CSV = RESULTS_DIR / "pdf_references.csv"

# 검증할 카테고리
CATEGORIES = [
    "Design Discipline",
    "Data About",
    "Data Modality",
    "AI methods",
    "AI Assistance Types (Lee and Kim, 2025)",
    "Design Phase",
    "Design Practice/Task"
]


class SampleVerifier:
    """표본검사 검증 시스템"""

    def __init__(self, sample_size=5):
        self.sample_size = sample_size
        self.classifications_df = None
        self.reasoning_df = None
        self.references_df = None
        self.codebook_df = None
        self.sample_indices = []
        self.verification_results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def load_data(self):
        """CSV 데이터 로드"""
        print("=== 데이터 로딩 ===")

        try:
            self.classifications_df = pd.read_csv(CLASSIFICATIONS_CSV)
            self.reasoning_df = pd.read_csv(REASONING_CSV)
            self.references_df = pd.read_csv(REFERENCES_CSV)
            # CodeBook의 실제 헤더는 2번째 행 (header=1)
            self.codebook_df = pd.read_csv(CODEBOOK_PATH, header=1)

            print(f"✓ Classifications: {len(self.classifications_df)} papers")
            print(f"✓ Reasoning: {len(self.reasoning_df)} papers")
            print(f"✓ References: {len(self.references_df)} papers")
            print(f"✓ CodeBook: {len(self.codebook_df)} categories")

            return True
        except Exception as e:
            print(f"❌ 데이터 로딩 실패: {e}")
            return False

    def select_sample(self):
        """무작위 표본 선택"""
        print(f"\n=== 무작위 표본 선택 ({self.sample_size}개 논문) ===")

        all_indices = self.classifications_df['Index'].tolist()
        self.sample_indices = random.sample(all_indices, min(self.sample_size, len(all_indices)))

        print(f"✓ 선택된 논문 Index: {self.sample_indices}")

        # 선택된 논문 정보 출력
        for idx in self.sample_indices:
            row = self.classifications_df[self.classifications_df['Index'] == idx].iloc[0]
            title = row.get('Article Title', 'N/A')
            print(f"  - Index {idx}: {title[:60]}...")

        return True

    def verify_codebook_enum(self) -> Dict:
        """1단계: CodeBook Enum 검증"""
        print("\n=== [1단계] CodeBook Enum 검증 ===")

        results = {
            'valid': 0,
            'invalid': 0,
            'details': []
        }

        # CodeBook에서 허용 옵션 추출
        # CodeBook 구조: 각 컬럼이 카테고리, 각 행이 해당 카테고리의 옵션
        allowed_options = {}

        # 각 카테고리 컬럼에서 옵션 추출
        for category in CATEGORIES:
            if category in self.codebook_df.columns:
                # NaN 제외하고 옵션 추출
                options = self.codebook_df[category].dropna().tolist()
                # 빈 문자열 제외
                options = [opt for opt in options if opt and str(opt).strip()]
                allowed_options[category] = options

        # 각 논문의 분류 검증
        for idx in self.sample_indices:
            class_row = self.classifications_df[self.classifications_df['Index'] == idx].iloc[0]

            for category in CATEGORIES:
                classification = str(class_row.get(category, ''))

                if pd.isna(classification) or classification == 'nan':
                    continue

                # Multiple/Multimodal 처리
                if classification.startswith('Multiple') or classification.startswith('Multimodal'):
                    results['valid'] += 1
                    is_valid = True
                    print(f"  ✓ Index {idx}, {category}: \"{classification[:40]}...\" (유효)")
                elif category in allowed_options and classification in allowed_options[category]:
                    results['valid'] += 1
                    is_valid = True
                    print(f"  ✓ Index {idx}, {category}: \"{classification[:40]}...\" (유효)")
                else:
                    results['invalid'] += 1
                    is_valid = False
                    print(f"  ❌ Index {idx}, {category}: 잘못된 옵션 '{classification}'")

                results['details'].append({
                    'Index': idx,
                    'Category': category,
                    'Classification': classification,
                    'Enum_Valid': is_valid
                })

        # 결과 출력
        total = results['valid'] + results['invalid']
        print(f"\n✓ 준수: {results['valid']}/{total} ({results['valid']/total*100:.1f}%)")
        if results['invalid'] > 0:
            print(f"❌ 위반: {results['invalid']}/{total} ({results['invalid']/total*100:.1f}%)")

        return results

    def extract_pdf_full_text(self, pdf_path: Path) -> str:
        """
        PDF에서 전문 텍스트 추출

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            전체 텍스트
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n\n"
                # null byte 제거
                return text.replace('\x00', '')
        except Exception as e:
            print(f"  ⚠ PDF 텍스트 추출 실패: {e}")
            return ""

    def extract_score_from_response(self, response: str) -> Tuple[int, str]:
        """
        Claude 자연어 응답에서 점수와 코멘트 추출

        Returns:
            (score, comment) tuple
        """
        # 점수 패턴 찾기: "5/5", "4점", "점수: 3" 등
        score_patterns = [
            r'(\d)[/점]',  # "5/5" 또는 "5점"
            r'점수[:\s]*(\d)',  # "점수: 5"
            r'평가[:\s]*(\d)',  # "평가: 5"
            r'^(\d)[/점\s]',  # 시작 부분 "5/5" 또는 "5점 "
        ]

        score = 0
        for pattern in score_patterns:
            match = re.search(pattern, response)
            if match:
                score = int(match.group(1))
                break

        # 기본값: 응답에서 1-5 숫자 찾기
        if score == 0:
            numbers = re.findall(r'\b([1-5])\b', response)
            if numbers:
                score = int(numbers[0])

        # 코멘트: 전체 응답 (간단히)
        comment = response.strip()[:200]  # 최대 200자

        return (score, comment)

    def verify_claude_with_pdf(self) -> Dict:
        """2단계: Claude CLI + PDF 파일 검증"""
        print("\n=== [2단계] Claude CLI + PDF 검증 ===")

        results = {
            'high': 0,  # 4-5점
            'medium': 0,  # 3점
            'low': 0,  # 1-2점
            'error': 0,
            'details': []
        }

        total_cells = len(self.sample_indices) * len(CATEGORIES)
        processed = 0

        for idx in self.sample_indices:
            # PDF 파일 찾기
            pdf_files = list(PAPERS_DIR.glob(f"{idx}_*.pdf"))

            if not pdf_files:
                print(f"\n  ⚠ Index {idx}: PDF 파일 없음 - 건너뜀")
                results['error'] += len(CATEGORIES)
                processed += len(CATEGORIES)
                continue

            pdf_path = pdf_files[0]
            print(f"\n  📄 PDF: {pdf_path.name}")

            # PDF 전문 텍스트 추출
            pdf_full_text = self.extract_pdf_full_text(pdf_path)
            if not pdf_full_text:
                print(f"  ⚠ PDF 텍스트 추출 실패 - 건너뜀")
                results['error'] += len(CATEGORIES)
                processed += len(CATEGORIES)
                continue

            class_row = self.classifications_df[self.classifications_df['Index'] == idx].iloc[0]
            reason_row = self.reasoning_df[self.reasoning_df['Index'] == idx].iloc[0]
            ref_row = self.references_df[self.references_df['Index'] == idx].iloc[0]

            for category in CATEGORIES:
                processed += 1
                classification = str(class_row.get(category, ''))
                reasoning = str(reason_row.get(category, ''))
                reference = str(ref_row.get(category, ''))

                # Claude CLI 프롬프트 (PDF 전문 포함)
                prompt = f"""[PDF 논문 전문]
{pdf_full_text[:30000]}

==========

[검증 대상]
Category: {category}
Classification: "{classification}"
Reasoning: "{reasoning}"
Reference Text: "{reference}"

평가 기준:
1. Reference Text가 위 PDF 논문에 실제로 있는가?
2. Classification이 Reference와 일치하는가?
3. Reasoning이 둘을 논리적으로 연결하는가?

1-5점 점수와 한 줄 코멘트로 간단히 답변해주세요.
예: "5/5 - Reference가 PDF Abstract에 정확히 존재함"
"""

                try:
                    # Claude CLI 호출
                    result = subprocess.run(
                        ['claude', '-p', prompt],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if result.returncode != 0:
                        print(f"    ⚠ {category}: Claude CLI 실행 실패")
                        results['error'] += 1
                        continue

                    # 응답에서 점수 추출
                    response_text = result.stdout.strip()
                    score, comment = self.extract_score_from_response(response_text)

                    if score == 0:
                        print(f"    ⚠ {category}: 점수 추출 실패 - 응답: {response_text[:50]}")
                        results['error'] += 1
                        continue

                    # 점수 분류
                    if score >= 4:
                        results['high'] += 1
                        level = 'high'
                        emoji = '✓'
                    elif score == 3:
                        results['medium'] += 1
                        level = 'medium'
                        emoji = '⚠'
                    else:
                        results['low'] += 1
                        level = 'low'
                        emoji = '❌'

                    print(f"    {emoji} {category}: {score}/5 - {comment[:60]}...")

                    results['details'].append({
                        'Index': idx,
                        'Category': category,
                        'Claude_Score': score,
                        'Claude_Level': level,
                        'Claude_Comment': comment
                    })

                    # 5개 셀마다 중간 저장
                    if processed % 5 == 0:
                        self.save_intermediate_results(results)

                except subprocess.TimeoutExpired:
                    print(f"    ⚠ {category}: Claude CLI 타임아웃")
                    results['error'] += 1
                except Exception as e:
                    print(f"    ⚠ {category}: 오류 - {e}")
                    results['error'] += 1

                # 진행률 표시
                print(f"    진행: {processed}/{total_cells} ({processed/total_cells*100:.1f}%)")

        # 결과 출력
        total = results['high'] + results['medium'] + results['low']
        if total > 0:
            print(f"\n✓ 높음 (4-5점): {results['high']}/{total} ({results['high']/total*100:.1f}%)")
            print(f"⚠ 보통 (3점): {results['medium']}/{total} ({results['medium']/total*100:.1f}%)")
            print(f"❌ 낮음 (1-2점): {results['low']}/{total} ({results['low']/total*100:.1f}%)")
        if results['error'] > 0:
            print(f"⚠ 오류: {results['error']}")

        return results

    def save_intermediate_results(self, claude_results):
        """중간 결과 저장"""
        # 간단한 진행 상황 JSON 저장
        progress_file = OUTPUT_DIR / f"verification_progress_{self.timestamp}.json"

        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'processed_count': len(claude_results['details']),
                'results_snapshot': claude_results
            }, f, indent=2, ensure_ascii=False)

    def generate_report(self, enum_results, claude_results):
        """검증 결과 리포트 생성 (JSON + CSV)"""
        print("\n=== 검증 결과 리포트 생성 ===")

        # JSON 리포트
        json_report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'sample_size': self.sample_size,
                'sample_indices': self.sample_indices,
                'total_cells': len(self.sample_indices) * len(CATEGORIES)
            },
            'summary': {
                'enum_valid': enum_results['valid'],
                'enum_invalid': enum_results['invalid'],
                'claude_high': claude_results['high'],
                'claude_medium': claude_results['medium'],
                'claude_low': claude_results['low'],
                'claude_error': claude_results['error']
            },
            'details': []
        }

        # 모든 결과 병합
        for idx in self.sample_indices:
            for category in CATEGORIES:
                row_data = {
                    'Index': idx,
                    'Category': category
                }

                # 분류 값
                class_row = self.classifications_df[self.classifications_df['Index'] == idx].iloc[0]
                row_data['Classification'] = str(class_row.get(category, ''))

                # Enum 검증 결과
                enum_detail = next((d for d in enum_results['details']
                                  if d['Index'] == idx and d['Category'] == category), None)
                if enum_detail:
                    row_data['Enum_Valid'] = enum_detail['Enum_Valid']

                # Claude 검증 결과
                claude_detail = next((d for d in claude_results['details']
                                    if d['Index'] == idx and d['Category'] == category), None)
                if claude_detail:
                    row_data['Claude_Score'] = claude_detail['Claude_Score']
                    row_data['Claude_Level'] = claude_detail['Claude_Level']
                    row_data['Claude_Comment'] = claude_detail['Claude_Comment']

                # Issues 플래그
                issues = []
                if enum_detail and not enum_detail['Enum_Valid']:
                    issues.append('ENUM_INVALID')
                if claude_detail and claude_detail['Claude_Score'] < 3:
                    issues.append('LOW_SCORE')

                row_data['Issues'] = ', '.join(issues) if issues else 'NONE'

                json_report['details'].append(row_data)

        # JSON 저장
        json_path = OUTPUT_DIR / f"sample_verification_{self.timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON 리포트: {json_path}")

        # CSV 저장
        csv_path = OUTPUT_DIR / f"sample_verification_{self.timestamp}.csv"
        df_report = pd.DataFrame(json_report['details'])
        df_report.to_csv(csv_path, index=False)
        print(f"✓ CSV 리포트: {csv_path}")

        # 불일치 사례 출력
        print("\n=== 불일치 사례 (액션 아이템) ===")
        issues_df = df_report[df_report['Issues'] != 'NONE']

        if len(issues_df) == 0:
            print("✓ 불일치 사례 없음!")
        else:
            print(f"⚠ 총 {len(issues_df)}개 이슈 발견:")
            for _, row in issues_df.iterrows():
                print(f"  - Index {row['Index']}, {row['Category']}: {row['Issues']}")

        return json_path, csv_path

    def run(self):
        """전체 검증 프로세스 실행"""
        print("=" * 60)
        print("표본검사 기반 코딩 결과 검증 시스템 (간소화)")
        print("=" * 60)

        # 데이터 로딩
        if not self.load_data():
            return False

        # 표본 선택
        if not self.select_sample():
            return False

        # 2단계 검증
        enum_results = self.verify_codebook_enum()
        claude_results = self.verify_claude_with_pdf()

        # 리포트 생성
        json_path, csv_path = self.generate_report(enum_results, claude_results)

        # 최종 요약
        print("\n" + "=" * 60)
        print("검증 완료!")
        print("=" * 60)
        print(f"✓ JSON 리포트: {json_path}")
        print(f"✓ CSV 리포트: {csv_path}")
        print("=" * 60)

        return True


if __name__ == "__main__":
    verifier = SampleVerifier(sample_size=10)
    success = verifier.run()
    sys.exit(0 if success else 1)
