/**
 * 애플리케이션 설정
 * 프로바이더 및 라우팅 설정을 포함
 */

import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    // Zone.js 변경 감지 최적화
    provideZoneChangeDetection({ eventCoalescing: true }), 
    
    // 라우터 프로바이더
    provideRouter(routes),
    
    // HTTP 클라이언트 프로바이더 (인터셉터 지원)
    provideHttpClient(withInterceptorsFromDi())
  ]
};
