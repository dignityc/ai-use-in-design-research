import pandas as pd

def filter_inclusion_y():
    df = pd.read_csv('input/PaperList.csv')
    
    filtered_df = df[df['Inclusion (Y/N/Q/R) for 2nd screening'] == 'Y']
    
    filtered_df.to_csv('output/step1_filtered_inclusion_y.csv', index=False)
    
    print(f"전체 논문 수: {len(df)}")
    print(f"Inclusion이 Y인 논문 수: {len(filtered_df)}")
    print("필터링된 결과가 'output/step1_filtered_inclusion_y.csv'에 저장되었습니다.")

if __name__ == "__main__":
    filter_inclusion_y()