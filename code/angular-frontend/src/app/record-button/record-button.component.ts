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
  visualizer: VisualizerComponent = new VisualizerComponent();
  buttonState: boolean = false;

  toggleRecording() {
    this.buttonState = !this.buttonState;
    console.log(this.buttonState ? "Recording started" : "Recording stopped");
    if(this.buttonState){
      setTimeout(() => {
        this.buttonState = false;
        this.stopAnimation();
        console.log("Recording stopped automatically after 5 seconds");
      }, 5000);
      this.stopAnimation()
    } else {
      this.startAnimation()
    }
  }

  startAnimation(): void{
    this.visualizer.startAnimation();
  }

  stopAnimation(): void{
    this.visualizer.stopAnimation();
  }
}
