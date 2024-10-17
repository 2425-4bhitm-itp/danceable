import './style/style.css';

console.log("💃💃💃");


// selins part (media recorder)

import { _startRecording} from "./mediaRecorder";
import {_stopRecording} from "./mediaRecorder";
import {playAudio} from "./mediaRecorder";

// Access DOM elements with appropriate type assertions
const recordButton = document.getElementById('recordBtn') as HTMLButtonElement;
const stopRecordButton = document.getElementById('recordStopBtn') as HTMLButtonElement;
const playAudioButton = document.getElementById('playAudioBtn') as HTMLButtonElement;
const fileInput = document.getElementById('file') as HTMLInputElement;
const filenameInput = document.getElementById('filename') as HTMLInputElement;

// Event listeners for the buttons
recordButton.addEventListener('click', () => {
    _startRecording(fileInput, filenameInput);
});

stopRecordButton.addEventListener('click', () => {
    _stopRecording(fileInput, filenameInput);
});

playAudioButton.addEventListener('click', () => {
    playAudio();
});

