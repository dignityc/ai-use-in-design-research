#!/usr/bin/env python3
"""
Abstract NLP 분석 + 타임라인 시각화 통합 워크플로우
"""

import pandas as pd
import numpy as np
import os
import sys
import argparse
import warnings
from pathlib import Path

# NLP & ML 라이브러리
try:
    import spacy
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    from keybert import KeyBERT
    from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
    from sklearn.decomposition import LatentDirichletAllocation
    import umap
    import networkx as nx
except ImportError as e:
    print(f"⚠️  필요한 라이브러리가 설치되지 않았습니다: {e}")
    print("다음 명령어로 설치하세요:")
    print("pip install bertopic sentence-transformers keybert spacy umap-learn networkx")
    print("python -m spacy download en_core_web_sm")
    sys.exit(1)

# 시각화 라이브러리
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.style.use('seaborn-v0_8')
except ImportError as e:
    print(f"⚠️  시각화 라이브러리가 설치되지 않았습니다: {e}")
    print("pip install plotly matplotlib seaborn")
    sys.exit(1)

warnings.filterwarnings('ignore')

class DataPreprocessor:
    """데이터 로딩 및 전처리"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.nlp = None
        self._load_nlp_model()
        
        # Domain-specific stopwords for design research
        self.domain_stopwords = {
            'design', 'method', 'approach', 'model', 'paper', 'study', 'research', 
            'propose', 'present', 'develop', 'system', 'result', 'show', 'based',
            'analysis', 'framework', 'algorithm', 'technique', 'process', 'data',
            'user', 'product', 'application', 'performance', 'evaluation', 'experiment'
        }
    
    def _load_nlp_model(self):
        """spaCy 모델 로드"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy 영어 모델 로드 완료")
        except OSError:
            print("❌ spaCy 영어 모델을 찾을 수 없습니다.")
            print("다음 명령어로 설치하세요: python -m spacy download en_core_web_sm")
            sys.exit(1)
    
    def load_data(self):
        """Result_2.csv 데이터 로드"""
        print("📄 데이터 로딩 중...")
        df = pd.read_csv(self.data_path)
        
        # 필요한 컬럼 확인
        required_cols = ['Article Title', 'Publication Year', 'Abstract', 'AI methods', 'Design Practice/Task']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_cols}")
        
        print(f"   총 {len(df)}개 논문 로드 완료")
        print(f"   연도 범위: {df['Publication Year'].min()}-{df['Publication Year'].max()}")
        return df
    
    def preprocess_text(self, text):
        """텍스트 전처리 (소문자화, 불용어 제거, 표제어 추출)"""
        if pd.isna(text) or text == '':
            return ""
        
        # spaCy로 처리
        doc = self.nlp(str(text).lower())
        
        # 표제어 추출, 불용어 제거, 짧은 토큰 제거, domain stopwords 제거
        tokens = [
            token.lemma_ for token in doc 
            if not token.is_stop 
            and not token.is_punct 
            and not token.is_space
            and len(token.lemma_) > 2
            and token.lemma_ not in self.domain_stopwords
            and token.pos_ in ['NOUN', 'ADJ', 'VERB']  # 주요 품사만
        ]
        
        return ' '.join(tokens)
    
    def preprocess_data(self, df):
        """전체 데이터 전처리"""
        print("🔧 텍스트 전처리 중...")
        
        # Abstract 전처리
        df['processed_abstract'] = df['Abstract'].apply(self.preprocess_text)
        
        # 빈 abstract 제거
        df = df[df['processed_abstract'].str.len() > 10].copy()
        
        # AI methods 정규화
        df['AI methods'] = df['AI methods'].fillna('Not specified')
        
        # 연도별 분포 확인
        print("📊 연도별 논문 수:")
        year_counts = df['Publication Year'].value_counts().sort_index()
        for year, count in year_counts.items():
            print(f"   {year}: {count}편")
        
        # 전처리된 데이터 저장
        output_path = os.path.join(os.path.dirname(self.data_path), '..', 'output', 'nlp_analysis', 'data', 'processed_abstracts.csv')
        df.to_csv(output_path, index=False)
        print(f"💾 전처리된 데이터 저장: {output_path}")
        
        return df

