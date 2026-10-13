const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json') ? await response.json() : null

  if (!response.ok) {
    const detail = payload && typeof payload === 'object' ? payload.detail || payload.message : null
    throw new Error(detail || `Request failed with status ${response.status}`)
  }

  return payload
}

export async function fetchApplications() {
  return requestJson('/applications')
}

export async function createApplication(data) {
  return requestJson('/applications', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateApplication(id, data) {
  return requestJson(`/applications/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteApplication(id) {
  return requestJson(`/applications/${id}`, {
    method: 'DELETE',
  })
}

export async function analyzeDescription(text) {
  return requestJson('/analyze', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export { API_BASE_URL }
