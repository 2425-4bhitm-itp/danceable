export class StreamRecorder {
    mediaRecorder: MediaRecorder | null = null;
    audioChunks: Blob[] = [];
    audioBlob: Blob | null = null;

    async startRecording() {
        try {
            // Request permission and access to the microphone
            const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true
                }
            });

            this.mediaRecorder = new MediaRecorder(stream);

            this.audioChunks = [];

            this.mediaRecorder.start();

            this.mediaRecorder.addEventListener("dataavailable", (event: BlobEvent) => {
                this.audioChunks.push(event.data);
            });

            this.mediaRecorder.addEventListener("stop", () => {
                if (this.audioChunks.length > 0) {
                    this.audioBlob = new Blob(this.audioChunks, {type: "audio/webm"});
                }
            });
        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    }

    async stopRecording(): Promise<void> {
        return new Promise<void>((resolve) => {
            if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
                const tracks = this.mediaRecorder.stream.getTracks();
                tracks.forEach(track => track.stop());

                this.mediaRecorder.addEventListener("stop", () => {
                    if (this.audioChunks.length > 0) {
                        this.audioBlob = new Blob(this.audioChunks, {type: "audio/webm"});
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

    async getAudioFile(): Promise<File> {
        if (!this.audioBlob) {
            throw new Error("No audio blob to be found.");
        }

        return new File([this.audioBlob!], "recorded_audio.webm", {type: "audio/webm"});
    }

    async sendRecordedAudio(): Promise<void> {
        const file = await this.getAudioFile();

        console.log("sending recording");
        const url = "/api/upload";
        console.log(file);

        const formData = new FormData();
        formData.append("file", file);
        formData.append("fileName", "recorded_audio.webm");

        const response = await fetch(url, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            console.log(response)
            throw new Error("Failed to upload file: (" + response.status + ") \"" + response.statusText + "\"");
        }

        const responseData = await response.json();
        console.log("Response:", responseData);
    }

    playAudio(): void {
        if (this.audioBlob) {
            const audio = new Audio(URL.createObjectURL(this.audioBlob));
            audio.volume = 0.5;
            audio.play();
        } else {
            console.error("No audio blob available to play");
        }
    }
}