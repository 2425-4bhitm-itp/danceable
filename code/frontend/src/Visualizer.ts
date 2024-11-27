export class Visualizer {
    private audioContext: AudioContext;
    private analyser: AnalyserNode;
    private processFrame: (data: Uint8Array) => void;
    private animationFrameId: number = 0;

    //audioContext object for processing audio
    //processFrame = function for processing audio file
    // processerror = a function for handeling errors

    constructor(audioContext: AudioContext, processFrame: (data: Uint8Array) => void, processError?: (error: Error) => void) {
        this.audioContext = audioContext;
        this.analyser = this.audioContext.createAnalyser();
        this.processFrame = processFrame;
        this.connectStream = this.connectStream.bind(this);
        navigator.mediaDevices.getUserMedia({audio: true, video: false})
            // getUserMedia API is used to get access to the users microphone
            .then(this.connectStream)
            //if allowed use connectStream
            .catch((error) => {
                if (processError) {
                    processError(error)
                }
            });
        //if not allowed catch error
    }

    connectStream(stream: MediaStream) {
        // if stream is available call connectStream method
        // Make an AnalyserNode to analyse the audio
        const source = this.audioContext.createMediaStreamSource(stream);
        //MediaStreamSource is being made out of the audio stream
        source.connect(this.analyser);
        // Connecting audio-stream and analyser
        this.analyser.smoothingTimeConstant = 0.5;
        this.analyser.fftSize = 32;
        //smoothing and fft size = anzahl frequenzbaender

        this.initRenderLoop();
    }


    private initRenderLoop() {
        const frequencyData = new Uint8Array(this.analyser.frequencyBinCount);
        //create array storing frequency data
        const processFrame = this.processFrame || (() => {
        });
        //if no process frame metod, use empty one

        const renderFrame = () => {
            this.analyser.getByteFrequencyData(frequencyData);
            //frequency data update in array
            processFrame(frequencyData);
            //processframe function is called with updated data

            this.animationFrameId = requestAnimationFrame(renderFrame);
            //get next animation loop
        };
        this.animationFrameId = requestAnimationFrame(renderFrame);
        //starting animation
    }

    stopVisualizer() {
        cancelAnimationFrame(this.animationFrameId);
    }
}