class TopicModeling:
    """BERTopic을 이용한 토픽 모델링"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.topic_model = None
        
    def create_topic_model(self, abstracts, min_topic_size=3):
        """BERTopic 모델 생성 및 학습"""
        print("🧠 BERTopic 토픽 모델링 시작...")
        
        # UMAP과 HDBSCAN 파라미터 설정 (작은 데이터셋에 맞게)
        umap_model = umap.UMAP(
            n_neighbors=15, 
            n_components=5, 
            min_dist=0.0, 
            metric='cosine',
            random_state=42
        )
        
        # BERTopic 모델 설정
        self.topic_model = BERTopic(
            embedding_model=self.sentence_model,
            umap_model=umap_model,
            min_topic_size=min_topic_size,
            nr_topics="auto",
            calculate_probabilities=True,
            verbose=True
        )
        
        # 토픽 모델링 실행
        topics, probs = self.topic_model.fit_transform(abstracts)
        
        print(f"✅ {len(self.topic_model.get_topic_info())} 개 토픽 발견")
        
        return topics, probs
    
    def analyze_topics_over_time(self, abstracts, years, topics):
        """연도별 토픽 진화 분석"""
        print("📈 연도별 토픽 진화 분석...")
        
        # timestamps 형식으로 변환
        timestamps = [f"{year}-01-01" for year in years]
        
        try:
            topics_over_time = self.topic_model.topics_over_time(
                abstracts, 
                topics, 
                timestamps,
                nr_bins=len(set(years))
            )
            
            # 결과 저장
            topics_over_time.to_csv(
                os.path.join(self.output_dir, 'data', 'topic_evolution.csv'),
                index=False
            )
            
            return topics_over_time
        except Exception as e:
            print(f"⚠️  연도별 토픽 분석 중 오류: {e}")
            return None
    
    def save_topic_info(self):
        """토픽 정보 저장"""
        if self.topic_model:
            topic_info = self.topic_model.get_topic_info()
            topic_info.to_csv(
                os.path.join(self.output_dir, 'data', 'topic_info.csv'),
                index=False
            )
            
            # 각 토픽의 상위 키워드 저장
            topics_dict = {}
            for topic_id in topic_info['Topic']:
                if topic_id != -1:  # outlier topic 제외
                    topic_words = self.topic_model.get_topic(topic_id)
                    topics_dict[f"Topic_{topic_id}"] = [word for word, _ in topic_words[:10]]
            
            # 토픽 키워드를 JSON으로 저장
            import json
            with open(os.path.join(self.output_dir, 'data', 'topic_keywords.json'), 'w') as f:
                json.dump(topics_dict, f, indent=2)
            
            print("💾 토픽 정보 저장 완료")

class SemanticAnalysis:
    """키워드 분석 및 시맨틱 네트워크"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.keyword_model = KeyBERT('all-MiniLM-L6-v2')
        
    def extract_keywords(self, abstracts, top_k=10):
        """KeyBERT를 이용한 키워드 추출"""
        print("🔑 키워드 추출 중...")
        
        all_keywords = []
        for i, abstract in enumerate(abstracts):
            try:
                keywords = self.keyword_model.extract_keywords(
                    abstract, 
                    keyphrase_ngram_range=(1, 2),
                    stop_words='english',
                    top_k=top_k
                )
                all_keywords.append([kw[0] for kw in keywords])
            except:
                all_keywords.append([])
                
        return all_keywords
    
    def build_cooccurrence_network(self, keyword_lists, ai_methods):
        """키워드 공출현 네트워크 구축"""
        print("🕸️ 키워드 공출현 네트워크 구축...")
        
        # 공출현 매트릭스 생성
        from collections import defaultdict, Counter
        cooccurrence = defaultdict(int)
        keyword_counts = Counter()
        keyword_to_methods = defaultdict(set)
        
        for keywords, method in zip(keyword_lists, ai_methods):
            # 키워드 빈도 계산
            for kw in keywords:
                keyword_counts[kw] += 1
                keyword_to_methods[kw].add(method)
            
            # 공출현 계산
            for i, kw1 in enumerate(keywords):
                for kw2 in keywords[i+1:]:
                    pair = tuple(sorted([kw1, kw2]))
                    cooccurrence[pair] += 1
        
        # NetworkX 그래프 생성
        G = nx.Graph()
        
        # 노드 추가 (상위 키워드만)
        top_keywords = [kw for kw, count in keyword_counts.most_common(50)]
        for kw in top_keywords:
            G.add_node(kw, 
                      frequency=keyword_counts[kw],
                      methods=list(keyword_to_methods[kw]))
        
        # 엣지 추가 (공출현 빈도가 2 이상인 것만)
        for (kw1, kw2), freq in cooccurrence.items():
            if freq >= 2 and kw1 in top_keywords and kw2 in top_keywords:
                G.add_edge(kw1, kw2, weight=freq)
        
        # 네트워크 저장
        import pickle
        with open(os.path.join(self.output_dir, 'models', 'semantic_network.pkl'), 'wb') as f:
            pickle.dump(G, f)
            
        print(f"✅ 네트워크 생성 완료: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지")
        
        return G

