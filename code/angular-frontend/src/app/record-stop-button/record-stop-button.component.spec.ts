import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecordStopButtonComponent } from './record-stop-button.component';

describe('RecordStopButtonComponent', () => {
  let component: RecordStopButtonComponent;
  let fixture: ComponentFixture<RecordStopButtonComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecordStopButtonComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecordStopButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
