import axios from 'axios'

// In production, set NEXT_PUBLIC_API_URL to your backend URL (e.g., https://your-app.railway.app)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for AI operations
})

// Authentication removed for now - no token needed

export default api

// Auth API removed for now

// Skills API
export const skillsAPI = {
  uploadResume: (file: File, domain?: string, target_role?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (domain) formData.append('domain', domain)
    if (target_role) formData.append('target_role', target_role)
    return api.post('/api/skills/upload-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  analyzeGaps: () => api.post('/api/skills/analyze-gaps'),
  getTrending: (domain?: string, limit?: number) =>
    api.get('/api/skills/trending', { params: { domain, limit } }),
  getForecast: (skillName: string) =>
    api.get(`/api/skills/forecast/${skillName}`),
}

// Roadmaps API
export const roadmapsAPI = {
  generate: (data: { target_role: string; target_timeline_months: number; domain?: string }) =>
    api.post('/api/roadmaps/generate', data),
  getAll: () => api.get('/api/roadmaps/'),
  getById: (id: number) => api.get(`/api/roadmaps/${id}`),
}

// Curriculum API
export const curriculumAPI = {
  upload: (name: string, program?: string, file?: File, curriculum_text?: string) => {
    const formData = new FormData()
    formData.append('name', name)
    if (program) formData.append('program', program)
    if (file) formData.append('file', file)
    if (curriculum_text) formData.append('curriculum_text', curriculum_text)
    return api.post('/api/curriculum/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getAll: () => api.get('/api/curriculum/'),
  getById: (id: number) => api.get(`/api/curriculum/${id}`),
  analyze: (id: number) => api.post(`/api/curriculum/${id}/analyze`),
}

// Analytics API
export const analyticsAPI = {
  getSkillHeatmap: (domain?: string) =>
    api.get('/api/analytics/skill-heatmap', { params: { domain } }),
  getDemandVsSupply: (domain?: string) =>
    api.get('/api/analytics/demand-vs-supply', { params: { domain } }),
  getTrendGrowth: (skillNames?: string) =>
    api.get('/api/analytics/trend-growth', { params: { skill_names: skillNames } }),
  getEmployabilityReadiness: () => api.get('/api/analytics/employability-readiness'),
  getInstitutionReadiness: () => api.get('/api/analytics/institution-readiness'),
}
