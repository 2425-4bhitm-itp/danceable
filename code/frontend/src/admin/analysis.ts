import { ChartManager } from "../ChartManager";

const chartManager: ChartManager = new ChartManager("chart");

chartManager.addDataSetFromAPI();

chartManager.drawCharts();