import { Chart, ChartData, ChartItem, ChartOptions } from "chart.js/auto";

export abstract class LineChartManager {
  charts: Chart[] = [];

  chartDatas: ChartData[] = [];

  canvases: HTMLCollectionOf<HTMLCanvasElement> | [] = [];
  canvasesClassName: string;

  xAxisText: string;
  yAxisText: string;

  options: ChartOptions;

  constructor(canvasesClassName: string = "chart", xAxisText: string, yAxisText: string) {
    this.canvasesClassName = canvasesClassName;
    this.xAxisText = xAxisText;
    this.yAxisText = yAxisText;

    this.options = {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: this.xAxisText
          },
          beginAtZero: true
        },
        y: {
          title: {
            display: true,
            text: this.yAxisText
          }
        }
      }
    }
  }

  protected addDataSet(labels: number[], values: number[]): void {
    this.chartDatas.push(
      {
        labels: labels,
        datasets: [{
          label: this.yAxisText + " vs " + this.xAxisText,
          data: values,
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          tension: 0.1,
          fill: false
        }]
      }
    );
  }

  protected removeDataSet(index: number): void {
    if (index <= this.chartDatas.length && index >= 0) {
      this.chartDatas.splice(index, 1);
    } else {
      throw Error("Index must be between 0 and " + this.chartDatas.length);
    }
  }

  protected removeAllData(): void {
    this.chartDatas = [];
  }

  protected drawCharts(): void {
    this.clearCharts();

    this.canvases = document.getElementsByClassName(this.canvasesClassName) as HTMLCollectionOf<HTMLCanvasElement>;

    for (let i = 0; i < Math.min(this.canvases.length, this.chartDatas.length); i++) {
      const ctx = (this.canvases[i] as HTMLCanvasElement).getContext("2d");

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

  protected clearCharts(): void {
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