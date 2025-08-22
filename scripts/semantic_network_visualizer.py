#!/usr/bin/env python3
"""
시맨틱 네트워크 시각화 시스템
- AI Method/Design Task별 색상 및 모양 구분
- 다양한 레이아웃 (Spring, Circular, Kamada-Kawai)
- 중심성 기반 노드 크기 조절
- 정적 및 인터랙티브 시각화
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

from typing import Dict, List, Tuple

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.patches import Patch
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    plt.rcParams['font.size'] = 10
    plt.rcParams['figure.dpi'] = 300
    sns.set_palette("husl")
except ImportError as e:
    print(f"⚠️  라이브러리 누락: {e}")
    print("필요한 라이브러리: networkx matplotlib seaborn plotly")
    exit(1)

class SemanticNetworkVisualizer:
    """시맨틱 네트워크 시각화기"""
    
    def __init__(self):
        self.nodes_df = None
        self.edges_df = None
        self.network = None
        
        # AI Method별 색상 매핑
        self.ai_method_colors = {
            'Traditional ML': '#2E8B57',      # 시그린
            'Deep Learning': '#4169E1',       # 로얄블루  
            'Generative AI': '#DC143C',       # 크림슨
            'Exploratory Data Analysis': '#FF8C00',  # 다크오렌지
            'Multiple': '#9370DB'             # 미디움퍼플
        }
        
        # Design Task별 모양 매핑 (matplotlib markers)
        self.design_task_markers = {
            'Discovery': 'o',    # 원
            'Define': 's',       # 사각형
            'Develop': '^',      # 삼각형
            'Delivery': 'D',     # 다이아몬드
            'Multiple': 'X'      # X자
        }
        
        # Design Task별 크기 배수
        self.design_task_sizes = {
            'Discovery': 1.0,
            'Define': 1.2,
            'Develop': 1.4,
            'Delivery': 1.6,
            'Multiple': 1.8
        }
    
    def load_network_data(self, data_dir: str) -> bool:
        """네트워크 데이터 로드"""
        try:
            nodes_file = os.path.join(data_dir, 'network_nodes.csv')
            edges_file = os.path.join(data_dir, 'network_edges.csv')
            
            self.nodes_df = pd.read_csv(nodes_file)
            self.edges_df = pd.read_csv(edges_file)
            
            # NetworkX 그래프 재구성
            self.network = nx.Graph()
            
            # 노드 추가
            for _, row in self.nodes_df.iterrows():
                self.network.add_node(
                    row['keyword'],
                    **{col: row[col] for col in self.nodes_df.columns if col != 'keyword'}
                )
            
            # 엣지 추가
            for _, row in self.edges_df.iterrows():
                self.network.add_edge(row['source'], row['target'], weight=row['weight'])
            
            print(f"✅ 네트워크 데이터 로드 완료:")
            print(f"   - 노드: {len(self.nodes_df)}개")
            print(f"   - 엣지: {len(self.edges_df)}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 네트워크 데이터 로드 실패: {e}")
            return False
    
    def create_static_network_visualization(self, 
                                          output_dir: str,
                                          layout: str = 'spring',
                                          min_degree: int = 2,
                                          figsize: Tuple[int, int] = (16, 12)) -> str:
        """정적 네트워크 시각화 생성"""
        print(f"🎨 정적 네트워크 시각화 생성 ({layout} 레이아웃)...")
        
        # 연결도 기준 노드 필터링
        filtered_nodes = [node for node in self.network.nodes() 
                         if self.network.degree(node) >= min_degree]
        subgraph = self.network.subgraph(filtered_nodes).copy()
        
        print(f"📊 시각화 대상: {len(filtered_nodes)}개 노드 (최소 연결도: {min_degree})")
        
        # 레이아웃 설정
        if layout == 'spring':
            pos = nx.spring_layout(subgraph, k=3, iterations=50, seed=42)
        elif layout == 'circular':
            pos = nx.circular_layout(subgraph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(subgraph)
        else:
            pos = nx.spring_layout(subgraph, k=3, iterations=50, seed=42)
        
        # 시각화 생성
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        ax.set_facecolor('white')
        
        # AI Method별 노드 그룹 시각화
        ai_methods = self.nodes_df['dominant_ai_method'].unique()
        
        for ai_method in ai_methods:
            # 해당 AI Method 노드들
            method_nodes = [node for node in filtered_nodes 
                           if self.network.nodes[node].get('dominant_ai_method') == ai_method]
            
            if not method_nodes:
                continue
            
            # Design Task별로 다시 분리하여 시각화
            design_tasks = set([self.network.nodes[node].get('dominant_design_task', 'Develop') 
                               for node in method_nodes])
            
            for design_task in design_tasks:
                task_nodes = [node for node in method_nodes 
                             if self.network.nodes[node].get('dominant_design_task') == design_task]
                
                if not task_nodes:
                    continue
                
                # 노드 크기 (빈도 기반)
                node_sizes = [self.network.nodes[node].get('frequency', 1) * 100 * 
                             self.design_task_sizes.get(design_task, 1.0) 
                             for node in task_nodes]
                
                # 노드 위치
                node_positions = [pos[node] for node in task_nodes]
                
                # 노드 시각화
                nx.draw_networkx_nodes(
                    subgraph.subgraph(task_nodes),
                    pos,
                    nodelist=task_nodes,
                    node_color=self.ai_method_colors.get(ai_method, '#808080'),
                    node_shape=self.design_task_markers.get(design_task, 'o'),
                    node_size=node_sizes,
                    alpha=0.8,
                    ax=ax
                )
        
        # 엣지 시각화 (가중치 기반 두께)
        edges = subgraph.edges()
        weights = [subgraph[u][v].get('weight', 1) for u, v in edges]
        max_weight = max(weights) if weights else 1
        
        nx.draw_networkx_edges(
            subgraph,
            pos,
            edgelist=edges,
            width=[w / max_weight * 3 for w in weights],
            alpha=0.4,
            edge_color='gray',
            ax=ax
        )
        
        # 고빈도 키워드 라벨 (상위 20개)
        high_freq_nodes = sorted(filtered_nodes, 
                                key=lambda x: self.network.nodes[x].get('frequency', 1), 
                                reverse=True)[:20]
        
        labels = {node: node for node in high_freq_nodes}
        nx.draw_networkx_labels(
            subgraph,
            pos,
            labels,
            font_size=8,
            font_color='black',
            font_weight='bold',
            ax=ax
        )
        
        # 범례 생성
        self._add_legend(ax)
        
        # 제목 및 스타일링
        ax.set_title(f'Semantic Network of Keywords in AI Design Research\n'
                    f'({len(filtered_nodes)} nodes, {len(edges)} edges, {layout} layout)',
                    fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        # 저장
        output_file = os.path.join(output_dir, f'semantic_network_{layout}.png')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ 정적 시각화 저장: {output_file}")
        return output_file
    
    def create_ai_method_subnetworks(self, output_dir: str, figsize: Tuple[int, int] = (20, 15)) -> List[str]:
        """AI Method별 서브네트워크 시각화"""
        print("🔬 AI Method별 서브네트워크 생성...")
        
        ai_methods = self.nodes_df['dominant_ai_method'].unique()
        output_files = []
        
        # 전체 서브플롯 생성
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        axes = axes.flatten()
        
        for i, ai_method in enumerate(ai_methods[:6]):  # 최대 6개까지
            ax = axes[i]
            
            # 해당 AI Method 노드들로 서브그래프 생성
            method_nodes = [node for node in self.network.nodes() 
                           if self.network.nodes[node].get('dominant_ai_method') == ai_method
                           and self.network.degree(node) >= 1]  # 최소 1개 연결
            
            if not method_nodes:
                ax.axis('off')
                ax.set_title(f'{ai_method}\n(No connected nodes)', fontsize=12)
                continue
            
            subgraph = self.network.subgraph(method_nodes).copy()
            
            # 가장 큰 연결 컴포넌트만 선택
            if len(subgraph.nodes()) > 0:
                largest_cc = max(nx.connected_components(subgraph), key=len)
                subgraph = subgraph.subgraph(largest_cc).copy()
            
            if len(subgraph.nodes()) == 0:
                ax.axis('off')
                ax.set_title(f'{ai_method}\n(No connected component)', fontsize=12)
                continue
            
            # 레이아웃
            pos = nx.spring_layout(subgraph, k=1, iterations=50, seed=42)
            
            # 노드 크기 (빈도 기반)
            node_sizes = [subgraph.nodes[node].get('frequency', 1) * 50 for node in subgraph.nodes()]
            
            # 노드 색상 (Design Task 기반)
            node_colors = []
            for node in subgraph.nodes():
                design_task = subgraph.nodes[node].get('dominant_design_task', 'Develop')
                if design_task == 'Discovery':
                    node_colors.append('#1f77b4')
                elif design_task == 'Define':
                    node_colors.append('#ff7f0e')  
                elif design_task == 'Develop':
                    node_colors.append('#2ca02c')
                elif design_task == 'Delivery':
                    node_colors.append('#d62728')
                else:
                    node_colors.append('#9467bd')
            
            # 노드 시각화
            nx.draw_networkx_nodes(
                subgraph, pos,
                node_color=node_colors,
                node_size=node_sizes,
                alpha=0.8,
                ax=ax
            )
            
            # 엣지 시각화
            edges = subgraph.edges()
            if edges:
                weights = [subgraph[u][v].get('weight', 1) for u, v in edges]
                max_weight = max(weights) if weights else 1
                
                nx.draw_networkx_edges(
                    subgraph, pos,
                    width=[w / max_weight * 2 for w in weights],
                    alpha=0.5,
                    edge_color='gray',
                    ax=ax
                )
            
            # 라벨 (상위 빈도 노드만)
            if len(subgraph.nodes()) <= 15:
                labels = {node: node for node in subgraph.nodes()}
                nx.draw_networkx_labels(
                    subgraph, pos, labels,
                    font_size=8, font_weight='bold',
                    ax=ax
                )
            else:
                # 상위 10개만 라벨 표시
                top_nodes = sorted(subgraph.nodes(), 
                                 key=lambda x: subgraph.nodes[x].get('frequency', 1), 
                                 reverse=True)[:10]
                labels = {node: node for node in top_nodes}
                nx.draw_networkx_labels(
                    subgraph, pos, labels,
                    font_size=7, font_weight='bold',
                    ax=ax
                )
            
            ax.set_title(f'{ai_method}\n({len(subgraph.nodes())} nodes, {len(subgraph.edges())} edges)',
                        fontsize=12, fontweight='bold')
            ax.axis('off')
        
        # 빈 서브플롯 제거
        for j in range(len(ai_methods), len(axes)):
            axes[j].axis('off')
        
        plt.suptitle('AI Method-specific Keyword Networks', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        output_file = os.path.join(output_dir, 'network_by_ai_method.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        output_files.append(output_file)
        print(f"✅ AI Method별 서브네트워크 저장: {output_file}")
        
        return output_files
    
    def create_interactive_network(self, output_dir: str) -> str:
        """인터랙티브 네트워크 생성 (Plotly)"""
        print("🌐 인터랙티브 네트워크 생성...")
        
        # 연결도 기준 필터링 (너무 많은 노드는 성능 저하)
        min_degree = 2
        filtered_nodes = [node for node in self.network.nodes() 
                         if self.network.degree(node) >= min_degree]
        subgraph = self.network.subgraph(filtered_nodes).copy()
        
        # 레이아웃
        pos = nx.spring_layout(subgraph, k=2, iterations=50, seed=42)
        
        # 엣지 트레이스
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            weight = subgraph[edge[0]][edge[1]].get('weight', 1)
            edge_info.append(f"{edge[0]} ↔ {edge[1]} (co-occurrence: {weight})")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='lightgray'),
            hoverinfo='none',
            mode='lines'
        )
        
        # 노드 트레이스들 (AI Method별)
        node_traces = []
        
        for ai_method in self.ai_method_colors.keys():
            method_nodes = [node for node in filtered_nodes 
                           if subgraph.nodes[node].get('dominant_ai_method') == ai_method]
            
            if not method_nodes:
                continue
            
            node_x = [pos[node][0] for node in method_nodes]
            node_y = [pos[node][1] for node in method_nodes]
            
            # 노드 크기 (빈도 기반)
            node_sizes = [subgraph.nodes[node].get('frequency', 1) * 8 + 10 
                         for node in method_nodes]
            
            # 호버 정보
            hover_texts = []
            for node in method_nodes:
                attrs = subgraph.nodes[node]
                hover_text = (f"<b>{node}</b><br>"
                            f"Frequency: {attrs.get('frequency', 1)}<br>"
                            f"AI Method: {attrs.get('dominant_ai_method', 'N/A')}<br>"
                            f"Design Task: {attrs.get('dominant_design_task', 'N/A')}<br>"
                            f"Degree: {subgraph.degree(node)}<br>"
                            f"Betweenness: {attrs.get('betweenness_centrality', 0):.3f}")
                hover_texts.append(hover_text)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                hovertext=hover_texts,
                text=method_nodes,
                textposition="middle center",
                textfont=dict(size=8),
                name=ai_method,
                marker=dict(
                    size=node_sizes,
                    color=self.ai_method_colors[ai_method],
                    line=dict(width=2, color='white'),
                    opacity=0.8
                )
            )
            
            node_traces.append(node_trace)
        
        # 레이아웃 설정
        layout = go.Layout(
            title=dict(
                text='Interactive Semantic Network of AI Design Research Keywords',
                x=0.5,
                font=dict(size=16)
            ),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Node size = keyword frequency, Color = dominant AI method<br>"
                     "Hover for details, Click legend to filter",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=10)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        # 피그 생성
        fig = go.Figure(data=[edge_trace] + node_traces, layout=layout)
        
        # 저장
        output_file = os.path.join(output_dir, 'interactive_network.html')
        fig.write_html(output_file)
        
        print(f"✅ 인터랙티브 네트워크 저장: {output_file}")
        return output_file
    
    def _add_legend(self, ax):
        """범례 추가"""
        # AI Method 색상 범례
        ai_legend_elements = [Patch(facecolor=color, label=method) 
                             for method, color in self.ai_method_colors.items()]
        
        # Design Task 모양 범례  
        task_legend_elements = []
        for task, marker in self.design_task_markers.items():
            task_legend_elements.append(
                plt.Line2D([0], [0], marker=marker, color='gray', 
                          linestyle='None', markersize=8, label=task)
            )
        
        # 두 개의 범례 생성
        legend1 = ax.legend(handles=ai_legend_elements, 
                           title="AI Methods", 
                           loc='upper left', 
                           bbox_to_anchor=(0, 1))
        
        legend2 = ax.legend(handles=task_legend_elements, 
                           title="Design Tasks", 
                           loc='upper left', 
                           bbox_to_anchor=(0, 0.7))
        
        # 첫 번째 범례를 다시 추가 (덮어씌워지지 않도록)
        ax.add_artist(legend1)

def main():
    """메인 실행 함수"""
    print("🎨 시맨틱 네트워크 시각화 시스템 시작")
    print("=" * 50)
    
    # 경로 설정
    data_dir = '/Users/outcode.jongmokim/Documents/paper_review_with_llm/output/semantic_network_analysis/data'
    viz_dir = '/Users/outcode.jongmokim/Documents/paper_review_with_llm/output/semantic_network_analysis/visualizations'
    
    # 시각화기 초기화
    visualizer = SemanticNetworkVisualizer()
    
    # 1. 데이터 로드
    if not visualizer.load_network_data(data_dir):
        return
    
    # 2. 정적 네트워크 시각화 (다양한 레이아웃)
    layouts = ['spring', 'circular', 'kamada_kawai']
    for layout in layouts:
        visualizer.create_static_network_visualization(
            viz_dir, layout=layout, min_degree=2
        )
    
    # 3. AI Method별 서브네트워크
    visualizer.create_ai_method_subnetworks(viz_dir)
    
    # 4. 인터랙티브 네트워크
    visualizer.create_interactive_network(viz_dir)
    
    print("\n✅ 모든 시각화 완료!")
    print(f"📁 저장 위치: {viz_dir}")

if __name__ == "__main__":
    main()