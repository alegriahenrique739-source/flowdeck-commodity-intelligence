import type {
  ApiInfoResponse,
  CurvesBuildResponse,
  DemoRunResponse,
  DemoSampleFilesResponse,
  FuturesAnalyzeResponse,
  HealthResponse,
  HedgeSimulationResponse,
  MarketDataValidationResponse,
  NetExposureResponse,
  PhysicalAnalyzeResponse,
  RunDetail,
  RunListResponse,
  RunsQuery,
  StressResponse,
  StressScenarioName
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_FLOWDECK_API_BASE_URL || "http://127.0.0.1:8000";

export class FlowDeckApiError extends Error {
  details: unknown;
  errors: unknown[];

  constructor(message: string, details?: unknown, errors: unknown[] = []) {
    super(message);
    this.name = "FlowDeckApiError";
    this.details = details;
    this.errors = errors;
  }
}

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    headers: {
      Accept: "application/json"
    }
  });

  if (!response.ok) {
    throw await responseError(response);
  }

  return response.json() as Promise<T>;
}

async function requestPostJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    cache: "no-store",
    headers: {
      Accept: "application/json"
    }
  });

  if (!response.ok) {
    throw await responseError(response);
  }

  return response.json() as Promise<T>;
}

async function requestFormJson<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
    cache: "no-store",
    headers: {
      Accept: "application/json"
    }
  });

  if (!response.ok) {
    throw await responseError(response);
  }

  return response.json() as Promise<T>;
}

async function responseError(response: Response): Promise<FlowDeckApiError> {
  let message = `FlowDeck API request failed with status ${response.status}.`;
  let details: unknown;
  let errors: unknown[] = [];
  try {
    const payload = await response.json();
    const detail = payload?.detail;
    message = detail?.message || detail?.error || message;
    details = detail?.details ?? detail;
    errors = Array.isArray(detail?.errors)
      ? detail.errors
      : Array.isArray(detail?.details?.errors)
        ? detail.details.errors
        : [];
  } catch {
    // Keep the status-based fallback when the API response is not JSON.
  }
  return new FlowDeckApiError(message, details, errors);
}

export function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/health");
}

export function getApiInfo(): Promise<ApiInfoResponse> {
  return requestJson<ApiInfoResponse>("/api/info");
}

export function getRuns(params: RunsQuery = {}): Promise<RunListResponse> {
  const query = new URLSearchParams();
  if (params.limit) {
    query.set("limit", String(params.limit));
  }
  if (params.status) {
    query.set("status", params.status);
  }
  if (params.run_type) {
    query.set("run_type", params.run_type);
  }

  const suffix = query.toString() ? `?${query.toString()}` : "";
  return requestJson<RunListResponse>(`/runs${suffix}`);
}

export function getRun(runId: string): Promise<RunDetail> {
  return requestJson<RunDetail>(`/runs/${encodeURIComponent(runId)}`);
}

export function getRunReportUrl(runId: string): string {
  return `${API_BASE_URL}/runs/${encodeURIComponent(runId)}/report`;
}

export function getApiDocsUrl(): string {
  return `${API_BASE_URL}/docs`;
}

export function getOpenApiUrl(): string {
  return `${API_BASE_URL}/openapi.json`;
}

export function getDemoSampleFiles(): Promise<DemoSampleFilesResponse> {
  return requestJson<DemoSampleFilesResponse>("/demo/sample-files");
}

export function runSampleDemo(params: {
  targetHedgeRatio?: string;
  stressScenario?: StressScenarioName;
} = {}): Promise<DemoRunResponse> {
  const query = new URLSearchParams();
  query.set("target_hedge_ratio", params.targetHedgeRatio || "0.80");
  query.set("stress_scenario", params.stressScenario || "PARALLEL_DOWN_5");
  return requestPostJson<DemoRunResponse>(`/demo/run?${query.toString()}`);
}

export function validateMarketData(
  file: File
): Promise<MarketDataValidationResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return requestFormJson<MarketDataValidationResponse>(
    "/market-data/validate",
    formData
  );
}

export function buildCurves(file: File): Promise<CurvesBuildResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return requestFormJson<CurvesBuildResponse>("/curves/build", formData);
}

export function analyzeFutures(file: File): Promise<FuturesAnalyzeResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return requestFormJson<FuturesAnalyzeResponse>(
    "/positions/futures/analyze",
    formData
  );
}

export function analyzePhysical(file: File): Promise<PhysicalAnalyzeResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return requestFormJson<PhysicalAnalyzeResponse>(
    "/positions/physical/analyze",
    formData
  );
}

export function computeNetExposure(
  futuresFile: File,
  physicalFile: File
): Promise<NetExposureResponse> {
  const formData = new FormData();
  formData.append("futures_file", futuresFile);
  formData.append("physical_file", physicalFile);
  return requestFormJson<NetExposureResponse>("/exposure/net", formData);
}

export function simulateHedge(
  futuresFile: File,
  physicalFile: File,
  targetHedgeRatio: string,
  contractSizeBbl: string
): Promise<HedgeSimulationResponse> {
  const formData = new FormData();
  formData.append("futures_file", futuresFile);
  formData.append("physical_file", physicalFile);
  formData.append("target_hedge_ratio", targetHedgeRatio);
  formData.append("contract_size_bbl", contractSizeBbl);
  return requestFormJson<HedgeSimulationResponse>("/hedging/simulate", formData);
}

export function runStress(
  futuresFile: File,
  physicalFile: File,
  scenarioName: StressScenarioName
): Promise<StressResponse> {
  const formData = new FormData();
  formData.append("futures_file", futuresFile);
  formData.append("physical_file", physicalFile);
  formData.append("scenario_name", scenarioName);
  return requestFormJson<StressResponse>("/risk/stress", formData);
}

export async function generateExcelReport(
  marketDataFile: File,
  futuresFile: File,
  physicalFile: File,
  targetHedgeRatio: string,
  stressScenario: StressScenarioName
): Promise<void> {
  const formData = new FormData();
  formData.append("market_data_file", marketDataFile);
  formData.append("futures_file", futuresFile);
  formData.append("physical_file", physicalFile);
  formData.append("target_hedge_ratio", targetHedgeRatio);
  formData.append("stress_scenario", stressScenario);

  const response = await fetch(`${API_BASE_URL}/reports/excel`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw await responseError(response);
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = "flowdeck_workspace_report.xlsx";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}
