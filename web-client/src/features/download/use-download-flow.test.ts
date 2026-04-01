import {
  createInitialDownloadFlowState,
  downloadFlowReducer,
} from './use-download-flow'

describe('downloadFlowReducer', () => {
  it('resets transient state when a submit starts', () => {
    const current = {
      ...createInitialDownloadFlowState(),
      error: 'Previous failure',
      isSuccess: true,
      progress: 55,
      statusMessage: 'Old message',
    }

    const next = downloadFlowReducer(current, { type: 'submitStarted' })

    expect(next.isDownloading).toBe(true)
    expect(next.progress).toBe(0)
    expect(next.statusMessage).toBe('Starting download...')
    expect(next.error).toBeNull()
    expect(next.isSuccess).toBe(false)
  })

  it('stores stream progress and terminal states through actions', () => {
    const initial = {
      ...createInitialDownloadFlowState(),
      isDownloading: true,
    }

    const withProgress = downloadFlowReducer(initial, {
      type: 'progressReceived',
      event: { status: 'downloading', progress: 42, log: 'Downloading' },
    })
    const completed = downloadFlowReducer(withProgress, {
      type: 'completed',
      event: { status: 'completed', progress: 100, message: 'Download successful' },
    })
    const finished = downloadFlowReducer(completed, { type: 'finished' })

    expect(withProgress.progress).toBe(42)
    expect(withProgress.statusMessage).toBe('Downloading')
    expect(completed.isSuccess).toBe(true)
    expect(completed.statusMessage).toBe('Download successful')
    expect(finished.isDownloading).toBe(false)
  })
})
