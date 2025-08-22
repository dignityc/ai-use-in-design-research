#!/usr/bin/env python3
"""
개선된 인사이트 중심 NLP 분석 워크플로우
- 데이터 정규화
- 의미적 유사도 기반 시맨틱 네트워크  
- 스토리 기반 분석 및 시각화
"""

import pandas as pd
import numpy as np
import os
import re
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# 필수 라이브러리 체크 및 로드
try:
    from sentence_transformers import SentenceTransformer
    from keybert import KeyBERT
    from sklearn.metrics.pairwise import cosine_similarity
    import networkx as nx
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    plt.style.use('default')
except ImportError as e:
    print(f"⚠️  라이브러리 누락: {e}")
    print("가상환경에서 다음 명령어로 설치하세요:")
    print("pip install sentence-transformers keybert scikit-learn networkx matplotlib seaborn plotly")
    exit(1)

class DataNormalizer:
    """데이터 정규화 클래스"""
    
    def __init__(self):
        # AI Methods 정규화 룰
        self.ai_method_rules = {
            # Traditional ML 그룹
            r'.*traditional\s*ml.*': 'Traditional ML',
            r'.*machine\s*learning.*': 'Traditional ML', 
            r'.*svm.*': 'Traditional ML',
            r'.*random\s*forest.*': 'Traditional ML',
            r'.*xgboost.*': 'Traditional ML',
            r'.*bayesian.*': 'Traditional ML',
            r'.*exploratory\s*data\s*analysis.*': 'Traditional ML',
            r'.*shallow\s*models.*': 'Traditional ML',
            
            # Deep Learning 그룹
            r'.*deep\s*models.*': 'Deep Learning',
            r'.*deep\s*learning.*': 'Deep Learning', 
            r'.*cnn.*': 'Deep Learning',
            r'.*convolutional.*': 'Deep Learning',
            r'.*neural\s*network.*': 'Deep Learning',
            r'.*lstm.*': 'Deep Learning',
            r'.*transformer.*': 'Deep Learning',
            r'.*bert.*': 'Deep Learning',
            
            # Generative AI 그룹
            r'.*gen\s*ai.*': 'Generative AI',
            r'.*generative\s*ai.*': 'Generative AI',
            r'.*gan.*': 'Generative AI',
            r'.*stable\s*diffusion.*': 'Generative AI',
            r'.*llm.*': 'Generative AI',
            r'.*gpt.*': 'Generative AI',
            r'.*chatgpt.*': 'Generative AI',
            r'.*midjourney.*': 'Generative AI',
            
            # Reinforcement Learning 그룹
            r'.*reinforcement\s*learning.*': 'Reinforcement Learning',
            r'.*rl.*': 'Reinforcement Learning',
            r'.*q.learning.*': 'Reinforcement Learning',
        }
        
        # Design Tasks 정규화 룰
        self.design_task_rules = {
            r'.*discover.*': 'Discovery',
            r'.*define.*': 'Define', 
            r'.*develop.*': 'Develop',
            r'.*deliver.*': 'Delivery',
            r'.*evaluation.*': 'Delivery',
            r'.*testing.*': 'Delivery',
            r'.*validation.*': 'Delivery',
        }
    
    def normalize_ai_methods(self, text):
        """AI Methods 정규화"""
        if pd.isna(text):
            return 'Other'
            
        text_lower = str(text).lower()
        
        # 룰 기반 매칭
        for pattern, category in self.ai_method_rules.items():
            if re.search(pattern, text_lower):
                return category
        
        # Multiple 처리
        if 'multiple' in text_lower or ',' in text:
            return 'Hybrid'
            
        return 'Other'
    
    def normalize_design_tasks(self, text):
        """Design Tasks 정규화"""
        if pd.isna(text):
            return 'Other'
            
        text_lower = str(text).lower()
        
        # 룰 기반 매칭
        for pattern, category in self.design_task_rules.items():
            if re.search(pattern, text_lower):
                return category
        
        return 'Other'
    
    def normalize_data(self, df):
        """전체 데이터 정규화"""
        print("🔧 데이터 정규화 시작...")
        
        df_normalized = df.copy()
        
        # AI Methods 정규화
        df_normalized['AI_Method_Normalized'] = df['AI methods'].apply(self.normalize_ai_methods)
        
        # Design Tasks 정규화
        df_normalized['Design_Task_Normalized'] = df['Design Practice/Task'].apply(self.normalize_design_tasks)
        
        # 정규화 결과 리포트
        print("📊 AI Methods 정규화 결과:")
        ai_counts = df_normalized['AI_Method_Normalized'].value_counts()
        for method, count in ai_counts.items():
            print(f"   {method}: {count}편")
        
        print("\n📊 Design Tasks 정규화 결과:")
        task_counts = df_normalized['Design_Task_Normalized'].value_counts()
        for task, count in task_counts.items():
            print(f"   {task}: {count}편")
        
        return df_normalized

