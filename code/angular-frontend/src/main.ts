import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { NavbarComponent } from './app/navbar/navbar.component';
import { RecordButtonComponent } from './app/record-button/record-button.component';


bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));

  bootstrapApplication(NavbarComponent, appConfig)
  .catch((err) => console.error(err));

  bootstrapApplication(RecordButtonComponent, appConfig)
  .catch((err) => console.error(err));