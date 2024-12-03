import "../style/tailwind.css";

import { ChartManager } from "../ChartManager";

const CANVAS_CLASS_NAME = "chart";

const chartManager: ChartManager = new ChartManager(CANVAS_CLASS_NAME);

window.onload = (e) => {
  const loadChart = document.getElementById("loadChartButton");
  const canvasContainer = document.getElementById("canvasContainer");
  const pathLocationInput: HTMLInputElement | null = document.querySelector("input#pathLocationInput");

  if (loadChart && canvasContainer && pathLocationInput) {
    loadChart.addEventListener("click", () => {
      const locationPath = pathLocationInput.value;

      if (locationPath.endsWith(".wav")) {
        chartManager.addDataSetFromFilePathApi(locationPath).then(() => {
          createNumberOfCanvasElements(1, canvasContainer);

          chartManager.drawCharts();
        });
      } else {
        chartManager.addDataSetsFromDirectoryPathApi(locationPath).then((numberOfDataSets) => {
          createNumberOfCanvasElements(numberOfDataSets, canvasContainer);

          chartManager.drawCharts();
        });
      }
    });
  }
};

function createNumberOfCanvasElements(numberOfCanvesElements: number, parentElement: HTMLElement) {
  parentElement.innerHTML = "";

  let canvases: HTMLCanvasElement[] = [];

  for (let i = 0; i < numberOfCanvesElements; i++) {
    const canvas: HTMLCanvasElement = document.createElement("canvas");
    canvas.classList.add(CANVAS_CLASS_NAME);
    canvases.push(canvas);
  }

  parentElement.append(...canvases);
}