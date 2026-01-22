'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { skillsAPI } from '@/lib/api'
import { AlertCircle, TrendingUp, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Link from 'next/link'

export default function GapsPage() {
  const router = useRouter()
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const runAnalysis = async () => {
    setLoading(true)
    try {
      const response = await skillsAPI.analyzeGaps()
      setAnalysis(response.data)
      toast.success('Skill gap analysis completed!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runAnalysis()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Analyzing your skills...</div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <AlertCircle className="mx-auto text-yellow-500 mb-4" size={64} />
            <h2 className="text-2xl font-semibold mb-2">No Analysis Available</h2>
            <p className="text-gray-600 mb-6">Please upload your resume first.</p>
            <Link
              href="/dashboard/resume"
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
            >
              Upload Resume
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const highPriorityGaps = analysis.skill_gaps?.filter((g: any) => g.priority === 'high') || []
  const shortTermSkills = analysis.priority_skills_short_term || []
  const longTermSkills = analysis.priority_skills_long_term || []

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link href="/dashboard" className="text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Dashboard
        </Link>

        <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
          <h1 className="text-3xl font-bold mb-4">Skill Gap Analysis</h1>
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-600">
                {(analysis.overall_gap_score * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600">Overall Gap Score</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-red-600">
                {highPriorityGaps.length}
              </div>
              <div className="text-sm text-gray-600">High Priority Gaps</div>
            </div>
          </div>
        </div>

        {/* Priority Skills */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <TrendingUp className="mr-2 text-primary-600" size={24} />
              Short-term Priority Skills
            </h2>
            <ul className="space-y-2">
              {shortTermSkills.length > 0 ? (
                shortTermSkills.map((skill: string, idx: number) => (
                  <li key={idx} className="flex items-center text-gray-700">
                    <CheckCircle className="mr-2 text-green-500" size={16} />
                    {skill}
                  </li>
                ))
              ) : (
                <li className="text-gray-500">No short-term priorities identified</li>
              )}
            </ul>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <TrendingUp className="mr-2 text-primary-600" size={24} />
              Long-term Priority Skills
            </h2>
            <ul className="space-y-2">
              {longTermSkills.length > 0 ? (
                longTermSkills.map((skill: string, idx: number) => (
                  <li key={idx} className="flex items-center text-gray-700">
                    <CheckCircle className="mr-2 text-blue-500" size={16} />
                    {skill}
                  </li>
                ))
              ) : (
                <li className="text-gray-500">No long-term priorities identified</li>
              )}
            </ul>
          </div>
        </div>

        {/* Detailed Skill Gaps */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-6">Detailed Skill Gaps</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Skill</th>
                  <th className="text-left py-3 px-4">Gap Score</th>
                  <th className="text-left py-3 px-4">Priority</th>
                  <th className="text-left py-3 px-4">Timeframe</th>
                  <th className="text-left py-3 px-4">Current Demand</th>
                  <th className="text-left py-3 px-4">Future Demand</th>
                </tr>
              </thead>
              <tbody>
                {analysis.skill_gaps?.map((gap: any, idx: number) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{gap.skill_name}</td>
                    <td className="py-3 px-4">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{ width: `${gap.gap_score * 100}%` }}
                        />
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          gap.priority === 'high'
                            ? 'bg-red-100 text-red-800'
                            : gap.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {gap.priority}
                      </span>
                    </td>
                    <td className="py-3 px-4">{gap.timeframe}</td>
                    <td className="py-3 px-4">{gap.current_demand_score.toFixed(1)}</td>
                    <td className="py-3 px-4">{gap.future_demand_score.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Link
            href="/dashboard/roadmap"
            className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 inline-block"
          >
            Generate Learning Roadmap
          </Link>
        </div>
      </div>
    </div>
  )
}
