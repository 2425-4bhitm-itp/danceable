import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import {Visualizer} from "./app/classes/Visualizer";
import { StreamRecorder } from "./app/classes/StreamRecorder";

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));




