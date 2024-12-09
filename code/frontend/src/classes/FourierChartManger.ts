import { LineChartManager } from "./LineChartManager";
import { FourierAnalysisData } from "./FourierAnalysisData";

export class FourierChartManger extends LineChartManager {
  fourierAnalysisDatas: FourierAnalysisData[] = [];

  infoClassName: string;

  constructor(canvasesClassName: string = "chart", infoClassName: string = "info") {
    super(canvasesClassName, "Frequency (Hz)", "Magnitude");

    this.infoClassName = infoClassName;
  }

  addFourierDataSet(fourierAnalysisData: FourierAnalysisData) {
    this.fourierAnalysisDatas.push(fourierAnalysisData);

    super.addDataSet(fourierAnalysisData.frequencies.map(
      f => Math.round(f * 100) / 100),
      fourierAnalysisData.magnitudes
    );
  }

  removeFourierDataSet(index: number) {
    if (index <= this.fourierAnalysisDatas.length && index >= 0) {
      super.removeDataSet(index);

      this.fourierAnalysisDatas.splice(index, 1);
    } else {
      throw Error("Index must be between 0 and " + Math.min(this.fourierAnalysisDatas.length, this.chartDatas.length));
    }
  }

  removeAllFourierData() {
    super.removeAllData();
    this.fourierAnalysisDatas = [];
  }

  private async fetchDataByFilePathFromAPI(filePath: string): Promise<FourierAnalysisData> {
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
      this.addFourierDataSet(data);
    }
  }

  private async fetchDataByDirPathFromAPI(directoryPath: string, concurrent: boolean = false): Promise<[FourierAnalysisData]> {
    const url = "/api/upload/dir" + (concurrent ? "-concurrent" : "");

    try {
      const response = await fetch(url + "?dirPath=" + directoryPath);

      if (!response.ok) {
        throw new Error(`(${response.status}) ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error("Error when fetching data: " + (error as Error).message);
    }
  }

  async addDataSetsFromDirectoryPathApi(directoryPath: string): Promise<number> {
    const data = await this.fetchDataByDirPathFromAPI(directoryPath, true);

    for (let i = 0; i < data.length; i++) {
      if (data[i].frequencies.length !== data[i].magnitudes.length) {
        console.error("Mismatch between frequencies and magnitudes length");
      } else {
        this.addFourierDataSet(data[i]);
      }
    }

    return data.length;
  }

  drawFourierCharts(): void {
    super.drawCharts();

    const infoElements = document.getElementsByClassName(this.infoClassName);

    for (let i = 0; i < Math.min(infoElements.length, this.fourierAnalysisDatas.length); i++) {
      infoElements[i].innerHTML = `<b>${this.fourierAnalysisDatas[i].fileName}</b> (${this.fourierAnalysisDatas[i].bpm} <bpm></bpm>)`;
    }
  }

  clearAllFourierCharts() {
    super.clearCharts();
  }
}