class ResearchLandscape:
    """임베딩 기반 연구 지형도"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def create_embedding_landscape(self, abstracts, df):
        """Abstract 임베딩 및 UMAP 차원축소"""
        print("🗺️ 연구 지형도 생성 중...")
        
        # Abstract 임베딩 생성
        embeddings = self.sentence_model.encode(abstracts, show_progress_bar=True)
        
        # UMAP으로 2D 축소
        reducer = umap.UMAP(
            n_neighbors=15,
            min_dist=0.1,
            n_components=2,
            metric='cosine',
            random_state=42
        )
        
        embedding_2d = reducer.fit_transform(embeddings)
        
        # 결과를 DataFrame에 추가
        df_viz = df.copy()
        df_viz['x'] = embedding_2d[:, 0]
        df_viz['y'] = embedding_2d[:, 1]
        
        # 임베딩 저장
        import pickle
        with open(os.path.join(self.output_dir, 'models', 'embeddings.pkl'), 'wb') as f:
            pickle.dump({
                'embeddings': embeddings,
                'embedding_2d': embedding_2d,
                'reducer': reducer
            }, f)
        
        # 시각화 데이터 저장
        df_viz.to_csv(
            os.path.join(self.output_dir, 'data', 'research_landscape.csv'),
            index=False
        )
        
        print("💾 연구 지형도 데이터 저장 완료")
        
        return df_viz

class TimelineVisualizations:
    """타임라인 시각화 생성"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.viz_dir = os.path.join(output_dir, 'visualizations')
    
    def create_method_timeline(self, df):
        """AI Method 연도별 변화 시각화"""
        print("📊 AI Method 타임라인 생성...")
        
        # 연도별 AI Method 분포 계산
        method_timeline = df.groupby(['Publication Year', 'AI methods']).size().unstack(fill_value=0)
        
        # Stacked Area Chart 생성
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set3
        for i, method in enumerate(method_timeline.columns):
            fig.add_trace(go.Scatter(
                x=method_timeline.index,
                y=method_timeline[method],
                mode='lines',
                stackgroup='one',
                name=method,
                line=dict(color=colors[i % len(colors)])
            ))
        
        fig.update_layout(
            title="AI Methods Over Time (Stacked Area)",
            xaxis_title="Publication Year",
            yaxis_title="Number of Papers",
            hovermode='x unified',
            width=1000,
            height=600
        )
        
        # HTML로 저장
        fig.write_html(os.path.join(self.viz_dir, 'method_timeline.html'))
        
        return fig
    
    def create_heatmap(self, df):
        """Year × Task × Method 히트맵"""
        print("🔥 Year × Task × Method 히트맵 생성...")
        
        # 피봇 테이블 생성
        heatmap_data = df.groupby(['Publication Year', 'Design Practice/Task', 'AI methods']).size().reset_index(name='count')
        
        # Plotly 히트맵
        fig = px.density_heatmap(
            heatmap_data,
            x='Publication Year',
            y='Design Practice/Task',
            z='count',
            color_continuous_scale='Viridis',
            title='Research Patterns: Year × Task × Method Intensity'
        )
        
        fig.update_layout(width=1000, height=600)
        fig.write_html(os.path.join(self.viz_dir, 'research_heatmap.html'))
        
        return fig

