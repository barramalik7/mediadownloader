import type {
  DownloadClientErrorCode,
  DownloadFormValues,
  DownloadStreamEvent,
  ErrorDetailResponse,
  PreflightCheck,
  PreflightResponse,
} from './types'

type ParsedEvents = {
  events: DownloadStreamEvent[]
  remainder: string
}

export class DownloadClientError extends Error {
  constructor(
    message: string,
    readonly code: DownloadClientErrorCode,
  ) {
    super(message)
    this.name = 'DownloadClientError'
  }
}

export function extractDownloadStreamEvents(buffer: string): ParsedEvents {
  const events: DownloadStreamEvent[] = []
  const chunks = buffer.split('\n\n')
  const remainder = chunks.pop() ?? ''

  for (const chunk of chunks) {
    if (!chunk.startsWith('data: ')) {
      continue
    }

    const payload = chunk.slice(6).trim()

    if (!payload) {
      continue
    }

    try {
      events.push(JSON.parse(payload) as DownloadStreamEvent)
    } catch {
      continue
    }
  }

  return { events, remainder }
}

async function fetchPreflightStatus() {
  const response = await fetch('/api/health/preflight')

  if (!response.ok) {
    throw new Error('Preflight request failed')
  }

  return (await response.json()) as PreflightResponse
}

function getFirstFailingCheck(checks: Record<string, PreflightCheck>) {
  return Object.entries(checks).find(([, value]) => !value.ok)
}

function buildPreflightErrorMessage(payload: PreflightResponse) {
  const failingCheck = getFirstFailingCheck(payload.checks)

  if (!failingCheck) {
    return payload.status_message
  }

  const [name, details] = failingCheck

  if (details.hint) {
    return `${payload.status_message} ${name}: ${details.hint}`
  }

  return `${payload.status_message} ${name} is not ready.`
}

async function resolveStartupFailure() {
  try {
    const payload = await fetchPreflightStatus()

    if (payload.status === 'degraded') {
      return new DownloadClientError(buildPreflightErrorMessage(payload), 'degraded_runtime')
    }
  } catch {
    // Fall back to the generic backend-unreachable message below.
  }

  return new DownloadClientError(
    'Backend is not reachable. Start the backend server or verify the Vite proxy target.',
    'backend_unreachable',
  )
}

export async function downloadMediaStream(
  values: DownloadFormValues,
  onEvent: (event: DownloadStreamEvent) => void,
) {
  let response: Response

  try {
    response = await fetch('/api/download/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    })
  } catch {
    throw await resolveStartupFailure()
  }

  if (!response.ok) {
    let message = 'Failed to start download'
    let code: DownloadClientErrorCode = 'request_failed'

    try {
      const errorData = (await response.json()) as Partial<ErrorDetailResponse>
      message = errorData.detail ?? message
      code = errorData.code ?? code
    } catch {
      // Keep the fallback message when the response is not JSON.
    }

    throw new DownloadClientError(message, code)
  }

  if (!response.body) {
    throw await resolveStartupFailure()
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let completed = false

  while (true) {
    const { done, value } = await reader.read()

    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })

    const { events, remainder } = extractDownloadStreamEvents(buffer)
    buffer = remainder

    for (const event of events) {
      onEvent(event)

      if (event.status === 'completed') {
        completed = true
      }

      if (event.status === 'error') {
        throw new DownloadClientError(event.message, event.code)
      }
    }
  }

  const finalEvents = extractDownloadStreamEvents(buffer).events

  for (const event of finalEvents) {
    onEvent(event)

    if (event.status === 'completed') {
      completed = true
    }

    if (event.status === 'error') {
      throw new DownloadClientError(event.message, event.code)
    }
  }

  if (!completed) {
    throw new DownloadClientError('Connection closed unexpectedly', 'connection_closed')
  }
}
