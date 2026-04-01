export type {
  DownloadErrorCode,
  DownloadStartErrorCode,
  DownloadStreamEvent,
  ErrorDetailResponse,
  PreflightCheck,
  PreflightResponse,
} from './generated-contract'

export type DownloadFormat = 'mp4' | 'mp3' | 'jpg' | 'png'

export type DownloadFormValues = {
  url: string
  quality: string
  format: DownloadFormat
}

export type DownloadClientErrorCode =
  | import('./generated-contract').DownloadErrorCode
  | import('./generated-contract').DownloadStartErrorCode
  | 'backend_unreachable'
  | 'degraded_runtime'
  | 'connection_closed'
  | 'request_failed'

export type DownloadFlowState = {
  values: DownloadFormValues
  isDownloading: boolean
  progress: number
  statusMessage: string
  error: string | null
  errorCode: DownloadClientErrorCode | null
  isSuccess: boolean
}
