#!/bin/bash
# PDF 분석기 자동 실행 스크립트

# 작업 디렉토리 이동
cd /Users/outcode.jongmokim/Documents/paper_review_with_llm/coding_work/scripts

# 가상환경 활성화 (필요시)
# source ../../venv/bin/activate

# 로그 파일명 (타임스탬프)
LOG_FILE="../logs/pdf_analyzer_$(date +%Y%m%d_%H%M%S).log"

# PDF 분석기 실행 (30개씩 처리)
python3 pdf_analyzer.py 30 > "$LOG_FILE" 2>&1

# 완료 알림 (선택사항)
echo "PDF 분석 완료: $(date)" >> "$LOG_FILE"
