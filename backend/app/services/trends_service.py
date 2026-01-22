"""
Google Trends integration service for skill demand forecasting
"""

from pytrends.request import TrendReq
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class TrendsService:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    def get_trend_data(self, skill_keywords: List[str], timeframe: str = 'today 12-m') -> Dict[str, Any]:
        """
        Get Google Trends data for skill keywords
        
        Args:
            skill_keywords: List of skill names to analyze
            timeframe: Time range for trends (e.g., 'today 12-m', 'today 3-m')
        
        Returns:
            Dictionary with trend data for each skill
        """
        results = {}
        
        for skill in skill_keywords:
            try:
                # Build payload
                self.pytrends.build_payload([skill], timeframe=timeframe, geo='IN')  # India-focused
                
                # Get interest over time
                interest_over_time = self.pytrends.interest_over_time()
                
                if not interest_over_time.empty:
                    # Calculate average interest
                    avg_interest = interest_over_time[skill].mean()
                    
                    # Calculate growth rate (compare first half vs second half)
                    mid_point = len(interest_over_time) // 2
                    first_half_avg = interest_over_time[skill][:mid_point].mean()
                    second_half_avg = interest_over_time[skill][mid_point:].mean()
                    
                    if first_half_avg > 0:
                        growth_rate = ((second_half_avg - first_half_avg) / first_half_avg) * 100
                    else:
                        growth_rate = 0
                    
                    # Get related queries
                    related_queries = self.pytrends.related_queries()
                    
                    results[skill] = {
                        "average_interest": float(avg_interest),
                        "growth_rate": float(growth_rate),
                        "trend_data": interest_over_time[skill].to_dict(),
                        "related_queries": related_queries.get(skill, {}).get('rising', pd.DataFrame()).to_dict('records') if related_queries.get(skill) else []
                    }
                else:
                    results[skill] = {
                        "average_interest": 0.0,
                        "growth_rate": 0.0,
                        "trend_data": {},
                        "related_queries": []
                    }
            except Exception as e:
                print(f"Error fetching trends for {skill}: {e}")
                results[skill] = {
                    "average_interest": 0.0,
                    "growth_rate": 0.0,
                    "trend_data": {},
                    "related_queries": []
                }
        
        return results
    
    def classify_skill_trend(self, growth_rate: float, avg_interest: float) -> str:
        """
        Classify skill into trend categories
        
        Returns:
            'emerging', 'high-growth', 'saturated', or 'declining'
        """
        if growth_rate > 30 and avg_interest < 50:
            return "emerging"
        elif growth_rate > 15:
            return "high-growth"
        elif growth_rate < -10:
            return "declining"
        else:
            return "saturated"
    
    def forecast_skill_demand(
        self,
        skill: str,
        current_demand: float,
        growth_rate: float
    ) -> Dict[str, float]:
        """
        Forecast skill demand for 6 months, 1 year, and 3 years
        
        Uses simple exponential growth model based on current growth rate
        """
        # Simple forecasting model
        # In production, use more sophisticated time-series forecasting
        
        forecast_6m = current_demand * (1 + (growth_rate / 100) * 0.5)
        forecast_1y = current_demand * (1 + (growth_rate / 100))
        forecast_3y = current_demand * (1 + (growth_rate / 100) * 3)
        
        # Cap forecasts to reasonable ranges
        forecast_6m = max(0, min(100, forecast_6m))
        forecast_1y = max(0, min(100, forecast_1y))
        forecast_3y = max(0, min(100, forecast_3y))
        
        return {
            "forecast_6m": forecast_6m,
            "forecast_1y": forecast_1y,
            "forecast_3y": forecast_3y
        }
    
    def analyze_multiple_skills(self, skills: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple skills and return comprehensive trend analysis
        """
        trend_data = self.get_trend_data(skills)
        results = []
        
        for skill, data in trend_data.items():
            trend_status = self.classify_skill_trend(
                data["growth_rate"],
                data["average_interest"]
            )
            
            forecasts = self.forecast_skill_demand(
                skill,
                data["average_interest"],
                data["growth_rate"]
            )
            
            results.append({
                "skill": skill,
                "current_demand": data["average_interest"],
                "growth_rate": data["growth_rate"],
                "trend_status": trend_status,
                "forecasts": forecasts,
                "trend_data": data["trend_data"]
            })
        
        return results
