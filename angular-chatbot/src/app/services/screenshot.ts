/**
 * 스크린샷 서비스
 * 브라우저 정보 수집 및 스크린샷 관련 기능을 담당
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, firstValueFrom } from 'rxjs';
import { catchError } from 'rxjs/operators';

// 브라우저 정보 인터페이스
export interface BrowserInfo {
  window: {
    innerWidth: number;
    innerHeight: number;
    outerWidth: number;
    outerHeight: number;
    screenX: number;
    screenY: number;
  };
  screen: {
    width: number;
    height: number;
    availWidth: number;
    availHeight: number;
  };
  chatbot: {
    rect: DOMRect;
    scrollX: number;
    scrollY: number;
  };
  userAgent: string;
  timestamp: string;
}

// 스크린샷 API 응답 인터페이스
interface ScreenshotApiResponse {
  status: string;
  message: string;
  timestamp: string;
  data?: any;
}

// ShowUI 분석 결과 인터페이스
export interface ShowUIAnalysisResult {
  success: boolean;
  query: string;
  coordinates?: [number, number];
  absolute_coordinates?: [number, number];
  image_size?: [number, number];
  result_image_url?: string;
  processing_time?: number;
  display_surface?: string; // 화면 공유 타입 추가
  error?: string;
}

// 서버 클릭 요청 인터페이스
export interface ServerClickRequest {
  x: number;
  y: number;
  browserInfo: BrowserInfo;
  action: string;
  timestamp: string;
}

// 서버 클릭 응답 인터페이스
export interface ServerClickResponse {
  success: boolean;
  message: string;
  clicked_coordinates: [number, number];
  timestamp: string;
  error?: string;
}

// 서버 스크린샷 요청 인터페이스
export interface ServerScreenshotRequest {
  query: string;
  auto_click: boolean;
}

// 서버 스크린샷 응답 인터페이스
export interface ServerScreenshotResponse {
  success: boolean;
  query: string;
  coordinates?: [number, number];
  absolute_coordinates?: [number, number];
  image_size?: [number, number];
  result_image_filename?: string;
  processing_time?: number;
  click_executed?: boolean;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ScreenshotService {
  // API 엔드포인트 설정
  private readonly API_BASE_URL = '/api';
  private readonly SCREENSHOT_ENDPOINT = `${this.API_BASE_URL}/take-screenshot`;
  private readonly SHOWUI_BASE_URL = 'http://localhost:8001';
  private readonly CLICK_ENDPOINT = `${this.SHOWUI_BASE_URL}/api/click-coordinate`;
  

  
  // 브라우저 영역 마스킹 설정 (항상 활성화)
  private readonly maskBrowserEnabled = true;
  
  // 서버 스크린샷 사용 설정
  private useServerScreenshot = true;

  constructor(private http: HttpClient) {}

  /**
   * 화면 캡처 후 ShowUI 분석을 수행
   * @param query 찾고자 하는 UI 요소 설명
   * @returns ShowUI 분석 결과
   */
  async captureAndAnalyzeWithShowUI(query: string): Promise<ShowUIAnalysisResult> {
    try {
      console.log(`화면 캡처 분석 시작: "${query}"`);

      // 서버 스크린샷 사용 시
      if (this.useServerScreenshot) {
        return await this.serverScreenshotAndAnalyze(query);
      }

      // 클라이언트 스크린샷 사용 시 (기존 로직)
      return await this.clientScreenshotAndAnalyze(query);

    } catch (error) {
      console.error('화면 캡처 분석 실패:', error);
      return {
        success: false,
        query: query,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  /**
   * 서버에서 스크린샷 캡처 및 분석
   * @param query 찾고자 하는 UI 요소 설명
   * @returns ShowUI 분석 결과
   */
  private async serverScreenshotAndAnalyze(query: string): Promise<ShowUIAnalysisResult> {
    try {
      console.log('🖥️ 서버 스크린샷 모드 사용');
      
      const requestBody: ServerScreenshotRequest = {
        query: query,
        auto_click: true
      };

      const headers = new HttpHeaders({
        'Content-Type': 'application/json',
      });

      const response = await firstValueFrom(
        this.http.post<ServerScreenshotResponse>(
          `${this.SHOWUI_BASE_URL}/api/server-screenshot-and-find`, 
          requestBody, 
          { headers }
        ).pipe(
          catchError(this.handleShowUIError)
        )
      );

      return {
        success: response.success,
        query: response.query,
        coordinates: response.coordinates,
        absolute_coordinates: response.absolute_coordinates,
        image_size: response.image_size,
        result_image_url: response.result_image_filename ? 
          `${this.SHOWUI_BASE_URL}/download_result/${response.result_image_filename}` : undefined,
        processing_time: response.processing_time,
        display_surface: 'server',
        error: response.error
      };

    } catch (error) {
      throw new Error(`서버 스크린샷 분석 실패: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 클라이언트에서 스크린샷 캡처 및 분석 (기존 로직)
   * @param query 찾고자 하는 UI 요소 설명
   * @returns ShowUI 분석 결과
   */
  private async clientScreenshotAndAnalyze(query: string): Promise<ShowUIAnalysisResult> {
    try {
      console.log('📱 클라이언트 스크린샷 모드 사용');

      // 화면 캡처 API 사용
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        throw new Error('화면 캡처 기능이 지원되지 않는 브라우저입니다.');
      }

      // 브라우저 정보 수집
      const browserInfo = this.getBrowserLocationInfo();
      
      // 화면 캡처 (전체 화면을 우선적으로 선택하도록 힌트 제공)
      const displayMediaOptions: any = {
        video: {
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          frameRate: { ideal: 30 }
        },
        audio: false
      };
      
      // Chrome/Edge에서 전체 화면 우선 선택을 위한 추가 옵션
      if ('getDisplayMedia' in navigator.mediaDevices) {
        displayMediaOptions.preferCurrentTab = false;
        displayMediaOptions.selfBrowserSurface = 'exclude';
        displayMediaOptions.systemAudio = 'exclude';
      }
      
      const stream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions);

      // 선택된 화면 공유 타입 감지
      const videoTrack = stream.getVideoTracks()[0];
      const displaySurface = (videoTrack.getSettings() as any).displaySurface;
      console.log(`화면 공유 타입: ${displaySurface}`);

      // 전체 화면이 아닌 경우 경고
      if (displaySurface !== 'monitor') {
        console.warn('⚠️ 전체 화면이 선택되지 않았습니다. UI 분석 정확도가 떨어질 수 있습니다.');
      }

      // 캔버스로 이미지 캡처
      const capturedImage = await this.captureFrameFromStream(stream, browserInfo, displaySurface);
      
      // ShowUI 서버로 분석 요청
      const analysisResult = await this.sendImageToShowUI(capturedImage, query);
      
      // 화면 공유 타입 정보 추가
      analysisResult.display_surface = displaySurface;
      
      console.log('분석 완료:', analysisResult);
      return analysisResult;

    } catch (error) {
      throw new Error(`클라이언트 스크린샷 분석 실패: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * 스트림에서 프레임을 캡처하여 전체 화면 이미지 생성
   * @param stream 미디어 스트림
   * @param browserInfo 브라우저 정보 (브라우저 영역 제외용)
   * @param displaySurface 화면 공유 타입 ('monitor', 'browser', 'application')
   * @returns Base64 인코딩된 이미지
   */
  private async captureFrameFromStream(stream: MediaStream, browserInfo: BrowserInfo, displaySurface?: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      video.onloadedmetadata = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        if (!ctx) {
          reject(new Error('Canvas 컨텍스트를 가져올 수 없습니다.'));
          return;
        }

        // 전체 화면 크기 설정
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // 전체 화면 그리기
        ctx.drawImage(video, 0, 0);
        
        // 브라우저 영역 마스킹 처리 (전체 화면 캡처 시 항상 적용)
        if (displaySurface === 'monitor') {
          this.maskBrowserArea(ctx, canvas, browserInfo);
        }
        
        const browserX = browserInfo.window.screenX;
        const browserY = browserInfo.window.screenY;
        const browserWidth = browserInfo.window.outerWidth;
        const browserHeight = browserInfo.window.outerHeight;
        
        // 화면 공유 타입에 따른 로깅
        const shareTypeMap: { [key: string]: string } = {
          'monitor': '🖥️ 전체 화면',
          'browser': '🌐 브라우저 탭',
          'application': '📱 애플리케이션 창'
        };
        const shareTypeName = shareTypeMap[displaySurface || 'unknown'] || '❓ 알 수 없음';
        
        console.log(`화면 공유 타입: ${shareTypeName} (${displaySurface})`);
        console.log(`캡처 영역: 브라우저 [${browserX}, ${browserY}] ${browserWidth}×${browserHeight}`);
        
        if (displaySurface === 'monitor') {
          console.log('✅ 브라우저 영역 마스킹 적용됨');
        }
        
        // 스트림 정리
        stream.getTracks().forEach(track => track.stop());
        
        // Base64로 변환 (data:image/png;base64, 제거)
        const dataUrl = canvas.toDataURL('image/png');
        const base64 = dataUrl.split(',')[1];
        
        resolve(base64);
      };

      video.onerror = () => {
        reject(new Error('비디오 로딩 중 오류 발생'));
      };
    });
  }

  /**
   * ShowUI 서버에 이미지 분석 요청
   * @param imageBase64 Base64 인코딩된 이미지
   * @param query 찾고자 하는 UI 요소 설명
   * @returns ShowUI 분석 결과
   */
  private async sendImageToShowUI(imageBase64: string, query: string): Promise<ShowUIAnalysisResult> {
    try {
      const showUIUrl = 'http://localhost:8001/find_click_position';
      
      const requestBody = {
        image_base64: imageBase64,
        query: query
      };

      const response = await firstValueFrom(
        this.http.post<any>(showUIUrl, requestBody, {
          headers: {
            'Content-Type': 'application/json'
          }
        }).pipe(
          catchError(this.handleShowUIError)
        )
      );

      // ShowUI 응답을 우리 형식으로 변환
      return {
        success: response.success,
        query: response.query,
        coordinates: response.coordinates,
        absolute_coordinates: response.absolute_coordinates,
        image_size: response.image_size,
        result_image_url: response.result_image_filename ? 
          `http://localhost:8001/download_result/${response.result_image_filename}` : undefined,
        processing_time: response.processing_time,
        error: response.error
      };

    } catch (error) {
      console.error('서버 요청 실패:', error);
      throw error;
    }
  }

  /**
   * ShowUI 오류 처리
   * @param error HTTP 오류
   * @returns Observable<never>
   */
  private handleShowUIError = (error: any): Observable<never> => {
    let errorMessage = '알 수 없는 오류가 발생했습니다.';
    
    if (error.error instanceof ErrorEvent) {
      errorMessage = `클라이언트 오류: ${error.error.message}`;
    } else {
      switch (error.status) {
        case 0:
          errorMessage = '서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.';
          break;
        case 400:
          errorMessage = '잘못된 요청입니다. 입력 데이터를 확인하세요.';
          break;
        case 422:
          errorMessage = '좌표 파싱에 실패했습니다. 다른 설명으로 다시 시도해보세요.';
          break;
        case 503:
          errorMessage = '모델이 아직 로드되지 않았습니다. 잠시 후 다시 시도하세요.';
          break;
        case 500:
          errorMessage = '서버 내부 오류가 발생했습니다.';
          break;
        default:
          errorMessage = `서버 오류 (${error.status}): ${error.message}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  };

  /**
   * 서버에 화면 좌표 클릭 요청
   * @param x 클릭할 화면 절대 x 좌표
   * @param y 클릭할 화면 절대 y 좌표
   * @returns 서버 클릭 응답
   */
  async requestServerClick(x: number, y: number): Promise<ServerClickResponse> {
    try {
      console.log(`서버에 화면 좌표 [${x}, ${y}] 클릭 요청`);
      
      // 브라우저 정보 수집
      const browserInfo = this.getBrowserLocationInfo();
      
      // 서버에 클릭 요청
      const response = await firstValueFrom(this.callClickAPI(x, y, browserInfo));
      
      if (response) {
        console.log('서버 클릭 처리 완료:', response);
        return response;
      } else {
        throw new Error('서버 응답이 비어있습니다.');
      }
      
    } catch (error) {
      console.error('서버 클릭 요청 실패:', error);
      throw error;
    }
  }

  /**
   * 클릭 API 호출
   * @param x 클릭할 x 좌표
   * @param y 클릭할 y 좌표
   * @param browserInfo 브라우저 정보
   * @returns Observable<ServerClickResponse>
   */
  private callClickAPI(x: number, y: number, browserInfo: BrowserInfo): Observable<ServerClickResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    const requestBody: ServerClickRequest = {
      x: x,
      y: y,
      browserInfo: browserInfo,
      action: 'click_coordinate',
      timestamp: new Date().toISOString()
    };

    return this.http.post<ServerClickResponse>(this.CLICK_ENDPOINT, requestBody, { headers })
      .pipe(
        catchError(this.handleClickError)
      );
  }

  /**
   * 클릭 API 오류 처리
   * @param error HTTP 오류 객체
   * @returns Observable<never>
   */
  private handleClickError = (error: any): Observable<never> => {
    let errorMessage = '알 수 없는 오류가 발생했습니다.';
    
    if (error.error instanceof ErrorEvent) {
      // 클라이언트 측 오류
      errorMessage = `클라이언트 오류: ${error.error.message}`;
    } else {
      // 서버 측 오류
      switch (error.status) {
        case 0:
          errorMessage = '클릭 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.';
          break;
        case 400:
          errorMessage = '잘못된 클릭 요청입니다. 좌표를 확인하세요.';
          break;
        case 403:
          errorMessage = '클릭 권한이 없습니다. 접근성 권한을 확인하세요.';
          break;
        case 500:
          errorMessage = '서버에서 클릭 처리 중 오류가 발생했습니다.';
          break;
        default:
          errorMessage = `클릭 서버 오류 (${error.status}): ${error.message}`;
      }
    }
    
    console.error('ScreenshotService 클릭 오류:', errorMessage);
    return throwError(() => new Error(errorMessage));
  };

  /**
   * 현재 브라우저의 위치 및 크기 정보를 수집
   * @returns BrowserInfo 객체
   */
  getBrowserLocationInfo(): BrowserInfo {
    try {
      return {
        // 브라우저 창 정보
        window: {
          innerWidth: window.innerWidth,
          innerHeight: window.innerHeight,
          outerWidth: window.outerWidth,
          outerHeight: window.outerHeight,
          screenX: window.screenX || 0,
          screenY: window.screenY || 0
        },
        
        // 화면 정보
        screen: {
          width: window.screen.width,
          height: window.screen.height,
          availWidth: window.screen.availWidth,
          availHeight: window.screen.availHeight
        },
        
        // 챗봇 앱 영역 정보
        chatbot: {
          rect: document.body.getBoundingClientRect(),
          scrollX: window.scrollX || 0,
          scrollY: window.scrollY || 0
        },
        
        // 기타 정보
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('브라우저 정보 수집 중 오류 발생:', error);
      
      // 오류 발생 시 기본값 반환
      return this.getDefaultBrowserInfo();
    }
  }

  /**
   * 스크린샷 촬영 요청을 서버에 전송
   * @returns Promise<ScreenshotApiResponse>
   */
  async takeScreenshot(): Promise<ScreenshotApiResponse> {
    try {
      // 브라우저 정보 수집
      const browserInfo = this.getBrowserLocationInfo();
      
      // 서버에 스크린샷 요청
      const response = await firstValueFrom(this.callScreenshotAPI(browserInfo));
      
      if (response) {
        console.log('서버 스크린샷 처리 완료:', response);
        return response;
      } else {
        throw new Error('서버 응답이 비어있습니다.');
      }
      
    } catch (error) {
      console.error('서버 스크린샷 요청 실패:', error);
      throw error;
    }
  }

  /**
   * 스크린샷 API 호출
   * @param browserInfo 브라우저 정보
   * @returns Observable<ScreenshotApiResponse>
   */
  private callScreenshotAPI(browserInfo: BrowserInfo): Observable<ScreenshotApiResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    const requestBody = {
      browserInfo: browserInfo,
      action: 'take_screenshot',
      timestamp: new Date().toISOString()
    };

    return this.http.post<ScreenshotApiResponse>(this.SCREENSHOT_ENDPOINT, requestBody, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * 기본 브라우저 정보 반환 (오류 발생 시 사용)
   * @returns 기본 BrowserInfo 객체
   */
  private getDefaultBrowserInfo(): BrowserInfo {
    return {
      window: {
        innerWidth: 1024,
        innerHeight: 768,
        outerWidth: 1024,
        outerHeight: 800,
        screenX: 0,
        screenY: 0
      },
      screen: {
        width: 1920,
        height: 1080,
        availWidth: 1920,
        availHeight: 1040
      },
      chatbot: {
        rect: new DOMRect(0, 0, 1024, 768),
        scrollX: 0,
        scrollY: 0
      },
      userAgent: 'Unknown',
      timestamp: new Date().toISOString()
    };
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
    
    console.error('ScreenshotService 오류:', errorMessage);
    return throwError(errorMessage);
  }

  /**
   * 브라우저 정보 유효성 검사
   * @param browserInfo 검사할 브라우저 정보
   * @returns 유효하면 true
   */
  isValidBrowserInfo(browserInfo: BrowserInfo): boolean {
    return !!(
      browserInfo && 
      browserInfo.window && 
      browserInfo.screen && 
      browserInfo.chatbot &&
      typeof browserInfo.window.innerWidth === 'number' &&
      typeof browserInfo.window.innerHeight === 'number'
    );
  }

  /**
   * 현재 화면 크기가 모바일인지 확인
   * @returns 모바일 화면이면 true
   */
  isMobileScreen(): boolean {
    return window.innerWidth <= 768;
  }

  /**
   * 현재 화면 크기가 태블릿인지 확인
   * @returns 태블릿 화면이면 true
   */
  isTabletScreen(): boolean {
    return window.innerWidth > 768 && window.innerWidth <= 1024;
  }

  /**
   * 현재 화면 크기가 데스크톱인지 확인
   * @returns 데스크톱 화면이면 true
   */
  isDesktopScreen(): boolean {
    return window.innerWidth > 1024;
  }

  /**
   * 현재 브라우저가 전체화면 모드인지 확인
   * @returns 전체화면이면 true
   */
  isFullscreen(): boolean {
    return !!(
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement
    );
  }

  /**
   * 브라우저 영역을 검정색으로 마스크 처리
   * @param ctx Canvas 2D 컨텍스트
   * @param canvas Canvas 객체
   * @param browserInfo 브라우저 정보
   */
  private maskBrowserArea(ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement, browserInfo: BrowserInfo): void {
    // 브라우저 창 전체 영역 정보
    const browserX = browserInfo.window.screenX;
    const browserY = browserInfo.window.screenY;
    const browserWidth = browserInfo.window.outerWidth;
    const browserHeight = browserInfo.window.outerHeight;
    
    // 화면 해상도와 캔버스 크기를 고려한 스케일 계산
    const scaleX = canvas.width / browserInfo.screen.width;
    const scaleY = canvas.height / browserInfo.screen.height;
    
    // 스케일 적용한 브라우저 영역 좌표
    const maskedX = Math.round(browserX * scaleX);
    const maskedY = Math.round(browserY * scaleY);
    const maskedWidth = Math.round(browserWidth * scaleX);
    const maskedHeight = Math.round(browserHeight * scaleY);
    
    // 경계 검사
    if (maskedX < 0 || maskedY < 0 || 
        maskedX + maskedWidth > canvas.width || 
        maskedY + maskedHeight > canvas.height) {
      console.warn('브라우저 영역이 캔버스 범위를 벗어남:', {
        maskedArea: [maskedX, maskedY, maskedWidth, maskedHeight],
        canvasSize: [canvas.width, canvas.height]
      });
      return;
    }
    
    // 검정색으로 마스크 처리
    ctx.fillStyle = '#000000';
    ctx.fillRect(maskedX, maskedY, maskedWidth, maskedHeight);
    
    console.log(`브라우저 영역 마스킹: [${maskedX}, ${maskedY}] ${maskedWidth}×${maskedHeight}`);
    console.log(`스케일 비율: X=${scaleX.toFixed(3)}, Y=${scaleY.toFixed(3)}`);
  }

  /**
   * 서버 스크린샷 모드 활성화
   */
  enableServerScreenshot(): void {
    this.useServerScreenshot = true;
    console.log('🖥️ 서버 스크린샷 모드 활성화됨');
  }

  /**
   * 서버 스크린샷 모드 비활성화 (클라이언트 모드)
   */
  disableServerScreenshot(): void {
    this.useServerScreenshot = false;
    console.log('📱 클라이언트 스크린샷 모드 활성화됨');
  }

  /**
   * 서버 스크린샷 모드 상태 조회
   * @returns 서버 스크린샷 모드가 활성화되어 있으면 true
   */
  isServerScreenshotEnabled(): boolean {
    return this.useServerScreenshot;
  }

  /**
   * 서버 스크린샷 모드 토글
   * @returns 변경 후 서버 스크린샷 모드 상태
   */
  toggleServerScreenshot(): boolean {
    this.useServerScreenshot = !this.useServerScreenshot;
    console.log(this.useServerScreenshot ? '🖥️ 서버 스크린샷 모드 활성화됨' : '📱 클라이언트 스크린샷 모드 활성화됨');
    return this.useServerScreenshot;
  }
}
