export type RunStatus = "SUCCESS" | "FAILED" | "RUNNING";
export type RunType = "DEMO_WORKFLOW";

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface ApiInfoResponse {
  service: string;
  version: string;
  environment: string;
  docs_url: string;
  openapi_url: string;
  frontend_expected_origin_examples: string[];
}

export interface DemoSampleFilesResponse {
  market_data_file: string;
  futures_positions_file: string;
  physical_cargoes_file: string;
  descriptions?: Record<string, string>;
  note: string;
}

export interface DemoRunSummary {
  number_of_curves: number;
  number_of_net_exposure_buckets: number;
  total_net_exposure_bbl: string | number;
  total_post_hedge_absolute_exposure_bbl: string | number;
  total_stress_pnl_usd: string | number;
}

export interface DemoRunResponse {
  run_id: string;
  status: RunStatus | string;
  created_at: string;
  completed_at: string;
  summary: DemoRunSummary;
  report_url: string;
  run_detail_url: string;
  assumptions: string[];
}

export interface RunInputFiles {
  market_data_file?: string | null;
  futures_positions_file?: string | null;
  physical_cargoes_file?: string | null;
  [key: string]: string | null | undefined;
}

export interface RunOutputFiles {
  excel_report_path?: string | null;
  [key: string]: string | null | undefined;
}

export interface RunSummary {
  number_of_curves?: number;
  number_of_net_exposure_buckets?: number;
  total_net_exposure_bbl?: string | number;
  total_post_hedge_absolute_exposure_bbl?: string | number;
  total_stress_pnl_usd?: string | number;
  [key: string]: string | number | undefined;
}

export interface RunDetail {
  run_id: string;
  run_type: RunType | string;
  status: RunStatus | string;
  created_at: string;
  completed_at?: string | null;
  input_files?: RunInputFiles;
  output_files?: RunOutputFiles;
  summary?: RunSummary;
  errors?: string[];
  notes?: string | null;
  [key: string]: unknown;
}

export interface RunListResponse {
  runs: RunDetail[];
  count: number;
}

export interface RunsQuery {
  limit?: number;
  status?: RunStatus | "";
  run_type?: RunType | "";
}

export type ApiRecord = Record<string, unknown>;

export interface MarketDataValidationResponse {
  valid: boolean;
  row_count: number;
  errors: unknown[];
  preview_rows: ApiRecord[];
}

export interface CurvesBuildResponse {
  curve_summaries: ApiRecord[];
  calendar_spreads: ApiRecord[];
}

export interface FuturesAnalyzeResponse {
  valid: boolean;
  row_count: number;
  exposure_aggregation: ApiRecord[];
  summary: ApiRecord;
}

export interface PhysicalAnalyzeResponse {
  valid: boolean;
  row_count: number;
  physical_exposure_aggregation: ApiRecord[];
  summary: ApiRecord;
}

export interface NetExposureResponse {
  net_exposure_buckets: ApiRecord[];
  summary: ApiRecord;
}

export interface HedgeSimulationResponse {
  net_exposure_result: ApiRecord;
  hedge_recommendations: ApiRecord[];
  hedge_summary: ApiRecord;
}

export interface StressResponse {
  net_exposure_result: ApiRecord;
  stress_bucket_results: ApiRecord[];
  stress_summary: ApiRecord;
}

export type StressScenarioName =
  | "PARALLEL_DOWN_5"
  | "PARALLEL_UP_5"
  | "BRENT_DOWN_5"
  | "BRENT_UP_5"
  | "WTI_DOWN_5";
