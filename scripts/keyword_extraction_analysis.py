#!/usr/bin/env python3
"""
키워드 추출 및 분석 시스템
- TF-IDF 기반 통계적 키워드 추출
- KeyBERT 기반 의미적 키워드 추출
- 도메인 특화 키워드 필터링 및 정규화
"""

import pandas as pd
import numpy as np
import os
import re
import warnings
warnings.filterwarnings('ignore')

from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set

try:
    import spacy
    from keybert import KeyBERT
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.style.use('default')
    sns.set_palette("husl")
except ImportError as e:
    print(f"⚠️  라이브러리 누락: {e}")
    print("필요한 라이브러리: keybert sentence-transformers scikit-learn")
    exit(1)

class KeywordExtractor:
    """다중 방법론 키워드 추출기"""
    
    def __init__(self):
        self.nlp = None
        self.keybert_model = None
        self.tfidf_vectorizer = None
        self.domain_keywords = self._load_domain_keywords()
        self.keyword_synonyms = self._load_keyword_synonyms()
        self._initialize_models()
    
    def _initialize_models(self):
        """모델 초기화"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy 영어 모델 로드 완료")
        except OSError:
            print("❌ spaCy 영어 모델을 찾을 수 없습니다.")
            print("설치: python -m spacy download en_core_web_sm")
            exit(1)
        
        try:
            sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.keybert_model = KeyBERT(model=sentence_model)
            print("✅ KeyBERT 모델 로드 완료")
        except Exception as e:
            print(f"❌ KeyBERT 모델 로드 실패: {e}")
            exit(1)
    
    def _load_domain_keywords(self) -> Set[str]:
        """연구 도메인 핵심 키워드 정의"""
        return {
            # AI/ML 관련
            'artificial intelligence', 'machine learning', 'deep learning', 
            'neural network', 'generative ai', 'gpt', 'bert', 'transformer',
            'cnn', 'rnn', 'gan', 'autoencoder', 'reinforcement learning',
            
            # Design 관련
            'user interface', 'user experience', 'ux', 'ui', 'hci',
            'human computer interaction', 'usability', 'user centered',
            'design thinking', 'interaction design', 'visual design',
            'product design', 'service design', 'industrial design',
            
            # 방법론/기술
            'optimization', 'algorithm', 'model', 'framework', 'system',
            'evaluation', 'experiment', 'analysis', 'methodology',
            'data mining', 'classification', 'prediction', 'recommendation',
            
            # 데이터/도메인
            'text', 'image', 'audio', 'video', 'multimodal', 'dataset',
            'emotion', 'sentiment', 'behavior', 'perception', 'cognition'
        }
    
    def _load_keyword_synonyms(self) -> Dict[str, str]:
        """키워드 동의어 매핑"""
        return {
            'ui': 'user interface',
            'ux': 'user experience', 
            'hci': 'human computer interaction',
            'ai': 'artificial intelligence',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'nn': 'neural network',
            'cnn': 'convolutional neural network',
            'rnn': 'recurrent neural network',
            'lstm': 'long short term memory',
            'gru': 'gated recurrent unit',
            'svm': 'support vector machine',
            'rf': 'random forest',
            'xgboost': 'extreme gradient boosting',
            'nlp': 'natural language processing',
            'cv': 'computer vision'
        }
    
    def normalize_keyword(self, keyword: str) -> str:
        """키워드 정규화 (동의어 통합)"""
        keyword_lower = keyword.lower().strip()
        return self.keyword_synonyms.get(keyword_lower, keyword_lower)
    
    def extract_tfidf_keywords(self, documents: List[str], top_k: int = 10) -> Dict[int, List[Tuple[str, float]]]:
        """TF-IDF 기반 키워드 추출"""
        
        # 커스텀 불용어 (도메인 일반 용어)
        custom_stop_words = set(ENGLISH_STOP_WORDS) | {
            'paper', 'study', 'research', 'method', 'approach', 'propose', 'proposed',
            'result', 'results', 'conclusion', 'finding', 'findings', 'show', 'shows',
            'present', 'presented', 'demonstrate', 'demonstrated', 'analysis', 'analyze',
            'evaluation', 'evaluate', 'experiment', 'experimental', 'data', 'dataset',
            'performance', 'effectiveness', 'efficiency', 'accuracy', 'quality',
            'based', 'using', 'used', 'application', 'applications', 'system', 'systems'
        }
        
        # TF-IDF 벡터라이저 설정
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),  # 1-3 단어 조합
            stop_words=list(custom_stop_words),
            min_df=2,  # 최소 2개 문서에서 등장
            max_df=0.7,  # 70% 이상 문서에서 등장하는 것은 제외
            lowercase=True,
            token_pattern=r'\b[a-zA-Z]{2,}\b'  # 2글자 이상 영문만
        )
        
        # TF-IDF 매트릭스 계산
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # 각 문서별 상위 키워드 추출
        doc_keywords = {}
        for doc_idx in range(len(documents)):
            # 해당 문서의 TF-IDF 점수
            doc_scores = tfidf_matrix[doc_idx].toarray().flatten()
            
            # 점수별 정렬
            keyword_indices = np.argsort(doc_scores)[::-1]
            
            # 상위 키워드 선택 (점수 > 0인 것만)
            doc_keywords[doc_idx] = []
            for idx in keyword_indices[:top_k]:
                if doc_scores[idx] > 0:
                    keyword = feature_names[idx]
                    normalized_keyword = self.normalize_keyword(keyword)
                    doc_keywords[doc_idx].append((normalized_keyword, doc_scores[idx]))
        
        return doc_keywords
    
    def extract_keybert_keywords(self, documents: List[str], top_k: int = 10) -> Dict[int, List[Tuple[str, float]]]:
        """KeyBERT 기반 의미적 키워드 추출"""
        doc_keywords = {}
        
        for doc_idx, document in enumerate(documents):
            try:
                # KeyBERT로 키워드 추출 (버전 0.9.0 API)
                keywords = self.keybert_model.extract_keywords(
                    document, 
                    keyphrase_ngram_range=(1, 3),
                    stop_words='english',
                    use_maxsum=True,
                    nr_candidates=20,
                    top_k=top_k * 2,
                    diversity=0.5
                )
                
                # 도메인 키워드 우선순위 적용 및 정규화
                filtered_keywords = []
                for keyword, score in keywords:
                    normalized_keyword = self.normalize_keyword(keyword)
                    
                    # 도메인 키워드면 점수 보정
                    if any(domain_kw in normalized_keyword.lower() for domain_kw in self.domain_keywords):
                        score *= 1.5  # 도메인 키워드 가중치 증가
                    
                    filtered_keywords.append((normalized_keyword, score))
                
                # 점수 기준 재정렬 후 상위 선택
                filtered_keywords = sorted(filtered_keywords, key=lambda x: x[1], reverse=True)
                doc_keywords[doc_idx] = filtered_keywords[:top_k]
                
            except Exception as e:
                print(f"⚠️  문서 {doc_idx} KeyBERT 처리 오류: {e}")
                doc_keywords[doc_idx] = []
        
        return doc_keywords
    
    def combine_keywords(self, tfidf_keywords: Dict, keybert_keywords: Dict, 
                        top_k: int = 15) -> Dict[int, List[Tuple[str, float]]]:
        """TF-IDF와 KeyBERT 키워드 결합"""
        combined_keywords = {}
        
        for doc_idx in tfidf_keywords.keys():
            keyword_scores = defaultdict(list)
            
            # TF-IDF 키워드 추가 (가중치 0.4)
            for keyword, score in tfidf_keywords.get(doc_idx, []):
                keyword_scores[keyword].append(score * 0.4)
            
            # KeyBERT 키워드 추가 (가중치 0.6)  
            for keyword, score in keybert_keywords.get(doc_idx, []):
                keyword_scores[keyword].append(score * 0.6)
            
            # 평균 점수 계산
            final_keywords = []
            for keyword, scores in keyword_scores.items():
                avg_score = np.mean(scores)
                final_keywords.append((keyword, avg_score))
            
            # 점수 기준 정렬 후 상위 선택
            final_keywords = sorted(final_keywords, key=lambda x: x[1], reverse=True)
            combined_keywords[doc_idx] = final_keywords[:top_k]
        
        return combined_keywords

def main():
    """메인 실행 함수"""
    print("🔍 키워드 추출 및 분석 시스템 시작")
    print("=" * 50)
    
    # 1. 데이터 로드
    input_file = '/Users/outcode.jongmokim/Documents/paper_review_with_llm/input/Result_2.csv'
    if not os.path.exists(input_file):
        print(f"❌ 입력 파일을 찾을 수 없습니다: {input_file}")
        return
    
    df = pd.read_csv(input_file)
    print(f"✅ 논문 데이터 로드: {len(df)}개")
    
    # Abstract가 있는 논문만 필터링
    df_with_abstract = df.dropna(subset=['Abstract'])
    print(f"✅ Abstract 포함 논문: {len(df_with_abstract)}개")
    
    # 2. 키워드 추출기 초기화
    extractor = KeywordExtractor()
    
    # 3. Abstract 목록 준비
    abstracts = df_with_abstract['Abstract'].tolist()
    
    print("\n📊 키워드 추출 시작...")
    
    # 4. TF-IDF 키워드 추출
    print("⚙️  TF-IDF 키워드 추출 중...")
    tfidf_keywords = extractor.extract_tfidf_keywords(abstracts, top_k=10)
    
    # 5. KeyBERT 키워드 추출  
    print("🤖 KeyBERT 키워드 추출 중...")
    keybert_keywords = extractor.extract_keybert_keywords(abstracts, top_k=10)
    
    # 6. 키워드 결합
    print("🔄 키워드 결합 중...")
    combined_keywords = extractor.combine_keywords(tfidf_keywords, keybert_keywords, top_k=15)
    
    # 7. 결과를 DataFrame으로 변환
    results = []
    for doc_idx, paper_info in df_with_abstract.iterrows():
        paper_index = list(df_with_abstract.index).index(doc_idx)  # 원본 인덱스에서 추출 인덱스로 변환
        
        if paper_index in combined_keywords:
            keywords_str = '; '.join([f"{kw}({score:.3f})" for kw, score in combined_keywords[paper_index]])
            tfidf_str = '; '.join([f"{kw}({score:.3f})" for kw, score in tfidf_keywords.get(paper_index, [])])
            keybert_str = '; '.join([f"{kw}({score:.3f})" for kw, score in keybert_keywords.get(paper_index, [])])
        else:
            keywords_str = tfidf_str = keybert_str = ""
        
        results.append({
            'Article Title': paper_info['Article Title'],
            'Publication Year': paper_info['Publication Year'],
            'AI_Method_Normalized': paper_info.get('AI_Method_Normalized', ''),
            'Design_Task_Normalized': paper_info.get('Design_Task_Normalized', ''),
            'Combined_Keywords': keywords_str,
            'TF_IDF_Keywords': tfidf_str,
            'KeyBERT_Keywords': keybert_str
        })
    
    # 8. 결과 저장
    output_dir = '/Users/outcode.jongmokim/Documents/paper_review_with_llm/output/semantic_network_analysis/data'
    
    results_df = pd.DataFrame(results)
    output_file = os.path.join(output_dir, 'extracted_keywords.csv')
    results_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✅ 키워드 추출 완료!")
    print(f"📁 저장 위치: {output_file}")
    print(f"📊 처리된 논문: {len(results_df)}개")
    
    # 9. 키워드 통계 출력
    all_keywords = []
    for doc_idx in combined_keywords:
        for keyword, score in combined_keywords[doc_idx]:
            all_keywords.append(keyword)
    
    keyword_counts = Counter(all_keywords)
    print(f"\n📈 추출된 고유 키워드: {len(keyword_counts)}개")
    print("\n🔝 상위 15개 빈도 키워드:")
    for keyword, count in keyword_counts.most_common(15):
        print(f"  {keyword}: {count}회")

if __name__ == "__main__":
    main()