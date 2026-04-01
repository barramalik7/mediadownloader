import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { DownloaderForm } from './DownloaderForm'

function createStreamResponse(chunks: string[]) {
  const encoder = new TextEncoder()

  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk))
      }

      controller.close()
    },
  })
}

describe('DownloaderForm', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('keeps the submit button disabled until a URL is entered', () => {
    render(<DownloaderForm />)

    expect(
      screen.getByRole('button', { name: /start download/i }),
    ).toBeDisabled()
  })

  it('shows an API error returned before the stream starts', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: 'Unsupported platform or invalid URL' }),
      }),
    )

    render(<DownloaderForm />)

    fireEvent.change(screen.getByLabelText(/media url/i), {
      target: { value: 'https://example.com/video' },
    })
    fireEvent.click(screen.getByRole('button', { name: /start download/i }))

    expect(
      await screen.findByText(/unsupported platform or invalid url/i),
    ).toBeInTheDocument()
  })

  it('updates progress and success state from streamed events', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        body: createStreamResponse([
          'data: {"status":"downloading","progress":42,"log":"Downloading"}\n\n',
          'data: {"status":"completed","progress":100,"message":"Download successful"}\n\n',
        ]),
      }),
    )

    render(<DownloaderForm />)

    fireEvent.change(screen.getByLabelText(/media url/i), {
      target: { value: 'https://youtube.com/watch?v=demo' },
    })
    fireEvent.click(screen.getByRole('button', { name: /start download/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/download completed successfully/i),
      ).toBeInTheDocument()
    })
  })
})
