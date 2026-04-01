import { useReducer } from 'react'
import type { FormEvent } from 'react'
import { DownloadClientError, downloadMediaStream } from './download-client'
import type {
  DownloadClientErrorCode,
  DownloadFlowState,
  DownloadFormValues,
  DownloadFormat,
  DownloadStreamEvent,
} from './types'

const initialValues: DownloadFormValues = {
  url: '',
  quality: '1',
  format: 'mp4',
}

export function createInitialDownloadFlowState(): DownloadFlowState {
  return {
    values: initialValues,
    isDownloading: false,
    progress: 0,
    statusMessage: '',
    error: null,
    errorCode: null,
    isSuccess: false,
  }
}

type DownloadFlowAction =
  | { type: 'urlChanged'; url: string }
  | { type: 'qualityChanged'; quality: string }
  | { type: 'formatChanged'; format: DownloadFormat }
  | { type: 'submitStarted' }
  | { type: 'progressReceived'; event: Extract<DownloadStreamEvent, { status: 'downloading' }> }
  | { type: 'completed'; event: Extract<DownloadStreamEvent, { status: 'completed' }> }
  | { type: 'failed'; message: string; code: DownloadClientErrorCode | null }
  | { type: 'finished' }

export function downloadFlowReducer(
  state: DownloadFlowState,
  action: DownloadFlowAction,
): DownloadFlowState {
  switch (action.type) {
    case 'urlChanged':
      return {
        ...state,
        values: {
          ...state.values,
          url: action.url,
        },
      }
    case 'qualityChanged':
      return {
        ...state,
        values: {
          ...state.values,
          quality: action.quality,
        },
      }
    case 'formatChanged':
      return {
        ...state,
        values: {
          ...state.values,
          format: action.format,
        },
      }
    case 'submitStarted':
      return {
        ...state,
        isDownloading: true,
        progress: 0,
        statusMessage: 'Starting download...',
        error: null,
        errorCode: null,
        isSuccess: false,
      }
    case 'progressReceived':
      return {
        ...state,
        progress: action.event.progress ?? state.progress,
        statusMessage: action.event.log ?? state.statusMessage,
      }
    case 'completed':
      return {
        ...state,
        progress: action.event.progress ?? 100,
        statusMessage: action.event.message,
        isSuccess: true,
      }
    case 'failed':
      return {
        ...state,
        error: action.message,
        errorCode: action.code,
        statusMessage: 'Download failed',
      }
    case 'finished':
      return {
        ...state,
        isDownloading: false,
      }
    default:
      return state
  }
}

export function useDownloadFlow() {
  const [state, dispatch] = useReducer(downloadFlowReducer, undefined, createInitialDownloadFlowState)

  function setUrl(url: string) {
    dispatch({ type: 'urlChanged', url })
  }

  function setQuality(quality: string) {
    dispatch({ type: 'qualityChanged', quality })
  }

  function setFormat(format: DownloadFormat) {
    dispatch({ type: 'formatChanged', format })
  }

  function handleEvent(event: DownloadStreamEvent) {
    if (event.status === 'downloading') {
      dispatch({ type: 'progressReceived', event })
      return
    }

    if (event.status === 'completed') {
      dispatch({ type: 'completed', event })
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!state.values.url) {
      return
    }

    dispatch({ type: 'submitStarted' })

    try {
      await downloadMediaStream(state.values, handleEvent)
    } catch (error) {
      dispatch({
        type: 'failed',
        message: error instanceof Error ? error.message : 'An unknown error occurred',
        code: error instanceof DownloadClientError ? error.code : null,
      })
    } finally {
      dispatch({ type: 'finished' })
    }
  }

  return {
    ...state,
    setUrl,
    setQuality,
    setFormat,
    handleSubmit,
  }
}
