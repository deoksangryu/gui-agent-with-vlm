/**
 * 메인 앱 컴포넌트
 * 챗봇 애플리케이션의 최상위 컴포넌트로 상태 관리와 자식 컴포넌트 간의 통신을 담당
 */

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

// 자식 컴포넌트들 import
import { HeaderComponent } from './components/header/header';
import { ChatMessagesComponent } from './components/chat-messages/chat-messages';
import { MessageInputComponent } from './components/message-input/message-input';

// 서비스들 import
import { ChatService } from './services/chat';
import { ScreenshotService, ShowUIAnalysisResult, ServerClickResponse } from './services/screenshot';

// 인터페이스 정의
export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    HeaderComponent,
    ChatMessagesComponent,
    MessageInputComponent
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent implements OnInit {
  title = 'angular-chatbot-app';

  // 채팅 메시지 배열 - 모든 대화 내용을 저장
  messages: Message[] = [];

  // 로딩 상태 - AI 응답 대기 중일 때 true
  isLoading = false;

  // 모달 표시 상태 및 내용
  showModal = false;
  modalTitle = '';
  modalContent = '';

  // 자동 클릭 예약 관리
  private autoClickTimer: any = null;
  private isAutoClickScheduled = false;

  constructor(
    private chatService: ChatService,
    private screenshotService: ScreenshotService
  ) {}

  ngOnInit(): void {
    // 컴포넌트 초기화 시 필요한 설정이 있다면 여기에 추가
    console.log('챗봇 애플리케이션이 초기화되었습니다.');
    
    // 사용법 안내 메시지 추가
    const welcomeMessage: Message = {
      id: this.generateMessageId(),
      content: `👋 **UI Automation Chatbot**\n\n💡 Enter the UI element to find within quotes`,
      isUser: false,
      timestamp: new Date()
    };
    this.messages.push(welcomeMessage);
  }

  /**
   * 사용자가 메시지를 제출했을 때 호출되는 핸들러
   * @param messageContent 사용자가 입력한 메시지 내용
   */
  async handleMessageSubmit(messageContent: string): Promise<void> {
    if (!messageContent.trim() || this.isLoading) {
      return;
    }

    const trimmedMessage = messageContent.trim();

    // 자동 클릭 취소 명령어 확인
    if (this.isAutoClickScheduled && 
        (trimmedMessage.toLowerCase() === '취소' || 
         trimmedMessage.toLowerCase() === 'cancel' || 
         trimmedMessage.toLowerCase() === '취소하기')) {
      
      // 사용자 메시지 추가
      const userMessage: Message = {
        id: this.generateMessageId(),
        content: trimmedMessage,
        isUser: true,
        timestamp: new Date()
      };
      this.messages.push(userMessage);
      
      // 자동 클릭 취소
      this.cancelAutoClick();
      return;
    }

    // 로딩 상태 시작
    this.isLoading = true;

    try {
      // '화면 설명' 커맨드 처리
      if (trimmedMessage === '화면 설명') {
        // 사용자 메시지 추가
        const userMessage: Message = {
          id: this.generateMessageId(),
          content: trimmedMessage,
          isUser: true,
          timestamp: new Date()
        };
        this.messages.push(userMessage);
        
        await this.handleScreenDescription();
        return;
      }

      // UI 찾기 패턴 확인 (따옴표 안의 텍스트)
      const uiSearchPattern = /'([^']+)'/;
      const match = trimmedMessage.match(uiSearchPattern);
      
      if (match && match[1]) {
        // UI 찾기 명령으로 처리 (사용자 메시지 추가하지 않음)
        const targetElement = match[1].trim();
        await this.handleUISearchFromChat(targetElement, trimmedMessage);
        return;
      }

      // 일반 채팅 메시지일 경우에만 사용자 메시지 추가
      const userMessage: Message = {
        id: this.generateMessageId(),
        content: trimmedMessage,
        isUser: true,
        timestamp: new Date()
      };
      this.messages.push(userMessage);

      // 일반 채팅 메시지로 처리
      await this.handleRegularChat(trimmedMessage);

    } catch (error) {
      console.error('메시지 전송 중 오류 발생:', error);
      
      // 오류 메시지를 AI 응답으로 추가
      const errorMessage: Message = {
        id: this.generateMessageId(),
        content: 'Sorry, an error occurred. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(errorMessage);
    } finally {
      // 로딩 상태 종료
      this.isLoading = false;
    }
  }

  /**
   * 채팅에서 UI 찾기 명령 처리
   * @param targetElement 찾을 UI 요소
   * @param originalMessage 원본 메시지
   */
  private async handleUISearchFromChat(targetElement: string, originalMessage: string): Promise<void> {
    try {
      this.currentQuery = targetElement;
      
      // 서버 모드인지 확인
      const isServerMode = this.screenshotService.isServerScreenshotEnabled();
      
      // 클라이언트 모드일 때만 화면 공유 안내 메시지 표시
      if (!isServerMode) {
        const guideMessage: Message = {
          id: this.generateMessageId(),
          content: `📺 Screen sharing dialog will appear. Please select "Entire Screen" (not browser tab) for accurate UI detection.`,
          isUser: false,
          timestamp: new Date()
        };
        this.messages.push(guideMessage);
      }
      
      // 스크린샷 캡처 및 ShowUI 분석 실행
      const result = await this.screenshotService.captureAndAnalyzeWithShowUI(targetElement);
      
      // 분석 메시지 표시
      const analysisMessage: Message = {
        id: this.generateMessageId(),
        content: `🔍 Analyzing screen for UI element...`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(analysisMessage);

      // 결과 처리
      this.displayShowUIResult(result);
      
    } catch (error) {
      console.error('UI 요소 검색 중 오류 발생:', error);
      const errorMessage: Message = {
        id: this.generateMessageId(),
        content: `❌ Error occurred while searching for UI element.`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(errorMessage);
    }
  }

  /**
   * 일반 채팅 메시지 처리
   * @param messageContent 메시지 내용
   */
  private async handleRegularChat(messageContent: string): Promise<void> {
    // 브라우저 정보 수집
    const browserInfo = this.screenshotService.getBrowserLocationInfo();
    
    // ChatService를 통해 AI 응답 요청
    const aiResponse = await this.chatService.sendMessageWithBrowserInfo(
      messageContent,
      browserInfo
    );

    // AI 응답을 메시지 배열에 추가
    const aiMessage: Message = {
      id: this.generateMessageId(),
      content: aiResponse,
      isUser: false,
      timestamp: new Date()
    };
    this.messages.push(aiMessage);
  }

  /**
   * '화면 설명' 커맨드 처리
   */
  private async handleScreenDescription(): Promise<void> {
    try {
      // Qwen2VL 서버 상태 확인
      const isServerAvailable = await this.chatService.checkQwen2vlServerHealth();
      if (!isServerAvailable) {
        throw new Error('Qwen2VL 서버에 연결할 수 없습니다.');
      }
      
      // 서버에서 스크린샷 캡처 및 분석
      const analysisResult = await this.chatService.analyzeScreenshotWithQwen2vl('현재 화면에 있는 내용을 설명해주세요.');
      
      // 응답 추가
      const responseMessage: Message = {
        id: this.generateMessageId(),
        content: analysisResult,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(responseMessage);
      
    } catch (error) {
      console.error('❌ 화면 설명 분석 실패:', error);
      const errorMessage: Message = {
        id: this.generateMessageId(),
        content: `화면 설명 분석 중 오류가 발생했습니다: ${error}`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(errorMessage);
    }
  }

  /**
   * 헤더 컴포넌트에서 ShowUI 스크린샷 분석 요청이 발생했을 때 호출되는 핸들러
   */
  async handleShowUIScreenshotRequest(): Promise<void> {
    // 서버 모드인지 확인
    const isServerMode = this.screenshotService.isServerScreenshotEnabled();
    const modeText = isServerMode ? "server will capture the screen automatically" : "you'll need to select screen sharing";
    
    // 사용자에게 찾고자 하는 UI 요소 설명을 입력받음
    const query = prompt(`Please describe the UI element you want to find on the screen:\n(${modeText})\n\nExample: "Login button", "Search box", "Menu icon"`);
    
    if (!query || !query.trim()) {
      return; // 사용자가 취소하거나 빈 값을 입력한 경우
    }

    // UI 찾기 모드에서는 채팅 메시지를 추가하지 않고 바로 분석 실행
    this.currentQuery = query.trim();
    this.executeShowUIAnalysis();
  }

  // 현재 쿼리 저장
  currentQuery: string = '';

  /**
   * 실제 화면 분석 실행 (간소화됨)
   */
  async executeShowUIAnalysis(): Promise<void> {
    this.isLoading = true;

    try {
      // ShowUI 화면 캡처 및 분석 수행
      const result = await this.screenshotService.captureAndAnalyzeWithShowUI(this.currentQuery);
      
      // 캡처 완료 후 분석 시작 메시지 표시
      const analysisMessage: Message = {
        id: this.generateMessageId(),
        content: `🔍 Analyzing screen for "${this.currentQuery}" UI element...`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(analysisMessage);
      
      // 분석 결과를 채팅에 표시
      this.displayShowUIResult(result);
      
    } catch (error) {
      console.error('ShowUI 스크린샷 분석 중 오류 발생:', error);
      
      // 오류 메시지만 추가
      const errorMessage: Message = {
        id: this.generateMessageId(),
        content: `❌ Error occurred during ShowUI analysis.\nError: ${error instanceof Error ? error.message : String(error)}`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(errorMessage);
    } finally {
      // 로딩 상태 종료
      this.isLoading = false;
      this.currentQuery = '';
    }
  }

  /**
   * ShowUI 분석 결과를 채팅 메시지로 표시
   * @param result ShowUI 분석 결과
   */
  private displayShowUIResult(result: ShowUIAnalysisResult): void {
    console.log('ShowUI 분석 결과:', result);
    
    if (result.success && result.coordinates) {
      // 화면 공유 타입에 따른 아이콘 매핑
      const shareTypeMap: { [key: string]: string } = {
        'monitor': '🖥️',
        'browser': '🌐', 
        'application': '📱'
      };
      const shareIcon = shareTypeMap[result.display_surface || 'unknown'] || '📸';

      // 성공한 경우 간단한 결과 메시지 추가
      const resultMessage: Message = {
        id: this.generateMessageId(),
        content: `✅ Found!`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(resultMessage);

      // Y 좌표 조정 (+5 픽셀로 더 정확한 클릭)
      const adjustedX = result.absolute_coordinates![0] - 60;
      const adjustedY = result.absolute_coordinates![1] + 80;
      
      // 더블 클릭 실행 (포커스 + 실제 클릭)
      //this.executeBrowserClick(adjustedX, adjustedX);
      this.executeDoubleClick(adjustedX, adjustedY);
      
    } else {
      // 실패한 경우 오류 메시지 추가
      const errorMessage: Message = {
        id: this.generateMessageId(),
        content: `❌ Analysis failed\n\n` +
                 `• Search term: "${result.query}"\n` +
                 `• Error: ${result.error}`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(errorMessage);
    }
  }

  /**
   * 지정된 시간 후 화면의 절대 좌표 위치를 클릭
   * @param x 클릭할 x 좌표 (화면 절대 좌표)
   * @param y 클릭할 y 좌표 (화면 절대 좌표)
   * @param delaySeconds 클릭 실행까지 대기할 시간 (초)
   */
  private scheduleAutoClick(x: number, y: number, delaySeconds: number = 5): void {
    console.log(`${delaySeconds}초 후 좌표 [${x}, ${y}]를 클릭합니다.`);
    
    // 이전 타이머가 있다면 취소
    this.cancelAutoClick();
    
    // 자동 클릭 예약 상태 설정
    this.isAutoClickScheduled = true;
    
    // 카운트다운 표시
    let countdown = delaySeconds;
    this.autoClickTimer = setInterval(() => {
      countdown--;
      
              if (countdown <= 0 && this.isAutoClickScheduled) {
          clearInterval(this.autoClickTimer);
          this.autoClickTimer = null;
          this.isAutoClickScheduled = false;
          // 실제 클릭 실행
          this.executeClick(x, y);
        } else if (!this.isAutoClickScheduled) {
          // 취소된 경우
          clearInterval(this.autoClickTimer);
          this.autoClickTimer = null;
        }
    }, 1000);
  }

  /**
   * 예약된 자동 클릭을 취소
   */
  private cancelAutoClick(): void {
    if (this.autoClickTimer) {
      clearInterval(this.autoClickTimer);
      this.autoClickTimer = null;
    }
    
    if (this.isAutoClickScheduled) {
      this.isAutoClickScheduled = false;
      
      const cancelMessage: Message = {
        id: this.generateMessageId(),
        content: `🚫 Auto click canceled.`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(cancelMessage);
      
      console.log('Auto click canceled.');
    }
  }

  /**
   * 포커스 맞추기 + 실제 클릭을 위한 더블 클릭 실행
   * @param x 클릭할 x 좌표 (화면 절대 좌표)
   * @param y 클릭할 y 좌표 (화면 절대 좌표)
   */
  private async executeDoubleClick(x: number, y: number): Promise<void> {
    try {
      console.log(`더블 클릭 시작: 좌표 [${x}, ${y}]`);
      
      // 첫 번째 클릭 (포커스 맞줌 완료, 1초 후 실제 클릭...);
      console.log('1단계: 포커스 맞줌 완료, 1초 후 실제 클릭...');
      await this.executeClick(x, y, true); // silent = true
      
      // 중간 진행 상황 메시지
      const focusMessage: Message = {
        id: this.generateMessageId(),
        content: `🎯 Focus set, clicking in 1 second...`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(focusMessage);
      
      // 1초 대기
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 두 번째 클릭 (실제 액션) - 메시지 출력
      console.log('2단계: 실제 액션 클릭 실행');
      await this.executeClick(x, y, false); // silent = false
      
      console.log('더블 클릭 완료');
      
    } catch (error) {
      console.error('더블 클릭 실행 중 오류 발생:', error);
      
      const errorMessage: Message = {
        id: this.generateMessageId(),
        content: `❌ Error occurred during double click execution.`,
        isUser: false,
        timestamp: new Date()
      };
      this.messages.push(errorMessage);
    }
  }

  /**
   * 화면의 절대 좌표 위치에 클릭 이벤트를 발생시킴 (서버 기반)
   * @param x 클릭할 x 좌표 (화면 절대 좌표)
   * @param y 클릭할 y 좌표 (화면 절대 좌표)
   * @param silent 메시지 출력 여부 (기본값: false)
   */
  private async executeClick(x: number, y: number, silent: boolean = false): Promise<void> {
    try {
      console.log(`서버를 통해 화면 좌표 [${x}, ${y}]에 클릭 요청 (silent: ${silent})`);
      
      // 서버에 클릭 요청 전송
      const clickResult = await this.screenshotService.requestServerClick(x, y);
      
      if (clickResult.success) {
        // 서버 클릭 성공 - 조용한 모드가 아닐 때만 메시지 출력
        if (!silent) {
          const successMessage: Message = {
            id: this.generateMessageId(),
            content: `✅ Click completed!`,
            isUser: false,
            timestamp: new Date()
          };
          this.messages.push(successMessage);
        }
        
        console.log('서버 클릭 완료:', clickResult);
        
      } else {
        // 서버 클릭 실패 - 항상 오류 메시지 출력
        const errorMessage: Message = {
          id: this.generateMessageId(),
          content: `❌ Click failed: ${clickResult.error || clickResult.message}`,
          isUser: false,
          timestamp: new Date()
        };
        this.messages.push(errorMessage);
      }
      
    } catch (error) {
      console.error('서버 클릭 요청 중 오류 발생:', error);
      
      // 서버 연결 실패 시 폴백: 브라우저 내 클릭 시도
      if (!silent) {
        const fallbackMessage: Message = {
          id: this.generateMessageId(),
          content: `⚠️ Server connection failed, trying browser click...`,
          isUser: false,
          timestamp: new Date()
        };
        this.messages.push(fallbackMessage);
      }
      
      // 폴백: 기존 브라우저 내 클릭 로직 실행
      this.executeBrowserClick(x, y, silent);
    }
  }

  /**
   * 브라우저 내에서 클릭 실행 (폴백 기능)
   * @param x 클릭할 x 좌표 (화면 절대 좌표)
   * @param y 클릭할 y 좌표 (화면 절대 좌표)
   * @param silent 메시지 출력 여부 (기본값: false)
   */
  private executeBrowserClick(x: number, y: number, silent: boolean = false): void {
    try {
      console.log(`브라우저 내에서 좌표 [${x}, ${y}] 클릭 시도`);
      
      // 브라우저 창의 위치와 크기 정보 가져오기
      const browserInfo = this.screenshotService.getBrowserLocationInfo();
      
      // 화면 절대 좌표를 브라우저 윈도우 상대 좌표로 변환
      const windowX = x - browserInfo.window.screenX;
      const windowY = y - browserInfo.window.screenY;
      
      // 브라우저 창 경계 확인
      if (windowX < 0 || windowY < 0 || 
          windowX > browserInfo.window.outerWidth || 
          windowY > browserInfo.window.outerHeight) {
        
        if (!silent) {
          const warningMessage: Message = {
            id: this.generateMessageId(),
            content: `⚠️ Click position is outside the browser area.`,
            isUser: false,
            timestamp: new Date()
          };
          this.messages.push(warningMessage);
        }
        return;
      }

      // 브라우저 내부 콘텐츠 영역으로 좌표 조정
      const chromeHeight = browserInfo.window.outerHeight - browserInfo.window.innerHeight;
      const contentX = windowX;
      const contentY = windowY - chromeHeight;
      
      // 뷰포트 경계 확인
      if (contentX < 0 || contentY < 0 || 
          contentX > browserInfo.window.innerWidth || 
          contentY > browserInfo.window.innerHeight) {
        
        if (!silent) {
          const warningMessage: Message = {
            id: this.generateMessageId(),
            content: `⚠️ Click position is outside the content area.`,
            isUser: false,
            timestamp: new Date()
          };
          this.messages.push(warningMessage);
        }
        return;
      }
      
      // 클릭할 요소 찾기
      const targetElement = document.elementFromPoint(contentX, contentY);
      
      if (targetElement) {
        // 클릭 이벤트 발생
        const clickEvent = new MouseEvent('click', {
          view: window,
          bubbles: true,
          cancelable: true,
          clientX: contentX,
          clientY: contentY,
          screenX: x,
          screenY: y,
          button: 0
        });
        
        targetElement.dispatchEvent(clickEvent);
        
        // 포커스 설정
        if (targetElement instanceof HTMLInputElement || 
            targetElement instanceof HTMLTextAreaElement || 
            targetElement instanceof HTMLSelectElement) {
          targetElement.focus();
        }
        
        // 클릭 성공 메시지 - 조용한 모드가 아닐 때만 출력
        if (!silent) {
          const successMessage: Message = {
            id: this.generateMessageId(),
            content: `✅ Click completed!`,
            isUser: false,
            timestamp: new Date()
          };
          this.messages.push(successMessage);
        }
        
        console.log('브라우저 내 클릭 완료:', targetElement);
        
      } else {
        if (!silent) {
          const errorMessage: Message = {
            id: this.generateMessageId(),
            content: `❌ No clickable element found.`,
            isUser: false,
            timestamp: new Date()
          };
          this.messages.push(errorMessage);
        }
      }
      
    } catch (error) {
      console.error('브라우저 내 클릭 실행 중 오류 발생:', error);
      
      if (!silent) {
        const errorMessage: Message = {
          id: this.generateMessageId(),
          content: `❌ Error occurred during click execution.`,
          isUser: false,
          timestamp: new Date()
        };
        this.messages.push(errorMessage);
      }
    }
  }

  /**
   * HTML 요소의 정보를 문자열로 반환
   * @param element HTML 요소
   * @returns 요소 정보 문자열
   */
  private getElementInfo(element: Element): string {
    const tag = element.tagName.toLowerCase();
    const id = element.id ? `#${element.id}` : '';
    const classes = element.className ? `.${element.className.split(' ').filter(c => c).join('.')}` : '';
    const text = element.textContent?.trim().substring(0, 30) || '';
    const textInfo = text ? ` "${text}${text.length > 30 ? '...' : ''}"` : '';
    
    return `${tag}${id}${classes}${textInfo}`;
  }

  /**
   * 헤더 컴포넌트에서 스크린샷 요청이 발생했을 때 호출되는 핸들러
   */
  async handleScreenshotRequest(): Promise<void> {
    try {
      // ScreenshotService를 통해 스크린샷 처리
      const screenshotResult = await this.screenshotService.takeScreenshot();
      
      // 성공 시 결과를 모달로 표시
      this.showScreenshotModal(screenshotResult);
      
    } catch (error) {
      console.error('스크린샷 처리 중 오류 발생:', error);
      
      // 오류 시 브라우저 정보만 표시
      const browserInfo = this.screenshotService.getBrowserLocationInfo();
      this.showBrowserInfoModal(browserInfo);
    }
  }

  /**
   * 스크린샷 결과를 모달로 표시
   * @param result 스크린샷 처리 결과
   */
  private showScreenshotModal(result: any): void {
    this.modalTitle = 'Screenshot Processing Complete';
    this.modalContent = `
      <div style="text-align: left; font-family: monospace; font-size: 0.875rem; line-height: 1.6;">
        <p><strong>Status:</strong> ${result.status || 'Complete'}</p>
        <p><strong>Processing Time:</strong> ${result.timestamp || new Date().toISOString()}</p>
        <p><strong>Additional Info:</strong> ${result.message || 'Screenshot processed successfully.'}</p>
      </div>
    `;
    this.showModal = true;
  }

  /**
   * 브라우저 정보를 모달로 표시
   * @param browserInfo 브라우저 위치 및 크기 정보
   */
  private showBrowserInfoModal(browserInfo: any): void {
    this.modalTitle = 'Browser Location Info (for Server)';
    this.modalContent = `
      <div style="text-align: left; font-family: monospace; font-size: 0.875rem; line-height: 1.6;">
        <p><strong>Browser Window:</strong></p>
        <p>• Position: (${browserInfo.window.screenX}, ${browserInfo.window.screenY})</p>
        <p>• Size: ${browserInfo.window.outerWidth} × ${browserInfo.window.outerHeight}</p>
        <p>• Inner: ${browserInfo.window.innerWidth} × ${browserInfo.window.innerHeight}</p>
        
        <p style="margin-top: 1rem;"><strong>Screen Info:</strong></p>
        <p>• Resolution: ${browserInfo.screen.width} × ${browserInfo.screen.height}</p>
        
        <p style="margin-top: 1rem;"><strong>Chatbot Area:</strong></p>
        <p>• Position: (${Math.round(browserInfo.chatbot.rect.left)}, ${Math.round(browserInfo.chatbot.rect.top)})</p>
        <p>• Size: ${Math.round(browserInfo.chatbot.rect.width)} × ${Math.round(browserInfo.chatbot.rect.height)}</p>
      </div>
    `;
    this.showModal = true;
  }

  /**
   * 모달을 닫는 함수
   */
  closeModal(): void {
    this.showModal = false;
    this.modalTitle = '';
    this.modalContent = '';
  }

  /**
   * 고유한 메시지 ID 생성
   * @returns 고유한 문자열 ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 서버 스크린샷 모드 토글
   */
  toggleServerScreenshot(): void {
    const isEnabled = this.screenshotService.toggleServerScreenshot();
    const message: Message = {
      id: this.generateMessageId(),
      content: isEnabled 
        ? '🖥️ Server screenshot mode enabled. Screenshots will be captured on the server.'
        : '📱 Client screenshot mode enabled. Screenshots will be captured in the browser.',
      isUser: false,
      timestamp: new Date()
    };
    this.messages.push(message);
  }
}
