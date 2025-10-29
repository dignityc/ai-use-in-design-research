#!/usr/bin/env python3
"""
토픽 모델링 중심 분석
- Abstract 기반 토픽 모델링
- 연도별 토픽 트렌드 분석
- 토픽과 AI Methods/Design Practice 관계 분석
"""

import pandas as pd
import numpy as np
import os
import re
import warnings
warnings.filterwarnings('ignore')

# 필수 라이브러리
try:
    import spacy
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    import matplotlib.pyplot as plt
    import seaborn as sns
    import umap
    plt.style.use('default')
    sns.set_palette("husl")
except ImportError as e:
    print(f"⚠️  라이브러리 누락: {e}")
    print("가상환경에서 실행하세요: source venv/bin/activate")
    exit(1)

class AbstractPreprocessor:
    """Abstract 텍스트 전처리 (도메인 정보 보존)"""
    
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """spaCy 모델 로드"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy 영어 모델 로드 완료")
        except OSError:
            print("❌ spaCy 영어 모델을 찾을 수 없습니다.")
            print("설치: python -m spacy download en_core_web_sm")
            exit(1)
    
    def preprocess_abstract(self, text):
        """단일 Abstract 전처리"""
        if pd.isna(text) or text == '':
            return ""
        
        # 기본 정제
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # 특수문자 제거
        text = re.sub(r'\d+', '', text)       # 숫자 제거
        text = re.sub(r'\s+', ' ', text)      # 다중 공백 정리
        
        # spaCy 처리
        doc = self.nlp(text)
        
        # 토큰 필터링
        tokens = []
        for token in doc:
            # 조건: 불용어 아님, 구두점 아님, 공백 아님, 2글자 초과, 주요 품사
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and
                len(token.lemma_) > 2 and  # 2글자 이하만 제거 (AI, UI 보존)
                token.pos_ in ['NOUN', 'ADJ', 'VERB']):
                tokens.append(token.lemma_)
        
        return ' '.join(tokens)
    
    def preprocess_abstracts(self, abstracts):
        """전체 Abstract 리스트 전처리"""
        print("🔧 Abstract 텍스트 전처리 중...")
        print("   - 도메인 특화 불용어 보존 (design, method, approach 등)")
        print("   - 2글자 이하만 제거 (AI, UI 같은 중요 용어 보존)")
        
        processed = []
        valid_indices = []
        
        for i, abstract in enumerate(abstracts):
            processed_text = self.preprocess_abstract(abstract)
            if len(processed_text.split()) >= 5:  # 최소 5단어 이상
                processed.append(processed_text)
                valid_indices.append(i)
        
        print(f"   ✅ {len(processed)}/{len(abstracts)}개 Abstract 전처리 완료")
        return processed, valid_indices

class TopicAnalyzer:
    """BERTopic 기반 토픽 모델링 및 분석"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.model = None
        self.topics = None
        self.probabilities = None
        
        # 출력 디렉토리 생성
        os.makedirs(os.path.join(output_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'visualizations'), exist_ok=True)
    
    def perform_topic_modeling(self, processed_abstracts, min_topic_size=3):
        """BERTopic 토픽 모델링 실행"""
        print("🧠 BERTopic 토픽 모델링 시작...")
        
        # Sentence Transformer 모델
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # UMAP 설정 (작은 데이터셋용)
        umap_model = umap.UMAP(
            n_neighbors=min(15, len(processed_abstracts)//3),
            n_components=5,
            min_dist=0.0,
            metric='cosine',
            random_state=42
        )
        
        # BERTopic 모델 설정
        self.model = BERTopic(
            embedding_model=sentence_model,
            umap_model=umap_model,
            min_topic_size=min_topic_size,
            nr_topics="auto",
            calculate_probabilities=True,
            verbose=True
        )
        
        # 토픽 모델링 실행
        self.topics, self.probabilities = self.model.fit_transform(processed_abstracts)
        
        # 토픽 정보 출력
        topic_info = self.model.get_topic_info()
        print(f"✅ {len(topic_info)-1}개 토픽 발견 (outlier 제외)")
        
        return self.topics, topic_info
    
    def create_topic_labels(self, topic_info):
        """토픽별 의미있는 라벨 생성"""
        print("🏷️ 토픽 라벨링 중...")
        
        topic_labels = {}
        
        for _, row in topic_info.iterrows():
            topic_id = row['Topic']
            if topic_id == -1:  # outlier topic
                topic_labels[topic_id] = "Outlier"
                continue
            
            # BERTopic에서 직접 키워드 가져오기
            topic_words = self.model.get_topic(topic_id)
            if topic_words:
                keywords = [word for word, _ in topic_words[:3]]  # 상위 3개 키워드
                label = " + ".join([kw.title() for kw in keywords])
                topic_labels[topic_id] = label
            else:
                topic_labels[topic_id] = f"Topic {topic_id}"
        
        print("📋 생성된 토픽 라벨:")
        for topic_id, label in topic_labels.items():
            if topic_id != -1:
                count = topic_info[topic_info['Topic'] == topic_id]['Count'].iloc[0]
                print(f"   Topic {topic_id}: {label} ({count}편)")
        
        return topic_labels
    
    def analyze_topic_trends(self, df_with_topics, topic_labels):
        """연도별 토픽 트렌드 분석"""
        print("📈 연도별 토픽 트렌드 분석...")
        
        # 연도별 토픽 분포 계산
        topic_timeline = df_with_topics.groupby(['Publication Year', 'Topic']).size().unstack(fill_value=0)
        
        # outlier topic 제거
        if -1 in topic_timeline.columns:
            topic_timeline = topic_timeline.drop(columns=[-1])
        
        # 시각화
        plt.figure(figsize=(14, 8))
        
        colors = plt.cm.Set1(np.linspace(0, 1, len(topic_timeline.columns)))
        
        for i, topic in enumerate(topic_timeline.columns):
            label = topic_labels.get(topic, f"Topic {topic}")
            plt.plot(topic_timeline.index, topic_timeline[topic], 
                    marker='o', linewidth=2, markersize=6, 
                    color=colors[i], label=label)
        
        plt.title('Research Topic Trends Over Time (2020-2025)', fontsize=16, pad=20)
        plt.xlabel('Publication Year', fontsize=12)
        plt.ylabel('Number of Papers', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # 트렌드 인사이트 추가
        insights = []
        for topic in topic_timeline.columns:
            timeline = topic_timeline[topic]
            if len(timeline) >= 3:
                peak_year = timeline.idxmax()
                peak_count = timeline.max()
                if peak_count >= 3:  # 의미있는 크기의 토픽만
                    recent_trend = timeline.iloc[-2:].mean() - timeline.iloc[:2].mean()
                    trend_dir = "성장" if recent_trend > 0 else "감소"
                    label = topic_labels.get(topic, f"Topic {topic}")
                    insights.append(f"{label}: {peak_year}년 피크({peak_count}편), 최근 {trend_dir}")
        
        # 인사이트 텍스트 박스
        if insights:
            insight_text = "Key Trends:\n" + "\n".join(insights[:3])
            plt.text(0.02, 0.98, insight_text, transform=plt.gca().transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        save_path = os.path.join(self.output_dir, 'visualizations', 'topic_trends_timeline.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"💾 토픽 트렌드 차트 저장: {save_path}")
        
        return topic_timeline, insights
    
    def analyze_topic_ai_methods(self, df_with_topics, topic_labels):
        """토픽 × AI Methods 관계 분석"""
        print("🤖 토픽 × AI Methods 관계 분석...")
        
        # 교차표 생성
        crosstab = pd.crosstab(df_with_topics['Topic'], df_with_topics['AI_Method_Normalized'])
        
        # outlier topic 제거
        if -1 in crosstab.index:
            crosstab = crosstab.drop(index=[-1])
        
        # 토픽 라벨로 인덱스 변경
        crosstab.index = [topic_labels.get(topic, f"Topic {topic}") for topic in crosstab.index]
        
        # 히트맵 시각화
        plt.figure(figsize=(10, 8))
        
        sns.heatmap(crosstab, annot=True, fmt='d', cmap='Blues', 
                   cbar_kws={'label': 'Number of Papers'})
        
        plt.title('Research Topics × AI Methods Matrix', fontsize=16, pad=20)
        plt.xlabel('AI Methods', fontsize=12)
        plt.ylabel('Research Topics', fontsize=12)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        
        # 주요 패턴 분석
        patterns = []
        for topic in crosstab.index:
            dominant_method = crosstab.loc[topic].idxmax()
            count = crosstab.loc[topic].max()
            if count >= 2:  # 의미있는 패턴만
                patterns.append(f"{topic}: {dominant_method} 중심({count}편)")
        
        # 패턴 텍스트 박스
        if patterns:
            pattern_text = "Key Patterns:\n" + "\n".join(patterns[:4])
            plt.text(1.02, 0.98, pattern_text, transform=plt.gca().transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        save_path = os.path.join(self.output_dir, 'visualizations', 'topic_ai_methods_matrix.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"💾 토픽-AI Methods 매트릭스 저장: {save_path}")
        
        return crosstab, patterns
    
    def analyze_topic_design_practice(self, df_with_topics, topic_labels):
        """토픽 × Design Practice 관계 분석"""
        print("🎨 토픽 × Design Practice 관계 분석...")
        
        # 교차표 생성
        crosstab = pd.crosstab(df_with_topics['Topic'], df_with_topics['Design_Task_Normalized'])
        
        # outlier topic 제거
        if -1 in crosstab.index:
            crosstab = crosstab.drop(index=[-1])
        
        # 토픽 라벨로 인덱스 변경
        crosstab.index = [topic_labels.get(topic, f"Topic {topic}") for topic in crosstab.index]
        
        # 히트맵 시각화
        plt.figure(figsize=(8, 8))
        
        sns.heatmap(crosstab, annot=True, fmt='d', cmap='Greens',
                   cbar_kws={'label': 'Number of Papers'})
        
        plt.title('Research Topics × Design Practice Matrix', fontsize=16, pad=20)
        plt.xlabel('Design Practice', fontsize=12)
        plt.ylabel('Research Topics', fontsize=12)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        
        # 주요 패턴 분석
        patterns = []
        for topic in crosstab.index:
            dominant_practice = crosstab.loc[topic].idxmax()
            count = crosstab.loc[topic].max()
            if count >= 2:
                patterns.append(f"{topic}: {dominant_practice} 중심({count}편)")
        
        # 패턴 텍스트 박스
        if patterns:
            pattern_text = "Key Patterns:\n" + "\n".join(patterns[:4])
            plt.text(1.02, 0.98, pattern_text, transform=plt.gca().transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        
        # 저장
        save_path = os.path.join(self.output_dir, 'visualizations', 'topic_design_practice_matrix.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"💾 토픽-Design Practice 매트릭스 저장: {save_path}")
        
        return crosstab, patterns

class TopicModelingWorkflow:
    """토픽 모델링 워크플로우 메인 클래스"""
    
    def __init__(self, data_path=None):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if data_path is None:
            # 기존 정규화 데이터 사용
            self.data_path = os.path.join(self.base_dir, '../results', 'nlp_analysis_improved', 'data', 'normalized_data.csv')
        else:
            self.data_path = data_path
        
        self.output_dir = os.path.join(self.base_dir, '../results', 'topic_modeling_analysis')
        
        # 모듈 초기화
        self.preprocessor = AbstractPreprocessor()
        self.analyzer = TopicAnalyzer(self.output_dir)
    
    def run_topic_analysis(self):
        """전체 토픽 모델링 분석 실행"""
        print("🚀 토픽 모델링 중심 분석 시작\n")
        
        try:
            # 1. 데이터 로딩
            print("📄 정규화된 데이터 로딩...")
            if not os.path.exists(self.data_path):
                print("❌ 정규화된 데이터를 찾을 수 없습니다.")
                print("먼저 improved_nlp_analysis.py를 실행하세요.")
                return None
            
            df = pd.read_csv(self.data_path)
            print(f"   총 {len(df)}개 논문 로드")
            
            # 2. Abstract 전처리
            abstracts = df['Abstract'].tolist()
            processed_abstracts, valid_indices = self.preprocessor.preprocess_abstracts(abstracts)
            
            if len(processed_abstracts) < 10:
                print("❌ 처리 가능한 Abstract가 너무 적습니다.")
                return None
            
            # 유효한 논문만 필터링
            df_valid = df.iloc[valid_indices].copy()
            
            # 3. 토픽 모델링 실행
            topics, topic_info = self.analyzer.perform_topic_modeling(processed_abstracts)
            
            # 토픽 정보를 데이터프레임에 추가
            df_valid['Topic'] = topics
            df_valid['Processed_Abstract'] = processed_abstracts
            
            # 4. 토픽 라벨링
            topic_labels = self.analyzer.create_topic_labels(topic_info)
            
            # 5. 연도별 토픽 트렌드 분석
            topic_timeline, trend_insights = self.analyzer.analyze_topic_trends(df_valid, topic_labels)
            
            # 6. 토픽 × AI Methods 관계 분석
            ai_crosstab, ai_patterns = self.analyzer.analyze_topic_ai_methods(df_valid, topic_labels)
            
            # 7. 토픽 × Design Practice 관계 분석
            practice_crosstab, practice_patterns = self.analyzer.analyze_topic_design_practice(df_valid, topic_labels)
            
            # 8. 결과 저장
            self.save_results(df_valid, topic_info, topic_labels, 
                            trend_insights, ai_patterns, practice_patterns)
            
            print("\n✅ 토픽 모델링 분석 완료!")
            print(f"📁 결과물 위치: {self.output_dir}")
            
            return {
                'df_with_topics': df_valid,
                'topic_info': topic_info,
                'topic_labels': topic_labels,
                'trends': trend_insights,
                'ai_patterns': ai_patterns,
                'practice_patterns': practice_patterns
            }
            
        except Exception as e:
            print(f"❌ 분석 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_results(self, df_with_topics, topic_info, topic_labels, 
                    trend_insights, ai_patterns, practice_patterns):
        """분석 결과 저장"""
        
        # 데이터 저장
        data_dir = os.path.join(self.output_dir, 'data')
        
        # 토픽이 배정된 논문 데이터
        df_with_topics.to_csv(os.path.join(data_dir, 'papers_with_topics.csv'), index=False)
        
        # 토픽 정보
        topic_info.to_csv(os.path.join(data_dir, 'topic_info.csv'), index=False)
        
        # 토픽 라벨
        import json
        with open(os.path.join(data_dir, 'topic_labels.json'), 'w', encoding='utf-8') as f:
            json.dump(topic_labels, f, ensure_ascii=False, indent=2)
        
        # 종합 리포트 생성
        report_path = os.path.join(self.output_dir, 'topic_analysis_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 토픽 모델링 분석 리포트\n\n")
            
            f.write("## 📊 발견된 토픽들\n")
            for topic_id, label in topic_labels.items():
                if topic_id != -1:
                    count = topic_info[topic_info['Topic'] == topic_id]['Count'].iloc[0]
                    f.write(f"- **{label}**: {count}편 논문\n")
            f.write("\n")
            
            f.write("## 📈 연도별 토픽 트렌드\n")
            for insight in trend_insights[:5]:
                f.write(f"- {insight}\n")
            f.write("\n")
            
            f.write("## 🤖 토픽별 주요 AI 기법\n")
            for pattern in ai_patterns[:5]:
                f.write(f"- {pattern}\n")
            f.write("\n")
            
            f.write("## 🎨 토픽별 주요 디자인 단계\n")
            for pattern in practice_patterns[:5]:
                f.write(f"- {pattern}\n")
            f.write("\n")
            
            f.write("## 📁 생성된 시각화\n")
            f.write("- `topic_trends_timeline.png`: 연도별 토픽 관심도 변화\n")
            f.write("- `topic_ai_methods_matrix.png`: 토픽별 AI 기법 분포\n")
            f.write("- `topic_design_practice_matrix.png`: 토픽별 디자인 단계 분포\n")
        
        print(f"📝 종합 리포트 생성: {report_path}")

def main():
    """메인 실행 함수"""
    workflow = TopicModelingWorkflow()
    results = workflow.run_topic_analysis()
    
    if results:
        print("\n🎉 토픽 모델링 분석이 완료되었습니다!")
        print("\n📊 주요 결과:")
        print("   - 연구자들의 연도별 관심 토픽 변화")
        print("   - 토픽별 주요 AI 기법 및 디자인 단계")
        print("   - 토픽 라이프사이클 시각화")

if __name__ == "__main__":
    main()