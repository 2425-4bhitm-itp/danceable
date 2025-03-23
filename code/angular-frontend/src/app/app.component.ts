import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {RecordStopButtonComponent} from './record-stop-button/record-stop-button.component';
import {RecordButtonComponent} from './record-button/record-button.component';
import {NavbarComponent} from './navbar/navbar.component';


@Component({
  selector: 'app-root',
  imports: [RecordStopButtonComponent, RecordButtonComponent, NavbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'angular-frontend';
}
