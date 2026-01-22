'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { TrendingUp, Users, BookOpen, BarChart3, ArrowRight } from 'lucide-react'

export default function Home() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">SGIP</h1>
              <span className="ml-2 text-sm text-gray-600">Skill Gap Intelligence Platform</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/dashboard" 
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Predict. Learn. Succeed.
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            AI-powered skill intelligence platform that analyzes job markets, predicts emerging skills, 
            and guides learners and institutions toward future-ready education and careers.
          </p>
          <div className="flex justify-center space-x-4">
            <Link 
              href="/dashboard"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-primary-700 flex items-center"
            >
              Get Started
              <ArrowRight className="ml-2" size={20} />
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <TrendingUp className="text-primary-600 mb-4" size={40} />
            <h3 className="text-xl font-semibold mb-2">Skill Forecasting</h3>
            <p className="text-gray-600">
              Predict future high-demand skills using Google Trends and AI analysis
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <Users className="text-primary-600 mb-4" size={40} />
            <h3 className="text-xl font-semibold mb-2">Gap Analysis</h3>
            <p className="text-gray-600">
              Identify skill gaps at individual and institutional levels
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <BookOpen className="text-primary-600 mb-4" size={40} />
            <h3 className="text-xl font-semibold mb-2">Personalized Roadmaps</h3>
            <p className="text-gray-600">
              AI-generated learning paths tailored to your career goals
            </p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <BarChart3 className="text-primary-600 mb-4" size={40} />
            <h3 className="text-xl font-semibold mb-2">Curriculum Alignment</h3>
            <p className="text-gray-600">
              Align academic curricula with industry needs and future demands
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
