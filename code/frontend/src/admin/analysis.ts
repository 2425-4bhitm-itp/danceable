import "../style/tailwind.css";

import { FourierChartManger } from "../classes/FourierChartManger";

const CHART_CANVAS_CLASS_NAME = "chart";
const CHART_INFO_CLASS_NAME = "info";

const chartManager: FourierChartManger = new FourierChartManger(CHART_CANVAS_CLASS_NAME, CHART_INFO_CLASS_NAME);

window.onload = (_) => {
  const loadChart = document.getElementById("loadChartButton");
  const canvasContainerParent = document.getElementById("canvasContainerParent");
  const pathLocationInput: HTMLInputElement | null = document.querySelector("input#pathLocationInput");

  if (loadChart && canvasContainerParent && pathLocationInput) {
    loadChart.addEventListener("click", () => {
      const locationPath = pathLocationInput.value;

      if (locationPath.endsWith(".wav")) {
        chartManager.addDataSetFromFilePathApi(locationPath).then(() => {
          createNumberOfGraphContainers(1, canvasContainerParent);

          chartManager.drawFourierCharts();
        });
      } else {
        chartManager.addDataSetsFromDirectoryPathApi(locationPath).then((numberOfDataSets) => {
          createNumberOfGraphContainers(numberOfDataSets, canvasContainerParent);

          chartManager.drawFourierCharts();
        });
      }
    });
  }
};

function createNumberOfGraphContainers(numberOfGraphs: number, parentElement: HTMLElement) {
  parentElement.innerHTML = "";

  let graphContainers: HTMLElement[] = [];

  for (let i = 0; i < numberOfGraphs; i++) {
    const graphContainer: HTMLElement = document.createElement("div");
    graphContainer.classList.add("graphContainer");

    graphContainer.classList.add(numberOfGraphs > 1 ? "w-1/2" : "w-full");

    const canvas: HTMLCanvasElement = document.createElement("canvas");
    canvas.classList.add(CHART_CANVAS_CLASS_NAME);

    const info: HTMLElement = document.createElement("div");
    info.classList.add("info");

    graphContainer.appendChild(canvas);
    graphContainer.appendChild(info);

    graphContainers.push(graphContainer);
  }

  parentElement.append(...graphContainers);
}