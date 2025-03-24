import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecordSvgComponent } from './record-svg.component';

describe('RecordSvgComponent', () => {
  let component: RecordSvgComponent;
  let fixture: ComponentFixture<RecordSvgComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecordSvgComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecordSvgComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
