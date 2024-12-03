export class StreamRecorder {
  mediaRecorder: MediaRecorder | null = null;
  audioChunks: Blob[] = [];
  audioBlob: Blob | null = null;

  async startRecording() {
    try {
      // Request permission and access to the microphone
      const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
        }
      });

      this.mediaRecorder = new MediaRecorder(stream);

      this.audioChunks = []; // clear audio chunks

      this.mediaRecorder.start();

      this.mediaRecorder.addEventListener('dataavailable', (event: BlobEvent) => {
        this.audioChunks.push(event.data);
      });

      this.mediaRecorder.addEventListener('stop', () => {
        if (this.audioChunks.length > 0) {
          this.audioBlob = new Blob(this.audioChunks, {type: 'audio/wav'});
        }
      });
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  }

  async stopRecording(): Promise<void> {
    return new Promise<void>((resolve) => {
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.addEventListener('stop', () => {
          if (this.audioChunks.length > 0) {
            this.audioBlob = new Blob(this.audioChunks, {type: 'audio/wav'});
            console.log("Audio Blob created successfully");
          }
          resolve();  // Resolve the promise when the stop event is fully handled
        });

        this.mediaRecorder.stop();
      } else {
        resolve();  // If mediaRecorder is already inactive, resolve immediately
      }
    });
  }

  async sendRecordedAudio(): Promise<void> {
    if (this.audioBlob) {
      console.log('sending recording');
      const url = '/api/upload';
      const file = new File([this.audioBlob!], "recorded_audio.wav", {type: 'audio/wav'});
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
      console.error("No blob could be found");
    }
  }
}