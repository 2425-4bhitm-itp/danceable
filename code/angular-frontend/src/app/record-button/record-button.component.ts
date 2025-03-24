import { Component } from '@angular/core';
import {RecordStopButtonComponent} from '../record-stop-button/record-stop-button.component';
import {RecordSvgComponent} from '../record-svg/record-svg.component';
import {VisualizerComponent} from '../visualizer/visualizer.component';

@Component({
  selector: 'app-record-button',
  imports: [
    RecordStopButtonComponent,
    RecordSvgComponent,
    VisualizerComponent
  ],
  templateUrl: './record-button.component.html',
  styleUrl: './record-button.component.css',
})
export class RecordButtonComponent {
  buttonState = true
}
