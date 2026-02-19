export type Discipline = 'ARCH' | 'MECH' | 'ELEC' | 'PLUMB';
export type ChangeType = 'MOVE' | 'RESIZE' | 'RELOCATE';
export type JobStatus = 'pending' | 'completed' | 'failed';

export interface BBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Element {
  id: string;
  discipline: Discipline;
  category: string;
  level: string;
  bbox: BBox;
  connectors?: string[];
  params?: Record<string, unknown>;
}

export interface ChangeEvent {
  type: ChangeType;
  elementIds: string[];
  delta?: { dx: number; dy: number };
  newBbox?: BBox;
  metadata?: Record<string, unknown>;
}

export interface ProjectModel {
  projectId: string;
  elements: Element[];
}

export interface AnalyzeRequest {
  datasetId?: string;
  datasetJson?: ProjectModel;
  changeEvent: ChangeEvent;
}

export interface AnalyzeAcceptedResponse {
  jobId: string;
  status: JobStatus;
}

export interface ImpactReason {
  ruleId: 'intersection' | 'clearance' | 'connector';
  description: string;
  pathElementIds: string[];
}

export interface ImpactedElement {
  id: string;
  discipline: Discipline;
  category: string;
  severity: number;
  reasons: ImpactReason[];
}

export interface AnalyzeResult {
  impactedElements: ImpactedElement[];
  summary: {
    totalImpacted: number;
    byDiscipline: Record<Discipline, number>;
    maxSeverity: number;
  };
}

export interface JobResponse {
  jobId: string;
  status: JobStatus;
  request: {
    datasetId: string;
    resolvedModel: ProjectModel;
    changeEvent: ChangeEvent;
  };
  result: AnalyzeResult | null;
}

export interface DatasetOption {
  id: string;
  label: string;
  description: string;
}

export interface ChangePreset {
  id: string;
  datasetId: string;
  label: string;
  description: string;
  changeEvent: ChangeEvent;
}

export interface DatasetsResponse {
  datasets: DatasetOption[];
}

export interface PresetsResponse {
  presets: ChangePreset[];
}
