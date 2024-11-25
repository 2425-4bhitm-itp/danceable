// Declare necessary variables and their types
let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];
let audioBlob: Blob | null = null;  // Initialize as null for safety
let timeout: number | undefined;


// Function to start recording audio

async function startRecording(): Promise<void> {
  try {
    // Request permission and access to the microphone
    const stream: MediaStream = await navigator.mediaDevices.getUserMedia({ audio: {
        echoCancellation: true,
      } });

    // Initialize MediaRecorder with the audio stream
    mediaRecorder = new MediaRecorder(stream);

    // Clear any previous audio chunks
    audioChunks = [];

    // Start recording
    mediaRecorder.start();

    // Event listener for when audio data becomes available
    mediaRecorder.addEventListener('dataavailable', (event: BlobEvent) => {
      audioChunks.push(event.data);
    });

    // Event listener for when the recording is stopped
    mediaRecorder.addEventListener('stop', () => {
      if (audioChunks.length > 0) {
        // Create a Blob from the audio chunks
        audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      }
    });
  } catch (error) {
    console.error('Error accessing microphone:', error);
  }
}

// Function to handle recording logic with a timeout
export async function _startRecording(fileInput:HTMLInputElement, filenameInput:HTMLInputElement): Promise<void> {
  let recordingDescription = document.getElementById("recording-description");
  let stopBtn = document.getElementById("recordStopBtn");
  let svg = document.getElementById("svg");
  let clearVisualizer = document.getElementById("visualizer")
  if (clearVisualizer){
    clearVisualizer.style.display="block";
  }
  if(recordingDescription && stopBtn && svg){
    svg.style.display="none";
    recordingDescription.style.display="none";
    stopBtn.style.display="block";
    //TODO set button to display block
  }
  await startRecording();

  console.log("Audio Recording started!");

  // Automatically stop recording after 10 seconds
  timeout = window.setTimeout(async () => {
    await stopRecording();  // Make sure recording stops first
    console.log("Audio Recording stopped!");
    //await addToForm(fileInput, filenameInput);  // Only add to form once recording is stopped and audioBlob is ready
  }, 10 * 1000);  // 10 seconds
}

// Function to stop recording manually and clear timeout
export async function _stopRecording(fileInput:HTMLInputElement, filenameInput:HTMLInputElement): Promise<void> {
  let clearVisualizer = document.getElementById("visualizer");
  if (clearVisualizer){
    clearVisualizer.style.display="none";
  }
  if (timeout) {
    clearTimeout(timeout);
    console.log("Audio Recording stopped manually!");
    await stopRecording();

    // Ensure recording is stopped before proceeding
    //await addToForm(fileInput, filenameInput);  // Only add to form once recording is stopped and audioBlob is ready
  }
}

// Function to stop the media recording
async function stopRecording(): Promise<void> {
  return new Promise<void>((resolve) => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      // Stop the media recorder
      mediaRecorder.addEventListener('stop', () => {
        if (audioChunks.length > 0) {
          // Create a Blob from the audio chunks after recording has stopped
          audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          console.log("Audio Blob created successfully");
        }
        resolve();  // Resolve the promise when the stop event is fully handled
      });
      mediaRecorder.stop();
    } else {
      resolve();  // If mediaRecorder is already inactive, resolve immediately
    }
  });
}

// Function to play the recorded audio
export function playAudio(): void {
  if (audioBlob) {
    const audio = new Audio(URL.createObjectURL(audioBlob));
    audio.volume = 0.5;
    audio.play();
  } else {
    console.error('No audio blob available to play');
  }
}

// Function to add the audio blob to a form as a file
export async function addToForm(fileInput:HTMLInputElement, filenameInput:HTMLInputElement): Promise<void> {
  if (audioBlob) {
    const file = new File([audioBlob], "recorded_audio.wav", { type: 'audio/wav' });

    // Create a DataTransfer object to hold the file
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);

    // Assign the file to the file input
    fileInput.files = dataTransfer.files;

    // Set the filename value
    filenameInput.value = "recorded_audio.wav";
  } else {
    console.error('No audio blob available to add to form');
  }
}
