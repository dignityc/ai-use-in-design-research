#!/usr/bin/env python3
"""
네트워크 인사이트 분석 시스템
- 브릿지 키워드 식별 (서로 다른 클러스터 연결)
- 시간축 트렌드 키워드 분석
- 연구 갭 및 기회 식별
- 키워드 진화 패턴 분석
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats
    plt.style.use('default')
    sns.set_palette("husl")
except ImportError as e:
    print(f"⚠️  라이브러리 누락: {e}")
    print("필요한 라이브러리: networkx matplotlib seaborn scipy")
    exit(1)

class NetworkInsightsAnalyzer:
    """네트워크 인사이트 분석기"""
    
    def __init__(self):
        self.network = None
        self.nodes_df = None
        self.edges_df = None
        self.keywords_df = None
        
    def load_data(self, data_dir: str) -> bool:
        """데이터 로드"""
        try:
            # 네트워크 데이터
            self.nodes_df = pd.read_csv(os.path.join(data_dir, 'network_nodes.csv'))
            self.edges_df = pd.read_csv(os.path.join(data_dir, 'network_edges.csv'))
            
            # 키워드 원본 데이터
            self.keywords_df = pd.read_csv(os.path.join(data_dir, 'extracted_keywords.csv'))
            
            # NetworkX 그래프 재구성
            self.network = nx.Graph()
            
            for _, row in self.nodes_df.iterrows():
                self.network.add_node(
                    row['keyword'],
                    **{col: row[col] for col in self.nodes_df.columns if col != 'keyword'}
                )
            
            for _, row in self.edges_df.iterrows():
                self.network.add_edge(row['source'], row['target'], weight=row['weight'])
            
            print(f"✅ 데이터 로드 완료:")
            print(f"   - 네트워크: {self.network.number_of_nodes()}개 노드, {self.network.number_of_edges()}개 엣지")
            print(f"   - 논문 데이터: {len(self.keywords_df)}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def identify_bridge_keywords(self, top_k: int = 10) -> pd.DataFrame:
        """브릿지 키워드 식별 (betweenness centrality 기반)"""
        print("🌉 브릿지 키워드 분석 중...")
        
        # Betweenness centrality 계산
        betweenness = nx.betweenness_centrality(self.network)
        
        # 노드별 커뮤니티 연결 정보
        bridge_data = []
        
        for keyword in self.network.nodes():
            # 이웃 노드들의 커뮤니티 분포
            neighbors = list(self.network.neighbors(keyword))
            neighbor_communities = []
            neighbor_ai_methods = []
            neighbor_design_tasks = []
            
            for neighbor in neighbors:
                neighbor_communities.append(
                    self.network.nodes[neighbor].get('community', 0)
                )
                ai_method = self.network.nodes[neighbor].get('dominant_ai_method', 'Traditional ML')
                design_task = self.network.nodes[neighbor].get('dominant_design_task', 'Develop')
                
                # NaN 값 처리
                if pd.isna(ai_method) or not ai_method:
                    ai_method = 'Traditional ML'
                if pd.isna(design_task) or not design_task:
                    design_task = 'Develop'
                
                neighbor_ai_methods.append(str(ai_method))
                neighbor_design_tasks.append(str(design_task))
            
            # 다양성 지표 계산
            unique_communities = len(set(neighbor_communities)) if neighbor_communities else 0
            unique_ai_methods = len(set(neighbor_ai_methods)) if neighbor_ai_methods else 0
            unique_design_tasks = len(set(neighbor_design_tasks)) if neighbor_design_tasks else 0
            
            bridge_data.append({
                'keyword': keyword,
                'betweenness_centrality': betweenness.get(keyword, 0),
                'degree': self.network.degree(keyword),
                'frequency': self.network.nodes[keyword].get('frequency', 1),
                'unique_communities_connected': unique_communities,
                'unique_ai_methods_connected': unique_ai_methods,
                'unique_design_tasks_connected': unique_design_tasks,
                'bridge_score': (betweenness.get(keyword, 0) * 
                               (unique_communities + unique_ai_methods + unique_design_tasks)),
                'dominant_ai_method': str(self.network.nodes[keyword].get('dominant_ai_method', 'Traditional ML')),
                'dominant_design_task': str(self.network.nodes[keyword].get('dominant_design_task', 'Develop')),
                'connected_ai_methods': '; '.join(set(neighbor_ai_methods)),
                'connected_design_tasks': '; '.join(set(neighbor_design_tasks))
            })
        
        bridge_df = pd.DataFrame(bridge_data)
        bridge_df = bridge_df.sort_values('bridge_score', ascending=False).head(top_k)
        
        print(f"🔝 상위 {len(bridge_df)}개 브릿지 키워드:")
        for _, row in bridge_df.head(5).iterrows():
            print(f"   {row['keyword']}: Bridge Score {row['bridge_score']:.3f}")
        
        return bridge_df
    
    def analyze_temporal_trends(self) -> pd.DataFrame:
        """시간축 키워드 트렌드 분석"""
        print("📈 시간축 트렌드 분석 중...")
        
        # 연도별 키워드 빈도 계산
        year_keyword_freq = defaultdict(lambda: defaultdict(int))
        keyword_year_data = defaultdict(list)
        
        for _, row in self.keywords_df.iterrows():
            year = row.get('Publication Year', 2020)
            keywords = self._extract_keywords_from_row(row)
            
            for keyword in keywords:
                if keyword in self.network.nodes():  # 네트워크에 포함된 키워드만
                    year_keyword_freq[year][keyword] += 1
                    keyword_year_data[keyword].append(year)
        
        # 키워드별 트렌드 분석
        trend_data = []
        
        for keyword in self.network.nodes():
            years = keyword_year_data.get(keyword, [])
            if len(years) < 2:  # 최소 2번 이상 등장한 키워드만
                continue
            
            # 시간 통계
            first_year = min(years)
            last_year = max(years)
            avg_year = np.mean(years)
            year_span = last_year - first_year
            
            # 트렌드 계산 (최근 증가/감소)
            recent_freq = sum(1 for y in years if y >= 2022)  # 2022년 이후
            early_freq = sum(1 for y in years if y <= 2021)   # 2021년 이전
            
            trend_score = recent_freq - early_freq if early_freq > 0 else recent_freq
            
            # 성장률 계산
            growth_rate = 0
            if early_freq > 0:
                growth_rate = (recent_freq - early_freq) / early_freq * 100
            
            trend_data.append({
                'keyword': keyword,
                'total_frequency': len(years),
                'first_appearance': first_year,
                'last_appearance': last_year,
                'average_year': avg_year,
                'year_span': year_span,
                'early_period_freq': early_freq,
                'recent_period_freq': recent_freq,
                'trend_score': trend_score,
                'growth_rate': growth_rate,
                'dominant_ai_method': self.network.nodes[keyword].get('dominant_ai_method', ''),
                'trend_category': self._categorize_trend(trend_score, growth_rate, avg_year)
            })
        
        trend_df = pd.DataFrame(trend_data)
        trend_df = trend_df.sort_values('trend_score', ascending=False)
        
        print(f"📊 트렌드 분석 완료: {len(trend_df)}개 키워드")
        
        # 카테고리별 분포
        category_counts = trend_df['trend_category'].value_counts()
        print("트렌드 카테고리 분포:")
        for category, count in category_counts.items():
            print(f"   {category}: {count}개")
        
        return trend_df
    
    def identify_research_gaps(self) -> pd.DataFrame:
        """연구 갭 및 기회 식별"""
        print("🔍 연구 갭 분석 중...")
        
        # AI Method × Design Task 조합 분석
        method_task_combinations = defaultdict(int)
        method_task_keywords = defaultdict(list)
        
        for keyword in self.network.nodes():
            ai_method = self.network.nodes[keyword].get('dominant_ai_method', 'Traditional ML')
            design_task = self.network.nodes[keyword].get('dominant_design_task', 'Develop')
            frequency = self.network.nodes[keyword].get('frequency', 1)
            
            combination = f"{ai_method} × {design_task}"
            method_task_combinations[combination] += frequency
            method_task_keywords[combination].append(keyword)
        
        # 모든 가능한 조합 생성
        ai_methods = ['Traditional ML', 'Deep Learning', 'Generative AI', 'Exploratory Data Analysis']
        design_tasks = ['Discovery', 'Define', 'Develop', 'Delivery']
        
        gap_data = []
        
        for ai_method in ai_methods:
            for design_task in design_tasks:
                combination = f"{ai_method} × {design_task}"
                
                frequency = method_task_combinations.get(combination, 0)
                keywords = method_task_keywords.get(combination, [])
                
                # 갭 점수 (빈도가 낮을수록 높은 점수)
                max_freq = max(method_task_combinations.values()) if method_task_combinations else 1
                gap_score = max_freq - frequency
                
                # 기회 점수 (인근 조합의 활성도 기반)
                opportunity_score = self._calculate_opportunity_score(
                    ai_method, design_task, method_task_combinations
                )
                
                gap_data.append({
                    'ai_method': ai_method,
                    'design_task': design_task,
                    'combination': combination,
                    'keyword_count': len(keywords),
                    'total_frequency': frequency,
                    'gap_score': gap_score,
                    'opportunity_score': opportunity_score,
                    'representative_keywords': '; '.join(keywords[:5]) if keywords else 'None',
                    'research_potential': self._assess_research_potential(gap_score, opportunity_score),
                    'suggested_research_areas': self._suggest_research_areas(ai_method, design_task)
                })
        
        gap_df = pd.DataFrame(gap_data)
        gap_df = gap_df.sort_values(['gap_score', 'opportunity_score'], ascending=[False, False])
        
        print(f"🎯 연구 갭 분석 완료:")
        print("상위 5개 연구 기회:")
        for _, row in gap_df.head(5).iterrows():
            print(f"   {row['combination']}: Gap Score {row['gap_score']:.1f}, "
                  f"Potential {row['research_potential']}")
        
        return gap_df
    
    def _extract_keywords_from_row(self, row) -> List[str]:
        """행에서 키워드 추출"""
        keywords_str = row.get('Combined_Keywords', '')
        if pd.isna(keywords_str) or not keywords_str.strip():
            return []
        
        keywords = []
        keyword_pairs = keywords_str.split(';')
        
        for pair in keyword_pairs:
            if '(' in pair and ')' in pair:
                try:
                    keyword = pair.split('(')[0].strip().lower()
                    keywords.append(keyword)
                except:
                    continue
        
        return keywords
    
    def _categorize_trend(self, trend_score: float, growth_rate: float, avg_year: float) -> str:
        """트렌드 카테고리화"""
        if trend_score > 2:
            return "Rising Star"  # 최근 급증
        elif trend_score > 0:
            return "Growing"      # 증가 중
        elif trend_score == 0:
            return "Stable"       # 안정적
        elif avg_year >= 2022:
            return "Recent Entry" # 최근 등장
        else:
            return "Declining"    # 감소 중
    
    def _calculate_opportunity_score(self, ai_method: str, design_task: str, 
                                   combinations: Dict[str, int]) -> float:
        """기회 점수 계산 (인근 조합의 활성도 기반)"""
        # 같은 AI Method의 다른 Task들의 평균 활성도
        same_method_scores = []
        for task in ['Discovery', 'Define', 'Develop', 'Delivery']:
            if task != design_task:
                combo = f"{ai_method} × {task}"
                same_method_scores.append(combinations.get(combo, 0))
        
        # 같은 Design Task의 다른 Method들의 평균 활성도
        same_task_scores = []
        for method in ['Traditional ML', 'Deep Learning', 'Generative AI', 'Exploratory Data Analysis']:
            if method != ai_method:
                combo = f"{method} × {design_task}"
                same_task_scores.append(combinations.get(combo, 0))
        
        # 기회 점수 = 인근 조합들의 평균 활성도
        all_scores = same_method_scores + same_task_scores
        return np.mean(all_scores) if all_scores else 0
    
    def _assess_research_potential(self, gap_score: float, opportunity_score: float) -> str:
        """연구 잠재력 평가"""
        if gap_score > 15 and opportunity_score > 5:
            return "Very High"
        elif gap_score > 10 and opportunity_score > 3:
            return "High"
        elif gap_score > 5 or opportunity_score > 1:
            return "Medium"
        else:
            return "Low"
    
    def _suggest_research_areas(self, ai_method: str, design_task: str) -> str:
        """연구 영역 제안"""
        suggestions = {
            ('Generative AI', 'Discovery'): "AI-powered user research, automated persona generation",
            ('Generative AI', 'Define'): "AI-assisted problem definition, requirement generation",
            ('Generative AI', 'Delivery'): "Automated design delivery, AI-generated presentations",
            ('Deep Learning', 'Discovery'): "Deep user behavior analysis, pattern recognition in user data",
            ('Deep Learning', 'Define'): "AI-driven problem classification, deep requirement analysis",
            ('Deep Learning', 'Delivery'): "Automated quality assessment, deep testing analysis",
            ('Traditional ML', 'Discovery'): "Statistical user research, ML-based user segmentation",
            ('Traditional ML', 'Delivery'): "Performance prediction, traditional ML evaluation metrics",
            ('Exploratory Data Analysis', 'Develop'): "Data-driven development, EDA-guided design iteration",
            ('Exploratory Data Analysis', 'Delivery'): "Statistical evaluation, EDA-based testing"
        }
        
        return suggestions.get((ai_method, design_task), 
                              f"Novel applications of {ai_method} in {design_task} phase")
    
    def save_insights(self, output_dir: str):
        """인사이트 분석 결과 저장"""
        print("💾 인사이트 분석 결과 저장 중...")
        
        # 1. 브릿지 키워드
        bridge_keywords = self.identify_bridge_keywords(15)
        bridge_keywords.to_csv(os.path.join(output_dir, 'bridge_keywords.csv'), index=False)
        
        # 2. 트렌드 키워드
        trending_keywords = self.analyze_temporal_trends()
        trending_keywords.to_csv(os.path.join(output_dir, 'trending_keywords.csv'), index=False)
        
        # 3. 연구 갭
        research_gaps = self.identify_research_gaps()
        research_gaps.to_csv(os.path.join(output_dir, 'research_opportunities.csv'), index=False)
        
        print("✅ 인사이트 분석 결과 저장 완료:")
        print(f"   - bridge_keywords.csv: {len(bridge_keywords)}개")
        print(f"   - trending_keywords.csv: {len(trending_keywords)}개") 
        print(f"   - research_opportunities.csv: {len(research_gaps)}개")

def main():
    """메인 실행 함수"""
    print("🔍 네트워크 인사이트 분석 시스템 시작")
    print("=" * 50)
    
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'results', 'semantic_network_analysis', 'data')
    insights_dir = os.path.join(base_dir, 'results', 'semantic_network_analysis', 'insights')
    
    # 분석기 초기화
    analyzer = NetworkInsightsAnalyzer()
    
    # 1. 데이터 로드
    if not analyzer.load_data(data_dir):
        return
    
    # 2. 인사이트 분석 및 저장
    analyzer.save_insights(insights_dir)
    
    print("\n✅ 인사이트 분석 완료!")
    print(f"📁 결과 저장: {insights_dir}")

if __name__ == "__main__":
    main()