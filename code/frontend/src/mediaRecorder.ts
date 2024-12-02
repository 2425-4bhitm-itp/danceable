let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];
let audioBlob: Blob | null = null;  // Initialize as null for safety

export async function startRecording(): Promise<void> {
    try {
        // Request permission and access to the microphone
        const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
            }
        });

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
                audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
            }
        });
    } catch (error) {
        console.error('Error accessing microphone:', error);
    }
}

export async function stopRecording(): Promise<void> {
    return new Promise<void>((resolve) => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            // Stop the media recorder
            mediaRecorder.addEventListener('stop', () => {
                if (audioChunks.length > 0) {
                    // Create a Blob from the audio chunks after recording has stopped
                    audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
                    console.log("Audio Blob created successfully");
                }
                resolve();  // Resolve the promise when the stop event is fully handled
            });
            mediaRecorder.stop();
            // sendRecordedAudio();
        } else {
            resolve();  // If mediaRecorder is already inactive, resolve immediately
        }
    });
}

// Function to play the recorded audio

// export function playAudio(): void {
//     if (audioBlob) {
//         const audio = new Audio(URL.createObjectURL(audioBlob));
//         audio.volume = 0.5;
//         audio.play();
//     } else {
//         console.error('No audio blob available to play');
//     }
// }

// Function to add the audio blob to a form as a file
// export async function addToForm(fileInput: HTMLInputElement, filenameInput: HTMLInputElement): Promise<void> {
//     if (audioBlob) {
//         const file = new File([audioBlob], "recorded_audio.wav", {type: 'audio/wav'});
//
//         // Create a DataTransfer object to hold the file
//         const dataTransfer = new DataTransfer();
//         dataTransfer.items.add(file);
//
//         // Assign the file to the file input
//         fileInput.files = dataTransfer.files;
//
//         // Set the filename value
//         filenameInput.value = "recorded_audio.wav";
//     } else {
//         console.error('No audio blob available to add to form');
//     }
// }

export async function sendRecordedAudio(){
    if (audioBlob) {
        console.log('sending recording');
        const url = '/api/upload';
        const file = new File([audioBlob!], "recorded_audio.wav", {type: 'audio/wav'});
        console.log(file);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('fileName', "recorded_audio.wav");

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to upload file');
            }

            const responseData = await response.json();
            console.log('Response:', responseData);
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    } else {
        console.log("no audio blob found!!");
    }
}