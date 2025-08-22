#!/usr/bin/env python3
"""
Script to add abstracts to Result_2.csv by matching titles with PaperList.csv
"""

import pandas as pd
import sys
import os

def add_abstracts_to_result2():
    # Define file paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result2_path = os.path.join(base_dir, 'input', 'Result_2.csv')
    paperlist_path = os.path.join(base_dir, 'input', 'PaperList.csv')
    
    try:
        # Read the CSV files
        print("📄 Reading Result_2.csv...")
        result2_df = pd.read_csv(result2_path)
        print(f"   Loaded {len(result2_df)} papers from Result_2.csv")
        
        print("📄 Reading PaperList.csv...")
        paperlist_df = pd.read_csv(paperlist_path)
        print(f"   Loaded {len(paperlist_df)} papers from PaperList.csv")
        
        # Check if Abstract column already exists in Result_2
        if 'Abstract' in result2_df.columns:
            print("⚠️  Abstract column already exists in Result_2.csv")
            return
        
        # Extract relevant columns from PaperList (Title and Abstract)
        abstracts_df = paperlist_df[['Article Title', 'Abstract']].copy()
        
        # Merge Result_2 with abstracts based on Article Title
        print("🔗 Matching titles and adding abstracts...")
        merged_df = result2_df.merge(
            abstracts_df, 
            on='Article Title', 
            how='left'
        )
        
        # Insert Abstract column at position 5 (after DOI Link)
        columns = list(merged_df.columns)
        abstract_col = columns.pop(columns.index('Abstract'))
        
        # Find the position to insert (after DOI Link)
        insert_position = columns.index('DOI Link') + 1
        columns.insert(insert_position, abstract_col)
        
        # Reorder the dataframe
        merged_df = merged_df[columns]
        
        # Check for missing abstracts
        missing_abstracts = merged_df['Abstract'].isna().sum()
        successful_matches = len(merged_df) - missing_abstracts
        
        # Fill missing abstracts with placeholder text
        merged_df['Abstract'] = merged_df['Abstract'].fillna('Abstract not found in PaperList.csv')
        
        # Save the updated Result_2.csv
        print("💾 Saving updated Result_2.csv...")
        merged_df.to_csv(result2_path, index=False)
        
        # Print match report
        print("\n📊 MATCH REPORT:")
        print(f"   Total papers in Result_2.csv: {len(result2_df)}")
        print(f"   Successful matches: {successful_matches}")
        print(f"   Missing abstracts: {missing_abstracts}")
        print(f"   Success rate: {(successful_matches / len(result2_df)) * 100:.1f}%")
        
        if missing_abstracts > 0:
            print("\n🔍 Papers with missing abstracts:")
            missing_papers = merged_df[merged_df['Abstract'] == 'Abstract not found in PaperList.csv']
            for idx, paper in missing_papers.iterrows():
                print(f"   - {paper['Article Title']}")
        
        print(f"\n✅ Successfully updated Result_2.csv with Abstract column!")
        print(f"   Backup saved as Result_2_backup.csv")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    add_abstracts_to_result2()