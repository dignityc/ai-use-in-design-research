import pandas as pd
import re

def filter_service_ui_design_improved():
    df = pd.read_csv('final_filtered_list.csv')
    
    print(f"전체 필터링된 논문 수: {len(df)}")
    
    # 1. 카테고리 컬럼에서 SERVICE, UI.UX, UI/UX 관련 항목 필터링
    service_ui_categories = ['SERVICE', 'UI.UX', 'UI/UX', 'UI.UX, SERVICE']
    category_filtered = df[df['ENGINEERING.PRODUCT/UI.UX/SERVICE'].isin(service_ui_categories)]
    
    # 2. 개선된 키워드 기반 필터링
    # 정확한 단어 매칭을 위해 단어 경계(\b) 사용
    precise_keywords = [
        r'\buser interface\b', r'\buser experience\b', r'\bUX\b', 
        r'\binteraction design\b', r'\busability\b', r'\bservice design\b',
        r'\buser-centered\b', r'\bhuman-computer interaction\b', r'\bHCI\b',
        r'\buser study\b', r'\buser evaluation\b', r'\buser preference\b', 
        r'\buser behavior\b', r'\bcustomer experience\b', r'\buser satisfaction\b',
        r'\bvisual design\b', r'\bdesign thinking\b'
    ]
    
    # 일반적인 키워드 (덜 정확하지만 중요한 개념들)
    general_keywords = [
        'interface', 'interaction', 'service', 'usability', 
        'user-centered', 'customer', 'user'
    ]
    
    keyword_filtered_indices = []
    keyword_details = {}  # 어떤 키워드로 매칭되었는지 저장
    
    for idx, row in df.iterrows():
        title = str(row['Article Title']).lower() if pd.notna(row['Article Title']) else ''
        abstract = str(row['Abstract']).lower() if pd.notna(row['Abstract']) else ''
        note = str(row['Note']).lower() if pd.notna(row['Note']) else ''
        
        combined_text = f"{title} {abstract} {note}"
        matched_keywords = []
        
        # 정확한 키워드 매칭
        for pattern in precise_keywords:
            if re.search(pattern, combined_text, re.IGNORECASE):
                matched_keywords.append(pattern.replace(r'\b', ''))
        
        # 일반 키워드는 더 엄격한 조건으로
        for keyword in general_keywords:
            # 제목이나 노트에 포함되어야 함 (초록에서만 나오는 것은 제외)
            if (keyword in title or keyword in note) and len(keyword) > 3:
                matched_keywords.append(keyword)
        
        # 매칭된 키워드가 있으면 선택
        if matched_keywords:
            keyword_filtered_indices.append(idx)
            keyword_details[idx] = matched_keywords
    
    keyword_filtered = df.loc[keyword_filtered_indices]
    
    # 3. 두 결과 합치기 (중복 제거)
    combined_indices = list(set(category_filtered.index.tolist() + keyword_filtered_indices))
    final_service_ui_df = df.loc[combined_indices]
    
    # 결과 저장
    final_service_ui_df.to_csv('service_ui_design_papers_improved.csv', index=False)
    
    print(f"카테고리 기반 필터링 결과: {len(category_filtered)}개")
    print(f"키워드 기반 필터링 결과: {len(keyword_filtered)}개") 
    print(f"최종 서비스/UI 디자인 관련 논문: {len(final_service_ui_df)}개")
    print("개선된 결과가 'service_ui_design_papers_improved.csv'에 저장되었습니다.")
    
    # 키워드 매칭 예시 출력
    print("\n=== 키워드 매칭 예시 (처음 5개) ===")
    count = 0
    for idx in keyword_filtered_indices[:5]:
        row = df.loc[idx]
        print(f"\n논문: {row['Article Title']}")
        print(f"카테고리: {row['ENGINEERING.PRODUCT/UI.UX/SERVICE']}")
        print(f"매칭된 키워드: {keyword_details[idx]}")
        print(f"노트: {row['Note']}")
        count += 1

if __name__ == "__main__":
    filter_service_ui_design_improved()