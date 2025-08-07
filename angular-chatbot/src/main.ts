/**
 * Angular 애플리케이션의 메인 진입점
 * 애플리케이션을 부트스트랩하고 설정을 적용
 */

import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app';

// 애플리케이션 부트스트랩
bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error('애플리케이션 시작 중 오류 발생:', err));
