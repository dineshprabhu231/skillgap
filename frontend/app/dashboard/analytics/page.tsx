'use client'

import { useState, useEffect } from 'react'
import { analyticsAPI, skillsAPI } from '@/lib/api'
import { BarChart3, TrendingUp } from 'lucide-react'
import Link from 'next/link'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function AnalyticsPage() {
  const [heatmapData, setHeatmapData] = useState<any[]>([])
  const [trendData, setTrendData] = useState<any[]>([])
  const [trendingSkills, setTrendingSkills] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const [heatmap, trends, trending] = await Promise.all([
        analyticsAPI.getSkillHeatmap(),
        analyticsAPI.getTrendGrowth(),
        skillsAPI.getTrending(undefined, 10),
      ])
      setHeatmapData(heatmap.data.skills || [])
      setTrendData(trends.data.trends || [])
      setTrendingSkills(trending.data || [])
    } catch (error) {
      console.error('Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading analytics...</div>
      </div>
    )
  }

  // Prepare chart data
  const trendingChartData = trendingSkills.map((skill) => ({
    name: skill.name,
    current: skill.current_demand_score,
    future: skill.future_demand_score,
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link href="/dashboard" className="text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Dashboard
        </Link>

        <h1 className="text-3xl font-bold mb-8">Analytics Dashboard</h1>

        {/* Trending Skills Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <TrendingUp className="mr-2 text-primary-600" size={24} />
            Top Trending Skills
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendingChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="current" fill="#0ea5e9" name="Current Demand" />
              <Bar dataKey="future" fill="#10b981" name="Future Demand" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Skill Heatmap Table */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <BarChart3 className="mr-2 text-primary-600" size={24} />
            Skill Demand Heatmap
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Skill</th>
                  <th className="text-left py-3 px-4">Domain</th>
                  <th className="text-left py-3 px-4">Current Demand</th>
                  <th className="text-left py-3 px-4">Future Demand</th>
                  <th className="text-left py-3 px-4">Trend Status</th>
                </tr>
              </thead>
              <tbody>
                {heatmapData.slice(0, 20).map((skill, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{skill.skill}</td>
                    <td className="py-3 px-4">{skill.domain || 'N/A'}</td>
                    <td className="py-3 px-4">{skill.current_demand?.toFixed(1) || 0}</td>
                    <td className="py-3 px-4">{skill.future_demand?.toFixed(1) || 0}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          skill.trend_status === 'emerging'
                            ? 'bg-green-100 text-green-800'
                            : skill.trend_status === 'high-growth'
                            ? 'bg-blue-100 text-blue-800'
                            : skill.trend_status === 'declining'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {skill.trend_status || 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Trend Growth Charts */}
        {trendData.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Trend Growth Analysis</h2>
            <div className="space-y-6">
              {trendData.slice(0, 3).map((trend, idx) => (
                <div key={idx}>
                  <h3 className="font-semibold mb-2">{trend.skill}</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={trend.trend_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#0ea5e9"
                        name="Search Interest"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                  <div className="mt-2 text-sm text-gray-600">
                    Growth Rate: {trend.growth_rate?.toFixed(1)}% • Status: {trend.classification}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
