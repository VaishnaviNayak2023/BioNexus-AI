const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Projects
export async function getProjects() {
  return fetchWithAuth('/api/projects');
}

export async function createProject(data: { name: string; description?: string }) {
  return fetchWithAuth('/api/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteProject(id: number) {
  return fetchWithAuth(`/api/projects/${id}`, {
    method: 'DELETE',
  });
}

// Analyses
export async function uploadSequenceFile(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/analyses/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload error: ${response.status}`);
  }

  return response.json();
}

export async function createAnalysis(data: {
  sample_id: number;
  name: string;
  marker?: string;
  taxon?: string;
  region?: string;
  settings?: any;
}) {
  return fetchWithAuth('/api/analyses', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAnalyses() {
  return fetchWithAuth('/api/analyses');
}

export async function getAnalysis(id: number) {
  return fetchWithAuth(`/api/analyses/${id}`);
}
