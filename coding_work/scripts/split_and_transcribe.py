#!/usr/bin/env python3
"""
긴 오디오 파일 분할 및 전사 시스템
25MB OpenAI API 제한을 우회하기 위한 자동 분할 전사
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import argparse
import logging
from audio_transcriber import AudioTranscriber


class AudioSplitter:
    """오디오 파일 분할 및 전사 관리 클래스"""

    def __init__(self, segment_duration: int = 600):
        """
        초기화

        Args:
            segment_duration: 분할 단위 (초, 기본값: 600초 = 10분)
        """
        self.segment_duration = segment_duration
        self.temp_folder = Path(__file__).parent.parent / "results" / "audio_temp"
        self.temp_folder.mkdir(parents=True, exist_ok=True)

        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 로깅 설정
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """로깅 시스템 설정"""
        logger = logging.getLogger('AudioSplitter')
        logger.setLevel(logging.INFO)

        # 로그 디렉토리
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)

        # 파일 핸들러
        log_file = log_dir / f'audio_splitter_{self.timestamp}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def get_audio_duration(self, audio_path: Path) -> float:
        """
        오디오 파일 길이 확인 (초)

        Args:
            audio_path: 오디오 파일 경로

        Returns:
            오디오 길이 (초)
        """
        cmd = [
            'ffprobe', '-i', str(audio_path),
            '-show_entries', 'format=duration',
            '-v', 'quiet',
            '-of', 'csv=p=0'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        self.logger.info(f"오디오 길이: {duration:.2f}초 ({duration/60:.1f}분)")
        return duration

    def split_audio(self, audio_path: Path) -> list[Path]:
        """
        오디오 파일을 지정된 길이로 분할

        Args:
            audio_path: 원본 오디오 파일 경로

        Returns:
            분할된 파일 경로 리스트
        """
        self.logger.info(f"오디오 분할 시작: {audio_path.name}")

        # 파일 길이 확인
        duration = self.get_audio_duration(audio_path)
        num_segments = int(duration / self.segment_duration) + 1

        self.logger.info(f"{self.segment_duration}초 단위로 {num_segments}개 조각 생성 예정")

        # 분할 실행
        segment_files = []
        base_name = audio_path.stem

        for i in range(num_segments):
            start_time = i * self.segment_duration
            output_file = self.temp_folder / f"{base_name}_part{i+1:02d}.m4a"

            cmd = [
                'ffmpeg', '-i', str(audio_path),
                '-ss', str(start_time),
                '-t', str(self.segment_duration),
                '-c', 'copy',
                '-y',  # 덮어쓰기
                str(output_file)
            ]

            self.logger.info(f"[{i+1}/{num_segments}] 분할 중: {output_file.name}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                segment_files.append(output_file)
            else:
                self.logger.error(f"분할 실패: {output_file.name}")
                self.logger.error(result.stderr)

        self.logger.info(f"분할 완료: {len(segment_files)}개 파일 생성")
        return segment_files

    def transcribe_segments(
        self,
        segment_files: list[Path],
        language: str = 'ko'
    ) -> list[dict]:
        """
        분할된 파일들을 각각 전사

        Args:
            segment_files: 분할된 파일 경로 리스트
            language: 언어 코드

        Returns:
            전사 결과 리스트
        """
        self.logger.info(f"전사 시작: {len(segment_files)}개 파일")

        transcriber = AudioTranscriber()
        results = []

        for idx, segment_file in enumerate(segment_files, 1):
            self.logger.info(f"[{idx}/{len(segment_files)}] 전사 중: {segment_file.name}")

            result = transcriber.transcribe_audio(segment_file, language=language)

            if result['status'] == 'success':
                # 세그먼트 정보 추가
                result['segment_index'] = idx
                result['segment_file'] = segment_file.name
                results.append(result)
                self.logger.info(f"✅ 전사 완료: {result['statistics']['text_length']} 글자")
            else:
                self.logger.error(f"❌ 전사 실패: {segment_file.name}")
                results.append(result)

        return results

    def merge_transcriptions(
        self,
        results: list[dict],
        original_filename: str
    ) -> dict:
        """
        전사 결과들을 하나로 통합

        Args:
            results: 전사 결과 리스트
            original_filename: 원본 파일명

        Returns:
            통합된 전사 결과
        """
        self.logger.info("전사 결과 통합 중...")

        # 성공한 결과만 필터링
        success_results = [r for r in results if r['status'] == 'success']

        if not success_results:
            self.logger.error("전사 성공한 파일이 없습니다")
            return {
                "filename": original_filename,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": "All segments failed"
            }

        # 전체 텍스트 병합
        full_text = " ".join([r['transcription']['text'] for r in success_results])

        # 통합 결과
        merged_result = {
            "filename": original_filename,
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4o-transcribe",
            "language": success_results[0]['language'],
            "transcription": {
                "text": full_text
            },
            "segments_info": {
                "total_segments": len(results),
                "successful_segments": len(success_results),
                "failed_segments": len(results) - len(success_results)
            },
            "statistics": {
                "text_length": len(full_text),
                "word_count": len(full_text.split())
            },
            "segment_details": [
                {
                    "segment_index": r['segment_index'],
                    "segment_file": r['segment_file'],
                    "text_length": r['statistics']['text_length'],
                    "word_count": r['statistics']['word_count']
                }
                for r in success_results
            ],
            "status": "success"
        }

        self.logger.info(f"통합 완료: {len(full_text)} 글자, {len(full_text.split())} 단어")
        return merged_result

    def cleanup_temp_files(self, segment_files: list[Path]):
        """임시 분할 파일 삭제"""
        self.logger.info("임시 파일 정리 중...")
        for segment_file in segment_files:
            if segment_file.exists():
                segment_file.unlink()
                self.logger.debug(f"삭제: {segment_file.name}")

        self.logger.info("임시 파일 정리 완료")

    def process_large_audio(
        self,
        audio_path: Path,
        language: str = 'ko',
        cleanup: bool = True
    ) -> dict:
        """
        큰 오디오 파일 자동 분할 및 전사 (전체 프로세스)

        Args:
            audio_path: 원본 오디오 파일 경로
            language: 언어 코드
            cleanup: 임시 파일 자동 삭제 여부

        Returns:
            통합된 전사 결과
        """
        self.logger.info(f"=== 큰 오디오 파일 처리 시작: {audio_path.name} ===")

        # 1. 오디오 분할
        segment_files = self.split_audio(audio_path)

        if not segment_files:
            self.logger.error("분할 실패")
            return {
                "filename": audio_path.name,
                "status": "failed",
                "error": "Audio splitting failed"
            }

        # 2. 각 세그먼트 전사
        results = self.transcribe_segments(segment_files, language=language)

        # 3. 결과 통합
        merged_result = self.merge_transcriptions(results, audio_path.name)

        # 4. 결과 저장
        output_folder = Path(__file__).parent.parent / "results" / "audio_transcription"
        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = output_folder / f"{audio_path.stem}_{self.timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_result, f, ensure_ascii=False, indent=2)

        self.logger.info(f"결과 저장: {output_file}")

        # 5. 임시 파일 정리
        if cleanup:
            self.cleanup_temp_files(segment_files)

        self.logger.info("=== 처리 완료 ===")
        return merged_result


def main():
    """CLI 실행"""
    parser = argparse.ArgumentParser(
        description='큰 오디오 파일 자동 분할 및 전사',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
사용 예시:
  # 기본 (10분씩 분할)
  python3 split_and_transcribe.py --file large_audio.m4a --language ko

  # 5분씩 분할
  python3 split_and_transcribe.py --file large_audio.m4a --language ko --segment 300

  # 임시 파일 보존
  python3 split_and_transcribe.py --file large_audio.m4a --language ko --no-cleanup
        '''
    )

    parser.add_argument('--file', type=str, required=True, help='오디오 파일 경로')
    parser.add_argument(
        '--language',
        type=str,
        default='ko',
        help='언어 코드 (ISO-639-1: ko, en 등, 기본값: ko)'
    )
    parser.add_argument(
        '--segment',
        type=int,
        default=600,
        help='분할 단위 (초, 기본값: 600 = 10분)'
    )
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='임시 분할 파일 보존 (기본: 자동 삭제)'
    )

    args = parser.parse_args()

    audio_path = Path(args.file)
    if not audio_path.exists():
        print(f"❌ 파일이 존재하지 않습니다: {audio_path}")
        sys.exit(1)

    try:
        splitter = AudioSplitter(segment_duration=args.segment)
        result = splitter.process_large_audio(
            audio_path,
            language=args.language,
            cleanup=not args.no_cleanup
        )

        if result['status'] == 'success':
            print(f"\n✅ 전사 완료!")
            print(f"📝 총 {result['statistics']['text_length']} 글자")
            print(f"📊 {result['segments_info']['successful_segments']}/{result['segments_info']['total_segments']} 세그먼트 성공")
        else:
            print(f"\n❌ 전사 실패")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
