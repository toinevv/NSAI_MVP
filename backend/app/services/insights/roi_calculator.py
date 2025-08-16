"""
ROI Calculator for NewSystem.AI
Calculates time savings, cost savings, and return on investment
Critical for proving value to customers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ROICalculator:
    """
    Calculates ROI metrics for workflow automation opportunities
    Based on industry standards for logistics operations
    """
    
    # Industry standard costs (adjustable per customer)
    DEFAULT_HOURLY_RATE = 25.00  # USD per hour for warehouse operator
    DEFAULT_WORKING_DAYS = 250   # Annual working days
    DEFAULT_WORKING_HOURS = 8    # Daily working hours
    
    # Implementation costs (estimates)
    IMPLEMENTATION_COSTS = {
        "simple": 5000,      # Basic RPA/integration
        "moderate": 15000,   # Custom development
        "complex": 50000     # Full system integration
    }
    
    # Automation efficiency factors
    AUTOMATION_EFFICIENCY = {
        "high": 0.95,      # 95% of manual time saved
        "medium": 0.75,     # 75% of manual time saved
        "low": 0.50         # 50% of manual time saved
    }
    
    def calculate_roi(
        self,
        analysis_results: Dict[str, Any],
        hourly_rate: float = None,
        implementation_budget: float = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive ROI metrics
        
        Args:
            analysis_results: Analysis results from GPT-4V
            hourly_rate: Custom hourly rate (optional)
            implementation_budget: Available budget (optional)
            
        Returns:
            ROI metrics including savings, costs, and payback period
        """
        hourly_rate = hourly_rate or self.DEFAULT_HOURLY_RATE
        opportunities = analysis_results.get("automation_opportunities", [])
        
        if not opportunities:
            return self._empty_roi_result()
        
        # Calculate metrics for each opportunity
        opportunity_metrics = []
        total_daily_minutes_saved = 0
        total_implementation_cost = 0
        
        for opp in opportunities:
            metrics = self._calculate_opportunity_metrics(opp, hourly_rate)
            opportunity_metrics.append(metrics)
            total_daily_minutes_saved += metrics["daily_minutes_saved"]
            total_implementation_cost += metrics["implementation_cost"]
        
        # Calculate aggregate metrics
        total_daily_hours_saved = total_daily_minutes_saved / 60
        total_weekly_hours_saved = total_daily_hours_saved * 5
        total_monthly_hours_saved = total_daily_hours_saved * 20
        total_annual_hours_saved = total_daily_hours_saved * self.DEFAULT_WORKING_DAYS
        
        # Calculate cost savings
        daily_savings = total_daily_hours_saved * hourly_rate
        weekly_savings = total_weekly_hours_saved * hourly_rate
        monthly_savings = total_monthly_hours_saved * hourly_rate
        annual_savings = total_annual_hours_saved * hourly_rate
        
        # Calculate payback period
        payback_months = 0
        roi_percentage = 0
        
        if monthly_savings > 0 and total_implementation_cost > 0:
            payback_months = total_implementation_cost / monthly_savings
            roi_percentage = ((annual_savings - total_implementation_cost) / total_implementation_cost) * 100
        
        # Determine implementation priority
        priority = self._determine_priority(
            annual_savings,
            total_implementation_cost,
            payback_months
        )
        
        # Create summary
        result = {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            
            # Time savings
            "time_savings": {
                "daily_hours": round(total_daily_hours_saved, 2),
                "weekly_hours": round(total_weekly_hours_saved, 2),
                "monthly_hours": round(total_monthly_hours_saved, 2),
                "annual_hours": round(total_annual_hours_saved, 2),
                "percentage_of_workday": round((total_daily_hours_saved / self.DEFAULT_WORKING_HOURS) * 100, 1)
            },
            
            # Cost savings
            "cost_savings": {
                "daily_usd": round(daily_savings, 2),
                "weekly_usd": round(weekly_savings, 2),
                "monthly_usd": round(monthly_savings, 2),
                "annual_usd": round(annual_savings, 2),
                "hourly_rate_used": hourly_rate
            },
            
            # Implementation costs
            "implementation": {
                "total_cost_usd": round(total_implementation_cost, 2),
                "payback_period_months": round(payback_months, 1),
                "roi_percentage": round(roi_percentage, 1),
                "priority": priority,
                "within_budget": implementation_budget is None or total_implementation_cost <= implementation_budget
            },
            
            # Opportunity breakdown
            "opportunities": opportunity_metrics,
            
            # Executive summary
            "executive_summary": self._generate_executive_summary(
                total_annual_hours_saved,
                annual_savings,
                total_implementation_cost,
                payback_months,
                len(opportunities)
            ),
            
            # Recommendations
            "recommendations": self._generate_recommendations(
                opportunity_metrics,
                implementation_budget
            )
        }
        
        logger.info(f"ROI calculated: ${annual_savings:,.0f} annual savings, {payback_months:.1f} month payback")
        
        return result
    
    def _calculate_opportunity_metrics(
        self,
        opportunity: Dict[str, Any],
        hourly_rate: float
    ) -> Dict[str, Any]:
        """Calculate metrics for a single opportunity"""
        
        # Extract data with defaults
        daily_minutes = opportunity.get("time_saved_daily_minutes", 0)
        if daily_minutes == 0:
            # Try to calculate from frequency and time per occurrence
            frequency = opportunity.get("frequency_daily", 1)
            time_per = opportunity.get("time_per_occurrence_minutes", 0)
            daily_minutes = frequency * time_per
        
        complexity = opportunity.get("implementation_complexity", "moderate")
        potential = opportunity.get("automation_potential", "medium")
        
        # Calculate actual time saved (considering automation efficiency)
        efficiency = self.AUTOMATION_EFFICIENCY.get(potential, 0.75)
        actual_daily_minutes = daily_minutes * efficiency
        
        # Calculate costs
        implementation_cost = self.IMPLEMENTATION_COSTS.get(complexity.lower(), 15000)
        
        # Calculate savings
        daily_hours = actual_daily_minutes / 60
        annual_hours = daily_hours * self.DEFAULT_WORKING_DAYS
        annual_savings = annual_hours * hourly_rate
        
        # Calculate ROI for this opportunity
        roi = 0
        payback = 0
        if annual_savings > 0 and implementation_cost > 0:
            roi = ((annual_savings - implementation_cost) / implementation_cost) * 100
            payback = implementation_cost / (annual_savings / 12)  # Months
        
        return {
            "description": opportunity.get("description", opportunity.get("workflow_type", "Unknown")),
            "daily_minutes_saved": round(actual_daily_minutes, 1),
            "annual_hours_saved": round(annual_hours, 1),
            "annual_cost_savings": round(annual_savings, 2),
            "implementation_cost": implementation_cost,
            "implementation_complexity": complexity,
            "automation_potential": potential,
            "roi_percentage": round(roi, 1),
            "payback_months": round(payback, 1),
            "efficiency_factor": efficiency,
            "recommendation": opportunity.get("recommendation", opportunity.get("specific_recommendation", ""))
        }
    
    def _determine_priority(
        self,
        annual_savings: float,
        implementation_cost: float,
        payback_months: float
    ) -> str:
        """Determine implementation priority based on metrics"""
        
        if payback_months <= 3:
            return "immediate"  # Quick win
        elif payback_months <= 6 and annual_savings > 50000:
            return "high"       # High value, reasonable payback
        elif payback_months <= 12:
            return "medium"     # Standard priority
        elif annual_savings > implementation_cost * 2:
            return "strategic"  # Long-term but high value
        else:
            return "low"        # Consider carefully
    
    def _generate_executive_summary(
        self,
        annual_hours: float,
        annual_savings: float,
        implementation_cost: float,
        payback_months: float,
        opportunity_count: int
    ) -> str:
        """Generate executive summary text"""
        
        if annual_savings == 0:
            return "No significant automation opportunities identified in this recording."
        
        # Calculate FTE equivalent
        fte_equivalent = annual_hours / (self.DEFAULT_WORKING_HOURS * self.DEFAULT_WORKING_DAYS)
        
        summary = f"Analysis identified {opportunity_count} automation opportunities "
        summary += f"that could save {annual_hours:,.0f} hours annually "
        summary += f"(equivalent to {fte_equivalent:.1f} FTE). "
        summary += f"This represents ${annual_savings:,.0f} in cost savings per year. "
        
        if implementation_cost > 0:
            summary += f"With an estimated implementation cost of ${implementation_cost:,.0f}, "
            summary += f"the investment would pay back in {payback_months:.1f} months."
        
        return summary
    
    def _generate_recommendations(
        self,
        opportunities: List[Dict[str, Any]],
        budget: Optional[float]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Sort by ROI
        sorted_opps = sorted(opportunities, key=lambda x: x["roi_percentage"], reverse=True)
        
        # Quick wins (payback < 3 months)
        quick_wins = [o for o in sorted_opps if o["payback_months"] <= 3]
        if quick_wins:
            recommendations.append(
                f"Start with {len(quick_wins)} quick win(s) that pay back in under 3 months: " +
                ", ".join([o["description"] for o in quick_wins[:3]])
            )
        
        # High ROI opportunities
        high_roi = [o for o in sorted_opps if o["roi_percentage"] > 200]
        if high_roi:
            recommendations.append(
                f"Focus on high-ROI opportunities with {high_roi[0]['roi_percentage']:.0f}% return: " +
                high_roi[0]["description"]
            )
        
        # Budget-conscious recommendation
        if budget:
            within_budget = [o for o in sorted_opps if o["implementation_cost"] <= budget]
            if within_budget:
                total_savings = sum(o["annual_cost_savings"] for o in within_budget)
                recommendations.append(
                    f"Within ${budget:,.0f} budget, you can automate {len(within_budget)} workflows " +
                    f"for ${total_savings:,.0f} annual savings"
                )
        
        # Strategic recommendation
        total_annual_savings = sum(o["annual_cost_savings"] for o in opportunities)
        if total_annual_savings > 100000:
            recommendations.append(
                "Consider a phased automation program to capture the full value potential"
            )
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def _empty_roi_result(self) -> Dict[str, Any]:
        """Return empty ROI result when no opportunities found"""
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "time_savings": {
                "daily_hours": 0,
                "weekly_hours": 0,
                "monthly_hours": 0,
                "annual_hours": 0,
                "percentage_of_workday": 0
            },
            "cost_savings": {
                "daily_usd": 0,
                "weekly_usd": 0,
                "monthly_usd": 0,
                "annual_usd": 0,
                "hourly_rate_used": self.DEFAULT_HOURLY_RATE
            },
            "implementation": {
                "total_cost_usd": 0,
                "payback_period_months": 0,
                "roi_percentage": 0,
                "priority": "none",
                "within_budget": True
            },
            "opportunities": [],
            "executive_summary": "No automation opportunities identified in this recording.",
            "recommendations": []
        }
    
    def generate_comparison(
        self,
        current_state: Dict[str, Any],
        future_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate before/after comparison for visualization
        
        Args:
            current_state: Current workflow metrics
            future_state: Projected metrics after automation
            
        Returns:
            Comparison data for visualization
        """
        return {
            "current": {
                "daily_hours": current_state.get("total_hours_daily", 8),
                "manual_tasks": current_state.get("manual_task_count", 0),
                "error_rate": current_state.get("error_rate_percentage", 5),
                "processing_time": current_state.get("average_processing_minutes", 10),
                "annual_cost": current_state.get("annual_labor_cost", 50000)
            },
            "future": {
                "daily_hours": future_state.get("total_hours_daily", 6),
                "manual_tasks": future_state.get("manual_task_count", 0),
                "error_rate": future_state.get("error_rate_percentage", 1),
                "processing_time": future_state.get("average_processing_minutes", 2),
                "annual_cost": future_state.get("annual_labor_cost", 35000)
            },
            "improvements": {
                "time_reduction_percentage": 25,
                "error_reduction_percentage": 80,
                "cost_reduction_percentage": 30,
                "productivity_increase_percentage": 35
            }
        }


# Singleton instance
_roi_calculator: Optional[ROICalculator] = None

def get_roi_calculator() -> ROICalculator:
    """Get singleton ROI calculator instance"""
    global _roi_calculator
    if _roi_calculator is None:
        _roi_calculator = ROICalculator()
    return _roi_calculator