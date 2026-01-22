'use client'

import { useState, useEffect } from 'react'
import { analyticsAPI } from '@/lib/api'
import { TrendingUp, Upload, FileText, BarChart3 } from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
  const [readiness, setReadiness] = useState<any>(null)
  const [userType, setUserType] = useState<'student' | 'institution'>('student')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      // Try to get student readiness first
      try {
        const readinessResponse = await analyticsAPI.getEmployabilityReadiness()
        setReadiness(readinessResponse.data)
        setUserType('student')
      } catch (error) {
        // If student data not available, try institution
        try {
          const readinessResponse = await analyticsAPI.getInstitutionReadiness()
          setReadiness(readinessResponse.data)
          setUserType('institution')
        } catch (error) {
          // No data available yet
        }
      }
    } catch (error) {
      console.error('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  const isStudent = userType === 'student'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">SGIP Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-700 hover:text-primary-600">
                Home
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to SGIP!
          </h2>
          <p className="text-gray-600">
            {isStudent 
              ? 'Analyze your skills and discover your learning path'
              : 'Manage your curriculum and track alignment with industry needs'}
          </p>
        </div>

        {/* Readiness Score */}
        {readiness && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h3 className="text-xl font-semibold mb-4">
              {isStudent ? 'Employability Readiness' : 'Institution Readiness'}
            </h3>
            {isStudent ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-600">
                    {readiness.readiness_score?.toFixed(0) || 0}%
                  </div>
                  <div className="text-sm text-gray-600">Overall Readiness</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-600">
                    {readiness.domain_coverage?.toFixed(0) || 0}%
                  </div>
                  <div className="text-sm text-gray-600">Domain Coverage</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-600">
                    {readiness.skills_covered || 0}/{readiness.total_skills_required || 0}
                  </div>
                  <div className="text-sm text-gray-600">Skills Covered</div>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-600">
                    {readiness.placement_readiness?.toFixed(0) || 0}%
                  </div>
                  <div className="text-sm text-gray-600">Placement Readiness</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-600">
                    {readiness.industry_collaboration?.toFixed(0) || 0}%
                  </div>
                  <div className="text-sm text-gray-600">Industry Collaboration</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-600">
                    {readiness.accreditation?.toFixed(0) || 0}%
                  </div>
                  <div className="text-sm text-gray-600">Accreditation</div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isStudent ? (
            <>
              <Link href="/dashboard/resume" className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
                <Upload className="text-primary-600 mb-4" size={40} />
                <h3 className="text-xl font-semibold mb-2">Upload Resume</h3>
                <p className="text-gray-600">Upload your resume to analyze your current skills</p>
              </Link>

              <Link href="/dashboard/gaps" className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
                <TrendingUp className="text-primary-600 mb-4" size={40} />
                <h3 className="text-xl font-semibold mb-2">Skill Gap Analysis</h3>
                <p className="text-gray-600">Identify gaps between your skills and market demand</p>
              </Link>

              <Link href="/dashboard/roadmap" className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
                <FileText className="text-primary-600 mb-4" size={40} />
                <h3 className="text-xl font-semibold mb-2">Learning Roadmap</h3>
                <p className="text-gray-600">Get a personalized learning path to your dream role</p>
              </Link>
            </>
          ) : (
            <>
              <Link href="/dashboard/curriculum" className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
                <Upload className="text-primary-600 mb-4" size={40} />
                <h3 className="text-xl font-semibold mb-2">Upload Curriculum</h3>
                <p className="text-gray-600">Upload your curriculum for analysis and alignment</p>
              </Link>

              <Link href="/dashboard/analytics" className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
                <BarChart3 className="text-primary-600 mb-4" size={40} />
                <h3 className="text-xl font-semibold mb-2">Analytics Dashboard</h3>
                <p className="text-gray-600">View skill trends and market insights</p>
              </Link>

              <Link href="/dashboard/recommendations" className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
                <TrendingUp className="text-primary-600 mb-4" size={40} />
                <h3 className="text-xl font-semibold mb-2">Recommendations</h3>
                <p className="text-gray-600">Get AI-powered curriculum improvement suggestions</p>
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
