#!/usr/bin/env python3
"""
단일 PDF 파일 디버깅 스크립트
09078363.pdf 파일의 Claude 응답을 확인
"""

import sys
import json
import subprocess
import re
from pathlib import Path
from pdf_title_fixer import PDFTitleFixer

def main():
    print("🔍 09078363.pdf 디버깅 시작")
    
    # PDFTitleFixer 초기화
    fixer = PDFTitleFixer()
    
    # Google Sheets 연결
    if not fixer.connect_to_sheets():
        print("❌ Google Sheets 연결 실패")
        return
    
    # Mark='J' 논문 제목 가져오기
    paper_titles = fixer.get_marked_paper_titles()
    print(f"📋 {len(paper_titles)}개 논문 제목 로드")
    
    # PDF 파일 경로
    pdf_path = Path("../../Papers/09078363.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF 파일 없음: {pdf_path}")
        return
    
    print(f"📖 PDF 텍스트 추출: {pdf_path.name}")
    
    # PDF 텍스트 추출
    pdf_text = fixer.extract_pdf_text(pdf_path)
    if not pdf_text:
        print("❌ PDF 텍스트 추출 실패")
        return
    
    print(f"✅ 텍스트 길이: {len(pdf_text)} 문자")
    
    # Claude 프롬프트 생성
    prompt = f"""이 PDF의 제목을 아래 리스트에서 찾아주세요.

PDF 텍스트:
{pdf_text[:1500]}

논문 제목 리스트:
{chr(10).join([f"{i+1:2d}. {title}" for i, title in enumerate(paper_titles)])}

위 리스트에서 PDF와 가장 관련 있는 제목을 하나 선택해주세요. 
정확히 일치하지 않아도 가장 유사한 것을 찾아주세요.

JSON으로만 응답:
{{"matched_title": "선택한 제목"}}"""
    
    print("🤖 Claude 호출 중...")
    
    try:
        # Claude CLI 호출
        result = subprocess.run(
            ['claude', '-p', '--output-format', 'json', prompt], 
            capture_output=True, 
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ Claude CLI 실행 실패: {result.stderr}")
            return
        
        response = result.stdout.strip()
        print(f"🤖 Claude 응답 (첫 200자): {response[:200]}...")
        
        print("\n" + "="*60)
        print("🔍 전체 Claude 응답:")
        print("="*60)
        print(response)
        print("="*60 + "\n")
        
        # JSON 메타데이터 파싱
        try:
            response_metadata = json.loads(response)
            
            if 'result' in response_metadata:
                claude_answer = response_metadata['result']
                print(f"📝 Claude 실제 답변:")
                print(claude_answer)
                print()
                
                # JSON 패턴 찾기
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', claude_answer, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                    print(f"✅ 찾은 JSON: {json_str}")
                    
                    try:
                        answer_json = json.loads(json_str)
                        matched_title = answer_json.get('matched_title')
                        print(f"🎯 매칭된 제목: {matched_title}")
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON 파싱 실패: {e}")
                else:
                    print("❌ ```json 패턴을 찾을 수 없음")
                    
                    # 다른 JSON 패턴 시도
                    alt_json_match = re.search(r'\{[^{}]*"matched_title"[^{}]*\}', claude_answer)
                    if alt_json_match:
                        json_str = alt_json_match.group(0)
                        print(f"🔍 대안 JSON 찾음: {json_str}")
                        try:
                            answer_json = json.loads(json_str)
                            matched_title = answer_json.get('matched_title')
                            print(f"🎯 매칭된 제목: {matched_title}")
                        except json.JSONDecodeError as e:
                            print(f"❌ 대안 JSON 파싱 실패: {e}")
                    else:
                        print("❌ 어떤 JSON 패턴도 찾을 수 없음")
            else:
                print("❌ Claude 응답에 'result' 필드가 없음")
                
        except json.JSONDecodeError as e:
            print(f"❌ Claude 메타데이터 JSON 파싱 실패: {e}")
            
    except subprocess.TimeoutExpired:
        print("❌ Claude CLI 타임아웃")
    except Exception as e:
        print(f"❌ 예외 발생: {str(e)}")

if __name__ == "__main__":
    main()