import { Chart, ChartData, ChartItem, ChartOptions } from "chart.js/auto";

interface UploadFileResponse {
  bpm: number;
  danceTypes: string[];
  frequencies: number[];
  magnitudes: number[];
}

export class ChartManager {
  charts: Chart[] = [];
  canvases: HTMLCollectionOf<HTMLCanvasElement> | [] = [];
  chartDatas: ChartData[] = [];
  canvasesClassName: string;

  options: ChartOptions = {
    responsive: true,
    scales: {
      x: {
        title: {
          display: true,
          text: "Frequency (Hz)"
        },
        beginAtZero: true
      },
      y: {
        title: {
          display: true,
          text: "Magnitude"
        }
      }
    }
  };

  constructor(canvasesClassName: string = "chart") {
    this.canvasesClassName = canvasesClassName;
  }

  addDataSet(frequencies: number[], magnitudes: number[]) {
    this.chartDatas.push(
      {
        labels: frequencies,
        datasets: [{
          label: "Magnitude vs Frequency",
          data: magnitudes,
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          tension: 0.1,
          fill: false
        }]
      }
    );
  }

  removeDataSet(index: number) {
    this.chartDatas.splice(index, 1);
  }

  removeAllDataSets() {
    this.chartDatas = [];
  }

  drawCharts() {
    this.canvases = document.getElementsByClassName(this.canvasesClassName) as HTMLCollectionOf<HTMLCanvasElement>;

    for (let i = 0; i < Math.min(this.canvases.length, this.chartDatas.length); i++) {
      const ctx = (this.canvases[i] as HTMLCanvasElement).getContext("2d");

      console.log(ctx);
      console.log(this.chartDatas[i]);

      if (ctx) {
        this.charts.push(
          new Chart(ctx as ChartItem, {
            type: "line",
            data: this.chartDatas[i],
            options: this.options
          }));
      }
    }
  }

  async addDataSetFromAPI() {
    const data = await this.fetchDataFromAPI();

    const frequencies: number[] = data.frequencies;
    const magnitudes: number[] = data.magnitudes;

    this.addDataSet(frequencies, magnitudes);
  }

  async fetchDataFromAPI(): Promise<UploadFileResponse> {
    const url = "/api/upload/file?filePath=/Users/samuelmayer/Downloads/long_footprints.wav";

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      console.log(data);

      return data;
    } catch (error) {
      throw new Error("smth went wrong");
    }
  }

  clearCanvases() {
    this.canvases = document.getElementsByClassName(this.canvasesClassName) as HTMLCollectionOf<HTMLCanvasElement>;

    for (let i = 0; i < this.charts.length; i++) {
      this.charts[i].destroy();
    }

    this.charts = [];

    for (let i = 0; i < this.canvases.length; i++) {
      const ctx = (this.canvases[i] as HTMLCanvasElement).getContext("2d");

      if (ctx && this.canvases[i]) {
        ctx.clearRect(0, 0, this.canvases[i].width, this.canvases[i].height);
      }
    }
  }

  drawChartToCanvas(canvas: HTMLCanvasElement, dataSetIndex: number = 0) {
    const ctx = canvas.getContext("2d");

    if (ctx) {
      this.charts.push(
        new Chart(ctx as ChartItem, {
          type: "line",
          data: this.chartDatas[dataSetIndex],
          options: this.options
        })
      );
    }
  }
}