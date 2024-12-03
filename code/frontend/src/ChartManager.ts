import { Chart, ChartData, ChartItem, ChartOptions } from "chart.js/auto";

interface FourierAnalysisData {
  bpm: number;
  danceTypes: string[];
  frequencies: number[];
  magnitudes: number[];
  fileName: string;
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
    this.clearCanvases();

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

  async addDataSetFromFilePathApi(filePath: string) {
    const data = await this.fetchDataFromAPI(filePath);

    if (data.frequencies.length !== data.magnitudes.length) {
      console.error("Mismatch between frequencies and magnitudes length");
    } else {
      this.addDataSet(data.frequencies, data.magnitudes);
    }
  }

  async addDataSetsFromDirectoryPathApi(directoryPath: string): Promise<number> {
    const data = await this.fetchDatasFromAPI(directoryPath);

    for (let i = 0; i < data.length; i++) {
      if (data[i].frequencies.length !== data[i].magnitudes.length) {
        console.error("Mismatch between frequencies and magnitudes length");
      } else {
        this.addDataSet(data[i].frequencies, data[i].magnitudes);
      }
    }

    return data.length;
  }

  private async fetchDataFromAPI(path: string): Promise<FourierAnalysisData> {
    console.log("fetch");
    const url = "/api/upload/file";

    try {
      const response = await fetch(url + "?filePath=" + path);

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error("Error when fetching data");
    }
  }

  private async fetchDatasFromAPI(directoryPath: string): Promise<[FourierAnalysisData]> {
    console.log("fetch datas");
    const url = "/api/upload/dir";

    try {
      const response = await fetch(url + "?dirPath=" + directoryPath);

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error("Error when fetching data");
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
}