import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { NavbarComponent } from './app/navbar/navbar.component';
import { RecordButtonComponent } from './app/record-button/record-button.component';
import {RecordStopButtonComponent} from './app/record-stop-button/record-stop-button.component';
import {Visualizer} from "./app/classes/Visualizer";
import { StreamRecorder } from "./app/classes/StreamRecorder";

  bootstrapApplication(NavbarComponent, appConfig)
  .catch((err) => console.error(err));

  bootstrapApplication(RecordButtonComponent, appConfig)
  .catch((err) => console.error(err));

  bootstrapApplication(RecordStopButtonComponent, appConfig)
    .catch((err)=> console.error(err));

let recorder = new StreamRecorder();

const recordButton = document.querySelector("app-record-button") as HTMLButtonElement;
const stopRecordButton = document.getElementById('record-stop-button') as HTMLButtonElement;

// audio visualizer

const visualMainElement = document.querySelector('#visualizer') as HTMLElement;
const visualValueCount = 16; // do not change
let visualElements: NodeListOf<HTMLDivElement>;

let visualizer: Visualizer;

let timeoutId: NodeJS.Timeout | null = null;
let intervalId: NodeJS.Timeout | null = null;

const createDOMElements = () => {
  for (let i = 0; i < visualValueCount; ++i) {
    visualMainElement.appendChild(document.createElement('div'));
  }

  visualElements = document.querySelectorAll('#visualizer div');
};

const init = () => {
  const audioContext = new AudioContext();

  visualMainElement.innerHTML = '';
  createDOMElements();

  //Swapping values around for a better visual effect
  const dataMap: { [key: number]: number } = {
    0: 15,
    1: 10,
    2: 8,
    3: 9,
    4: 6,
    5: 5,
    6: 2,
    7: 1,
    8: 0,
    9: 4,
    10: 3,
    11: 7,
    12: 11,
    13: 12,
    14: 13,
    15: 14
  };
  // create Mapping object for sorting frequency data for visualizing

  const processFrame = (data: Uint8Array): void => {
    const values = Array.from(data);
    // frequencydata in array
    for (let i = 0; i < visualValueCount; ++i) {
      // loop for number of visualizingElements
      const value = values[dataMap[i]] / 255;
      // get values form dataMap-object and normalise
      const elmStyles = visualElements[i].style;
      elmStyles.transform = `scaleY(${value})`;
      // elmStyles.opacity = Math.max(0, value);
      // change opacity of div elements based of frequency data
    }
  };

  const processError = (): void => {
    visualMainElement.classList.add('error');
    visualMainElement.innerText = 'Please allow access to your microphone to record audio';
  };

  visualizer = new Visualizer(audioContext, processFrame, processError);
};

recordButton.addEventListener('click', async () => {
  changeButtonStylingWhenRecordingStarted();
  await recorder.startRecording();
  init();

  // clearTimeoutIfExists();

  startTimer(5, async () => {
    await stopRecordingAndVisualizer();
  });

  // timeoutId = setTimeout(async () => {
  //     await stopRecordingAndVisualizer();
  // }, 1000 * 5);
});

stopRecordButton.addEventListener('click', async () => {
  await stopRecordingAndVisualizer();
});

async function stopRecordingAndVisualizer() {
  stopTimer();

  if (visualizer) {
    visualizer.stopVisualizer();
    document.querySelector("#visualizer")!.innerHTML = "";
  }

  changeRecordButtonStylingWhenRecordingStopped();

  await recorder.stopRecording();
  recorder.playAudio();

  await recorder.sendRecordedAudio();
}

function changeRecordButtonStylingWhenRecordingStopped(): void {
 if (recordButton){
   recordButton.style.display = "flex";
   stopRecordButton.classList.remove('flex');
   stopRecordButton.classList.add('hidden')
 }
}

function changeButtonStylingWhenRecordingStarted(): void {

  if (stopRecordButton) {
    recordButton.style.display = "hidden";
    stopRecordButton.classList.remove('hidden');
    stopRecordButton.classList.add('block');
  }
}

function clearTimeoutIfExists() {
  if (timeoutId) {
    clearTimeout(timeoutId);
    timeoutId = null;
  }
}

function startTimer(timeInSeconds: number, toDowWhenTimerOver: Function) {
  let timerBox = document.getElementById("timer");

  if (timerBox) {
    timerBox.innerHTML = String(timeInSeconds);

    intervalId = setInterval(() => {
      timeInSeconds -= 1
      timerBox.innerHTML = String(timeInSeconds);
      if (timeInSeconds <= 0) {
        stopTimer();
        toDowWhenTimerOver();
      }
    }, 1000);
  }
}

function stopTimer() {
  let timerBox = document.getElementById("timer");

  if (timerBox && intervalId) {
    clearInterval(intervalId);
    intervalId = null;
    timerBox.innerHTML = '';
  }
}
