"""
Paper Tracking Script
Google Sheets에서 논문 진행 상황을 추적하는 스크립트
- 2단계 필터링: Inclusion='Y' → Mark='M'
- 각 단계별 통계 및 진행 상황 리포트 생성
"""

import os
import sys
from pathlib import Path
import pandas as pd
from typing import Optional, Tuple

# 현재 스크립트의 상위 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from coding_work.scripts.google_sheets_connector import GoogleSheetsConnector


class PaperTracker:
    """논문 추적 및 필터링 클래스"""
    
    def __init__(self):
        """
        Paper Tracker 초기화
        
        기본 설정된 Google Sheets 연결 사용
        """
        self.connector = GoogleSheetsConnector()
        self.sheet_name = "3rd Screening"
        
    def connect(self) -> bool:
        """Google Sheets API 연결"""
        return self.connector.connect()
    
    def get_all_papers(self) -> pd.DataFrame:
        """모든 논문 데이터 가져오기"""
        try:
            sheet = self.connector.get_sheet(self.sheet_name)
            all_values = sheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                print("❌ 시트에 데이터가 없습니다.")
                return pd.DataFrame()
            
            # DataFrame 생성 (첫 번째 행을 헤더로 사용)
            headers = all_values[0]
            data = all_values[1:]
            df = pd.DataFrame(data, columns=headers)
            
            return df
            
        except Exception as e:
            print(f"❌ 데이터 가져오기 실패: {str(e)}")
            return pd.DataFrame()
    
    def get_inclusion_y_papers(self) -> Tuple[pd.DataFrame, dict]:
        """
        1단계 필터링: Inclusion='Y'인 논문들 추출
        
        Returns:
            tuple: (필터링된 DataFrame, 통계 정보)
        """
        print("🔍 1단계 필터링: Inclusion='Y' 논문 추출 중...")
        
        # 전체 데이터 로드
        all_papers = self.get_all_papers()
        
        if all_papers.empty:
            return pd.DataFrame(), {}
        
        total_count = len(all_papers)
        print(f"📊 전체 논문 수: {total_count}개")
        
        # Inclusion 컬럼 확인
        inclusion_col = None
        possible_names = [
            'Inclusion', 'inclusion', 'INCLUSION',
            'Inclusion (Y/N/Q)', 'Inclusion (Y/N/Q/R)',
            'Inclusion (Y/N/Q/R) for 2nd screening'
        ]
        
        # 정확한 매치 시도
        for col_name in possible_names:
            if col_name in all_papers.columns:
                inclusion_col = col_name
                break
        
        # 부분 매치 시도 (정확한 매치가 없는 경우)
        if inclusion_col is None:
            for col_name in all_papers.columns:
                if 'inclusion' in col_name.lower():
                    inclusion_col = col_name
                    break
        
        if inclusion_col is None:
            available_cols = list(all_papers.columns)
            print(f"❌ Inclusion 컬럼을 찾을 수 없습니다.")
            print(f"📋 사용 가능한 컬럼: {available_cols[:10]}...")
            return pd.DataFrame(), {}
        
        # Inclusion='Y' 필터링
        inclusion_y_papers = all_papers[
            all_papers[inclusion_col].str.upper().isin(['Y', 'YES'])
        ].copy()
        
        inclusion_y_count = len(inclusion_y_papers)
        inclusion_y_ratio = (inclusion_y_count / total_count * 100) if total_count > 0 else 0
        
        stats = {
            'total_count': total_count,
            'inclusion_y_count': inclusion_y_count,
            'inclusion_y_ratio': inclusion_y_ratio,
            'inclusion_col_name': inclusion_col
        }
        
        print(f"✅ Inclusion='Y' 논문: {inclusion_y_count}개 ({inclusion_y_ratio:.1f}%)")
        
        return inclusion_y_papers, stats
    
    def get_marked_papers(self, inclusion_y_papers: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        2단계 필터링: Mark='M'인 논문들 추출
        
        Args:
            inclusion_y_papers: 1단계 필터링된 DataFrame
            
        Returns:
            tuple: (최종 필터링된 DataFrame, 통계 정보)
        """
        print("🔍 2단계 필터링: Mark='J' 논문 추출 중...")
        
        if inclusion_y_papers.empty:
            return pd.DataFrame(), {}
        
        inclusion_y_count = len(inclusion_y_papers)
        
        # Mark 컬럼 확인
        mark_col = None
        possible_names = ['Mark', 'mark', 'MARK', 'Marked', 'marked']
        
        for col_name in possible_names:
            if col_name in inclusion_y_papers.columns:
                mark_col = col_name
                break
        
        if mark_col is None:
            available_cols = list(inclusion_y_papers.columns)
            print(f"❌ Mark 컬럼을 찾을 수 없습니다.")
            print(f"📋 사용 가능한 컬럼: {available_cols[:10]}...")
            return pd.DataFrame(), {}
        
        # Mark='J' 필터링
        marked_papers = inclusion_y_papers[
            inclusion_y_papers[mark_col].str.upper() == 'J'
        ].copy()
        
        marked_count = len(marked_papers)
        marked_ratio_total = (marked_count / inclusion_y_count * 100) if inclusion_y_count > 0 else 0
        
        stats = {
            'inclusion_y_count': inclusion_y_count,
            'marked_count': marked_count,
            'marked_ratio_in_inclusion': marked_ratio_total,
            'mark_col_name': mark_col
        }
        
        print(f"✅ Mark='J' 논문: {marked_count}개 (Inclusion='Y' 중 {marked_ratio_total:.1f}%)")
        
        return marked_papers, stats
    
    def show_sample_data(self, df: pd.DataFrame, title: str, max_samples: int = 3):
        """샘플 데이터 미리보기"""
        if df.empty:
            print(f"📋 {title}: 데이터 없음")
            return
        
        print(f"\n📋 {title} 샘플 ({min(len(df), max_samples)}개):")
        
        # 주요 컬럼들만 선택해서 보여주기
        display_cols = []
        important_cols = ['Article Title', 'Title', 'Author Full Names', 'Authors', 
                         'Publication Year', 'Year', 'Inclusion', 'Mark']
        
        for col in important_cols:
            if col in df.columns:
                display_cols.append(col)
        
        if not display_cols:
            # 첫 3개 컬럼만 표시
            display_cols = list(df.columns)[:3]
        
        sample_df = df[display_cols].head(max_samples)
        
        for idx, row in sample_df.iterrows():
            print(f"  {idx+1}. {row.iloc[0][:60]}..." if len(str(row.iloc[0])) > 60 else f"  {idx+1}. {row.iloc[0]}")
    
    def track_paper_status(self) -> dict:
        """
        전체 논문 추적 및 상태 리포트 생성
        
        Returns:
            dict: 종합 통계 정보
        """
        print("=" * 50)
        print("📊 Paper Tracking Report")
        print("=" * 50)
        
        # 1단계: Inclusion='Y' 필터링
        inclusion_y_papers, stage1_stats = self.get_inclusion_y_papers()
        
        if not stage1_stats:
            print("❌ 1단계 필터링 실패")
            return {}
        
        # 2단계: Mark='M' 필터링
        marked_papers, stage2_stats = self.get_marked_papers(inclusion_y_papers)
        
        if not stage2_stats:
            print("❌ 2단계 필터링 실패")
            return {}
        
        # 종합 통계 계산
        total_count = stage1_stats['total_count']
        inclusion_y_count = stage1_stats['inclusion_y_count']
        marked_count = stage2_stats['marked_count']
        
        marked_ratio_total = (marked_count / total_count * 100) if total_count > 0 else 0
        
        comprehensive_stats = {
            'total_papers': total_count,
            'inclusion_y_papers': inclusion_y_count,
            'marked_papers': marked_count,
            'inclusion_y_ratio': stage1_stats['inclusion_y_ratio'],
            'marked_ratio_in_inclusion': stage2_stats['marked_ratio_in_inclusion'],
            'marked_ratio_total': marked_ratio_total
        }
        
        # 최종 리포트 출력
        print(f"\n🎯 최종 결과:")
        print(f"   전체 논문: {total_count:,}개")
        print(f"   Inclusion='Y': {inclusion_y_count:,}개 ({stage1_stats['inclusion_y_ratio']:.1f}%)")
        print(f"   Mark='J': {marked_count:,}개 (전체 대비 {marked_ratio_total:.1f}%, Inclusion='Y' 중 {stage2_stats['marked_ratio_in_inclusion']:.1f}%)")
        
        # 샘플 데이터 출력
        self.show_sample_data(inclusion_y_papers, "Inclusion='Y' 논문들")
        self.show_sample_data(marked_papers, "Mark='J' 최종 논문들")
        
        print("=" * 50)
        print("✅ Paper Tracking 완료!")
        print("=" * 50)
        
        return comprehensive_stats


def main():
    """메인 실행 함수"""
    print("🚀 Paper Tracking Script 시작\n")
    
    # Paper Tracker 생성 및 연결 (기본 설정 사용)
    tracker = PaperTracker()
    
    if not tracker.connect():
        print("❌ Google Sheets 연결 실패")
        return False
    
    print("✅ Google Sheets 연결 성공")
    
    # 논문 추적 실행
    try:
        stats = tracker.track_paper_status()
        
        if stats:
            print(f"\n📊 요약:")
            print(f"   최종 Mark='J' 논문: {stats['marked_papers']}개")
            print(f"   전체 대비 비율: {stats['marked_ratio_total']:.1f}%")
            return True
        else:
            print("❌ 논문 추적 실패")
            return False
            
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n📋 문제 해결 체크리스트:")
        print("1. Google Sheets API 연결 확인")
        print("2. '2nd Screening (rescreening needed)' 시트 존재 확인")
        print("3. 'Inclusion' 및 'Mark' 컬럼 존재 확인")
        print("4. 서비스 계정 권한 확인")