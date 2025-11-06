"""
3rd Screening 시트 분석 스크립트
논문 스크리닝 워크플로우 및 inclusion/exclusion 결정 패턴 분석
"""

import pandas as pd
import sys
from pathlib import Path
from collections import Counter
import json

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from coding_work.scripts.google_sheets_connector import GoogleSheetsConnector


def analyze_3rd_screening():
    """3rd Screening 시트 종합 분석"""

    print("=" * 80)
    print("3rd Screening 워크플로우 분석")
    print("=" * 80)

    # Google Sheets 연결
    connector = GoogleSheetsConnector()
    if not connector.connect():
        print("❌ Google Sheets 연결 실패")
        return None

    print("✓ Google Sheets 연결 성공\n")

    # 3rd Screening 데이터 로드
    df = connector.get_paper_list(sheet_name="3rd Screening")

    if df.empty:
        print("❌ 3rd Screening 시트가 비어있습니다")
        return None

    print(f"✓ 3rd Screening 시트 로드: {len(df)}개 논문\n")

    # ============================================================
    # 1. 컬럼 구조 분석
    # ============================================================
    print("=" * 80)
    print("1. 컬럼 구조 분석")
    print("=" * 80)

    all_columns = df.columns.tolist()
    print(f"\n총 {len(all_columns)}개 컬럼:")
    for i, col in enumerate(all_columns, 1):
        non_null_count = df[col].notna().sum()
        null_count = df[col].isna().sum()
        print(f"{i:2d}. {col:<40} (Non-null: {non_null_count:3d}, Null: {null_count:3d})")

    # Notes 관련 컬럼 찾기
    notes_columns = [col for col in all_columns if 'note' in col.lower() or 'reason' in col.lower() or 'comment' in col.lower()]
    inclusion_columns = [col for col in all_columns if 'inclusion' in col.lower() or 'include' in col.lower()]
    exclusion_columns = [col for col in all_columns if 'exclusion' in col.lower() or 'exclude' in col.lower()]

    print(f"\n📝 Notes 관련 컬럼: {notes_columns}")
    print(f"✓ Inclusion 관련 컬럼: {inclusion_columns}")
    print(f"❌ Exclusion 관련 컬럼: {exclusion_columns}")

    # ============================================================
    # 2. Inclusion 상태 분석
    # ============================================================
    print("\n" + "=" * 80)
    print("2. Inclusion 상태 분석")
    print("=" * 80)

    if inclusion_columns:
        inclusion_col = inclusion_columns[0]

        # Inclusion 값 정규화 (대소문자, 공백 제거)
        df['Inclusion_normalized'] = df[inclusion_col].astype(str).str.strip().str.upper()

        inclusion_counts = df['Inclusion_normalized'].value_counts()
        print(f"\nInclusion 상태별 논문 수 (컬럼: '{inclusion_col}'):")
        for status, count in inclusion_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {status:15s}: {count:3d}개 ({percentage:5.1f}%)")

        # Y/N/Q 상태 요약
        y_count = df[df['Inclusion_normalized'] == 'Y'].shape[0]
        n_count = df[df['Inclusion_normalized'] == 'N'].shape[0]
        q_count = df[df['Inclusion_normalized'] == 'Q'].shape[0]
        blank_count = df[df['Inclusion_normalized'].isin(['', 'NAN'])].shape[0]

        print(f"\n📊 요약:")
        print(f"  ✓ Included (Y):        {y_count:3d}개 ({(y_count/len(df))*100:5.1f}%)")
        print(f"  ❌ Excluded (N):        {n_count:3d}개 ({(n_count/len(df))*100:5.1f}%)")
        print(f"  ❓ Questionable (Q):    {q_count:3d}개 ({(q_count/len(df))*100:5.1f}%)")
        print(f"  ⚪ Blank/Unknown:       {blank_count:3d}개 ({(blank_count/len(df))*100:5.1f}%)")
    else:
        print("\n⚠️  Inclusion 컬럼을 찾을 수 없습니다")

    # ============================================================
    # 3. Notes 분석
    # ============================================================
    print("\n" + "=" * 80)
    print("3. Notes 분석")
    print("=" * 80)

    if notes_columns:
        for notes_col in notes_columns:
            papers_with_notes = df[df[notes_col].notna()]
            print(f"\n📝 컬럼: '{notes_col}'")
            print(f"   Notes가 있는 논문: {len(papers_with_notes)}개 / {len(df)}개 ({(len(papers_with_notes)/len(df))*100:.1f}%)")

            if len(papers_with_notes) > 0:
                print(f"\n   샘플 Notes (처음 5개):")
                for idx, (i, row) in enumerate(papers_with_notes.head(5).iterrows(), 1):
                    title = row.get('Article Title', 'N/A')[:50]
                    note = str(row[notes_col])[:80]
                    inclusion = row.get('Inclusion_normalized', 'N/A')
                    print(f"   {idx}. [{inclusion}] {title}...")
                    print(f"      → {note}...")
                    print()
    else:
        print("\n⚠️  Notes 컬럼을 찾을 수 없습니다")

    # ============================================================
    # 4. Exclusion Reason 분석
    # ============================================================
    print("=" * 80)
    print("4. Exclusion Reason 분석")
    print("=" * 80)

    if exclusion_columns:
        for excl_col in exclusion_columns:
            excluded_papers = df[df[excl_col].notna()]
            print(f"\n❌ 컬럼: '{excl_col}'")
            print(f"   Exclusion Reason이 있는 논문: {len(excluded_papers)}개")

            if len(excluded_papers) > 0:
                # Exclusion Reason 카테고리화
                exclusion_reasons = excluded_papers[excl_col].value_counts()
                print(f"\n   상위 Exclusion Reasons:")
                for reason, count in exclusion_reasons.head(10).items():
                    print(f"   - {reason}: {count}개")
    else:
        # Notes에서 exclusion 관련 키워드 추출
        print("\n⚠️  Exclusion Reason 전용 컬럼은 없습니다")

        if notes_columns:
            notes_col = notes_columns[0]
            excluded_papers = df[(df['Inclusion_normalized'] == 'N') & (df[notes_col].notna())]

            if len(excluded_papers) > 0:
                print(f"\n   Inclusion='N'이면서 Notes가 있는 논문: {len(excluded_papers)}개")
                print(f"\n   샘플 Exclusion Notes (처음 10개):")
                for idx, (i, row) in enumerate(excluded_papers.head(10).iterrows(), 1):
                    title = row.get('Article Title', 'N/A')[:50]
                    note = str(row[notes_col])[:100]
                    print(f"   {idx}. {title}...")
                    print(f"      → {note}...")
                    print()

    # ============================================================
    # 5. Coded Papers 비교
    # ============================================================
    print("=" * 80)
    print("5. Coded Papers 비교")
    print("=" * 80)

    # Assigned_to='J' 필터링 (내가 담당하는 논문)
    if 'Assigned_to' in df.columns:
        my_papers = df[df['Assigned_to'].str.strip().str.upper() == 'J']
        print(f"\n👤 Assigned_to='J' (내가 담당): {len(my_papers)}개 논문")

        # Inclusion='Y' & Assigned_to='J'
        my_included_papers = my_papers[my_papers['Inclusion_normalized'] == 'Y']
        print(f"   - 이중 Inclusion='Y': {len(my_included_papers)}개 논문")

        # Coded 상태 확인 (CodedPapers_2 시트 또는 pdf_upload 컬럼)
        if 'pdf_upload' in df.columns or 'PDF_uploaded' in df.columns:
            pdf_col = 'pdf_upload' if 'pdf_upload' in df.columns else 'PDF_uploaded'
            coded_papers = my_included_papers[my_included_papers[pdf_col].str.strip().str.upper() == 'Y']
            uncoded_papers = my_included_papers[my_included_papers[pdf_col].str.strip().str.upper() != 'Y']

            print(f"   - 이중 PDF 업로드 완료: {len(coded_papers)}개")
            print(f"   - 이중 PDF 업로드 미완료: {len(uncoded_papers)}개")

            if len(uncoded_papers) > 0:
                print(f"\n   📋 PDF 업로드가 필요한 논문 (Inclusion='Y' & Assigned_to='J' & PDF 미업로드):")
                for idx, (i, row) in enumerate(uncoded_papers.head(10).iterrows(), 1):
                    index = row.get('Index', 'N/A')
                    title = row.get('Article Title', 'N/A')[:60]
                    print(f"   {idx}. [{index}] {title}...")
    else:
        print("\n⚠️  'Assigned_to' 컬럼을 찾을 수 없습니다")

    # ============================================================
    # 6. Common Patterns 분석
    # ============================================================
    print("\n" + "=" * 80)
    print("6. Common Patterns 분석")
    print("=" * 80)

    if notes_columns:
        notes_col = notes_columns[0]

        # Inclusion='Y' with Notes
        included_with_notes = df[(df['Inclusion_normalized'] == 'Y') & (df[notes_col].notna())]
        print(f"\n✓ Inclusion='Y' with Notes: {len(included_with_notes)}개")
        if len(included_with_notes) > 0:
            print(f"   샘플 (처음 5개):")
            for idx, (i, row) in enumerate(included_with_notes.head(5).iterrows(), 1):
                title = row.get('Article Title', 'N/A')[:50]
                note = str(row[notes_col])[:80]
                print(f"   {idx}. {title}...")
                print(f"      → {note}...")
                print()

        # Questionable (Q) Papers
        questionable_papers = df[df['Inclusion_normalized'] == 'Q']
        print(f"\n❓ Questionable (Q) Papers: {len(questionable_papers)}개")
        if len(questionable_papers) > 0:
            print(f"   샘플 (처음 5개):")
            for idx, (i, row) in enumerate(questionable_papers.head(5).iterrows(), 1):
                title = row.get('Article Title', 'N/A')[:50]
                note = str(row.get(notes_col, 'N/A'))[:80] if notes_col in row and pd.notna(row.get(notes_col)) else 'No notes'
                print(f"   {idx}. {title}...")
                print(f"      → {note}...")
                print()

    # ============================================================
    # 7. Insights & Recommendations
    # ============================================================
    print("=" * 80)
    print("7. Insights & Recommendations")
    print("=" * 80)

    insights = []

    if inclusion_columns:
        # Most common exclusion reasons from notes
        if notes_columns:
            notes_col = notes_columns[0]
            excluded_notes = df[(df['Inclusion_normalized'] == 'N') & (df[notes_col].notna())][notes_col].tolist()

            # 키워드 추출 (간단한 방법)
            exclusion_keywords = []
            keywords = ['not design', 'not ai', 'no design', 'no ai', 'review', 'survey',
                       'out of scope', 'duplicate', 'irrelevant', 'not relevant']

            for note in excluded_notes:
                note_lower = str(note).lower()
                for keyword in keywords:
                    if keyword in note_lower:
                        exclusion_keywords.append(keyword)

            keyword_counts = Counter(exclusion_keywords)

            print(f"\n🔍 Most Common Exclusion Keywords:")
            for keyword, count in keyword_counts.most_common(10):
                print(f"   - '{keyword}': {count}회")

            insights.append({
                'type': 'exclusion_reasons',
                'top_keywords': keyword_counts.most_common(5)
            })

        # Papers needing review
        y_count = df[df['Inclusion_normalized'] == 'Y'].shape[0]
        n_count = df[df['Inclusion_normalized'] == 'N'].shape[0]
        q_count = df[df['Inclusion_normalized'] == 'Q'].shape[0]
        blank_count = df[df['Inclusion_normalized'].isin(['', 'NAN'])].shape[0]

        print(f"\n📊 Papers Needing Review:")
        print(f"   - Questionable (Q): {q_count}개 → 재검토 필요")
        print(f"   - Blank/Unknown: {blank_count}개 → 스크리닝 필요")
        print(f"   - Total needing attention: {q_count + blank_count}개")

        insights.append({
            'type': 'papers_needing_review',
            'questionable': q_count,
            'blank': blank_count,
            'total': q_count + blank_count
        })

    # ============================================================
    # 8. 분석 결과 저장
    # ============================================================
    print("\n" + "=" * 80)
    print("8. 분석 결과 저장")
    print("=" * 80)

    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)

    # CSV 저장
    csv_path = output_dir / '3rd_screening_analysis.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ CSV 저장: {csv_path}")

    # Insights JSON 저장
    insights_path = output_dir / '3rd_screening_insights.json'
    with open(insights_path, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    print(f"✓ Insights JSON 저장: {insights_path}")

    # 요약 통계 저장
    summary = {
        'total_papers': len(df),
        'inclusion_stats': {
            'Y': y_count,
            'N': n_count,
            'Q': q_count,
            'blank': blank_count
        },
        'columns': all_columns,
        'notes_columns': notes_columns,
        'inclusion_columns': inclusion_columns,
        'exclusion_columns': exclusion_columns
    }

    summary_path = output_dir / '3rd_screening_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"✓ Summary JSON 저장: {summary_path}")

    print("\n" + "=" * 80)
    print("✅ 3rd Screening 분석 완료!")
    print("=" * 80)

    return df


if __name__ == "__main__":
    analyze_3rd_screening()
