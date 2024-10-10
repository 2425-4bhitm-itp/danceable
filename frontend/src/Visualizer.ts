export class Visualizer {
    private audioContext: AudioContext;
    private analyser: AnalyserNode;
    private processFrame: (data: Uint8Array) => void;

    //audioContext object for processing audio
    //processFrame = function for processing audio file
    // processerror = a function for handeling errors

    constructor(audioContext: AudioContext, processFrame: (data: Uint8Array) => void, processError?: (error: Error) => void) {
        this.audioContext = audioContext;
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
        this.analyser = this.audioContext.createAnalyser();
        // Make an AnalyserNode to analyse the audio
        const source = this.audioContext.createMediaStreamSource(stream);
        //MediaStreamSource is being made out of the audio stream
        source.connect(this.analyser);
        // Connecting audio-stream and analyser
        this.analyser.smoothingTimeConstant = 0.5;
        this.analyser.fftSize = 32;
        //smoothing and fft size = anzahl frequenzbaender

        this.initRenderLoop(this.analyser);
    }


    private initRenderLoop(analyser: AnalyserNode) {
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

            requestAnimationFrame(renderFrame);
            //get next animation loop
        };
        requestAnimationFrame(renderFrame);
        //starting animation
    }
}