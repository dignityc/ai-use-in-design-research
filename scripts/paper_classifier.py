import os
import pandas as pd
import subprocess
import json
import re

def load_codebook():
    """CodeBook.csv를 읽어서 분류 카테고리를 로드합니다."""
    try:
        # 여러 인코딩 방식으로 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin1', 'utf-16']
        
        for encoding in encodings:
            try:
                codebook = pd.read_csv('input/CodeBook.csv', encoding=encoding)
                print(f"✅ CodeBook.csv를 {encoding} 인코딩으로 성공적으로 로드했습니다.")
                return codebook
            except UnicodeDecodeError:
                continue
        
        print("❌ 지원하는 인코딩으로 파일을 읽을 수 없습니다.")
        return None
        
    except Exception as e:
        print(f"CodeBook.csv 읽기 오류: {e}")
        return None

def create_classification_prompt(abstract, title, codebook):
    """Abstract와 CodeBook을 바탕으로 분류 프롬프트를 생성합니다."""
    
    # CodeBook에서 카테고리 정보 추출
    disciplines = codebook['Design Discipline'].dropna().unique()
    data_about = codebook['Data About (DATA SOURCE: sensor, design component(artifhact), natural language)'].dropna().unique()
    data_modalities = codebook['Data Modality'].dropna().unique()
    ai_methods = codebook['AI methods'].dropna().unique()
    ai_assistance_types = codebook['AI Assistance Types (Lee and Kim, 2025)'].dropna().unique()
    
    prompt = f"""
논문 제목: {title}

논문 Abstract:
{abstract}

위 논문을 아래 카테고리들로 정확히 분류해주세요. **반드시 제공된 카테고리 중에서만 선택**하고, 정확한 용어를 사용해주세요.

분류 카테고리:

1. Design Discipline - 다음 중 정확히 하나 선택하되, Multiple인 경우 구성 요소를 괄호 안에 명시:
- Insudtrial Design/ Engineering design/ product design
- Service Design /System Design/ Business design  
- UI/UX Design
- Multiple

예시: "Multiple (UI/UX Design + Service Design)", "Multiple (Engineering + Service Design)"

2. Data About - 다음 중 정확히 하나 선택:
- Perception
- Physiological
- Behavioral-based
- Product-based
- Generated
- Demographic
- Environmental

3. Data Modality - 다음 중 정확히 하나 선택하되, Multimodal인 경우 구성 요소를 괄호 안에 명시:
- Text
- Image
- Audio
- Video
- Time Series
- Multimodal

예시: "Multimodal (Text + Image)", "Multimodal (Audio + Video + Text)"

4. AI methods - 다음 중 정확히 하나 선택하되, 구체적인 모델명이 있으면 괄호 안에 포함:
- Traditional ML (shallow models)
- Deep models
- Gen AI
- Reinforcement learning
- Exploratory data analysis

예시: "Deep models (CNN, ResNet)", "Gen AI (GPT-4, BERT)", "Traditional ML (SVM, Random Forest)"

5. AI Assistance Types - 다음 중 정확히 하나 선택하되, Multiple인 경우 구성 요소를 괄호 안에 명시:
- Design generation
- Prediction
- Decision making (Validation, evaluation)
- Coordination
- Multiple
- Sense making

예시: "Multiple (Design generation + Prediction)", "Multiple (Coordination + Sense making)"

6. Design Practice/Task - 다음 중 정확히 하나 선택:
- Discovery
- Define
- Develop
- Delivery

중요 지침:
- 위 카테고리 목록에서 **정확한 용어**를 그대로 사용하세요
- 임의로 변경하거나 새로운 카테고리를 만들지 마세요
- AI methods에서 구체적 모델명을 아는 경우 괄호 안에 추가하세요

다음 JSON 형태로 응답해주세요:
{{
    "design_discipline": "정확한 카테고리명",
    "data_about": "정확한 카테고리명", 
    "data_modality": "정확한 카테고리명",
    "ai_methods": "정확한 카테고리명 (구체적 모델명)",
    "ai_assistance_types": "정확한 카테고리명",
    "design_practice_task": "정확한 카테고리명",
    "key_quotes": [
        "Abstract에서 추출한 중요 인용문 1",
        "Abstract에서 추출한 중요 인용문 2", 
        "Abstract에서 추출한 중요 인용문 3"
    ]
}}
"""
    return prompt

def call_claude_cli(prompt):
    """Claude CLI를 호출하여 응답을 받습니다."""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Claude CLI 호출 오류: {e}")
        return None
    except FileNotFoundError:
        print("Claude CLI가 설치되지 않았습니다. 'npm install -g @anthropic/claude-code' 를 실행해주세요.")
        return None

def parse_classification_response(response):
    """Claude의 분류 응답을 파싱합니다."""
    try:
        # JSON 블록을 찾기 위한 정규식
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # JSON 블록 없이 직접 JSON이 있는 경우
            json_str = response
        
        return json.loads(json_str)
    except Exception as e:
        print(f"분류 응답 파싱 오류: {e}")
        print(f"응답 내용: {response}")
        return None

