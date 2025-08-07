/**
 * 메시지 입력 컴포넌트
 * 사용자의 메시지 입력을 처리하고 전송 기능을 제공
 */

import { Component, EventEmitter, Output, Input, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-message-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './message-input.html',
  styleUrl: './message-input.css'
})
export class MessageInputComponent implements AfterViewInit {
  // 부모 컴포넌트로부터 받는 로딩 상태
  @Input() isLoading: boolean = false;

  // 부모 컴포넌트에게 메시지 전송을 알리는 이벤트 발생기
  @Output() messageSubmitted = new EventEmitter<string>();

  // 텍스트 입력 영역의 참조 (자동 크기 조절용)
  @ViewChild('messageTextarea', { static: false }) 
  private messageTextarea!: ElementRef<HTMLTextAreaElement>;

  // 현재 입력 중인 메시지 내용
  messageContent: string = '';

  ngAfterViewInit(): void {
    // 컴포넌트 초기화 후 텍스트 영역에 이벤트 리스너 추가
    this.setupTextareaAutoResize();
  }

  /**
   * 텍스트 영역 자동 크기 조절 설정
   * 내용에 따라 높이를 동적으로 조절
   */
  private setupTextareaAutoResize(): void {
    if (this.messageTextarea && this.messageTextarea.nativeElement) {
      const textarea = this.messageTextarea.nativeElement;
      
      // input 이벤트 리스너 추가
      textarea.addEventListener('input', () => {
        this.adjustTextareaHeight();
      });
    }
  }

  /**
   * 텍스트 영역 높이를 내용에 맞게 조절
   * 최소 높이와 최대 높이 제한 적용
   */
  private adjustTextareaHeight(): void {
    if (this.messageTextarea && this.messageTextarea.nativeElement) {
      const textarea = this.messageTextarea.nativeElement;
      
      // 높이를 초기화한 후 실제 스크롤 높이로 설정
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, 120); // 최대 120px
      textarea.style.height = newHeight + 'px';
    }
  }

  /**
   * 키보드 이벤트 처리
   * Enter: 메시지 전송, Shift+Enter: 줄바꿈
   */
  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * 전송 버튼 클릭 시 호출되는 메서드
   */
  onSendClick(): void {
    this.sendMessage();
  }

  /**
   * 메시지 전송 처리
   * 유효성 검사 후 부모 컴포넌트에게 이벤트 발생
   */
  private sendMessage(): void {
    const trimmedMessage = this.messageContent.trim();
    
    // 빈 메시지이거나 로딩 중일 때는 전송하지 않음
    if (!trimmedMessage || this.isLoading) {
      return;
    }

    // 부모 컴포넌트에게 메시지 전송 이벤트 발생
    this.messageSubmitted.emit(trimmedMessage);

    // 입력 필드 초기화
    this.messageContent = '';
    
    // 텍스트 영역 높이 초기화
    this.resetTextareaHeight();

    // 포커스를 텍스트 영역으로 다시 이동
    this.focusTextarea();
  }

  /**
   * 텍스트 영역 높이를 기본값으로 초기화
   */
  private resetTextareaHeight(): void {
    if (this.messageTextarea && this.messageTextarea.nativeElement) {
      this.messageTextarea.nativeElement.style.height = 'auto';
    }
  }

  /**
   * 텍스트 영역에 포커스 설정
   */
  private focusTextarea(): void {
    if (this.messageTextarea && this.messageTextarea.nativeElement) {
      // 약간의 지연 후 포커스 설정 (UI 업데이트 완료 대기)
      setTimeout(() => {
        this.messageTextarea.nativeElement.focus();
      }, 0);
    }
  }

  /**
   * 전송 버튼 활성화 상태 반환
   * @returns 메시지가 있고 로딩 중이 아닐 때 true
   */
  get canSend(): boolean {
    return this.messageContent.trim().length > 0 && !this.isLoading;
  }
}
