#!/usr/bin/env python3
"""
시맨틱 네트워크 구축 시스템
- 키워드 공출현(co-occurrence) 매트릭스 생성
- NetworkX 기반 그래프 구조 구축
- AI Method/Design Task별 노드 속성 설정
- 커뮤니티 탐지를 통한 키워드 클러스터링
"""

import pandas as pd
import numpy as np
import os
import re
import warnings
warnings.filterwarnings('ignore')

from collections import defaultdict, Counter
from itertools import combinations
from typing import Dict, List, Tuple, Set

try:
    import networkx as nx
    from scipy.sparse import csr_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.style.use('default')
    sns.set_palette("husl")
except ImportError as e:
    print(f"⚠️  라이브러리 누락: {e}")
    print("필요한 라이브러리: networkx scipy matplotlib seaborn")
    exit(1)

class SemanticNetworkBuilder:
    """시맨틱 네트워크 구축기"""
    
    def __init__(self):
        self.keywords_df = None
        self.cooccurrence_matrix = None
        self.network = None
        self.ai_method_colors = {
            'Traditional ML': '#2E8B57',      # 시그린
            'Deep Learning': '#4169E1',       # 로얄블루
            'Generative AI': '#DC143C',       # 크림슨
            'Exploratory Data Analysis': '#FF8C00',  # 다크오렌지
            'Multiple': '#9370DB'             # 미디움퍼플
        }
        self.design_task_shapes = {
            'Discovery': 'o',    # 원
            'Define': 's',       # 사각형
            'Develop': '^',      # 삼각형
            'Delivery': 'D',     # 다이아몬드
            'Multiple': 'X'      # X자
        }
        
    def load_keywords_data(self, file_path: str) -> bool:
        """키워드 데이터 로드"""
        try:
            self.keywords_df = pd.read_csv(file_path)
            print(f"✅ 키워드 데이터 로드: {len(self.keywords_df)}개 논문")
            return True
        except Exception as e:
            print(f"❌ 키워드 데이터 로드 실패: {e}")
            return False
    
    def extract_paper_keywords(self, keywords_str: str, score_threshold: float = 0.01) -> List[str]:
        """논문별 키워드 추출 (점수 임계값 적용)"""
        if pd.isna(keywords_str) or not keywords_str.strip():
            return []
        
        keywords = []
        # "keyword(score); keyword(score)" 형태 파싱
        keyword_pairs = keywords_str.split(';')
        
        for pair in keyword_pairs:
            pair = pair.strip()
            if '(' in pair and ')' in pair:
                try:
                    keyword = pair.split('(')[0].strip()
                    score_str = pair.split('(')[1].split(')')[0]
                    score = float(score_str)
                    
                    # 점수 임계값 적용
                    if score >= score_threshold and len(keyword) > 1:
                        keywords.append(keyword.lower())
                except (ValueError, IndexError):
                    continue
        
        return keywords
    
    def build_cooccurrence_matrix(self, min_cooccurrence: int = 2) -> np.ndarray:
        """키워드 공출현 매트릭스 구축"""
        print("🔄 공출현 매트릭스 구축 중...")
        
        # 모든 논문의 키워드 수집
        all_paper_keywords = []
        keyword_to_paper = defaultdict(list)
        
        for idx, row in self.keywords_df.iterrows():
            # Combined_Keywords 사용 (TF-IDF + KeyBERT 결합)
            paper_keywords = self.extract_paper_keywords(row['Combined_Keywords'])
            all_paper_keywords.append(paper_keywords)
            
            # 키워드별 논문 매핑
            for keyword in paper_keywords:
                keyword_to_paper[keyword].append(idx)
        
        # 고유 키워드 리스트 생성 (빈도 기준 필터링)
        keyword_counts = Counter()
        for keywords in all_paper_keywords:
            keyword_counts.update(keywords)
        
        # 최소 빈도 이상의 키워드만 선택
        valid_keywords = [kw for kw, count in keyword_counts.items() if count >= min_cooccurrence]
        keyword_to_idx = {kw: idx for idx, kw in enumerate(valid_keywords)}
        
        print(f"📊 분석 대상 키워드: {len(valid_keywords)}개 (최소 빈도: {min_cooccurrence})")
        
        # 공출현 매트릭스 초기화
        n_keywords = len(valid_keywords)
        cooccurrence = np.zeros((n_keywords, n_keywords), dtype=int)
        
        # 각 논문에서 키워드 쌍별 공출현 계산
        for paper_keywords in all_paper_keywords:
            # 유효한 키워드만 필터링
            valid_paper_keywords = [kw for kw in paper_keywords if kw in keyword_to_idx]
            
            # 키워드 쌍 조합 생성
            for kw1, kw2 in combinations(valid_paper_keywords, 2):
                idx1, idx2 = keyword_to_idx[kw1], keyword_to_idx[kw2]
                cooccurrence[idx1, idx2] += 1
                cooccurrence[idx2, idx1] += 1  # 대칭 매트릭스
        
        self.cooccurrence_matrix = cooccurrence
        self.keyword_list = valid_keywords
        
        # 결과 저장
        cooccurrence_df = pd.DataFrame(
            cooccurrence, 
            index=valid_keywords, 
            columns=valid_keywords
        )
        
        return cooccurrence_df
    
    def build_network_graph(self, min_edge_weight: int = 2) -> nx.Graph:
        """NetworkX 그래프 구축"""
        print("🕸️  네트워크 그래프 구축 중...")
        
        self.network = nx.Graph()
        
        # 노드 추가 (키워드별 속성 포함)
        keyword_attributes = self._calculate_keyword_attributes()
        
        for i, keyword in enumerate(self.keyword_list):
            attrs = keyword_attributes.get(keyword, {})
            self.network.add_node(
                keyword,
                frequency=attrs.get('frequency', 1),
                dominant_ai_method=attrs.get('dominant_ai_method', 'Traditional ML'),
                dominant_design_task=attrs.get('dominant_design_task', 'Develop'),
                papers=attrs.get('papers', [])
            )
        
        # 엣지 추가 (공출현 빈도 기반)
        edge_count = 0
        for i in range(len(self.keyword_list)):
            for j in range(i+1, len(self.keyword_list)):
                weight = self.cooccurrence_matrix[i, j]
                if weight >= min_edge_weight:
                    kw1, kw2 = self.keyword_list[i], self.keyword_list[j]
                    self.network.add_edge(kw1, kw2, weight=weight)
                    edge_count += 1
        
        print(f"📈 네트워크 구축 완료:")
        print(f"   - 노드: {self.network.number_of_nodes()}개")
        print(f"   - 엣지: {self.network.number_of_edges()}개")
        print(f"   - 연결 컴포넌트: {nx.number_connected_components(self.network)}개")
        
        return self.network
    
    def _calculate_keyword_attributes(self) -> Dict[str, Dict]:
        """키워드별 속성 계산 (AI 방법론, 디자인 태스크, 빈도 등)"""
        keyword_attrs = defaultdict(lambda: {
            'frequency': 0,
            'ai_methods': Counter(),
            'design_tasks': Counter(),
            'papers': [],
            'years': []
        })
        
        # 각 논문을 순회하며 키워드 속성 집계
        for idx, row in self.keywords_df.iterrows():
            keywords = self.extract_paper_keywords(row['Combined_Keywords'])
            ai_method = row.get('AI_Method_Normalized', 'Traditional ML')
            design_task = row.get('Design_Task_Normalized', 'Develop')
            year = row.get('Publication Year', 2020)
            paper_title = row.get('Article Title', f'Paper_{idx}')
            
            for keyword in keywords:
                if keyword in self.keyword_list:
                    keyword_attrs[keyword]['frequency'] += 1
                    keyword_attrs[keyword]['ai_methods'][ai_method] += 1
                    keyword_attrs[keyword]['design_tasks'][design_task] += 1
                    keyword_attrs[keyword]['papers'].append(paper_title)
                    keyword_attrs[keyword]['years'].append(year)
        
        # 최빈값 계산
        final_attrs = {}
        for keyword, attrs in keyword_attrs.items():
            final_attrs[keyword] = {
                'frequency': attrs['frequency'],
                'dominant_ai_method': attrs['ai_methods'].most_common(1)[0][0] if attrs['ai_methods'] else 'Traditional ML',
                'dominant_design_task': attrs['design_tasks'].most_common(1)[0][0] if attrs['design_tasks'] else 'Develop',
                'papers': attrs['papers'],
                'avg_year': np.mean(attrs['years']) if attrs['years'] else 2020
            }
        
        return final_attrs
    
    def detect_communities(self) -> Dict[str, int]:
        """커뮤니티 탐지 (Louvain 알고리즘)"""
        print("👥 커뮤니티 탐지 중...")
        
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(self.network)
            
            # 노드에 커뮤니티 속성 추가
            nx.set_node_attributes(self.network, partition, 'community')
            
            n_communities = len(set(partition.values()))
            print(f"✅ {n_communities}개 커뮤니티 탐지 완료")
            
            return partition
            
        except ImportError:
            print("⚠️  python-louvain 라이브러리 필요: pip install python-louvain")
            # 대안: NetworkX의 기본 커뮤니티 탐지
            try:
                communities = nx.community.greedy_modularity_communities(self.network)
                partition = {}
                for i, community in enumerate(communities):
                    for node in community:
                        partition[node] = i
                
                nx.set_node_attributes(self.network, partition, 'community')
                print(f"✅ {len(communities)}개 커뮤니티 탐지 완료 (대안 방법)")
                return partition
                
            except Exception as e:
                print(f"⚠️  커뮤니티 탐지 실패: {e}")
                # 기본값: 모든 노드를 하나의 커뮤니티로
                partition = {node: 0 for node in self.network.nodes()}
                nx.set_node_attributes(self.network, partition, 'community')
                return partition
    
    def save_network_data(self, output_dir: str):
        """네트워크 데이터 저장"""
        print("💾 네트워크 데이터 저장 중...")
        
        # 1. 공출현 매트릭스 저장
        cooccurrence_df = pd.DataFrame(
            self.cooccurrence_matrix,
            index=self.keyword_list,
            columns=self.keyword_list
        )
        cooccurrence_df.to_csv(os.path.join(output_dir, 'cooccurrence_matrix.csv'))
        
        # 2. 노드 속성 저장
        node_data = []
        for node in self.network.nodes():
            attrs = self.network.nodes[node]
            node_data.append({
                'keyword': node,
                'frequency': attrs.get('frequency', 1),
                'dominant_ai_method': attrs.get('dominant_ai_method', 'Traditional ML'),
                'dominant_design_task': attrs.get('dominant_design_task', 'Develop'),
                'community': attrs.get('community', 0),
                'degree': self.network.degree(node),
                'betweenness_centrality': nx.betweenness_centrality(self.network).get(node, 0),
                'closeness_centrality': nx.closeness_centrality(self.network).get(node, 0),
                'eigenvector_centrality': nx.eigenvector_centrality(self.network, max_iter=1000).get(node, 0)
            })
        
        nodes_df = pd.DataFrame(node_data)
        nodes_df.to_csv(os.path.join(output_dir, 'network_nodes.csv'), index=False)
        
        # 3. 엣지 속성 저장
        edge_data = []
        for u, v, attrs in self.network.edges(data=True):
            edge_data.append({
                'source': u,
                'target': v,
                'weight': attrs.get('weight', 1),
                'normalized_weight': attrs.get('weight', 1) / max([d['weight'] for _, _, d in self.network.edges(data=True)])
            })
        
        edges_df = pd.DataFrame(edge_data)
        edges_df.to_csv(os.path.join(output_dir, 'network_edges.csv'), index=False)
        
        # 4. 커뮤니티 정보 저장
        communities = defaultdict(list)
        for node in self.network.nodes():
            community_id = self.network.nodes[node].get('community', 0)
            communities[community_id].append(node)
        
        community_data = []
        for comm_id, members in communities.items():
            community_data.append({
                'community_id': comm_id,
                'size': len(members),
                'keywords': '; '.join(members),
                'dominant_ai_methods': self._get_community_dominant_attribute(members, 'dominant_ai_method'),
                'dominant_design_tasks': self._get_community_dominant_attribute(members, 'dominant_design_task')
            })
        
        communities_df = pd.DataFrame(community_data)
        communities_df.to_csv(os.path.join(output_dir, 'keyword_communities.csv'), index=False)
        
        print(f"✅ 네트워크 데이터 저장 완료:")
        print(f"   - cooccurrence_matrix.csv: {len(self.keyword_list)}x{len(self.keyword_list)}")
        print(f"   - network_nodes.csv: {len(node_data)}개 노드")
        print(f"   - network_edges.csv: {len(edge_data)}개 엣지")
        print(f"   - keyword_communities.csv: {len(community_data)}개 커뮤니티")
    
    def _get_community_dominant_attribute(self, members: List[str], attr_name: str) -> str:
        """커뮤니티 내 지배적 속성 계산"""
        attr_counter = Counter()
        for member in members:
            if member in self.network.nodes():
                attr_value = self.network.nodes[member].get(attr_name, '')
                if attr_value:
                    attr_counter[attr_value] += 1
        
        return attr_counter.most_common(1)[0][0] if attr_counter else 'Unknown'

