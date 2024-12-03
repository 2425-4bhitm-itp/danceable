import '../style/tailwind.css';

import { ChartManager } from "../ChartManager";

const chartManager: ChartManager = new ChartManager("chart");

window.onload = (e) => {
  const loadChart = document.getElementById("loadChartButton");

  if (loadChart) {
    console.log(loadChart);
    loadChart.addEventListener("click", () => {
      const filePathInput: HTMLInputElement | null = document.querySelector("input#filePathInput");

      if (filePathInput) {
        chartManager.addDataSetFromAPI(filePathInput.value).then(() => {
          chartManager.drawCharts();
        });
      }
    });
  }
};