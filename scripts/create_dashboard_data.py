#!/usr/bin/env python3
"""
인터랙티브 대시보드용 데이터 준비 스크립트
기존 토픽 분석 결과를 JSON 형태로 변환하여 HTML 대시보드에서 사용할 수 있게 합니다.
"""

import pandas as pd
import json
from pathlib import Path
from collections import Counter, defaultdict

class DashboardDataPreparer:
    def __init__(self):
        self.base_path = Path("/Users/outcode.jongmokim/Documents/paper_review_with_llm")
        self.input_path = self.base_path / "output" / "topic_modeling_analysis" / "data"
        self.output_path = self.base_path / "output"
        
        # 토픽 라벨 로드
        with open(self.input_path / "topic_labels.json", 'r') as f:
            self.topic_labels = json.load(f)
    
    def load_data(self):
        """모든 필요한 데이터 로드"""
        print("📊 토픽 분석 데이터 로딩 중...")
        
        # 논문 데이터 (토픽 포함)
        self.papers_df = pd.read_csv(self.input_path / "papers_with_topics.csv")
        print(f"✅ {len(self.papers_df)}개 논문 데이터 로드 완료")
        
        # 토픽 정보
        self.topic_info_df = pd.read_csv(self.input_path / "topic_info.csv")
        print(f"✅ {len(self.topic_info_df)}개 토픽 정보 로드 완료")
        
        return True
    
    def prepare_topic_overview(self):
        """토픽 개요 데이터 준비 (파이 차트용)"""
        print("🎯 토픽 개요 데이터 준비 중...")
        
        # 토픽별 논문 수 계산 (Outlier 제외)
        topic_counts = self.papers_df[self.papers_df['Topic'] != -1]['Topic'].value_counts().sort_index()
        
        overview_data = []
        for topic_id, count in topic_counts.items():
            topic_label = self.topic_labels.get(str(topic_id), f"Topic {topic_id}")
            # 토픽 정보에서 키워드 가져오기
            topic_info = self.topic_info_df[self.topic_info_df['Topic'] == topic_id]
            keywords = []
            if not topic_info.empty:
                representation = eval(topic_info.iloc[0]['Representation'])
                keywords = representation[:5]  # 상위 5개 키워드
            
            overview_data.append({
                'topic_id': int(topic_id),
                'topic_label': topic_label,
                'count': int(count),
                'keywords': keywords,
                'percentage': round((count / len(self.papers_df[self.papers_df['Topic'] != -1])) * 100, 1)
            })
        
        print(f"✅ {len(overview_data)}개 토픽 개요 데이터 생성")
        return overview_data
    
    def normalize_data_modality(self, modality):
        """
        Data Modality 값 정규화 - 멀티모달을 구성 요소로 분해
        멀티모달 조합은 각 구성 요소에 카운트를 분산
        """
        if pd.isna(modality):
            return []
            
        modality = str(modality).strip()
        modality_lower = modality.lower()
        
        # 결과를 리스트로 반환 (멀티모달의 경우 여러 요소)
        results = []
        
        # Multimodal 분해 처리
        if 'multimodal' in modality_lower:
            # Text + Audio 조합
            if 'text' in modality_lower and 'audio' in modality_lower:
                results.extend(['Text', 'Audio'])
            # Text + Image 조합  
            elif 'text' in modality_lower and 'image' in modality_lower:
                results.extend(['Text', 'Image'])
            # Audio + Image 조합
            elif 'audio' in modality_lower and 'image' in modality_lower:
                results.extend(['Audio', 'Image'])
            # Speech + Visual (Speech=Audio, Visual=Image)
            elif 'speech' in modality_lower or 'gesture' in modality_lower:
                results.extend(['Audio', 'Image'])
            # Time Series + Others
            elif 'time series' in modality_lower:
                results.append('Time Series')
            # 일반적인 Multimodal (구체적 조합 불명)
            else:
                results.append('Multimodal')
                
        # Time series 계열 (Time series and Text는 각각 분해)
        elif modality_lower in ['time series']:
            results.append('Time Series')
        elif 'time series and text' in modality_lower:
            results.extend(['Time Series', 'Text'])
            
        # Text 계열
        elif modality_lower in ['text', 'text?', 'text? (parameter estimates)']:
            results.append('Text')
        
        # Image 계열
        elif modality_lower in ['image']:
            results.append('Image')
            
        # Audio 계열
        elif modality_lower in ['audio']:
            results.append('Audio')
            
        # Behavioral → Time Series로 통합
        elif 'behavioral' in modality_lower:
            results.append('Time Series')
            
        # Generated 제거 (빈 리스트 반환)
        elif 'generated' in modality_lower:
            results = []  # Generated는 제거
            
        # 복합 타입 (text, graph, multimodal 등)
        elif ',' in modality_lower and 'multimodal' in modality_lower:
            results.append('Multimodal')
            
        # 그 외는 첫 글자 대문자로 정규화
        else:
            normalized = modality.title()
            if normalized not in ['Generated']:  # Generated 제외
                results.append(normalized)
        
        return results
    
    def normalize_design_practice(self, practice):
        """Design Practice 값 정규화 - Other 제거 및 적절한 카테고리로 재분류"""
        if pd.isna(practice):
            return None
            
        practice = str(practice).strip()
        practice_lower = practice.lower()
        
        # 오타 수정
        if practice_lower in ['dfine']:
            return 'Define'
        
        # Conversational interface design -> Define (요구사항 정의 단계)
        elif 'conversational interface design' in practice_lower or 'interface design' in practice_lower:
            return 'Define'
            
        # Emotion design -> Define (감정적 요구사항 정의)
        elif 'emotion design' in practice_lower:
            return 'Define'
            
        # Service design -> Define (서비스 요구사항 정의)
        elif 'service design' in practice_lower:
            return 'Define'
            
        # HCI interface -> Define (사용자 인터페이스 요구사항)
        elif 'hci' in practice_lower and 'interface' in practice_lower:
            return 'Define'
            
        # 기존 정규화된 값들 그대로 유지
        elif practice in ['Develop', 'Define', 'Discovery', 'Delivery']:
            return practice
            
        # 그 외 명확하지 않은 것들은 Develop로 (대부분의 구현/개발 관련)
        else:
            return 'Develop'

    def prepare_yearly_trends(self):
        """연도별 다차원 트렌드 데이터 준비 (토픽, AI Methods, Data Modality, Design Practice)"""
        print("📈 연도별 다차원 트렌드 데이터 준비 중...")
        
        # Outlier 제외하고 유효한 논문만 사용
        valid_papers = self.papers_df[self.papers_df['Topic'] != -1].copy()
        
        # Data Modality 정규화 적용
        valid_papers['Data_Modality_Normalized'] = valid_papers['Data Modality'].apply(self.normalize_data_modality)
        
        # Design Practice 정규화 적용 (Others 제거)
        valid_papers['Design_Practice_Normalized'] = valid_papers['Design Practice/Task'].apply(self.normalize_design_practice)
        
        years = sorted(valid_papers['Publication Year'].unique())
        
        yearly_trends = {
            'topics': [],
            'ai_methods': [],
            'data_modality': [],
            'design_practice': []
        }
        
        # 1. 토픽 트렌드 (기존)
        for year in years:
            year_papers = valid_papers[valid_papers['Publication Year'] == year]
            topic_counts = year_papers['Topic'].value_counts().sort_index()
            
            year_data = {
                'year': int(year),
                'categories': {}
            }
            
            for topic_id, count in topic_counts.items():
                topic_label = self.topic_labels.get(str(topic_id), f"Topic {topic_id}")
                year_data['categories'][topic_label] = int(count)
            
            yearly_trends['topics'].append(year_data)
        
        # 2. AI Methods 트렌드
        for year in years:
            year_papers = valid_papers[valid_papers['Publication Year'] == year]
            ai_method_counts = year_papers['AI_Method_Normalized'].value_counts()
            
            year_data = {
                'year': int(year),
                'categories': {}
            }
            
            for method, count in ai_method_counts.items():
                if pd.notna(method):  # NaN 값 제외
                    year_data['categories'][method] = int(count)
            
            yearly_trends['ai_methods'].append(year_data)
        
        # 3. Data Modality 트렌드 (정규화된 데이터 사용 - 멀티모달 분해 적용)
        for year in years:
            year_papers = valid_papers[valid_papers['Publication Year'] == year]
            
            # 멀티모달 분해를 적용하여 카운트
            modality_counts = {}
            
            for _, paper in year_papers.iterrows():
                normalized_modalities = self.normalize_data_modality(paper['Data Modality'])
                
                # 각 정규화된 modality에 대해 카운트 증가
                for modality in normalized_modalities:
                    if modality:  # 빈 문자열이 아닌 경우만
                        modality_counts[modality] = modality_counts.get(modality, 0) + 1
            
            year_data = {
                'year': int(year),
                'categories': modality_counts
            }
            
            yearly_trends['data_modality'].append(year_data)
        
        # 4. Design Practice 트렌드 (정규화된 데이터 사용)
        for year in years:
            year_papers = valid_papers[valid_papers['Publication Year'] == year]
            practice_counts = year_papers['Design_Practice_Normalized'].value_counts()
            
            year_data = {
                'year': int(year),
                'categories': {}
            }
            
            for practice, count in practice_counts.items():
                if pd.notna(practice):  # NaN 값 제외
                    year_data['categories'][practice] = int(count)
            
            yearly_trends['design_practice'].append(year_data)
        
        print(f"✅ {len(years)}년간의 4차원 트렌드 데이터 생성")
        print(f"   - 토픽 트렌드: {len(yearly_trends['topics'])}개 연도")
        print(f"   - AI Methods 트렌드: {len(yearly_trends['ai_methods'])}개 연도")  
        print(f"   - Data Modality 트렌드: {len(yearly_trends['data_modality'])}개 연도")
        print(f"   - Design Practice 트렌드: {len(yearly_trends['design_practice'])}개 연도")
        
        return yearly_trends
    
    def prepare_ai_methods_matrix(self):
        """토픽 × AI Methods 관계 매트릭스 준비"""
        print("🤖 AI Methods 매트릭스 데이터 준비 중...")
        
        valid_papers = self.papers_df[self.papers_df['Topic'] != -1].copy()
        
        # AI Methods별 토픽 분포
        matrix_data = []
        ai_methods = valid_papers['AI_Method_Normalized'].unique()
        
        for ai_method in ai_methods:
            if pd.isna(ai_method):
                continue
                
            method_papers = valid_papers[valid_papers['AI_Method_Normalized'] == ai_method]
            topic_dist = method_papers['Topic'].value_counts().sort_index()
            
            method_data = {
                'ai_method': ai_method,
                'topics': {}
            }
            
            for topic_id, count in topic_dist.items():
                topic_label = self.topic_labels.get(str(topic_id), f"Topic {topic_id}")
                method_data['topics'][topic_label] = int(count)
            
            matrix_data.append(method_data)
        
        print(f"✅ {len(matrix_data)}개 AI Methods 매트릭스 데이터 생성")
        return matrix_data
    
    def prepare_design_tasks_matrix(self):
        """토픽 × Design Tasks 관계 매트릭스 준비 (정규화된 Design Practice 사용)"""
        print("🎨 Design Tasks 매트릭스 데이터 준비 중...")
        
        valid_papers = self.papers_df[self.papers_df['Topic'] != -1].copy()
        
        # Design Practice 정규화 적용
        valid_papers['Design_Practice_Normalized'] = valid_papers['Design Practice/Task'].apply(self.normalize_design_practice)
        
        # Design Tasks별 토픽 분포
        matrix_data = []
        design_tasks = valid_papers['Design_Practice_Normalized'].unique()
        
        for design_task in design_tasks:
            if pd.isna(design_task):
                continue
                
            task_papers = valid_papers[valid_papers['Design_Practice_Normalized'] == design_task]
            topic_dist = task_papers['Topic'].value_counts().sort_index()
            
            task_data = {
                'design_task': design_task,
                'topics': {}
            }
            
            for topic_id, count in topic_dist.items():
                topic_label = self.topic_labels.get(str(topic_id), f"Topic {topic_id}")
                task_data['topics'][topic_label] = int(count)
            
            matrix_data.append(task_data)
        
        print(f"✅ {len(matrix_data)}개 Design Tasks 매트릭스 데이터 생성")
        return matrix_data
    
    def prepare_ai_methods_design_practices_matrix(self):
        """AI Methods × Design Practices 관계 매트릭스 준비 (정규화된 Design Practice 사용)"""
        print("🔗 AI Methods × Design Practices 매트릭스 데이터 준비 중...")
        
        valid_papers = self.papers_df[self.papers_df['Topic'] != -1].copy()
        
        # Design Practice 정규화 적용
        valid_papers['Design_Practice_Normalized'] = valid_papers['Design Practice/Task'].apply(self.normalize_design_practice)
        
        # AI Methods별 Design Practices 분포
        matrix_data = []
        ai_methods = valid_papers['AI_Method_Normalized'].unique()
        
        for ai_method in ai_methods:
            if pd.isna(ai_method):
                continue
                
            method_papers = valid_papers[valid_papers['AI_Method_Normalized'] == ai_method]
            practice_dist = method_papers['Design_Practice_Normalized'].value_counts()
            
            method_data = {
                'ai_method': ai_method,
                'design_practices': {}
            }
            
            for practice, count in practice_dist.items():
                if pd.notna(practice):  # NaN 값 제외
                    method_data['design_practices'][practice] = int(count)
            
            matrix_data.append(method_data)
        
        print(f"✅ {len(matrix_data)}개 AI Methods × Design Practices 매트릭스 데이터 생성")
        return matrix_data
    
    def prepare_data_modality_design_practices_matrix(self):
        """Data Modality × Design Practices 관계 매트릭스 준비 (정규화된 값들 사용)"""
        print("📊 Data Modality × Design Practices 매트릭스 데이터 준비 중...")
        
        valid_papers = self.papers_df[self.papers_df['Topic'] != -1].copy()
        
        # Design Practice 정규화 적용
        valid_papers['Design_Practice_Normalized'] = valid_papers['Design Practice/Task'].apply(self.normalize_design_practice)
        # Data Modality 정규화 적용
        valid_papers['Data_Modality_Normalized'] = valid_papers['Data Modality'].apply(self.normalize_data_modality)
        
        # Data Modality별 Design Practices 분포 (멀티모달 분해 적용)
        matrix_data = []
        
        # 모든 정규화된 Data Modality 수집
        all_modalities = set()
        for modalities_list in valid_papers['Data_Modality_Normalized']:
            if modalities_list:
                all_modalities.update(modalities_list)
        
        for modality in sorted(all_modalities):
            if not modality:  # 빈 문자열 제외
                continue
                
            # 해당 modality를 포함하는 논문들 찾기
            modality_papers = []
            for _, paper in valid_papers.iterrows():
                if modality in paper['Data_Modality_Normalized']:
                    modality_papers.append(paper)
            
            if not modality_papers:
                continue
                
            # DataFrame으로 변환하여 처리
            modality_df = pd.DataFrame(modality_papers)
            practice_dist = modality_df['Design_Practice_Normalized'].value_counts()
            
            modality_data = {
                'data_modality': modality,
                'design_practices': {}
            }
            
            for practice, count in practice_dist.items():
                if pd.notna(practice):  # NaN 값 제외
                    modality_data['design_practices'][practice] = int(count)
            
            matrix_data.append(modality_data)
        
        print(f"✅ {len(matrix_data)}개 Data Modality × Design Practices 매트릭스 데이터 생성")
        return matrix_data
    
    def prepare_paper_details(self):
        """논문 상세 정보 준비"""
        print("📄 논문 상세 정보 준비 중...")
        
        valid_papers = self.papers_df[self.papers_df['Topic'] != -1].copy()
        
        paper_details = []
        for _, paper in valid_papers.iterrows():
            topic_label = self.topic_labels.get(str(paper['Topic']), f"Topic {paper['Topic']}")
            
            detail = {
                'topic_id': int(paper['Topic']),
                'topic_label': topic_label,
                'title': paper['Article Title'],
                'authors': paper['Author Full Names'],
                'year': int(paper['Publication Year']),
                'journal': paper['Source Title'],
                'doi': paper['DOI Link'],
                'abstract': paper['Abstract'][:500] + "..." if len(str(paper['Abstract'])) > 500 else paper['Abstract'],
                'ai_method': paper['AI_Method_Normalized'],
                'design_task': paper['Design_Task_Normalized']
            }
            paper_details.append(detail)
        
        print(f"✅ {len(paper_details)}개 논문 상세 정보 생성")
        return paper_details
    
    def create_dashboard_json(self):
        """모든 데이터를 종합하여 대시보드용 JSON 생성"""
        print("🏗️  대시보드 데이터 통합 중...")
        
        dashboard_data = {
            'metadata': {
                'total_papers': len(self.papers_df[self.papers_df['Topic'] != -1]),
                'total_topics': len([k for k in self.topic_labels.keys() if k != '-1']),
                'year_range': [
                    int(self.papers_df['Publication Year'].min()),
                    int(self.papers_df['Publication Year'].max())
                ],
                'generated_at': pd.Timestamp.now().isoformat()
            },
            'topic_overview': self.prepare_topic_overview(),
            'yearly_trends': self.prepare_yearly_trends(),
            'ai_methods_matrix': self.prepare_ai_methods_matrix(),
            'design_tasks_matrix': self.prepare_design_tasks_matrix(),
            'ai_methods_design_practices_matrix': self.prepare_ai_methods_design_practices_matrix(),
            'data_modality_design_practices_matrix': self.prepare_data_modality_design_practices_matrix(),
            'paper_details': self.prepare_paper_details(),
            'topic_labels': self.topic_labels
        }
        
        return dashboard_data
    
    def save_dashboard_data(self, data):
        """대시보드 데이터를 JSON 파일로 저장"""
        output_file = self.output_path / "dashboard_data.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 대시보드 데이터 저장: {output_file}")
        print(f"📦 파일 크기: {output_file.stat().st_size / 1024:.1f} KB")
        
        return output_file

def main():
    """메인 실행 함수"""
    print("🚀 인터랙티브 대시보드 데이터 준비 시작")
    print("=" * 50)
    
    try:
        # 데이터 준비 클래스 초기화
        preparer = DashboardDataPreparer()
        
        # 데이터 로드
        preparer.load_data()
        
        # 대시보드용 JSON 데이터 생성
        dashboard_data = preparer.create_dashboard_json()
        
        # JSON 파일로 저장
        output_file = preparer.save_dashboard_data(dashboard_data)
        
        print("\n" + "=" * 50)
        print("✅ 대시보드 데이터 준비 완료!")
        print(f"📊 총 {dashboard_data['metadata']['total_papers']}개 논문")
        print(f"🎯 총 {dashboard_data['metadata']['total_topics']}개 토픽")
        print(f"📅 기간: {dashboard_data['metadata']['year_range'][0]}-{dashboard_data['metadata']['year_range'][1]}")
        print(f"💾 출력: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    main()