class SemanticNetworkBuilder:
    """의미적 유사도 기반 시맨틱 네트워크"""
    
    def __init__(self):
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.keyword_model = KeyBERT('all-MiniLM-L6-v2')
        
    def extract_all_keywords(self, abstracts, top_k=100):
        """모든 Abstract에서 키워드 추출"""
        print("🔑 전체 키워드 추출 중...")
        
        all_keywords = []
        for abstract in abstracts:
            try:
                keywords = self.keyword_model.extract_keywords(
                    abstract,
                    keyphrase_ngram_range=(1, 2),
                    stop_words='english',
                    top_k=10
                )
                all_keywords.extend([kw[0] for kw in keywords])
            except:
                continue
        
        # 빈도 기준 상위 키워드 선택
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, count in keyword_counts.most_common(top_k) if count >= 2]
        
        print(f"   추출된 상위 키워드: {len(top_keywords)}개")
        return top_keywords
    
    def build_semantic_network(self, keywords, ai_methods, similarity_threshold=0.7):
        """의미적 유사도 기반 네트워크 구축"""
        print("🕸️ 의미적 시맨틱 네트워크 구축 중...")
        
        # 키워드 임베딩 생성
        keyword_embeddings = self.sentence_model.encode(keywords)
        
        # 코사인 유사도 계산
        similarity_matrix = cosine_similarity(keyword_embeddings)
        
        # 네트워크 그래프 생성
        G = nx.Graph()
        
        # 노드 추가 (키워드별 AI Method 정보 포함)
        keyword_to_methods = defaultdict(set)
        for i, kw in enumerate(keywords):
            # 해당 키워드가 어떤 AI Method와 함께 나타나는지 추적 (간단화)
            G.add_node(kw, frequency=1)
        
        # 엣지 추가 (유사도 기준)
        edges_added = 0
        for i in range(len(keywords)):
            for j in range(i+1, len(keywords)):
                similarity = similarity_matrix[i][j]
                if similarity >= similarity_threshold:
                    G.add_edge(keywords[i], keywords[j], weight=similarity)
                    edges_added += 1
        
        print(f"✅ 네트워크 생성 완료: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지")
        
        return G