class GapAnalysis:
    """갭 분석 및 인사이트 생성"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.reports_dir = os.path.join(output_dir, 'reports')
    
    def analyze_gaps(self, df):
        """연구 갭 분석"""
        print("🔍 연구 갭 분석 중...")
        
        # AI Method × Design Task 교차표
        crosstab = pd.crosstab(df['AI methods'], df['Design Practice/Task'], margins=True)
        
        # 빈도가 낮은 조합 찾기
        gaps = []
        for method in crosstab.index[:-1]:  # 'All' 제외
            for task in crosstab.columns[:-1]:  # 'All' 제외
                count = crosstab.loc[method, task]
                if count == 0:
                    gaps.append((method, task, count, 'Empty'))
                elif count <= 2:
                    gaps.append((method, task, count, 'Low'))
        
        # 갭 분석 결과를 DataFrame으로
        gap_df = pd.DataFrame(gaps, columns=['AI Method', 'Design Task', 'Count', 'Gap Type'])
        gap_df.to_csv(os.path.join(self.output_dir, 'data', 'research_gaps.csv'), index=False)
        
        # 인사이트 리포트 생성
        self.generate_insights_report(df, crosstab, gap_df)
        
        return gap_df
    
    def generate_insights_report(self, df, crosstab, gap_df):
        """인사이트 리포트 생성"""
        report_path = os.path.join(self.reports_dir, 'research_insights.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# AI in Design Research: 분석 인사이트 리포트\n\n")
            
            # 기본 통계
            f.write("## 📊 기본 통계\n")
            f.write(f"- 총 논문 수: {len(df)}편\n")
            f.write(f"- 연도 범위: {df['Publication Year'].min()}-{df['Publication Year'].max()}\n")
            f.write(f"- 주요 AI 방법론: {df['AI methods'].value_counts().index[0]}\n")
            f.write(f"- 주요 디자인 태스크: {df['Design Practice/Task'].value_counts().index[0]}\n\n")
            
            # 연도별 트렌드
            f.write("## 📈 연도별 트렌드\n")
            year_counts = df['Publication Year'].value_counts().sort_index()
            f.write("| 연도 | 논문 수 |\n|------|--------|\n")
            for year, count in year_counts.items():
                f.write(f"| {year} | {count} |\n")
            f.write("\n")
            
            # 연구 갭
            f.write("## 🔍 연구 갭 분석\n")
            empty_gaps = gap_df[gap_df['Gap Type'] == 'Empty']
            f.write(f"### 완전히 빈 연구 영역 ({len(empty_gaps)}개)\n")
            for _, gap in empty_gaps.head(10).iterrows():
                f.write(f"- **{gap['AI Method']}** × **{gap['Design Task']}**\n")
            f.write("\n")
            
            low_gaps = gap_df[gap_df['Gap Type'] == 'Low']
            f.write(f"### 연구가 부족한 영역 ({len(low_gaps)}개)\n")
            for _, gap in low_gaps.head(10).iterrows():
                f.write(f"- **{gap['AI Method']}** × **{gap['Design Task']}** ({gap['Count']}편)\n")
            f.write("\n")
            
            # 향후 연구 방향
            f.write("## 🚀 향후 연구 방향 제안\n")
            f.write("1. **생성형 AI + 생리학적 데이터**: 감정 기반 디자인 자동화\n")
            f.write("2. **강화학습 + 서비스 디자인**: 적응형 사용자 경험 최적화\n")
            f.write("3. **멀티모달 AI + 지속가능성**: 환경 친화적 디자인 솔루션\n\n")
        
        print(f"📝 인사이트 리포트 생성: {report_path}")

class NLPAnalysisWorkflow:
    """메인 워크플로우 클래스"""
    
    def __init__(self, data_path=None):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if data_path is None:
            self.data_path = os.path.join(self.base_dir, 'input', 'Result_2.csv')
        else:
            self.data_path = data_path
            
        self.output_dir = os.path.join(self.base_dir, 'output', 'nlp_analysis')
        
        # 각 모듈 초기화
        self.preprocessor = DataPreprocessor(self.data_path)
        self.topic_modeling = TopicModeling(self.output_dir)
        self.semantic_analysis = SemanticAnalysis(self.output_dir)
        self.landscape = ResearchLandscape(self.output_dir)
        self.visualizations = TimelineVisualizations(self.output_dir)
        self.gap_analysis = GapAnalysis(self.output_dir)
        
    def run_full_analysis(self):
        """전체 분석 파이프라인 실행"""
        print("🚀 Abstract NLP 분석 + 타임라인 시각화 워크플로우 시작\n")
        
        try:
            # 1. 데이터 로딩 및 전처리
            df = self.preprocessor.load_data()
            df_processed = self.preprocessor.preprocess_data(df)
            
            # 2. 토픽 모델링
            abstracts = df_processed['processed_abstract'].tolist()
            topics, probs = self.topic_modeling.create_topic_model(abstracts)
            
            # 토픽 정보 저장
            self.topic_modeling.save_topic_info()
            
            # 연도별 토픽 진화
            topics_over_time = self.topic_modeling.analyze_topics_over_time(
                abstracts, df_processed['Publication Year'], topics
            )
            
            # 3. 키워드 분석
            keyword_lists = self.semantic_analysis.extract_keywords(abstracts)
            semantic_network = self.semantic_analysis.build_cooccurrence_network(
                keyword_lists, df_processed['AI methods']
            )
            
            # 4. 연구 지형도 생성
            landscape_df = self.landscape.create_embedding_landscape(abstracts, df_processed)
            
            # 5. 타임라인 시각화
            method_timeline = self.visualizations.create_method_timeline(df_processed)
            heatmap = self.visualizations.create_heatmap(df_processed)
            
            # 6. 갭 분석
            gaps = self.gap_analysis.analyze_gaps(df_processed)
            
            print("\n✅ 전체 분석 완료!")
            print(f"📁 결과 파일은 다음 위치에 저장되었습니다: {self.output_dir}")
            
            return {
                'processed_data': df_processed,
                'topics': topics,
                'keyword_lists': keyword_lists,
                'semantic_network': semantic_network,
                'landscape_data': landscape_df,
                'gaps': gaps
            }
            
        except Exception as e:
            print(f"❌ 분석 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_step(self, step_name):
        """특정 단계만 실행"""
        print(f"🔧 {step_name} 단계 실행 중...")
        
        if step_name == 'preprocess':
            df = self.preprocessor.load_data()
            return self.preprocessor.preprocess_data(df)
        elif step_name == 'topic_modeling':
            # 전처리된 데이터 로드 필요
            pass
        # 다른 단계들도 구현 가능
        
        print(f"⚠️  알 수 없는 단계: {step_name}")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Abstract NLP 분석 워크플로우')
    parser.add_argument('--data', type=str, help='데이터 파일 경로 (기본: input/Result_2.csv)')
    parser.add_argument('--step', type=str, help='특정 단계만 실행 (preprocess, topic_modeling, etc.)')
    
    args = parser.parse_args()
    
    # 워크플로우 초기화 및 실행
    workflow = NLPAnalysisWorkflow(args.data)
    
    if args.step:
        workflow.run_step(args.step)
    else:
        results = workflow.run_full_analysis()
        
        if results:
            print("\n🎉 분석이 성공적으로 완료되었습니다!")
            print("📊 생성된 주요 결과물:")
            print("   - 토픽 모델링 결과")
            print("   - 키워드 공출현 네트워크")
            print("   - 연구 지형도 (임베딩 기반)")
            print("   - AI 방법론 타임라인")
            print("   - 연구 갭 분석 리포트")

if __name__ == "__main__":
    main()