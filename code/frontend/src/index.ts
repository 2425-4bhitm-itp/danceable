import './style/style.css';
import './style/tailwind.css';
import { startRecording, stopRecording, sendRecordedAudio } from "./mediaRecorder";
import {Visualizer} from "./Visualizer";

console.log("💃💃💃");

// selins part (media recorder)

// Access DOM elements with appropriate type assertions
const recordButton = document.getElementById('recordBtn') as HTMLButtonElement;
const stopRecordButton = document.getElementById('recordStopBtn') as HTMLButtonElement;

// audio visualizer

const visualMainElement = document.querySelector('#visualizer') as HTMLElement;
const visualValueCount = 16;
let visualElements: NodeListOf<HTMLDivElement>;

let visualizer: Visualizer;

let timeoutId: number | any = null;

// Main element is chosen and visualizing elements is set to 16
const createDOMElements = () => {
    //function for creating DOM elements
    let i;
    for (i = 0; i < visualValueCount; ++i) {
        //loop for 16 iterations
        const elm = document.createElement('div');
        visualMainElement.appendChild(elm);
        // div is created and added to main

    }
    visualElements = document.querySelectorAll('#visualizer div');
    // all divs in main are saved in visualElements
};

// createDOMElements();
//show ausgangsstellung

const init = () => {
    // Creating initial DOM elements
    const audioContext = new AudioContext();
    const initDOM = () => {
        visualMainElement.innerHTML = '';
        createDOMElements();
    };
    // clear main and create new DOM elements
    initDOM();

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
            //loop for number of visualizingElements
            const value = values[dataMap[i]] / 255;
            //get values form dataMap-object and normalise
            const elmStyles = visualElements[i].style;
            elmStyles.transform = `scaleY(${value})`;
            // elmStyles.opacity = Math.max(0, value);
            // change opacity of div elements based of frequency data
        }
    };

    const processError = (): void => {
        visualMainElement.classList.add('error');
        // add error class to main
        visualMainElement.innerText = 'Please allow access to your microphone to record audio';
    };
    visualizer = new Visualizer(audioContext, processFrame, processError);
};

// Event listeners for the buttons
recordButton.addEventListener('click', () => {
    changeButtonStylingWhenRecordingStarted();
    console.log("record button clicked");
    startRecording();
    init();

    clearTimeoutIfExists();

    timeoutId = setTimeout(async () => {
        clearTimeoutIfExists();

        if (visualizer) {
            visualizer.stopVisualizer();
            document.querySelector("#visualizer")!.innerHTML = "";
        }
        changeRecordButtonStylingWhenRecordingStopped();
        await stopRecording();
        await sendRecordedAudio();
        console.log("Audio Recording stopped!");

    }, 1000 * 5);
    console.log("add timeout with id " + timeoutId);
});

stopRecordButton.addEventListener('click', async () => {
    console.log("stop record button clicked");

    clearTimeoutIfExists();

    if (visualizer) {
        visualizer.stopVisualizer();
        document.querySelector("#visualizer")!.innerHTML = "";
    }
    changeRecordButtonStylingWhenRecordingStopped();
    await stopRecording();
    await sendRecordedAudio();
});

function changeRecordButtonStylingWhenRecordingStopped(): void {
    let recordIcon = document.getElementById("svg");
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
        console.log("clear timeout with id " + timeoutId);

        clearTimeout(timeoutId);
        timeoutId = null;
    }
}