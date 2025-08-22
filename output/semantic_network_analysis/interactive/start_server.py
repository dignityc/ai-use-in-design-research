#!/usr/bin/env python3
"""
로컬 웹 서버 시작 스크립트
인터랙티브 대시보드를 로컬 서버에서 실행
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import signal
from pathlib import Path

def start_local_server():
    """로컬 HTTP 서버 시작"""
    
    # 현재 디렉토리를 interactive 폴더로 변경
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    PORT = 8080
    
    print("🌐 AI Design Research 시맨틱 네트워크 대시보드")
    print("=" * 60)
    print(f"🚀 로컬 서버 시작 중... (포트: {PORT})")
    
    try:
        # HTTP 서버 설정
        Handler = http.server.SimpleHTTPRequestHandler
        Handler.extensions_map.update({
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.html': 'text/html'
        })
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ 서버 시작 완료!")
            print(f"📁 서빙 디렉토리: {script_dir}")
            print()
            print("🔗 대시보드 접속 방법:")
            print(f"   👆 자체 완성형 (권장): http://localhost:{PORT}/self_contained_english_dashboard.html")
            print(f"   🌐 일반 버전:        http://localhost:{PORT}/english_dashboard.html")
            print()
            print("🎮 사용법:")
            print("   • 키워드 클릭: 연결된 키워드들 하이라이트")
            print("   • 검색: 상단 검색바에 키워드 입력")
            print("   • 필터링: 왼쪽 체크박스로 AI Method/Design Task 필터")
            print("   • 레이아웃: 드롭다운에서 다양한 배치 방식 선택")
            print("   • 드래그: 키워드를 끌어서 위치 조정")
            print()
            print("💡 추천 탐색 시나리오:")
            print('   1. "artificial intelligence" 검색 → 클릭 → 연결된 키워드들 확인')
            print('   2. "Generative AI"만 체크 → Gen AI 생태계 탐색')  
            print('   3. 레이아웃을 "원형"으로 변경 → 다른 관점에서 보기')
            print()
            print("🛑 서버 종료: Ctrl+C")
            print("=" * 60)
            
            # 자동으로 브라우저 열기
            dashboard_url = f"http://localhost:{PORT}/self_contained_english_dashboard.html"
            print(f"🌟 브라우저에서 대시보드 열기: {dashboard_url}")
            
            try:
                webbrowser.open(dashboard_url)
                print("✅ 브라우저 자동 오픈 완료!")
            except:
                print("⚠️  브라우저 자동 오픈 실패. 수동으로 위 URL을 열어주세요.")
            
            print()
            
            # 서버 실행
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\\n🛑 서버 종료됨. 대시보드를 종료합니다.")
        print("👋 감사합니다!")
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 포트 {PORT}가 이미 사용 중입니다.")
            print("다른 포트를 시도하거나 기존 서버를 종료하세요.")
            
            # 대안 포트들 시도
            for alt_port in [8081, 8082, 8083]:
                try:
                    print(f"🔄 포트 {alt_port} 시도 중...")
                    with socketserver.TCPServer(("", alt_port), Handler) as httpd:
                        dashboard_url = f"http://localhost:{alt_port}/self_contained_english_dashboard.html"
                        print(f"✅ 대안 포트에서 서버 시작: {dashboard_url}")
                        webbrowser.open(dashboard_url)
                        httpd.serve_forever()
                except OSError:
                    continue
            
            print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
            
        else:
            print(f"❌ 서버 시작 실패: {e}")

def signal_handler(sig, frame):
    """Ctrl+C 신호 처리"""
    print('\\n🛑 사용자가 서버를 종료했습니다.')
    print('👋 시맨틱 네트워크 탐험 즐거우셨나요?')
    sys.exit(0)

if __name__ == "__main__":
    # Ctrl+C 신호 처리 설정
    signal.signal(signal.SIGINT, signal_handler)
    
    print()
    print("🎯 시작하기 전에...")
    print("   이 스크립트는 로컬 웹 서버를 시작합니다.")
    print("   브라우저가 자동으로 열리고 대시보드에 접속됩니다.")
    print("   서버 종료는 Ctrl+C를 누르세요.")
    print()
    
    try:
        input("🚀 시작하려면 Enter를 누르세요... ")
        start_local_server()
    except KeyboardInterrupt:
        print("\\n👋 시작을 취소했습니다.")
        sys.exit(0)