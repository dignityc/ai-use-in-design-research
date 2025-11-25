#!/usr/bin/env python3
"""
오디오 파일 자동 전사 시스템
OpenAI Whisper API (gpt-4o-transcribe)를 활용한 음성-텍스트 변환
정확도 최우선 설정
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import argparse
import logging
import json
from typing import Dict, List, Optional
from openai import OpenAI


class AudioTranscriber:
    """오디오 파일 자동 전사 클래스 (정확도 최우선)"""

    SUPPORTED_FORMATS = ['.mp3', '.mp4', '.wav', '.m4a', '.flac', '.ogg', '.webm', '.mpeg', '.mpga']

    def __init__(self, output_folder: Optional[str] = None):
        """
        초기화

        Args:
            output_folder: 결과 저장 폴더 (None이면 기본 경로 사용)
        """
        # 기본 경로 설정
        if output_folder is None:
            output_folder = str(Path(__file__).parent.parent / "results" / "audio_transcription")

        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 로깅 설정
        self.logger = self._setup_logging()

        # OpenAI 클라이언트
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

        self.client = OpenAI(api_key=api_key)

        self.logger.info("AudioTranscriber 초기화 완료")
        self.logger.info(f"결과 저장 경로: {self.output_folder}")

    def _setup_logging(self) -> logging.Logger:
        """로깅 시스템 설정"""
        logger = logging.getLogger('AudioTranscriber')
        logger.setLevel(logging.INFO)

        # 로그 디렉토리
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)

        # 파일 핸들러
        log_file = log_dir / f'audio_transcriber_{self.timestamp}.log'
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

    def transcribe_audio(
        self,
        audio_path: Path,
        language: str = 'ko',
        model: str = 'gpt-4o-transcribe'
    ) -> Dict:
        """
        단일 오디오 파일 전사 (정확도 최우선)

        Args:
            audio_path: 오디오 파일 경로
            language: ISO-639-1 언어 코드 (예: 'ko', 'en')
            model: 전사 모델 (기본: gpt-4o-transcribe)

        Returns:
            전사 결과 딕셔너리 (전체 API 응답 + 메타데이터)
        """
        self.logger.info(f"전사 시작: {audio_path.name} (언어: {language}, 모델: {model})")

        try:
            with open(audio_path, 'rb') as audio_file:
                # OpenAI Whisper API 호출 (정확도 최우선 설정)
                # gpt-4o-transcribe는 response_format='json'만 지원
                transcript = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=language,
                    response_format='json',  # gpt-4o-transcribe 필수 형식
                    temperature=0  # 최대 일관성 (정확도 우선)
                )

            # API 응답을 딕셔너리로 변환
            # gpt-4o-transcribe는 기본 JSON 형식 (text 위주)
            result = {
                "filename": audio_path.name,
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "language": language,
                "transcription": {
                    "text": transcript.text
                },
                "status": "success"
            }

            # 추가 필드가 있으면 포함 (선택적)
            if hasattr(transcript, 'language'):
                result["transcription"]["detected_language"] = transcript.language
            if hasattr(transcript, 'duration'):
                result["transcription"]["duration"] = transcript.duration

            # 전사 텍스트 통계
            text_length = len(transcript.text)
            word_count = len(transcript.text.split())
            result["statistics"] = {
                "text_length": text_length,
                "word_count": word_count
            }

            self.logger.info(f"전사 완료: {audio_path.name} ({text_length} 글자, {word_count} 단어)")
            return result

        except Exception as e:
            self.logger.error(f"전사 실패: {audio_path.name} - {str(e)}")
            return {
                "filename": audio_path.name,
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "language": language,
                "error": str(e),
                "status": "failed"
            }

    def save_result(self, result: Dict, audio_path: Path) -> Path:
        """
        전사 결과를 JSON 파일로 저장

        Args:
            result: 전사 결과 딕셔너리
            audio_path: 원본 오디오 파일 경로

        Returns:
            저장된 JSON 파일 경로
        """
        # 파일명: {원본파일명}_{타임스탬프}.json
        base_name = audio_path.stem
        output_file = self.output_folder / f"{base_name}_{self.timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        self.logger.info(f"결과 저장: {output_file.name}")
        return output_file

    def process_single_file(self, audio_path: Path, language: str = 'ko') -> Optional[Path]:
        """
        단일 오디오 파일 처리

        Args:
            audio_path: 오디오 파일 경로
            language: 언어 코드

        Returns:
            저장된 JSON 파일 경로 (실패 시 None)
        """
        if not audio_path.exists():
            self.logger.error(f"파일이 존재하지 않습니다: {audio_path}")
            return None

        if audio_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            self.logger.warning(f"지원하지 않는 파일 형식: {audio_path.suffix}")
            return None

        # 전사 실행
        result = self.transcribe_audio(audio_path, language=language)

        # 결과 저장
        if result['status'] == 'success':
            return self.save_result(result, audio_path)
        else:
            # 실패한 경우도 JSON으로 저장 (에러 기록)
            return self.save_result(result, audio_path)

    def process_folder(
        self,
        folder_path: Path,
        language: str = 'ko',
        file_format: Optional[str] = None
    ) -> List[Path]:
        """
        폴더 내 모든 오디오 파일 배치 처리

        Args:
            folder_path: 오디오 파일 폴더 경로
            language: 언어 코드
            file_format: 특정 확장자만 처리 (예: 'mp3', None이면 모든 형식)

        Returns:
            저장된 JSON 파일 경로 리스트
        """
        if not folder_path.exists() or not folder_path.is_dir():
            self.logger.error(f"폴더가 존재하지 않습니다: {folder_path}")
            return []

        # 파일 목록 수집
        if file_format:
            pattern = f"*.{file_format.lstrip('.')}"
            audio_files = list(folder_path.glob(pattern))
        else:
            audio_files = [
                f for f in folder_path.iterdir()
                if f.suffix.lower() in self.SUPPORTED_FORMATS
            ]

        if not audio_files:
            self.logger.warning(f"처리할 오디오 파일이 없습니다: {folder_path}")
            return []

        self.logger.info(f"총 {len(audio_files)}개 파일 처리 시작")

        # 배치 처리
        results = []
        for idx, audio_file in enumerate(audio_files, 1):
            self.logger.info(f"[{idx}/{len(audio_files)}] 처리 중: {audio_file.name}")
            result_path = self.process_single_file(audio_file, language=language)
            if result_path:
                results.append(result_path)

        self.logger.info(f"배치 처리 완료: {len(results)}/{len(audio_files)} 성공")
        return results


def main():
    """CLI 실행"""
    parser = argparse.ArgumentParser(
        description='오디오 파일 자동 전사 (OpenAI gpt-4o-transcribe)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
사용 예시:
  # 단일 파일 전사 (한국어)
  python3 audio_transcriber.py --file audio.mp3 --language ko

  # 폴더 배치 처리 (영어)
  python3 audio_transcriber.py --folder /path/to/audio --language en

  # 특정 확장자만 (mp3)
  python3 audio_transcriber.py --folder /path/to/audio --language ko --format mp3

  # 백그라운드 실행
  nohup python3 audio_transcriber.py --folder /path/to/audio --language ko > ../logs/transcriber.log 2>&1 &
        '''
    )

    # 입력 방식
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', type=str, help='단일 오디오 파일 경로')
    input_group.add_argument('--folder', type=str, help='오디오 파일 폴더 경로')

    # 옵션
    parser.add_argument(
        '--language',
        type=str,
        default='ko',
        help='언어 코드 (ISO-639-1: ko, en, ja, zh 등, 기본값: ko)'
    )
    parser.add_argument(
        '--format',
        type=str,
        help='특정 파일 확장자만 처리 (예: mp3, wav)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='결과 저장 폴더 (기본값: coding_work/results/audio_transcription)'
    )

    args = parser.parse_args()

    try:
        # AudioTranscriber 초기화
        transcriber = AudioTranscriber(output_folder=args.output)

        # 단일 파일 처리
        if args.file:
            audio_path = Path(args.file)
            result_path = transcriber.process_single_file(audio_path, language=args.language)

            if result_path:
                print(f"\n✅ 전사 완료!")
                print(f"📄 결과 파일: {result_path}")
            else:
                print(f"\n❌ 전사 실패")
                sys.exit(1)

        # 폴더 배치 처리
        elif args.folder:
            folder_path = Path(args.folder)
            result_paths = transcriber.process_folder(
                folder_path,
                language=args.language,
                file_format=args.format
            )

            if result_paths:
                print(f"\n✅ 배치 처리 완료!")
                print(f"📁 총 {len(result_paths)}개 파일 전사 완료")
                print(f"📂 결과 폴더: {transcriber.output_folder}")
            else:
                print(f"\n❌ 처리된 파일이 없습니다")
                sys.exit(1)

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
