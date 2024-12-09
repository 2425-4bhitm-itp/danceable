import "../style/tailwind.css";

import { FourierChartManger } from "../classes/FourierChartManger";

const CHART_CANVAS_CLASS_NAME = "fourierChart";
const CHART_INFO_CLASS_NAME = "fourierChartInfo";

const GENERAL_INFO_MESSAGE = "Please provide the path to a `.wav` file or a directory containing `.wav` files.";

const chartManager: FourierChartManger = new FourierChartManger(CHART_CANVAS_CLASS_NAME, CHART_INFO_CLASS_NAME);

window.onload = (_: Event) => {
  const loadChart = document.getElementById("loadChartButton");
  const canvasContainerParent = document.getElementById("canvasContainerParent");
  const pathLocationInput: HTMLInputElement | null = document.querySelector("input#pathLocationInput");

  const systemMessageContainer = document.getElementById("systemMessage");


  if (loadChart instanceof HTMLButtonElement && canvasContainerParent && pathLocationInput && systemMessageContainer) {
    displayInfo(GENERAL_INFO_MESSAGE, systemMessageContainer);

    loadChart.addEventListener("click", async () => {
      if (pathLocationInput.value == "") {
        loadChart.disabled = false;
        displayInfo(GENERAL_INFO_MESSAGE, systemMessageContainer);
        return;
      }

      try {
        displayInfo("Loading...", systemMessageContainer);
        canvasContainerParent.innerHTML = "";

        loadChart.disabled = true;

        const locationPath = pathLocationInput.value;

        if (locationPath.endsWith(".wav")) {
          canvasContainerParent.append(...createNumberOfChartContainers(1));
          await chartManager.addDataSetFromFilePathApi(locationPath);

          chartManager.drawFourierCharts();
        } else {
          const numberOfDataSets = await chartManager.addDataSetsFromDirectoryPathApi(locationPath);
          canvasContainerParent.append(...createNumberOfChartContainers(numberOfDataSets));

          chartManager.drawFourierCharts();
        }

        loadChart.disabled = false;
        displayInfo(GENERAL_INFO_MESSAGE, systemMessageContainer);
      } catch (e) {
        displayError((e as Error).message, systemMessageContainer);
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

function displayError(errorMessage: string, errorContainer: HTMLElement) {
  errorContainer.classList.add("text-red-400");
  errorContainer.classList.remove("text-blue-400");
  errorContainer.innerHTML = errorMessage;
}

function displayInfo(infoMessage: string, infoContainer: HTMLElement) {
  infoContainer.classList.add("text-blue-400");
  infoContainer.classList.remove("text-red-400");
  infoContainer.innerHTML = infoMessage;
}