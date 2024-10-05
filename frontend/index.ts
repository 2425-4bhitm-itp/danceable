import { MediaRecorder, register } from 'extendable-media-recorder';
import { connect as wavConnect } from 'extendable-media-recorder-wav-encoder';

let mediaRecorder: MediaRecorder | null = null;
let audioBlobs: Blob[] = [];
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
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/wav'
    });

    // Add audio blobs while recording
    mediaRecorder.addEventListener('dataavailable', (event: BlobEvent) => {
      audioBlobs.push(event.data);
    });

    mediaRecorder.start();
  }).catch((e: Error) => {
    console.error(e);
  });
}

function stopRecording(): Promise<Blob | null> {
  return new Promise((resolve) => {
    if (!mediaRecorder) {
      resolve(null);
      return;
    }

    mediaRecorder.addEventListener('stop', () => {
      const mimeType = mediaRecorder?.mimeType;
      const audioBlob = new Blob(audioBlobs, { type: mimeType });

      if (capturedStream) {
        capturedStream.getTracks().forEach(track => track.stop());
      }

      resolve(audioBlob);
    });

    mediaRecorder.stop();
  });
}