class StoryAnalyzer:
    """스토리 기반 분석"""
    
    def __init__(self, df_normalized):
        self.df = df_normalized
    
    def analyze_ai_evolution(self):
        """AI 방법론 진화 분석"""
        print("📈 AI 방법론 진화 트렌드 분석...")
        
        # 연도별 AI Method 분포 계산
        evolution_data = self.df.groupby(['Publication Year', 'AI_Method_Normalized']).size().unstack(fill_value=0)
        
        # 비중 계산
        evolution_pct = evolution_data.div(evolution_data.sum(axis=1), axis=0) * 100
        
        # 주요 변화점 식별
        insights = []
        for method in evolution_pct.columns:
            pct_2020 = evolution_pct.loc[2020, method] if 2020 in evolution_pct.index else 0
            pct_2024 = evolution_pct.loc[2024, method] if 2024 in evolution_pct.index else 0
            change = pct_2024 - pct_2020
            
            if abs(change) > 10:  # 10% 이상 변화
                direction = "증가" if change > 0 else "감소"
                insights.append(f"{method}: {pct_2020:.1f}% → {pct_2024:.1f}% ({direction})")
        
        print("🔍 주요 AI 방법론 변화:")
        for insight in insights:
            print(f"   {insight}")
        
        return evolution_data, evolution_pct, insights
    
    def analyze_topic_lifecycle(self, topic_assignments):
        """토픽 라이프사이클 분석"""
        print("🔄 토픽 라이프사이클 분석...")
        
        # 토픽별 연도별 논문 수 계산
        df_with_topics = self.df.copy()
        df_with_topics['Topic'] = topic_assignments
        
        topic_timeline = df_with_topics.groupby(['Publication Year', 'Topic']).size().unstack(fill_value=0)
        
        # 토픽별 트렌드 분석
        topic_insights = []
        for topic in topic_timeline.columns:
            if topic == -1:  # outlier topic 제외
                continue
                
            timeline = topic_timeline[topic]
            peak_year = timeline.idxmax()
            peak_count = timeline.max()
            
            # 성장/감소 패턴 분석
            if len(timeline) >= 3:
                recent_trend = timeline.iloc[-2:].mean() - timeline.iloc[:2].mean()
                trend_direction = "성장" if recent_trend > 0 else "감소"
                topic_insights.append(f"Topic {topic}: {peak_year}년 피크({peak_count}편), 최근 {trend_direction}")
        
        print("🔍 주요 토픽 변화:")
        for insight in topic_insights:
            print(f"   {insight}")
        
        return topic_timeline, topic_insights
    
    def identify_research_gaps(self):
        """연구 갭 식별 및 구체적 아이디어 제안"""
        print("🎯 연구 갭 분석 및 아이디어 제안...")
        
        # Method × Task 교차표
        crosstab = pd.crosstab(self.df['AI_Method_Normalized'], self.df['Design_Task_Normalized'])
        
        # 빈 조합 및 부족한 조합 식별
        gaps = []
        opportunities = []
        
        for method in crosstab.index:
            for task in crosstab.columns:
                count = crosstab.loc[method, task]
                if count == 0:
                    # 구체적 연구 아이디어 생성
                    idea = self._generate_research_idea(method, task)
                    gaps.append((method, task, idea))
                elif count <= 2:
                    idea = self._generate_research_idea(method, task)
                    opportunities.append((method, task, count, idea))
        
        print(f"🔍 완전히 빈 연구 영역: {len(gaps)}개")
        print("   주요 연구 기회:")
        for method, task, idea in gaps[:5]:  # 상위 5개만
            print(f"   • {method} × {task}: {idea}")
        
        print(f"\n🔍 연구 부족 영역: {len(opportunities)}개")
        print("   확장 가능한 연구:")
        for method, task, count, idea in opportunities[:5]:  # 상위 5개만
            print(f"   • {method} × {task} ({count}편): {idea}")
        
        return gaps, opportunities, crosstab
    
    def _generate_research_idea(self, method, task):
        """AI Method와 Design Task 조합에 대한 구체적 연구 아이디어 생성"""
        ideas_map = {
            ('Generative AI', 'Discovery'): "사용자 니즈 발견을 위한 LLM 기반 인터뷰 분석 시스템",
            ('Generative AI', 'Define'): "요구사항 명세서 자동 생성을 위한 ChatGPT 활용 연구",
            ('Generative AI', 'Develop'): "Stable Diffusion을 활용한 프로토타입 자동 생성 도구",
            ('Generative AI', 'Delivery'): "AI 생성 디자인의 사용성 평가 프레임워크",
            
            ('Deep Learning', 'Discovery'): "사용자 행동 패턴 발견을 위한 딥러닝 기반 로그 분석",
            ('Deep Learning', 'Define'): "CNN을 활용한 디자인 요구사항 자동 분류 시스템",
            ('Deep Learning', 'Develop'): "GAN 기반 개인화 UI 컴포넌트 생성 연구",
            ('Deep Learning', 'Delivery'): "딥러닝 기반 디자인 품질 자동 평가 모델",
            
            ('Traditional ML', 'Discovery'): "고객 리뷰 마이닝을 통한 잠재 니즈 발굴 연구",
            ('Traditional ML', 'Define'): "클러스터링 기반 사용자 페르소나 자동 정의",
            ('Traditional ML', 'Develop'): "의사결정트리를 활용한 개인화 인터페이스 설계",
            ('Traditional ML', 'Delivery'): "A/B 테스트 자동화를 위한 ML 기반 성과 예측",
            
            ('Reinforcement Learning', 'Discovery'): "RL 에이전트를 통한 사용자 탐색 행동 모델링",
            ('Reinforcement Learning', 'Define'): "강화학습 기반 최적 UX 플로우 정의",
            ('Reinforcement Learning', 'Develop'): "적응형 UI 레이아웃 최적화 RL 시스템",
            ('Reinforcement Learning', 'Delivery'): "RL 기반 개인화 추천 시스템 성능 평가",
        }
        
        return ideas_map.get((method, task), f"{method}을 활용한 {task} 단계 혁신 연구")

