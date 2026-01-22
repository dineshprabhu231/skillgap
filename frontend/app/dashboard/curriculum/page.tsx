'use client'

import { useState, useEffect } from 'react'
import { curriculumAPI } from '@/lib/api'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

export default function CurriculumPage() {
  const [curricula, setCurricula] = useState<any[]>([])
  const [showForm, setShowForm] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    program: '',
    curriculum_text: '',
  })
  const [file, setFile] = useState<File | null>(null)

  useEffect(() => {
    loadCurricula()
  }, [])

  const loadCurricula = async () => {
    try {
      const response = await curriculumAPI.getAll()
      setCurricula(response.data)
    } catch (error) {
      console.error('Failed to load curricula')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file && !formData.curriculum_text) {
      toast.error('Please provide either a file or curriculum text')
      return
    }

    setUploading(true)
    try {
      await curriculumAPI.upload(
        formData.name,
        formData.program || undefined,
        file || undefined,
        formData.curriculum_text || undefined
      )
      toast.success('Curriculum uploaded successfully!')
      setShowForm(false)
      setFile(null)
      setFormData({ name: '', program: '', curriculum_text: '' })
      loadCurricula()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleAnalyze = async (id: number) => {
    try {
      await curriculumAPI.analyze(id)
      toast.success('Curriculum re-analyzed with latest data!')
      loadCurricula()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Analysis failed')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link href="/dashboard" className="text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Dashboard
        </Link>

        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Curriculum Management</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
          >
            {showForm ? 'Cancel' : 'Upload Curriculum'}
          </button>
        </div>

        {showForm && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <h2 className="text-2xl font-semibold mb-4">Upload Curriculum</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Curriculum Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="e.g., B.Tech Computer Science 2024"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Program (Optional)
                </label>
                <input
                  type="text"
                  value={formData.program}
                  onChange={(e) => setFormData({ ...formData, program: e.target.value })}
                  placeholder="e.g., B.Tech, M.Tech, B.Sc"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload File (PDF) or Enter Text
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 inline-block mb-4"
                  >
                    Choose PDF File
                  </label>
                  {file && (
                    <p className="text-sm text-gray-600 mb-4">Selected: {file.name}</p>
                  )}
                  <div className="text-sm text-gray-500 mb-2">OR</div>
                  <textarea
                    value={formData.curriculum_text}
                    onChange={(e) => setFormData({ ...formData, curriculum_text: e.target.value })}
                    placeholder="Paste curriculum text here..."
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={uploading}
                className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50"
              >
                {uploading ? 'Uploading...' : 'Upload Curriculum'}
              </button>
            </form>
          </div>
        )}

        {/* Curricula List */}
        <div className="space-y-6">
          {curricula.length === 0 ? (
            <div className="bg-white rounded-xl shadow-lg p-12 text-center">
              <FileText className="mx-auto text-gray-400 mb-4" size={64} />
              <h2 className="text-2xl font-semibold mb-2">No Curricula Yet</h2>
              <p className="text-gray-600 mb-6">Upload your first curriculum to get started!</p>
              <button
                onClick={() => setShowForm(true)}
                className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
              >
                Upload Curriculum
              </button>
            </div>
          ) : (
            curricula.map((curriculum) => (
              <div key={curriculum.id} className="bg-white rounded-xl shadow-lg p-8">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-2xl font-semibold">{curriculum.name}</h2>
                    {curriculum.program && (
                      <p className="text-gray-600">Program: {curriculum.program}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary-600">
                      {(curriculum.alignment_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-sm text-gray-600">Alignment Score</div>
                  </div>
                </div>

                {curriculum.extracted_skills && (
                  <div className="mb-4">
                    <h3 className="font-semibold mb-2">Extracted Skills:</h3>
                    <div className="flex flex-wrap gap-2">
                      {curriculum.extracted_skills.slice(0, 10).map((skill: string, idx: number) => (
                        <span
                          key={idx}
                          className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                      {curriculum.extracted_skills.length > 10 && (
                        <span className="text-gray-500 text-sm">
                          +{curriculum.extracted_skills.length - 10} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {curriculum.recommendations && (
                  <div className="space-y-4">
                    {curriculum.recommendations.skills_to_add && (
                      <div>
                        <h3 className="font-semibold mb-2 text-green-700">Skills to Add:</h3>
                        <ul className="list-disc list-inside text-gray-600">
                          {curriculum.recommendations.skills_to_add.slice(0, 5).map((skill: string, idx: number) => (
                            <li key={idx}>{skill}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {curriculum.recommendations.readiness_scores && (
                      <div className="grid grid-cols-3 gap-4 mt-4">
                        <div className="text-center">
                          <div className="text-xl font-bold">
                            {(curriculum.recommendations.readiness_scores.placements * 100).toFixed(0)}%
                          </div>
                          <div className="text-sm text-gray-600">Placement Readiness</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xl font-bold">
                            {(curriculum.recommendations.readiness_scores.industry_collaboration * 100).toFixed(0)}%
                          </div>
                          <div className="text-sm text-gray-600">Industry Collaboration</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xl font-bold">
                            {(curriculum.recommendations.readiness_scores.accreditation * 100).toFixed(0)}%
                          </div>
                          <div className="text-sm text-gray-600">Accreditation</div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="mt-6">
                  <button
                    onClick={() => handleAnalyze(curriculum.id)}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                  >
                    Re-analyze with Latest Data
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
