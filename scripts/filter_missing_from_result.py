import pandas as pd

def filter_missing_from_result():
    filtered_df = pd.read_csv('output/step1_filtered_inclusion_y.csv')
    result_df = pd.read_csv('input/Result.csv')
    
    print(f"필터링된 리스트 논문 수: {len(filtered_df)}")
    print(f"Result.csv 논문 수: {len(result_df)}")
    
    filtered_titles = set(filtered_df['Article Title'].str.strip())
    result_titles = set(result_df['Article Title'].str.strip())
    
    missing_titles = filtered_titles - result_titles
    
    final_filtered_df = filtered_df[filtered_df['Article Title'].str.strip().isin(missing_titles)]
    
    final_filtered_df.to_csv('output/step2_final_filtered_list.csv', index=False)
    
    print(f"Result.csv에 없는 논문 수: {len(final_filtered_df)}")
    print("최종 필터링된 결과가 'output/step2_final_filtered_list.csv'에 저장되었습니다.")
    
    overlap_titles = filtered_titles & result_titles
    print(f"겹치는 논문 수 (Result.csv에 이미 있는 논문): {len(overlap_titles)}")

if __name__ == "__main__":
    filter_missing_from_result()