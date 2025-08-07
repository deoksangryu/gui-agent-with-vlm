/**
 * 채팅 메시지 컴포넌트
 * 대화 내역을 표시하고 로딩 상태를 관리
 * 새로운 스크롤 레이아웃에 맞게 스크롤 로직 개선
 */

import { Component, Input, OnChanges, SimpleChanges, AfterViewChecked, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../app';

@Component({
  selector: 'app-chat-messages',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chat-messages.html',
  styleUrl: './chat-messages.css'
})
export class ChatMessagesComponent implements OnChanges, AfterViewChecked {
  // 부모 컴포넌트로부터 받는 메시지 배열
  @Input() messages: Message[] = [];
  
  // 부모 컴포넌트로부터 받는 로딩 상태
  @Input() isLoading: boolean = false;

  // 채팅 메시지 컨테이너의 참조 (스크롤 제어용)
  @ViewChild('messagesContainer', { static: false }) 
  private messagesContainer!: ElementRef;

  // 스크롤이 필요한지 추적하는 플래그
  private shouldScrollToBottom = false;

  /**
   * Input 속성이 변경될 때 호출되는 라이프사이클 훅
   * 새 메시지가 추가되거나 로딩 상태가 변경되면 스크롤을 하단으로 이동하도록 플래그 설정
   */
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['messages'] && changes['messages'].currentValue) {
      this.shouldScrollToBottom = true;
    }
    if (changes['isLoading']) {
      this.shouldScrollToBottom = true;
    }
  }

  /**
   * 뷰가 체크된 후 호출되는 라이프사이클 훅
   * 필요시 스크롤을 하단으로 이동
   */
  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  /**
   * 메시지 컨테이너의 스크롤을 하단으로 이동
   * 새로운 레이아웃에서는 상위 스크롤 영역을 찾아서 스크롤
   */
  private scrollToBottom(): void {
    try {
      // 현재 컴포넌트에서 상위로 올라가며 스크롤 가능한 영역 찾기
      let scrollElement = this.messagesContainer?.nativeElement;
      
      if (scrollElement) {
        // 상위 요소 중 chat-scroll-area 클래스를 가진 요소 찾기
        while (scrollElement && !scrollElement.classList?.contains('chat-scroll-area')) {
          scrollElement = scrollElement.parentElement;
        }
        
        // 스크롤 가능한 요소를 찾았다면 하단으로 스크롤
        if (scrollElement) {
          setTimeout(() => {
            scrollElement.scrollTop = scrollElement.scrollHeight;
          }, 0);
        }
      }
    } catch (error) {
      console.warn('스크롤 이동 중 오류:', error);
    }
  }

  /**
   * 메시지가 비어있는지 확인
   * @returns 메시지 배열이 비어있으면 true
   */
  get isEmpty(): boolean {
    return !this.messages || this.messages.length === 0;
  }

  /**
   * 메시지 추적을 위한 TrackBy 함수 (성능 최적화)
   * @param index 배열 인덱스
   * @param message 메시지 객체
   * @returns 추적 키로 사용할 메시지 ID
   */
  trackByMessageId(index: number, message: Message): string {
    return message.id;
  }
}
