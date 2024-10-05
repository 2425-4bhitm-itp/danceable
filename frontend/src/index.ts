import { MediaRecorder, register } from 'extendable-media-recorder';
import { connect as wavConnect } from 'extendable-media-recorder-wav-encoder';


//@ts-ignore
let mediaRecorder: MediaRecorder | null = null;
let audioBlobs: Blob[] = [];
// @ts-ignore
let timeout: Timeout | number;
// @ts-ignore
let blob: Blob | null = null;
let capturedStream: MediaStream | null = null;

// Register the extendable-media-recorder-wav-encoder
async function connect(): Promise<void> {
  await register(await wavConnect());
}

// Starts recording audio
function startRecording(): Promise<void> {
  return navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
    }
  }).then((stream: MediaStream) => {
    audioBlobs = [];
    capturedStream = stream;

    // Use the extended MediaRecorder library
    // @ts-ignore
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/wav'
    });

    // Add audio blobs while recording
    // @ts-ignore
    mediaRecorder.addEventListener('dataavailable', (event: BlobEvent) => {
      audioBlobs.push(event.data);
    });

    // @ts-ignore
    mediaRecorder.start();
  }).catch((e: Error) => {
    console.error(e);
  });
}

function stopRecording(): Promise<Blob | null> {
  return new Promise((resolve) => {
    if (!mediaRecorder) {
      resolve(null); // TODO
      return;
    }

    mediaRecorder.addEventListener('stop', () => {
      const mimeType = mediaRecorder?.mimeType; // audio/wav
      const audioBlob = new Blob(audioBlobs, { type: mimeType });

      if (capturedStream) {
        capturedStream.getTracks().forEach(track => track.stop());
      }

      resolve(audioBlob);
    });

    mediaRecorder.stop();
  });
}



// @ts-ignore
function playAudio() {
  if (blob) {
    const audio = new Audio();
    audio.src = URL.createObjectURL(blob);
    audio.volume = 0.5;
    audio.play();
  }
}

async function _startRecording() {
  await connect();
  await startRecording();
  console.log("Audio Recording started!")
  timeout = setTimeout(async () => {
    // @ts-ignore
    blob = await stopRecording()
    console.log("Audio Recording stopped!")
    await addToForm();
  }, 10 * 1000);
}

async function _stopRecording() {
  clearTimeout(timeout);
  console.log("Audio Recording stopped manually!")
  blob = await stopRecording();
  await addToForm();
}

async function addToForm() {
  // @ts-ignore
  const file = new File([blob], "recorded_audio.wav", { type: 'audio/wav' });
  // Create a DataTransfer object to hold the file
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  // @ts-ignore - Assign the FileList from DataTransfer to the file input element
  document.getElementById("file").files = dataTransfer.files;
  // @ts-ignore
  document.getElementById("filename").value = "recorded_audio.wav";
}



// Register the extendable-media-recorder-wav-encoder
// @ts-ignore
window.startRecording = _startRecording;
// @ts-ignore
window.stopRecording = _stopRecording;
// @ts-ignore
window.playAudio = playAudio;