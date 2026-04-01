import { DownloadClientError, downloadMediaStream, extractDownloadStreamEvents } from './download-client'

describe('extractDownloadStreamEvents', () => {
  it('returns complete events and preserves incomplete remainder', () => {
    const { events, remainder } = extractDownloadStreamEvents(
      'data: {"status":"downloading","progress":55,"log":"Halfway"}\n\n' +
        'data: {"status":"completed"',
    )

    expect(events).toEqual([
      {
        status: 'downloading',
        progress: 55,
        log: 'Halfway',
      },
    ])
    expect(remainder).toBe('data: {"status":"completed"')
  })

  it('ignores malformed payloads without crashing', () => {
    const { events, remainder } = extractDownloadStreamEvents(
      'data: {broken json}\n\n',
    )

    expect(events).toEqual([])
    expect(remainder).toBe('')
  })
})

describe('downloadMediaStream', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('throws an actionable degraded-runtime message when preflight reports missing dependencies', async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'degraded',
          status_message: 'Backend runtime is degraded.',
          checks: {
            ffmpeg: {
              ok: false,
              value: null,
              hint: 'Install ffmpeg and add it to PATH.',
              required_for: 'media conversion and merged video outputs',
            },
          },
        }),
      })

    vi.stubGlobal('fetch', fetchMock)

    await expect(
      downloadMediaStream(
        { url: 'https://www.youtube.com/watch?v=demo', quality: '1', format: 'mp4' },
        vi.fn(),
      ),
    ).rejects.toMatchObject({
      message: 'Backend runtime is degraded. ffmpeg: Install ffmpeg and add it to PATH.',
      code: 'degraded_runtime',
    } satisfies Partial<DownloadClientError>)
  })

  it('throws a backend-unreachable message when download and preflight checks both fail', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))

    vi.stubGlobal('fetch', fetchMock)

    await expect(
      downloadMediaStream(
        { url: 'https://www.youtube.com/watch?v=demo', quality: '1', format: 'mp4' },
        vi.fn(),
      ),
    ).rejects.toMatchObject({
      message: 'Backend is not reachable. Start the backend server or verify the Vite proxy target.',
      code: 'backend_unreachable',
    } satisfies Partial<DownloadClientError>)
  })

  it('throws stream error events with the machine-readable code attached', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(
              new TextEncoder().encode(
                'data: {"status":"error","code":"subprocess_failure","message":"Tool failed"}\n\n',
              ),
            )
            controller.close()
          },
        }),
      }),
    )

    await expect(
      downloadMediaStream(
        { url: 'https://www.youtube.com/watch?v=demo', quality: '1', format: 'mp4' },
        vi.fn(),
      ),
    ).rejects.toMatchObject({
      message: 'Tool failed',
      code: 'subprocess_failure',
    } satisfies Partial<DownloadClientError>)
  })
})