def main():
    """메인 실행 함수"""
    print("🕸️  시맨틱 네트워크 구축 시스템 시작")
    print("=" * 50)
    
    # 입력 및 출력 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'results', 'semantic_network_analysis', 'data', 'extracted_keywords.csv')
    output_dir = os.path.join(base_dir, 'results', 'semantic_network_analysis', 'data')
    
    # 네트워크 빌더 초기화
    builder = SemanticNetworkBuilder()
    
    # 1. 키워드 데이터 로드
    if not builder.load_keywords_data(input_file):
        return
    
    # 2. 공출현 매트릭스 구축
    cooccurrence_df = builder.build_cooccurrence_matrix(min_cooccurrence=2)
    print(f"📊 공출현 매트릭스: {cooccurrence_df.shape}")
    
    # 3. 네트워크 그래프 구축
    network = builder.build_network_graph(min_edge_weight=2)
    
    # 4. 커뮤니티 탐지
    communities = builder.detect_communities()
    
    # 5. 네트워크 데이터 저장
    builder.save_network_data(output_dir)
    
    # 6. 기본 통계 출력
    print("\n📈 네트워크 기본 통계:")
    print(f"   - 총 키워드(노드): {network.number_of_nodes()}개")
    print(f"   - 총 공출현 관계(엣지): {network.number_of_edges()}개")
    print(f"   - 평균 연결도: {np.mean([d for _, d in network.degree()]):.2f}")
    print(f"   - 네트워크 밀도: {nx.density(network):.4f}")
    print(f"   - 커뮤니티 개수: {len(set(communities.values()))}개")
    
    # 상위 중심성 키워드 출력
    centrality_measures = {
        'Degree': nx.degree_centrality(network),
        'Betweenness': nx.betweenness_centrality(network),
        'Closeness': nx.closeness_centrality(network),
        'Eigenvector': nx.eigenvector_centrality(network, max_iter=1000)
    }
    
    print("\n🔝 상위 중심성 키워드:")
    for measure_name, centrality in centrality_measures.items():
        top_keywords = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"   {measure_name}: {[kw for kw, score in top_keywords]}")

if __name__ == "__main__":
    main()