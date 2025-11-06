"""
Comprehensive Analysis of Coded Papers
Compares CodedPapers_2 with 3rd Screening data to identify patterns, gaps, and trends
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / 'coding_work' / 'scripts'))

from google_sheets_connector import GoogleSheetsConnector
import pandas as pd
import json

def main():
    print("=" * 80)
    print("📊 CODED PAPERS COMPREHENSIVE ANALYSIS")
    print("=" * 80)

    # Connect to Google Sheets
    connector = GoogleSheetsConnector()
    if not connector.connect():
        print("❌ Failed to connect to Google Sheets")
        return False

    print("\n✅ Connected to Google Sheets")

    # Read CodedPapers_2 sheet
    print("\n📥 Reading CodedPapers_2 sheet...")
    coded_sheet = connector.get_sheet("CodedPapers_2")
    coded_values = coded_sheet.get_all_values()

    if len(coded_values) < 2:
        print("❌ CodedPapers_2 sheet is empty")
        return False

    coded_headers = coded_values[0]
    coded_data = coded_values[1:]
    coded_df = pd.DataFrame(coded_data, columns=coded_headers)

    print(f"   ✅ Loaded {len(coded_df)} coded papers")
    print(f"   Columns: {list(coded_df.columns)}")

    # Read 3rd Screening sheet
    print("\n📥 Reading 3rd Screening sheet...")
    screening_sheet = connector.get_sheet("3rd Screening")
    screening_values = screening_sheet.get_all_values()

    if len(screening_values) < 2:
        print("❌ 3rd Screening sheet is empty")
        return False

    screening_headers = screening_values[0]
    screening_data = screening_values[1:]
    screening_df = pd.DataFrame(screening_data, columns=screening_headers)

    print(f"   ✅ Loaded {len(screening_df)} total papers")
    print(f"   Columns: {list(screening_df.columns)}")

    # Save raw data for analysis
    output_folder = Path(__file__).parent.parent / "results"
    output_folder.mkdir(exist_ok=True)

    print("\n💾 Saving raw data...")
    coded_df.to_csv(output_folder / "coded_papers_raw.csv", index=False, encoding='utf-8')
    screening_df.to_csv(output_folder / "screening_papers_raw.csv", index=False, encoding='utf-8')

    # Basic statistics
    print("\n" + "=" * 80)
    print("📈 BASIC STATISTICS")
    print("=" * 80)

    print(f"\nTotal papers in 3rd Screening: {len(screening_df)}")
    print(f"Total coded papers: {len(coded_df)}")
    print(f"Coding progress: {len(coded_df)}/{len(screening_df)} ({len(coded_df)/len(screening_df)*100:.1f}%)")

    # Year distribution in coded papers
    print("\n--- Year Distribution (Coded Papers) ---")
    if 'Publication Year' in coded_df.columns:
        year_dist = coded_df['Publication Year'].value_counts().sort_index()
        print(year_dist.to_string())

    # Year distribution in screening pool
    print("\n--- Year Distribution (Full Screening Pool) ---")
    if 'Publication Year' in screening_df.columns:
        year_dist_full = screening_df['Publication Year'].value_counts().sort_index()
        print(year_dist_full.to_string())

    # Design Discipline patterns
    print("\n--- Design Discipline Distribution ---")
    if 'Design Discipline' in coded_df.columns:
        discipline_dist = coded_df['Design Discipline'].value_counts()
        print(discipline_dist.to_string())

    # AI Methods patterns
    print("\n--- AI Methods Distribution ---")
    if 'AI methods' in coded_df.columns:
        ai_methods_dist = coded_df['AI methods'].value_counts()
        print(ai_methods_dist.to_string())

    # Data Modality patterns
    print("\n--- Data Modality Distribution ---")
    if 'Data Modality' in coded_df.columns:
        modality_dist = coded_df['Data Modality'].value_counts()
        print(modality_dist.to_string())

    # Design Phase patterns
    print("\n--- Design Phase Distribution ---")
    if 'Design Phase' in coded_df.columns:
        phase_dist = coded_df['Design Phase'].value_counts()
        print(phase_dist.to_string())

    # AI Assistance Types
    print("\n--- AI Assistance Types Distribution ---")
    if 'AI Assistance Types (Lee and Kim, 2025)' in coded_df.columns:
        assistance_dist = coded_df['AI Assistance Types (Lee and Kim, 2025)'].value_counts()
        print(assistance_dist.to_string())

    # Data About patterns
    print("\n--- Data About Distribution ---")
    if 'Data About' in coded_df.columns:
        data_about_dist = coded_df['Data About'].value_counts()
        print(data_about_dist.to_string())

    # Design Practice/Task patterns
    print("\n--- Design Practice/Task Distribution ---")
    if 'Design Practice/Task' in coded_df.columns:
        practice_dist = coded_df['Design Practice/Task'].value_counts()
        print(practice_dist.head(10).to_string())
        print(f"... ({len(practice_dist)} unique values total)")

    # Cross-tabulation: AI Methods × Design Discipline
    print("\n--- Cross-tabulation: AI Methods × Design Discipline ---")
    if 'AI methods' in coded_df.columns and 'Design Discipline' in coded_df.columns:
        cross_tab = pd.crosstab(coded_df['AI methods'], coded_df['Design Discipline'])
        print(cross_tab.to_string())

    # Cross-tabulation: Design Phase × AI Methods
    print("\n--- Cross-tabulation: Design Phase × AI Methods ---")
    if 'Design Phase' in coded_df.columns and 'AI methods' in coded_df.columns:
        cross_tab2 = pd.crosstab(coded_df['Design Phase'], coded_df['AI methods'])
        print(cross_tab2.to_string())

    # Cross-tabulation: Data Modality × AI Methods
    print("\n--- Cross-tabulation: Data Modality × AI Methods ---")
    if 'Data Modality' in coded_df.columns and 'AI methods' in coded_df.columns:
        cross_tab3 = pd.crosstab(coded_df['Data Modality'], coded_df['AI methods'])
        print(cross_tab3.to_string())

    # Save analysis summary as JSON
    analysis_summary = {
        "total_screening_papers": len(screening_df),
        "total_coded_papers": len(coded_df),
        "coding_progress_percent": round(len(coded_df)/len(screening_df)*100, 1),
        "year_distribution_coded": year_dist.to_dict() if 'Publication Year' in coded_df.columns else {},
        "year_distribution_screening": year_dist_full.to_dict() if 'Publication Year' in screening_df.columns else {},
        "design_discipline": discipline_dist.to_dict() if 'Design Discipline' in coded_df.columns else {},
        "ai_methods": ai_methods_dist.to_dict() if 'AI methods' in coded_df.columns else {},
        "data_modality": modality_dist.to_dict() if 'Data Modality' in coded_df.columns else {},
        "design_phase": phase_dist.to_dict() if 'Design Phase' in coded_df.columns else {},
        "ai_assistance_types": assistance_dist.to_dict() if 'AI Assistance Types (Lee and Kim, 2025)' in coded_df.columns else {},
        "data_about": data_about_dist.to_dict() if 'Data About' in coded_df.columns else {}
    }

    with open(output_folder / "analysis_summary.json", 'w', encoding='utf-8') as f:
        json.dump(analysis_summary, f, indent=2, ensure_ascii=False)

    print("\n✅ Analysis complete!")
    print(f"📁 Raw data saved to: {output_folder}")
    print(f"   - coded_papers_raw.csv")
    print(f"   - screening_papers_raw.csv")
    print(f"   - analysis_summary.json")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
