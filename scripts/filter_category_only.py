import pandas as pd

def filter_category_only():
    df = pd.read_csv('output/step2_final_filtered_list.csv')
    
    print(f"전체 필터링된 논문 수: {len(df)}")
    
    # 카테고리 기반으로만 필터링
    service_ui_categories = ['SERVICE', 'UI.UX', 'UI/UX', 'UI.UX, SERVICE']
    category_only_filtered = df[df['ENGINEERING.PRODUCT/UI.UX/SERVICE'].isin(service_ui_categories)]
    
    # 결과 저장
    category_only_filtered.to_csv('output/step4_category_only_papers.csv', index=False)
    
    print(f"카테고리 기반으로만 필터링된 논문 수: {len(category_only_filtered)}개")
    print("결과가 'output/step4_category_only_papers.csv'에 저장되었습니다.")
    
    # 카테고리별 분포 출력
    print("\n=== 카테고리별 분포 ===")
    category_dist = category_only_filtered['ENGINEERING.PRODUCT/UI.UX/SERVICE'].value_counts()
    for category, count in category_dist.items():
        print(f"{category}: {count}개")
    
    # 각 카테고리별 논문 예시 출력
    print("\n=== 카테고리별 논문 예시 ===")
    for category in service_ui_categories:
        papers_in_category = category_only_filtered[category_only_filtered['ENGINEERING.PRODUCT/UI.UX/SERVICE'] == category]
        if len(papers_in_category) > 0:
            print(f"\n[{category}] ({len(papers_in_category)}개):")
            for idx, row in papers_in_category.head(3).iterrows():  # 각 카테고리당 3개씩만
                print(f"  - {row['Article Title']}")
                print(f"    노트: {row['Note']}")

if __name__ == "__main__":
    filter_category_only()