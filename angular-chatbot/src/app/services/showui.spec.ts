import { TestBed } from '@angular/core/testing';

import { Showui } from './showui';

describe('Showui', () => {
  let service: Showui;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Showui);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
