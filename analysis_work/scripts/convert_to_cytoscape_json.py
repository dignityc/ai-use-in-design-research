#!/usr/bin/env python3
"""
Cytoscape.js JSON 데이터 변환기
네트워크 데이터를 Cytoscape.js 형태의 JSON으로 변환
"""

import pandas as pd
import json
import os
from typing import Dict, List, Any

def convert_network_to_cytoscape_json(data_dir: str, output_file: str):
    """네트워크 데이터를 Cytoscape.js JSON 형태로 변환"""
    
    print("🔄 Cytoscape.js JSON 데이터 변환 시작...")
    
    # 데이터 로드
    nodes_df = pd.read_csv(os.path.join(data_dir, 'network_nodes.csv'))
    edges_df = pd.read_csv(os.path.join(data_dir, 'network_edges.csv'))
    
    # AI Method별 색상 매핑
    ai_method_colors = {
        'Traditional ML': '#2E8B57',      # 시그린
        'Deep Learning': '#4169E1',       # 로얄블루
        'Generative AI': '#DC143C',       # 크림슨
        'Exploratory Data Analysis': '#FF8C00',  # 다크오렌지
        'Multiple': '#9370DB',            # 미디움퍼플
        'nan': '#808080',                 # 회색 (기본값)
        '': '#808080'
    }
    
    # Design Task별 모양 매핑
    design_task_shapes = {
        'Discovery': 'circle',
        'Define': 'square', 
        'Develop': 'triangle',
        'Delivery': 'diamond',
        'Multiple': 'star',
        'nan': 'ellipse',
        '': 'ellipse'
    }
    
    # 트렌드 카테고리 색상 (추가 정보용)
    trend_colors = {
        'Rising Star': '#FF1493',    # 딥핑크
        'Growing': '#32CD32',        # 라임그린
        'Stable': '#4682B4',         # 스틸블루
        'Recent Entry': '#FF6347',   # 토마토
        'Declining': '#696969'       # 딤그레이
    }
    
    # Cytoscape.js 형태 데이터 구조 생성
    cytoscape_data = {
        "elements": {
            "nodes": [],
            "edges": []
        },
        "layout": {"name": "cose"},
        "style": []
    }
    
    # 노드 변환
    print(f"📊 노드 변환: {len(nodes_df)}개")
    
    for _, row in nodes_df.iterrows():
        keyword = row['keyword']
        frequency = row.get('frequency', 1)
        ai_method = str(row.get('dominant_ai_method', 'Traditional ML'))
        design_task = str(row.get('dominant_design_task', 'Develop'))
        
        # NaN 처리
        if pd.isna(ai_method) or ai_method == 'nan':
            ai_method = 'Traditional ML'
        if pd.isna(design_task) or design_task == 'nan':
            design_task = 'Develop'
        
        node = {
            "data": {
                "id": keyword,
                "label": keyword,
                "frequency": int(frequency),
                "ai_method": ai_method,
                "design_task": design_task,
                "degree": int(row.get('degree', 1)),
                "betweenness_centrality": float(row.get('betweenness_centrality', 0)),
                "closeness_centrality": float(row.get('closeness_centrality', 0)),
                "eigenvector_centrality": float(row.get('eigenvector_centrality', 0)),
                "community": int(row.get('community', 0)),
                "color": ai_method_colors.get(ai_method, '#808080'),
                "shape": design_task_shapes.get(design_task, 'ellipse'),
                "size": max(20, min(80, frequency * 8)),  # 크기 범위 제한
                "is_bridge": frequency > 5 and row.get('betweenness_centrality', 0) > 0.02  # 브릿지 키워드 표시
            },
            "classes": f"ai-{ai_method.lower().replace(' ', '-')} task-{design_task.lower()}"
        }
        
        cytoscape_data["elements"]["nodes"].append(node)
    
    # 엣지 변환
    print(f"🔗 엣지 변환: {len(edges_df)}개")
    
    for _, row in edges_df.iterrows():
        source = row['source']
        target = row['target']
        weight = int(row.get('weight', 1))
        
        edge = {
            "data": {
                "id": f"{source}-{target}",
                "source": source,
                "target": target,
                "weight": weight,
                "width": max(1, min(8, weight * 2)),  # 선 두께
                "opacity": min(1.0, 0.3 + weight * 0.1)  # 투명도
            },
            "classes": f"weight-{min(5, weight)}"  # 가중치별 클래스
        }
        
        cytoscape_data["elements"]["edges"].append(edge)
    
    # 스타일 정의
    cytoscape_data["style"] = [
        {
            "selector": "node",
            "style": {
                "content": "data(label)",
                "text-valign": "center",
                "text-halign": "center",
                "background-color": "data(color)",
                "shape": "data(shape)",
                "width": "data(size)",
                "height": "data(size)",
                "font-size": "12px",
                "font-weight": "bold",
                "text-outline-color": "#ffffff",
                "text-outline-width": "2px",
                "border-width": "2px",
                "border-color": "#ffffff"
            }
        },
        {
            "selector": "edge",
            "style": {
                "width": "data(width)",
                "line-color": "#cccccc",
                "target-arrow-color": "#cccccc",
                "target-arrow-shape": "triangle",
                "curve-style": "bezier",
                "opacity": "data(opacity)"
            }
        },
        {
            "selector": "node:selected",
            "style": {
                "border-width": "4px",
                "border-color": "#FFD700",
                "background-color": "#FFD700"
            }
        },
        {
            "selector": "edge:selected",
            "style": {
                "line-color": "#FFD700",
                "width": "data(width)",
                "opacity": 1
            }
        },
        {
            "selector": ".highlighted",
            "style": {
                "background-color": "#FF6B6B",
                "border-color": "#FF6B6B",
                "border-width": "3px"
            }
        },
        {
            "selector": ".faded",
            "style": {
                "opacity": 0.2
            }
        }
    ]
    
    # AI Method별 스타일
    for method, color in ai_method_colors.items():
        class_name = f"ai-{method.lower().replace(' ', '-')}"
        cytoscape_data["style"].append({
            "selector": f".{class_name}",
            "style": {
                "background-color": color,
                "border-color": color
            }
        })
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cytoscape_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Cytoscape.js JSON 변환 완료:")
    print(f"   - 노드: {len(cytoscape_data['elements']['nodes'])}개")
    print(f"   - 엣지: {len(cytoscape_data['elements']['edges'])}개")
    print(f"   - 저장 위치: {output_file}")
    
    return cytoscape_data