def create_result_record(classification_result, paper_row):
    """Result.csv 구조에 맞는 새 레코드를 생성합니다."""
    
    # Notes 생성 (핵심 인용문들을 결합)
    notes = "\n".join([f'"{quote}"' for quote in classification_result.get('key_quotes', [])])
    
    # 새 레코드 생성
    new_record = {
        'Article Title': paper_row['Article Title'],
        'Author Full Names': paper_row['Author Full Names'],
        'Source Title': paper_row['Source Title'],
        'Publication Year': paper_row['Publication Year'],
        'DOI Link': paper_row['DOI Link'],
        'Design Discipline': classification_result.get('design_discipline', ''),
        'Data About': classification_result.get('data_about', ''),
        'Data Modality': classification_result.get('data_modality', ''),
        'AI methods': classification_result.get('ai_methods', ''),
        'AI Assistance Types (Lee and Kim, 2025)': classification_result.get('ai_assistance_types', ''),
        'Design Practice/Task': classification_result.get('design_practice_task', ''),
        'Notes': notes,
        'Questions': ''
    }
    
    return new_record

def display_papers(papers_df):
    """논문 목록을 보기 좋게 표시합니다."""
    print("\n사용 가능한 논문들:")
    print("=" * 80)
    
    for i, (idx, row) in enumerate(papers_df.iterrows()):
        title = row['Article Title']
        abstract = row['Abstract']
        abstract_preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
        
        print(f"{i+1}. {title}")
        print(f"   Abstract: {abstract_preview}")
        print(f"   카테고리: {row['ENGINEERING.PRODUCT/UI.UX/SERVICE']}")
        print("-" * 80)

def process_single_paper(paper_row, paper_index, total_papers, codebook, output_file):
    """단일 논문을 처리합니다."""
    title = paper_row['Article Title']
    print(f"\n논문 {paper_index}/{total_papers} 처리 중:")
    print(f"제목: {title}")
    
    # 분류 프롬프트 생성 및 Claude CLI 호출
    classification_prompt = create_classification_prompt(
        paper_row['Abstract'], 
        title, 
        codebook
    )
    classification_response = call_claude_cli(classification_prompt)
    if not classification_response:
        print("❌ Claude CLI 호출 실패")
        return False
    
    # 분류 결과 파싱
    classification_result = parse_classification_response(classification_response)
    if not classification_result:
        print("❌ 응답 파싱 실패")
        return False
    
    # 새 레코드 생성
    new_record = create_result_record(classification_result, paper_row)
    
    # 결과 저장
    if os.path.exists(output_file):
        # 기존 파일에 추가
        existing_df = pd.read_csv(output_file)
        new_df = pd.concat([existing_df, pd.DataFrame([new_record])], ignore_index=True)
    else:
        # 새 파일 생성
        new_df = pd.DataFrame([new_record])
    
    new_df.to_csv(output_file, index=False)
    
    print("✅ 분류 완료")
    print(f"   - Design Discipline: {classification_result.get('design_discipline', 'N/A')}")
    print(f"   - AI methods: {classification_result.get('ai_methods', 'N/A')}")
    
    return True

def main():
    """메인 실행 함수 - 모든 논문을 배치 처리"""
    print("🤖 Abstract 기반 논문 자동 분류 및 코딩 시스템 시작...")
    print("=" * 80)
    
    # 1. step4_category_only_papers.csv 로드
    try:
        papers_df = pd.read_csv('output/step4_category_only_papers.csv')
    except Exception as e:
        print(f"❌ CSV 파일 읽기 오류: {e}")
        return
    
    total_papers = len(papers_df)
    print(f"📚 총 {total_papers}개의 논문을 로드했습니다.")
    
    # 2. CodeBook 로드
    print("📖 CodeBook 로드 중...")
    codebook = load_codebook()
    if codebook is None:
        return
    
    # 3. 출력 파일 설정
    output_file = 'output/classified_papers.csv'
    print(f"💾 결과 저장 파일: {output_file}")
    
    # 4. 모든 논문 배치 처리
    print("\n🚀 배치 처리 시작...")
    successful_count = 0
    failed_papers = []
    
    for index, (_, paper_row) in enumerate(papers_df.iterrows(), 1):
        try:
            success = process_single_paper(paper_row, index, total_papers, codebook, output_file)
            if success:
                successful_count += 1
            else:
                failed_papers.append(paper_row['Article Title'])
        except Exception as e:
            print(f"❌ 논문 처리 중 오류: {e}")
            failed_papers.append(paper_row['Article Title'])
            continue
        
        # 진행률 표시
        if index % 5 == 0 or index == total_papers:
            progress = (index / total_papers) * 100
            print(f"\n📊 진행률: {index}/{total_papers} ({progress:.1f}%)")
    
    # 5. 최종 결과 보고
    print("\n" + "=" * 80)
    print("🎉 배치 처리 완료!")
    print(f"✅ 성공: {successful_count}개 논문")
    print(f"❌ 실패: {len(failed_papers)}개 논문")
    
    if failed_papers:
        print("\n실패한 논문들:")
        for i, title in enumerate(failed_papers, 1):
            print(f"   {i}. {title}")
    
    print(f"\n💾 모든 분류 결과가 {output_file}에 저장되었습니다.")
    
    # 6. 통계 정보 출력
    if successful_count > 0:
        try:
            final_df = pd.read_csv(output_file)
            print(f"\n📈 최종 통계:")
            print(f"   - 총 분류된 논문: {len(final_df)}개")
            
            # Design Discipline 분포
            if 'Design Discipline' in final_df.columns:
                discipline_counts = final_df['Design Discipline'].value_counts()
                print(f"   - Design Discipline 분포:")
                for discipline, count in discipline_counts.items():
                    print(f"     • {discipline}: {count}개")
                    
        except Exception as e:
            print(f"통계 정보 출력 중 오류: {e}")

if __name__ == "__main__":
    main()