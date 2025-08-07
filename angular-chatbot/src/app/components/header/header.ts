/**
 * 헤더 컴포넌트
 * 애플리케이션 상단의 로고와 스크린샷 버튼을 담당
 */

import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ScreenshotService } from '../../services/screenshot';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.css'
})
export class HeaderComponent {
  // 부모 컴포넌트에게 ShowUI 스크린샷 분석 요청을 알리는 이벤트 발생기
  @Output() showUIScreenshotRequested = new EventEmitter<void>();
  
  // 부모 컴포넌트에게 서버 스크린샷 토글 요청을 알리는 이벤트 발생기
  @Output() serverToggleRequested = new EventEmitter<void>();

  constructor(private screenshotService: ScreenshotService) {}

  /**
   * 서버 모드 상태 확인
   * @returns 서버 모드가 활성화되어 있으면 true
   */
  isServerMode(): boolean {
    return this.screenshotService.isServerScreenshotEnabled();
  }

  /**
   * 서버 모드 버튼 텍스트 반환
   * @returns 현재 모드에 따른 버튼 텍스트
   */
  getServerToggleText(): string {
    return this.isServerMode() ? '🖥️ 서버모드' : '📱 클라이언트모드';
  }

  /**
   * 서버 스크린샷 토글 버튼 클릭 시 호출되는 메서드
   * 부모 컴포넌트에게 서버 토글 요청 이벤트를 발생시킴
   */
  onServerToggleClick(): void {
    console.log('서버 스크린샷 토글 버튼이 클릭되었습니다.');
    this.serverToggleRequested.emit();
  }

  /**
   * ShowUI 스크린샷 분석 버튼 클릭 시 호출되는 메서드
   * 부모 컴포넌트에게 ShowUI 스크린샷 분석 요청 이벤트를 발생시킴
   */
  onShowUIScreenshotClick(): void {
    console.log('ShowUI 스크린샷 분석 버튼이 클릭되었습니다.');
    this.showUIScreenshotRequested.emit();
  }
}
