import "../style/tailwind.css";

import { FourierChartManger } from "../classes/FourierChartManger";

const CHART_CANVAS_CLASS_NAME = "fourierChart";
const CHART_INFO_CLASS_NAME = "fourierChartInfo";

const chartManager: FourierChartManger = new FourierChartManger(CHART_CANVAS_CLASS_NAME, CHART_INFO_CLASS_NAME);

window.onload = (_: Event) => {
  const loadChart = document.getElementById("loadChartButton");
  const canvasContainerParent = document.getElementById("canvasContainerParent");
  const pathLocationInput: HTMLInputElement | null = document.querySelector("input#pathLocationInput");

  if (loadChart && canvasContainerParent && pathLocationInput) {
    loadChart.addEventListener("click", () => {
      const locationPath = pathLocationInput.value;

      if (locationPath.endsWith(".wav")) {
        chartManager.addDataSetFromFilePathApi(locationPath).then(() => {
          canvasContainerParent.innerHTML = "";
          canvasContainerParent.append(...createNumberOfChartContainers(1));

          chartManager.drawFourierCharts();
        });
      } else {
        chartManager.addDataSetsFromDirectoryPathApi(locationPath).then((numberOfDataSets) => {
          canvasContainerParent.innerHTML = "";
          canvasContainerParent.append(...createNumberOfChartContainers(numberOfDataSets));

          chartManager.drawFourierCharts();
        });
      }
    });
  }
};

function createNumberOfChartContainers(numberOfCharts: number): HTMLElement[] {
  let chartContainers: HTMLElement[] = [];

  for (let i = 0; i < numberOfCharts; i++) {
    chartContainers.push(createChartContainer(numberOfCharts == 1));
  }

  return chartContainers;
}

function createChartContainer(isSingleContainer: boolean): HTMLElement {
  const chartContainer: HTMLElement = document.createElement("div");
  chartContainer.classList.add("graphContainer");

  chartContainer.classList.add(isSingleContainer ? "w-full" : "w-1/2");

  const canvas: HTMLCanvasElement = document.createElement("canvas");
  canvas.classList.add(CHART_CANVAS_CLASS_NAME);

  const info: HTMLElement = document.createElement("div");
  info.classList.add(CHART_INFO_CLASS_NAME);

  chartContainer.appendChild(canvas);
  chartContainer.appendChild(info);

  return chartContainer;
}