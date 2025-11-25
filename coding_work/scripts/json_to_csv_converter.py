#!/usr/bin/env python3
"""
오디오 전사 JSON 파일을 CSV로 변환
실제 오디오 duration 기반 timespan 계산
"""

import json
import subprocess
from pathlib import Path
from datetime import timedelta
import pandas as pd


def get_audio_duration(audio_path: Path) -> float:
    """
    ffprobe로 오디오 파일의 실제 duration 확인 (초)

    Args:
        audio_path: 오디오 파일 경로

    Returns:
        duration (초)
    """
    cmd = [
        'ffprobe', '-i', str(audio_path),
        '-show_entries', 'format=duration',
        '-v', 'quiet',
        '-of', 'csv=p=0'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def seconds_to_hms(seconds: float) -> str:
    """
    초를 HH:MM:SS 형식으로 변환

    Args:
        seconds: 초

    Returns:
        HH:MM:SS 형식 문자열
    """
    td = timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def process_json_files(json_folder: Path, audio_folder: Path, output_csv: Path):
    """
    JSON 파일들을 읽어서 CSV로 변환

    Args:
        json_folder: JSON 파일 폴더
        audio_folder: 원본 오디오 파일 폴더
        output_csv: 출력 CSV 파일 경로
    """
    # JSON 파일 목록 (타임스탬프 순서대로)
    json_files = sorted(json_folder.glob("*.json"))

    rows = []

    for json_file in json_files:
        print(f"처리 중: {json_file.name}")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 실패한 전사는 건너뛰기
        if data.get('status') == 'failed':
            print(f"  ⚠️ 실패한 전사, 건너뜀")
            continue

        filename = data['filename']

        # 원본 오디오 파일 경로
        audio_path = audio_folder / filename

        # 실제 duration 확인
        if audio_path.exists():
            total_duration = get_audio_duration(audio_path)
            print(f"  → Duration: {total_duration:.2f}초 ({seconds_to_hms(total_duration)})")
        else:
            print(f"  ⚠️ 원본 파일 없음: {audio_path}")
            total_duration = None

        # 통합된 전사만 CSV에 포함 (세그먼트 정보는 제외)
        if total_duration:
            timespan = f"00:00:00-{seconds_to_hms(total_duration)}"
        else:
            timespan = "00:00:00-Unknown"

        rows.append({
            'filename': filename,
            'timespan': timespan,
            'text': data['transcription']['text'],
            'word_count': data['statistics']['word_count'],
            'length': data['statistics']['text_length']
        })

    # DataFrame 생성
    df = pd.DataFrame(rows)

    # CSV 저장
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n✅ CSV 저장 완료: {output_csv}")
    print(f"📊 총 {len(df)} 행")


def main():
    # 경로 설정
    base_dir = Path(__file__).parent.parent
    json_folder = base_dir / "results" / "audio_transcription"
    audio_folder = base_dir.parent / "audio_files"
    output_csv = json_folder / "transcriptions.csv"

    print("=== JSON → CSV 변환 시작 ===\n")

    # 변환 실행
    process_json_files(json_folder, audio_folder, output_csv)

    print("\n=== 변환 완료 ===")


if __name__ == "__main__":
    main()
