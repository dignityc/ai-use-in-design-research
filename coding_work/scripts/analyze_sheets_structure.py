"""
Google Sheets 구조 분석 스크립트
CodeBook과 CodedPapers 시트의 구조를 분석하여 PDF 분류 기준과 출력 형식을 파악
"""

import os
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

# 상위 경로 추가 (google_sheets_connector 임포트용)
sys.path.append(str(Path(__file__).parent))
from google_sheets_connector import GoogleSheetsConnector


class SheetsStructureAnalyzer:
    """Google Sheets 구조 분석 클래스"""
    
    def __init__(self):
        """분석기 초기화"""
        self.connector = GoogleSheetsConnector()
        
    def connect_and_analyze(self) -> Dict[str, Any]:
        """
        Google Sheets에 연결하여 CodeBook과 CodedPapers 시트 구조 분석
        
        Returns:
            Dict: 분석 결과
        """
        print("🔗 Google Sheets 연결 중...")
        
        if not self.connector.connect():
            return {"error": "Google Sheets 연결 실패"}
        
        print("✅ Google Sheets 연결 성공")
        
        results = {
            "codebook_structure": None,
            "coded_papers_structure": None,
            "classification_criteria": {},
            "csv_headers": []
        }
        
        # 1. CodeBook 시트 분석
        print("\n📋 CodeBook 시트 분석 중...")
        try:
            codebook_data = self.analyze_codebook_sheet()
            results["codebook_structure"] = codebook_data
            print(f"✅ CodeBook 분석 완료: {len(codebook_data)} 분류 기준 발견")
        except Exception as e:
            print(f"❌ CodeBook 분석 실패: {str(e)}")
            results["codebook_error"] = str(e)
        
        # 2. CodedPapers 시트 분석 
        print("\n📄 CodedPapers 시트 분석 중...")
        try:
            coded_papers_data = self.analyze_coded_papers_sheet()
            results["coded_papers_structure"] = coded_papers_data
            print(f"✅ CodedPapers 분석 완료: {len(coded_papers_data['headers'])} 컬럼 발견")
        except Exception as e:
            print(f"❌ CodedPapers 분석 실패: {str(e)}")
            results["coded_papers_error"] = str(e)
        
        return results
    
    def analyze_codebook_sheet(self) -> Dict[str, Any]:
        """CodeBook 시트 구조 분석"""
        try:
            # CodeBook 시트 데이터 가져오기
            sheet = self.connector.get_sheet("CodeBook")
            all_values = sheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                raise ValueError("CodeBook 시트가 비어있거나 데이터가 부족합니다")
            
            # DataFrame 생성
            headers = all_values[0]
            data = all_values[1:]
            df = pd.DataFrame(data, columns=headers)
            
            print(f"📋 CodeBook 시트 구조:")
            print(f"   행 수: {len(df)}")
            print(f"   열 수: {len(df.columns)}")
            print(f"   컬럼들: {list(df.columns)}")
            
            # 분류 기준 추출
            classification_criteria = {}
            
            # 주요 분류를 찾기 (사용자가 언급한 6개 분류)
            target_classifications = [
                "디자인 디서플린", "design discipline", 
                "데이터 어바웃", "data about",
                "데이터 모달리티", "data modality", 
                "ai methods", "ai method",
                "ai assistance type", "ai assistance",
                "design phase", "design phases"
            ]
            
            # 각 행을 분석하여 분류 기준 찾기
            for idx, row in df.iterrows():
                row_text = " ".join(str(cell).lower() for cell in row if str(cell).strip())
                
                for target in target_classifications:
                    if target in row_text:
                        classification_criteria[target] = {
                            "row_index": idx,
                            "data": row.to_dict(),
                            "full_text": row_text[:200] + "..." if len(row_text) > 200 else row_text
                        }
                        break
            
            print(f"\n🎯 발견된 분류 기준: {len(classification_criteria)}개")
            for key in classification_criteria.keys():
                print(f"   - {key}")
            
            return {
                "dataframe": df,
                "headers": list(df.columns),
                "total_rows": len(df),
                "classification_criteria": classification_criteria,
                "raw_data": all_values
            }
            
        except Exception as e:
            print(f"❌ CodeBook 시트 분석 중 오류: {str(e)}")
            raise
    
    def analyze_coded_papers_sheet(self) -> Dict[str, Any]:
        """CodedPapers 시트 구조 분석"""
        try:
            # CodedPapers 시트 데이터 가져오기  
            sheet = self.connector.get_sheet("CodedPapers")
            all_values = sheet.get_all_values()
            
            if not all_values:
                raise ValueError("CodedPapers 시트가 비어있습니다")
            
            headers = all_values[0] if all_values else []
            data = all_values[1:] if len(all_values) > 1 else []
            
            print(f"📄 CodedPapers 시트 구조:")
            print(f"   헤더: {len(headers)}개")
            print(f"   데이터 행: {len(data)}개")
            
            print(f"\n📝 CSV 출력용 헤더 목록:")
            for i, header in enumerate(headers, 1):
                print(f"   {i:2d}. {header}")
            
            # 분류 관련 컬럼 찾기
            classification_columns = []
            for header in headers:
                header_lower = header.lower()
                if any(keyword in header_lower for keyword in 
                      ['design', 'data', 'ai', 'method', 'phase', 'practice', 'task', 'discipline']):
                    classification_columns.append(header)
            
            print(f"\n🎯 분류 관련 컬럼 ({len(classification_columns)}개):")
            for col in classification_columns:
                print(f"   - {col}")
            
            return {
                "headers": headers,
                "data_rows": len(data),
                "classification_columns": classification_columns,
                "sample_data": data[:3] if data else [],  # 처음 3행 샘플
                "raw_data": all_values
            }
            
        except Exception as e:
            print(f"❌ CodedPapers 시트 분석 중 오류: {str(e)}")
            raise
    
    def save_analysis_report(self, results: Dict[str, Any], output_path: str = None) -> str:
        """분석 결과를 파일로 저장"""
        if output_path is None:
            output_path = str(Path(__file__).parent.parent / "results" / "sheets_structure_analysis.json")
        
        # 결과 디렉토리 생성
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # DataFrame을 JSON 저장 가능한 형태로 변환
        import json
        
        json_results = {}
        for key, value in results.items():
            if key.endswith("_structure") and value and "dataframe" in value:
                # DataFrame을 딕셔너리로 변환
                json_results[key] = {
                    k: v for k, v in value.items() 
                    if k != "dataframe"  # DataFrame 제외
                }
                # DataFrame 정보를 별도 저장
                json_results[key]["dataframe_info"] = {
                    "shape": value["dataframe"].shape,
                    "columns": list(value["dataframe"].columns),
                    "sample_data": value["dataframe"].head(3).to_dict()
                }
            else:
                json_results[key] = value
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 분석 결과 저장: {output_path}")
        return output_path


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🔍 Google Sheets 구조 분석 시작")
    print("=" * 60)
    
    analyzer = SheetsStructureAnalyzer()
    
    # 구조 분석 실행
    results = analyzer.connect_and_analyze()
    
    if "error" in results:
        print(f"\n❌ 분석 실패: {results['error']}")
        return False
    
    # 결과 요약 출력
    print("\n" + "=" * 60)
    print("📊 분석 결과 요약")
    print("=" * 60)
    
    if results.get("codebook_structure"):
        cb_data = results["codebook_structure"]
        print(f"📋 CodeBook: {cb_data['total_rows']}행, {len(cb_data['headers'])}열")
        print(f"   분류 기준: {len(cb_data['classification_criteria'])}개 발견")
    
    if results.get("coded_papers_structure"):
        cp_data = results["coded_papers_structure"]
        print(f"📄 CodedPapers: {cp_data['data_rows']}행, {len(cp_data['headers'])}열")
        print(f"   분류 컬럼: {len(cp_data['classification_columns'])}개")
    
    # 분석 결과 저장
    output_file = analyzer.save_analysis_report(results)
    
    print(f"\n✅ 구조 분석 완료!")
    print(f"📁 결과 파일: {output_file}")
    
    return True


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n📋 문제해결 체크리스트:")
        print("1. Google Sheets API 인증 파일 확인")
        print("2. 스프레드시트 ID 및 시트명 확인")
        print("3. 네트워크 연결 상태 확인")