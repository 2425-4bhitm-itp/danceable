import {Component, EventEmitter, Output} from '@angular/core';

@Component({
  selector: 'app-record-stop-button',
  imports: [],
  templateUrl: './record-stop-button.component.html',
  styleUrl: './record-stop-button.component.css'
})
export class RecordStopButtonComponent {
  @Output() stop = new EventEmitter<void>();
}
