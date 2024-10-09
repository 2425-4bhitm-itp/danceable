class Visualizer {
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

const visualMainElement = document.querySelector('main') as HTMLElement;
const visualValueCount = 16;
let visualElements: NodeListOf<HTMLDivElement>;
//Main element is chosen and visualizing elements is set to 16
const createDOMElements = () => {
    //function for creating DOM elements
    let i;
    for (i = 0; i < visualValueCount; ++i){
        //loop for 16 iterations
        const elm = document.createElement('div');
        visualMainElement.appendChild(elm);
        //div is created and added to main

    }
    visualElements = document.querySelectorAll('main div');
    //all divs in main are saved in visualElements
};
createDOMElements();

const init = () => {
    // Creating initial DOM elements
    const audioContext = new AudioContext();
    const initDOM = () => {
        visualMainElement.innerHTML = '';
        createDOMElements();
    };
    //clear main and create new DOM elements
    initDOM();

    //Swapping values around for a better visual effect
    const dataMap: { [key: number]: number } = { 0: 15, 1: 10, 2: 8, 3: 9, 4: 6, 5: 5, 6: 2, 7: 1, 8: 0, 9: 4, 10: 3, 11: 7, 12: 11, 13: 12, 14: 13, 15: 14 };
    //create Mapping object for sorting frequency data for visualizing
    const processFrame = (data: Uint8Array): void => {
        const values = Array.from(data);
        //frequencydata in array
        for (let i = 0; i < visualValueCount; ++i){
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
        //add error class to main
        visualMainElement.innerText = 'Please allow access to your microphone to record audio';
    };
    const a = new Visualizer(audioContext, processFrame, processError);
};

init();
