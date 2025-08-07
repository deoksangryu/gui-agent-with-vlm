#!/usr/bin/env python3
"""
좌표 정확도 검증 도구
사용자가 화면을 클릭해서 실제 좌표를 확인할 수 있습니다.
"""

import time
import pyautogui
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading

class CoordinateChecker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("좌표 확인 도구")
        self.root.geometry("400x300")
        
        # 화면 크기 정보
        self.screen_width, self.screen_height = pyautogui.size()
        
        self.create_widgets()
        
    def create_widgets(self):
        # 정보 표시
        info_label = tk.Label(
            self.root, 
            text=f"화면 크기: {self.screen_width} × {self.screen_height}",
            font=("Arial", 12)
        )
        info_label.pack(pady=10)
        
        # 설명
        instruction = tk.Label(
            self.root,
            text="아래 버튼을 누르고 5초 후에\n원하는 위치를 클릭하세요",
            font=("Arial", 10),
            justify="center"
        )
        instruction.pack(pady=10)
        
        # 좌표 확인 버튼
        check_button = tk.Button(
            self.root,
            text="좌표 확인하기",
            command=self.start_coordinate_check,
            font=("Arial", 12),
            bg="lightblue",
            width=15,
            height=2
        )
        check_button.pack(pady=20)
        
        # 결과 표시 영역
        self.result_text = tk.Text(
            self.root,
            height=8,
            width=50,
            font=("Courier", 10)
        )
        self.result_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 초기 메시지
        self.result_text.insert("end", "좌표 확인 결과가 여기에 표시됩니다.\n\n")
        
    def start_coordinate_check(self):
        """좌표 확인 시작"""
        def countdown_and_check():
            # 카운트다운
            for i in range(5, 0, -1):
                self.result_text.insert("end", f"{i}초 후 클릭하세요...\n")
                self.result_text.see("end")
                self.root.update()
                time.sleep(1)
            
            self.result_text.insert("end", "지금 클릭하세요!\n")
            self.result_text.see("end")
            self.root.update()
            
            # 마우스 위치 모니터링
            start_pos = pyautogui.position()
            self.result_text.insert("end", f"대기 중... (현재 위치: {start_pos})\n")
            
            # 클릭 감지 (간단한 방법: 마우스 위치 변화 감지)
            clicked_pos = None
            timeout = 30  # 30초 타임아웃
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                current_pos = pyautogui.position()
                if current_pos != start_pos:
                    # 위치가 바뀌면 0.5초 대기 후 해당 위치 기록
                    time.sleep(0.5)
                    clicked_pos = pyautogui.position()
                    break
                time.sleep(0.1)
            
            if clicked_pos:
                self.result_text.insert("end", f"\n✅ 클릭 감지!\n")
                self.result_text.insert("end", f"📍 클릭된 좌표: [{clicked_pos.x}, {clicked_pos.y}]\n")
                self.result_text.insert("end", f"🕐 시간: {time.strftime('%H:%M:%S')}\n")
                self.result_text.insert("end", "-" * 40 + "\n")
            else:
                self.result_text.insert("end", "⏰ 타임아웃: 클릭이 감지되지 않았습니다.\n")
            
            self.result_text.see("end")
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=countdown_and_check)
        thread.daemon = True
        thread.start()
    
    def run(self):
        """앱 실행"""
        self.root.mainloop()

def main():
    """메인 함수"""
    print("좌표 확인 도구를 시작합니다...")
    
    # pyautogui 안전 설정
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    app = CoordinateChecker()
    app.run()

if __name__ == "__main__":
    main() 