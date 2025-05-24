import { Component } from '@angular/core';

@Component({
  selector: 'app-visualizer',
  imports: [],
  templateUrl: './visualizer.component.html',
  styleUrl: './visualizer.component.css'
})
export class VisualizerComponent {
  bars = document.querySelectorAll('.bar');

  startAnimation(): void {
    this.bars.forEach(bar => (bar as HTMLElement).style.animationPlayState = 'running');
  }

  stopAnimation(): void {
    this.bars.forEach(bar => (bar as HTMLElement).style.animationPlayState = 'paused');
  }
}
