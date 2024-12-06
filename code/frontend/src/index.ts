import './style/style.css';
import './style/tailwind.css';

import {Visualizer} from "./classes/Visualizer";
import { StreamRecorder } from "./classes/StreamRecorder";

let recorder = new StreamRecorder();

const recordButton = document.getElementById('recordBtn') as HTMLButtonElement;
const stopRecordButton = document.getElementById('recordStopBtn') as HTMLButtonElement;

// audio visualizer

const visualMainElement = document.querySelector('#visualizer') as HTMLElement;
const visualValueCount = 16; // do not change
let visualElements: NodeListOf<HTMLDivElement>;

let visualizer: Visualizer;

let timeoutId: number | any = null;

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

recordButton.addEventListener('click', () => {
    changeButtonStylingWhenRecordingStarted();
    recorder.startRecording().then();
    init();

    clearTimeoutIfExists();

    timeoutId = setTimeout(async () => {
        await stopRecordingAndVisualizer();
    }, 1000 * 5);
});

stopRecordButton.addEventListener('click', async () => {
    await stopRecordingAndVisualizer();
});

async function stopRecordingAndVisualizer() {
    clearTimeoutIfExists();

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
    let recordIcon = document.getElementById("recordIcon");
    let recordingDescription = document.getElementById("recording-description");
    let stopBtn = document.getElementById('recordStopBtn');

    if (recordIcon && recordingDescription && stopBtn) {
        recordIcon.style.display = "block";
        recordingDescription.style.display = "block";
        stopBtn.classList.remove('block');
        stopBtn.classList.add('hidden');
    }
}

function changeButtonStylingWhenRecordingStarted(): void {
    let recordingDescription = document.getElementById("recording-description");
    let stopBtn = document.getElementById("recordStopBtn");
    let svg = document.getElementById("svg");

    if (recordingDescription && stopBtn && svg) {
        svg.style.display = "none";
        recordingDescription.style.display = "none";
        stopBtn.classList.remove('hidden');
        stopBtn.classList.add('block');
    }
}

function clearTimeoutIfExists() {
    if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
    }
}