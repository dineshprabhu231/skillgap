'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { roadmapsAPI } from '@/lib/api'
import { FileText, Clock, BookOpen, Award, Code } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

export default function RoadmapPage() {
  const router = useRouter()
  const [roadmaps, setRoadmaps] = useState<any[]>([])
  const [generating, setGenerating] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    target_role: '',
    target_timeline_months: 12,
    domain: '',
  })

  useEffect(() => {
    loadRoadmaps()
  }, [])

  const loadRoadmaps = async () => {
    try {
      const response = await roadmapsAPI.getAll()
      setRoadmaps(response.data)
    } catch (error) {
      console.error('Failed to load roadmaps')
    }
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    setGenerating(true)
    try {
      await roadmapsAPI.generate(formData)
      toast.success('Roadmap generated successfully!')
      setShowForm(false)
      loadRoadmaps()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate roadmap')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link href="/dashboard" className="text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Dashboard
        </Link>

        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Learning Roadmaps</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
          >
            {showForm ? 'Cancel' : 'Generate New Roadmap'}
          </button>
        </div>

        {showForm && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <h2 className="text-2xl font-semibold mb-4">Generate Personalized Roadmap</h2>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Role
                </label>
                <input
                  type="text"
                  value={formData.target_role}
                  onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                  placeholder="e.g., AI Healthcare Analyst, Full Stack Developer"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timeline (months)
                  </label>
                  <input
                    type="number"
                    value={formData.target_timeline_months}
                    onChange={(e) =>
                      setFormData({ ...formData, target_timeline_months: parseInt(e.target.value) })
                    }
                    min="1"
                    max="36"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Domain (Optional)
                  </label>
                  <select
                    value={formData.domain}
                    onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select Domain</option>
                    <option value="AI">AI</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="FinTech">FinTech</option>
                    <option value="Cybersecurity">Cybersecurity</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={generating}
                className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50"
              >
                {generating ? 'Generating...' : 'Generate Roadmap'}
              </button>
            </form>
          </div>
        )}

        {/* Roadmaps List */}
        <div className="space-y-6">
          {roadmaps.length === 0 ? (
            <div className="bg-white rounded-xl shadow-lg p-12 text-center">
              <FileText className="mx-auto text-gray-400 mb-4" size={64} />
              <h2 className="text-2xl font-semibold mb-2">No Roadmaps Yet</h2>
              <p className="text-gray-600 mb-6">Generate your first personalized learning roadmap!</p>
              <button
                onClick={() => setShowForm(true)}
                className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
              >
                Generate Roadmap
              </button>
            </div>
          ) : (
            roadmaps.map((roadmap) => (
              <div key={roadmap.id} className="bg-white rounded-xl shadow-lg p-8">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-2xl font-semibold">{roadmap.title}</h2>
                    <p className="text-gray-600">
                      Target: {roadmap.target_role} • Timeline: {roadmap.target_timeline_months} months
                    </p>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(roadmap.generated_at).toLocaleDateString()}
                  </span>
                </div>

                {roadmap.roadmap_data?.steps && (
                  <div className="space-y-6 mt-6">
                    {roadmap.roadmap_data.steps.map((step: any, idx: number) => (
                      <div key={idx} className="border-l-4 border-primary-500 pl-6">
                        <div className="flex items-center mb-2">
                          <span className="bg-primary-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-semibold mr-3">
                            {step.step_number}
                          </span>
                          <h3 className="text-xl font-semibold">{step.skill}</h3>
                        </div>
                        <p className="text-gray-600 mb-4">{step.description}</p>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {step.prerequisites && step.prerequisites.length > 0 && (
                            <div>
                              <h4 className="font-semibold mb-2">Prerequisites:</h4>
                              <ul className="list-disc list-inside text-gray-600">
                                {step.prerequisites.map((p: string, i: number) => (
                                  <li key={i}>{p}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          <div>
                            <h4 className="font-semibold mb-2 flex items-center">
                              <Clock className="mr-2" size={16} />
                              Estimated Time: {step.estimated_time_weeks} weeks
                            </h4>
                          </div>
                        </div>

                        {step.suggested_courses && step.suggested_courses.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-semibold mb-2 flex items-center">
                              <BookOpen className="mr-2" size={16} />
                              Suggested Courses:
                            </h4>
                            <ul className="list-disc list-inside text-gray-600">
                              {step.suggested_courses.map((course: string, i: number) => (
                                <li key={i}>{course}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {step.suggested_certifications && step.suggested_certifications.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-semibold mb-2 flex items-center">
                              <Award className="mr-2" size={16} />
                              Certifications:
                            </h4>
                            <ul className="list-disc list-inside text-gray-600">
                              {step.suggested_certifications.map((cert: string, i: number) => (
                                <li key={i}>{cert}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {step.mini_projects && step.mini_projects.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-semibold mb-2 flex items-center">
                              <Code className="mr-2" size={16} />
                              Mini Projects:
                            </h4>
                            <ul className="list-disc list-inside text-gray-600">
                              {step.mini_projects.map((project: string, i: number) => (
                                <li key={i}>{project}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
