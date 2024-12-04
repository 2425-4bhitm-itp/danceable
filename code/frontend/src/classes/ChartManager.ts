import { Chart, ChartData, ChartItem, ChartOptions } from "chart.js/auto";
import { FourierAnalysisData } from "../FourierAnalysisData";

export class ChartManager {
  charts: Chart[] = [];

  chartDatas: ChartData[] = [];
  fourierAnalysisDatas: FourierAnalysisData[] = [];

  canvases: HTMLCollectionOf<HTMLCanvasElement> | [] = [];
  canvasesClassName: string;

  infoElements: HTMLCollectionOf<HTMLElement> | [] = [];
  infoClassName: string;

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

  constructor(canvasesClassName: string = "chart", infoClassName: string = "info") {
    this.canvasesClassName = canvasesClassName;
    this.infoClassName = infoClassName;
  }

  addDataSet(fourierAnalysisData: FourierAnalysisData) {
    this.fourierAnalysisDatas.push(fourierAnalysisData);

    console.log(fourierAnalysisData.frequencies);

    this.chartDatas.push(
      {
        labels: fourierAnalysisData.frequencies.map((f) => {return f.toFixed(2)}),
        datasets: [{
          label: "Magnitude vs Frequency",
          data: fourierAnalysisData.magnitudes,
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          tension: 0.1,
          fill: false
        }]
      }
    );
  }

  removeDataSet(index: number) {
    if (index <= Math.min(this.fourierAnalysisDatas.length, this.chartDatas.length) && index >= 0) {
      this.chartDatas.splice(index, 1);
      this.fourierAnalysisDatas.splice(index, 1);
    } else {
      throw Error("Index must be between 0 and " + Math.min(this.fourierAnalysisDatas.length, this.chartDatas.length));
    }
  }

  removeAllData() {
    this.chartDatas = [];
    this.fourierAnalysisDatas = [];
  }

  drawCharts() {
    this.clearCanvases();

    this.canvases = document.getElementsByClassName(this.canvasesClassName) as HTMLCollectionOf<HTMLCanvasElement>;
    this.infoElements = document.getElementsByClassName("info") as HTMLCollectionOf<HTMLElement>;

    for (let i = 0; i < Math.min(this.canvases.length, this.chartDatas.length, this.fourierAnalysisDatas.length); i++) {
      const ctx = (this.canvases[i] as HTMLCanvasElement).getContext("2d");

      if (ctx) {
        console.log(this.fourierAnalysisDatas[i]);

        if (i <= this.infoElements.length && this.infoElements[i]) {
          this.infoElements[i].innerHTML = `<b>${this.fourierAnalysisDatas[i].fileName}</b> (${this.fourierAnalysisDatas[i].bpm})`;
        }

        this.charts.push(
          new Chart(ctx as ChartItem, {
            type: "line",
            data: this.chartDatas[i],
            options: this.options
          }));
      }
    }
  }

  private async fetchDataByFilePathFromAPI(filePath: string): Promise<FourierAnalysisData> {
    console.log("fetch");
    const url = "/api/upload/file";

    try {
      const response = await fetch(url + "?filePath=" + filePath);

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error("Error when fetching data");
    }
  }

  async addDataSetFromFilePathApi(filePath: string) {
    const data: FourierAnalysisData = await this.fetchDataByFilePathFromAPI(filePath);

    if (data.frequencies.length !== data.magnitudes.length) {
      console.error("Mismatch between frequencies and magnitudes length");
    } else {
      this.addDataSet(data);
    }
  }

  private async fetchDataByDirPathFromAPI(directoryPath: string): Promise<[FourierAnalysisData]> {
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

  async addDataSetsFromDirectoryPathApi(directoryPath: string): Promise<number> {
    const data = await this.fetchDataByDirPathFromAPI(directoryPath);

    for (let i = 0; i < data.length; i++) {
      if (data[i].frequencies.length !== data[i].magnitudes.length) {
        console.error("Mismatch between frequencies and magnitudes length");
      } else {
        this.addDataSet(data[i]);
      }
    }

    return data.length;
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