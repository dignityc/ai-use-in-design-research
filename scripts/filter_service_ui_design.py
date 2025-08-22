import pandas as pd

def filter_service_ui_design():
    df = pd.read_csv('final_filtered_list.csv')
    
    print(f"전체 필터링된 논문 수: {len(df)}")
    
    # 1. 카테고리 컬럼에서 SERVICE, UI.UX, UI/UX 관련 항목 필터링
    service_ui_categories = ['SERVICE', 'UI.UX', 'UI/UX', 'UI.UX, SERVICE']
    category_filtered = df[df['ENGINEERING.PRODUCT/UI.UX/SERVICE'].isin(service_ui_categories)]
    
    # 2. 키워드 기반 필터링 (제목, 초록, 노트에서)
    ui_ux_keywords = [
        'user interface', 'user experience', 'UI', 'UX', 'interface', 'interaction', 
        'usability', 'service', 'user-centered', 'human-computer', 'HCI', 
        'user study', 'user evaluation', 'user preference', 'user behavior',
        'service design', 'customer experience', 'user satisfaction',
        'interaction design', 'visual design', 'design thinking'
    ]
    
    keyword_filtered_indices = []
    for idx, row in df.iterrows():
        title = str(row['Article Title']).lower() if pd.notna(row['Article Title']) else ''
        abstract = str(row['Abstract']).lower() if pd.notna(row['Abstract']) else ''
        note = str(row['Note']).lower() if pd.notna(row['Note']) else ''
        
        combined_text = f"{title} {abstract} {note}"
        
        # 키워드 중 하나라도 포함되면 선택
        if any(keyword.lower() in combined_text for keyword in ui_ux_keywords):
            keyword_filtered_indices.append(idx)
    
    keyword_filtered = df.loc[keyword_filtered_indices]
    
    # 3. 두 결과 합치기 (중복 제거)
    combined_indices = list(set(category_filtered.index.tolist() + keyword_filtered_indices))
    final_service_ui_df = df.loc[combined_indices]
    
    # 결과 저장
    final_service_ui_df.to_csv('service_ui_design_papers.csv', index=False)
    
    print(f"카테고리 기반 필터링 결과: {len(category_filtered)}개")
    print(f"키워드 기반 필터링 결과: {len(keyword_filtered)}개")
    print(f"최종 서비스/UI 디자인 관련 논문: {len(final_service_ui_df)}개")
    print("결과가 'service_ui_design_papers.csv'에 저장되었습니다.")
    
    # 카테고리별 분포 출력
    print("\n=== 카테고리별 분포 ===")
    category_dist = final_service_ui_df['ENGINEERING.PRODUCT/UI.UX/SERVICE'].value_counts()
    for category, count in category_dist.items():
        print(f"{category}: {count}개")

if __name__ == "__main__":
    filter_service_ui_design()