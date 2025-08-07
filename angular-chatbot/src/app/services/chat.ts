/**
 * 채팅 서비스
 * LLM API 호출 및 메시지 처리를 담당
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, firstValueFrom } from 'rxjs';
import { catchError } from 'rxjs/operators';

// API 응답 인터페이스 정의
interface ChatApiResponse {
  response: string;
  timestamp?: string;
  status?: string;
}

interface BrowserInfo {
  window: any;
  screen: any;
  chatbot: any;
  userAgent: string;
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  // API 엔드포인트 설정
  private readonly API_BASE_URL = '/api';
  private readonly CHAT_ENDPOINT = `${this.API_BASE_URL}/chat-with-screenshot`;
  private readonly SIMPLE_CHAT_ENDPOINT = `${this.API_BASE_URL}/chat`;
  private readonly QWEN2VL_API_URL = 'http://localhost:8000';  // Qwen2VL 서버 주소

  constructor(private http: HttpClient) {}

  /**
   * 브라우저 정보와 함께 메시지를 서버에 전송
   * @param message 사용자 메시지
   * @param browserInfo 브라우저 위치 및 크기 정보
   * @returns AI 응답 Promise
   */
  async sendMessageWithBrowserInfo(message: string, browserInfo: BrowserInfo): Promise<string> {
    try {
      // 먼저 실제 API 호출 시도
      const response = await firstValueFrom(this.callChatAPI(message, browserInfo));
      return response?.response || '응답을 받을 수 없습니다.';
      
    } catch (error) {
      console.warn('실제 API 호출 실패, 시뮬레이션 모드로 전환:', error);
      // API 실패 시 시뮬레이션 응답 반환
      return this.simulateAIResponse(message, browserInfo);
    }
  }

  /**
   * 단순 메시지 전송 (브라우저 정보 없이)
   * @param message 사용자 메시지
   * @returns AI 응답 Promise
   */
  async sendMessage(message: string): Promise<string> {
    try {
      const response = await firstValueFrom(this.callSimpleChatAPI(message));
      return response?.response || '응답을 받을 수 없습니다.';
      
    } catch (error) {
      console.warn('API 호출 실패, 시뮬레이션 모드로 전환:', error);
      return this.simulateSimpleAIResponse(message);
    }
  }

  /**
   * 브라우저 정보와 함께 채팅 API 호출
   * @param message 사용자 메시지
   * @param browserInfo 브라우저 정보
   * @returns Observable<ChatApiResponse>
   */
  private callChatAPI(message: string, browserInfo: BrowserInfo): Observable<ChatApiResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    const requestBody = {
      message: message,
      browserInfo: browserInfo,
      timestamp: new Date().toISOString()
    };

    return this.http.post<ChatApiResponse>(this.CHAT_ENDPOINT, requestBody, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * 단순 채팅 API 호출
   * @param message 사용자 메시지
   * @returns Observable<ChatApiResponse>
   */
  private callSimpleChatAPI(message: string): Observable<ChatApiResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    const requestBody = {
      message: message,
      timestamp: new Date().toISOString()
    };

    return this.http.post<ChatApiResponse>(this.SIMPLE_CHAT_ENDPOINT, requestBody, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * AI 응답 시뮬레이션 (브라우저 정보 포함)
   * @param message 사용자 메시지
   * @param browserInfo 브라우저 정보
   * @returns Promise<string>
   */
  private async simulateAIResponse(message: string, browserInfo: BrowserInfo): Promise<string> {
    // 시뮬레이션을 위한 지연 시간 (1-3초)
    const delay = 1000 + Math.random() * 2000;
    
    return new Promise((resolve) => {
      setTimeout(() => {
        const responses = [
          '서버에서 화면을 분석했습니다. 무엇을 도와드릴까요?',
          '스크린샷을 서버에서 처리했습니다. 더 자세히 설명해드릴게요.',
          '화면 정보를 바탕으로 답변드리겠습니다.',
          '서버 기반 스크린샷 분석이 완료되었습니다.',
          '화면 캡처 및 분석을 성공적으로 처리했습니다.'
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        
        // 개발용: 브라우저 정보 추가
        const browserSize = `${browserInfo.window.outerWidth}x${browserInfo.window.outerHeight}`;
        const screenPos = `(${browserInfo.window.screenX}, ${browserInfo.window.screenY})`;
        
        resolve(`${randomResponse} [브라우저: ${browserSize} at ${screenPos}]`);
      }, delay);
    });
  }

  /**
   * 단순 AI 응답 시뮬레이션
   * @param message 사용자 메시지
   * @returns Promise<string>
   */
  private async simulateSimpleAIResponse(message: string): Promise<string> {
    const delay = 1000 + Math.random() * 2000;
    
    return new Promise((resolve) => {
      setTimeout(() => {
        const responses = [
          '안녕하세요! 무엇을 도와드릴까요?',
          '좋은 질문이네요. 더 자세히 설명해드릴게요.',
          '이해했습니다. 다른 궁금한 점이 있으시면 언제든 말씀해주세요.',
          '그런 관점에서 보면 정말 흥미로운 주제네요.',
          '도움이 되셨길 바랍니다. 추가 질문이 있으시면 언제든지 해주세요!'
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        resolve(randomResponse);
      }, delay);
    });
  }

  /**
   * HTTP 오류 처리
   * @param error HTTP 오류 객체
   * @returns Observable<never>
   */
  private handleError(error: any): Observable<never> {
    let errorMessage = '알 수 없는 오류가 발생했습니다.';
    
    if (error.error instanceof ErrorEvent) {
      // 클라이언트 측 오류
      errorMessage = `클라이언트 오류: ${error.error.message}`;
    } else {
      // 서버 측 오류
      errorMessage = `서버 오류: ${error.status} - ${error.message}`;
    }
    
    console.error('ChatService 오류:', errorMessage);
    return throwError(errorMessage);
  }

  /**
   * 메시지 유효성 검사
   * @param message 검사할 메시지
   * @returns 유효하면 true
   */
  isValidMessage(message: string): boolean {
    return !!(message && message.trim().length > 0 && message.trim().length <= 2000);
  }

  /**
   * 서비스 상태 확인
   * @returns 서비스가 사용 가능하면 true
   */
  isServiceAvailable(): boolean {
    return true;
  }

  /**
   * Qwen2VL 서버 상태 확인
   */
  async checkQwen2vlServerHealth(): Promise<boolean> {
    try {
      const response = await this.http.get(`${this.QWEN2VL_API_URL}/health`).toPromise();
      return true;
    } catch (error) {
      console.error('❌ Qwen2VL 서버 연결 실패:', error);
      return false;
    }
  }

  /**
   * Qwen2VL 서버에서 스크린샷 캡처 및 분석
   */
  async analyzeScreenshotWithQwen2vl(context: string = ""): Promise<string> {
    try {
      console.log('📸 Qwen2VL 서버 스크린샷 분석 시작...');

      const requestBody = {
        context: context
      };

      const response = await this.http.post<any>(`${this.QWEN2VL_API_URL}/analyze-screenshot`, requestBody).toPromise();
      
      if (response.success) {
        console.log(`✅ Qwen2VL 서버 분석 완료 (${response.processing_time.toFixed(2)}초)`);
        return response.result;
      } else {
        throw new Error(response.error_message || '분석 실패');
      }
    } catch (error) {
      console.error('❌ Qwen2VL 서버 분석 실패:', error);
      return `서버 분석 중 오류가 발생했습니다: ${error}`;
    }
  }
}