class ImprovedVisualizer:
    """개선된 시각화 클래스"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        
    def create_ai_evolution_chart(self, evolution_pct, insights):
        """AI 방법론 진화 차트 (간단한 Stacked Bar)"""
        print("📊 AI 방법론 진화 차트 생성...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Stacked Bar Chart
        evolution_pct.plot(kind='bar', stacked=True, ax=ax, colormap='Set3')
        
        ax.set_title('AI Methods Evolution in Design Research (2020-2025)', fontsize=16, pad=20)
        ax.set_xlabel('Publication Year', fontsize=12)
        ax.set_ylabel('Percentage of Papers (%)', fontsize=12)
        ax.legend(title='AI Methods', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 핵심 인사이트 텍스트 추가
        insight_text = "Key Changes:\n" + "\n".join(insights[:3])
        ax.text(0.02, 0.98, insight_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.xticks(rotation=0)
        plt.tight_layout()
        
        # 저장
        save_path = os.path.join(self.output_dir, 'visualizations', 'ai_evolution_story.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"💾 저장됨: {save_path}")
    
    def create_research_gap_matrix(self, crosstab):
        """연구 갭 매트릭스 (간단한 히트맵)"""
        print("🔥 연구 갭 매트릭스 생성...")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 히트맵 생성
        sns.heatmap(crosstab, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
        
        ax.set_title('Research Gap Matrix: AI Methods × Design Tasks', fontsize=16, pad=20)
        ax.set_xlabel('Design Tasks', fontsize=12)
        ax.set_ylabel('AI Methods', fontsize=12)
        
        # 빈 셀 강조 메시지
        empty_cells = (crosstab == 0).sum().sum()
        ax.text(0.02, 0.98, f"Empty Research Areas: {empty_cells}", 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        save_path = os.path.join(self.output_dir, 'visualizations', 'research_gap_matrix.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"💾 저장됨: {save_path}")
    
    def create_topic_lifecycle_chart(self, topic_timeline, topic_insights):
        """토픽 라이프사이클 차트"""
        print("🔄 토픽 라이프사이클 차트 생성...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 주요 토픽만 선택 (outlier 제외)
        main_topics = [col for col in topic_timeline.columns if col != -1][:6]  # 상위 6개 토픽
        
        for topic in main_topics:
            ax.plot(topic_timeline.index, topic_timeline[topic], 
                   marker='o', linewidth=2, label=f'Topic {topic}')
        
        ax.set_title('Topic Lifecycle: Research Trends Over Time', fontsize=16, pad=20)
        ax.set_xlabel('Publication Year', fontsize=12)
        ax.set_ylabel('Number of Papers', fontsize=12)
        ax.legend(title='Research Topics', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # 인사이트 추가
        insight_text = "Key Trends:\n" + "\n".join(topic_insights[:3])
        ax.text(0.02, 0.98, insight_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        save_path = os.path.join(self.output_dir, 'visualizations', 'topic_lifecycle.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"💾 저장됨: {save_path}")

class ImprovedNLPWorkflow:
    """개선된 NLP 워크플로우 메인 클래스"""
    
    def __init__(self, data_path=None):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if data_path is None:
            self.data_path = os.path.join(self.base_dir, 'input', 'Result_2.csv')
        else:
            self.data_path = data_path
            
        self.output_dir = os.path.join(self.base_dir, 'output', 'nlp_analysis_improved')
        
        # 출력 디렉토리 생성
        os.makedirs(os.path.join(self.output_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'visualizations'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'reports'), exist_ok=True)
        
        # 모듈 초기화
        self.normalizer = DataNormalizer()
        self.network_builder = SemanticNetworkBuilder()
        self.visualizer = ImprovedVisualizer(self.output_dir)
    
    def run_improved_analysis(self):
        """개선된 분석 파이프라인 실행"""
        print("🚀 개선된 인사이트 중심 NLP 분석 시작\n")
        
        try:
            # 1. 데이터 로딩
            print("📄 데이터 로딩...")
            df = pd.read_csv(self.data_path)
            print(f"   총 {len(df)}개 논문 로드")
            
            # 2. 데이터 정규화 
            df_normalized = self.normalizer.normalize_data(df)
            
            # 정규화된 데이터 저장
            normalized_path = os.path.join(self.output_dir, 'data', 'normalized_data.csv')
            df_normalized.to_csv(normalized_path, index=False)
            print(f"💾 정규화된 데이터 저장: {normalized_path}\n")
            
            # 3. 스토리 기반 분석
            analyzer = StoryAnalyzer(df_normalized)
            
            # AI 방법론 진화 분석
            evolution_data, evolution_pct, ai_insights = analyzer.analyze_ai_evolution()
            
            # 연구 갭 분석
            gaps, opportunities, crosstab = analyzer.identify_research_gaps()
            
            # 4. 시각화 생성
            self.visualizer.create_ai_evolution_chart(evolution_pct, ai_insights)
            self.visualizer.create_research_gap_matrix(crosstab)
            
            # 5. 시맨틱 네트워크 (시간이 오래 걸릴 수 있음)
            print("\n🕸️ 의미적 시맨틱 네트워크 구축...")
            abstracts = df_normalized['Abstract'].dropna().tolist()[:50]  # 처리 속도를 위해 50개로 제한
            
            keywords = self.network_builder.extract_all_keywords(abstracts, top_k=30)
            if len(keywords) > 5:  # 키워드가 충분히 추출된 경우만
                semantic_network = self.network_builder.build_semantic_network(
                    keywords, df_normalized['AI_Method_Normalized']
                )
                
                # 네트워크 저장
                import pickle
                network_path = os.path.join(self.output_dir, 'data', 'semantic_network_improved.pkl')
                with open(network_path, 'wb') as f:
                    pickle.dump(semantic_network, f)
                print(f"💾 시맨틱 네트워크 저장: {network_path}")
            
            # 6. 최종 인사이트 리포트 생성
            self.generate_final_report(ai_insights, gaps[:5], opportunities[:5])
            
            print("\n✅ 개선된 분석 완료!")
            print(f"📁 결과물 위치: {self.output_dir}")
            
            return {
                'normalized_data': df_normalized,
                'ai_insights': ai_insights,
                'research_gaps': gaps,
                'opportunities': opportunities
            }
            
        except Exception as e:
            print(f"❌ 분석 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_final_report(self, ai_insights, top_gaps, top_opportunities):
        """최종 인사이트 리포트 생성"""
        report_path = os.path.join(self.output_dir, 'reports', 'final_insights.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# AI Design Research: 5년 변화 스토리 & 연구 기회\n\n")
            
            f.write("## 🚀 주요 발견점\n\n")
            f.write("### 1. AI 방법론 진화 패턴\n")
            for insight in ai_insights:
                f.write(f"- **{insight}**\n")
            f.write("\n")
            
            f.write("### 2. 완전히 비어있는 연구 영역 (Top 5)\n")
            for method, task, idea in top_gaps:
                f.write(f"- **{method} × {task}**: {idea}\n")
            f.write("\n")
            
            f.write("### 3. 확장 가능한 연구 기회 (Top 5)\n")
            for method, task, count, idea in top_opportunities:
                f.write(f"- **{method} × {task}** ({count}편 기존): {idea}\n")
            f.write("\n")
            
            f.write("## 🎯 2025-2026 연구 방향 예측\n")
            f.write("1. **Generative AI 확산**: 특히 Discovery, Define 단계에서 급성장 예상\n")
            f.write("2. **하이브리드 접근법**: 여러 AI 기법 조합 연구 증가\n")
            f.write("3. **실무 적용 연구**: 개념 증명에서 실제 도구 개발로 전환\n\n")
            
            f.write("## 📊 생성된 시각화\n")
            f.write("- `ai_evolution_story.png`: AI 방법론 5년 변화 스토리\n")
            f.write("- `research_gap_matrix.png`: Method × Task 연구 갭 매트릭스\n")
            f.write("- `semantic_network_improved.pkl`: 의미적 키워드 네트워크\n\n")
            
            f.write("---\n")
            f.write("*2020-2025 AI Design Research Analysis*\n")
        
        print(f"📝 최종 리포트 생성: {report_path}")

def main():
    """메인 실행 함수"""
    workflow = ImprovedNLPWorkflow()
    results = workflow.run_improved_analysis()
    
    if results:
        print("\n🎉 인사이트 중심 분석이 완료되었습니다!")
        print("\n📊 주요 결과물:")
        print("   - AI 방법론 5년 변화 스토리")
        print("   - 연구 갭 매트릭스 및 구체적 기회")
        print("   - 의미적 시맨틱 네트워크")
        print("   - 2025-2026 연구 방향 예측")

if __name__ == "__main__":
    main()