def create_metadata_json(data_dir: str, output_file: str):
    """메타데이터 JSON 생성 (필터링용)"""
    
    nodes_df = pd.read_csv(os.path.join(data_dir, 'network_nodes.csv'))
    
    # AI Methods 리스트
    ai_methods = nodes_df['dominant_ai_method'].dropna().unique().tolist()
    ai_methods = [str(method) for method in ai_methods if str(method) != 'nan']
    
    # Design Tasks 리스트  
    design_tasks = nodes_df['dominant_design_task'].dropna().unique().tolist()
    design_tasks = [str(task) for task in design_tasks if str(task) != 'nan']
    
    # 커뮤니티 리스트
    communities = sorted(nodes_df['community'].dropna().unique().tolist())
    
    # 통계 정보
    stats = {
        "total_nodes": len(nodes_df),
        "total_edges": len(pd.read_csv(os.path.join(data_dir, 'network_edges.csv'))),
        "avg_degree": float(nodes_df['degree'].mean()),
        "network_density": 0.0082,  # 이전 계산 값
        "communities_count": len(communities)
    }
    
    metadata = {
        "ai_methods": ai_methods,
        "design_tasks": design_tasks, 
        "communities": communities,
        "statistics": stats,
        "colors": {
            'Traditional ML': '#2E8B57',
            'Deep Learning': '#4169E1', 
            'Generative AI': '#DC143C',
            'Exploratory Data Analysis': '#FF8C00',
            'Multiple': '#9370DB'
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 메타데이터 JSON 생성: {output_file}")
    return metadata

def main():
    """메인 실행 함수"""
    print("🔄 Cytoscape.js 데이터 변환 시작")
    print("=" * 50)
    
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'results', 'semantic_network_analysis', 'data')
    interactive_dir = os.path.join(base_dir, 'results', 'semantic_network_analysis', 'interactive', 'data')
    
    # 1. 네트워크 데이터 변환
    network_json_file = os.path.join(interactive_dir, 'network_data.json')
    network_data = convert_network_to_cytoscape_json(data_dir, network_json_file)
    
    # 2. 메타데이터 생성
    metadata_json_file = os.path.join(interactive_dir, 'metadata.json')
    metadata = create_metadata_json(data_dir, metadata_json_file)
    
    print(f"\n✅ 모든 JSON 데이터 변환 완료!")
    print(f"📁 저장 위치: {interactive_dir}")

if __name__ == "__main__":
    main()