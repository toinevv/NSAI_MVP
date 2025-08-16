"""
Result Parser for GPT-4V Analysis
Parses and structures GPT-4V responses into actionable insights
Handles validation and error recovery for malformed responses
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from app.services.workflow_utils import get_workflow_detector

logger = logging.getLogger(__name__)


class ResultParser:
    """
    Parses GPT-4V analysis results into structured format
    Focuses on extracting actionable automation opportunities
    """
    
    def __init__(self):
        self.workflow_detector = get_workflow_detector()
    
    def parse_analysis_result(
        self,
        gpt_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse complete GPT-4V analysis response
        Handles both natural language and structured formats
        
        Args:
            gpt_response: Raw response from GPT-4V client
            
        Returns:
            Structured analysis results
        """
        if not gpt_response.get("success"):
            return self._create_error_result(gpt_response.get("error", "Analysis failed"))
        
        try:
            # Extract the analysis content
            analysis = gpt_response.get("analysis", {})
            
            # Check if this is natural language format
            if "natural_description" in analysis:
                return self._parse_natural_format(analysis, gpt_response)
            
            # Otherwise, parse as structured format (backwards compatibility)
            workflows = self._parse_workflows(analysis.get("workflows_detected", []))
            opportunities = self._parse_opportunities(analysis.get("automation_opportunities", []))
            time_breakdown = self._parse_time_breakdown(analysis.get("time_breakdown", {}))
            insights = self._parse_insights(analysis.get("key_insights", []))
            confidence = self._parse_confidence(analysis.get("confidence_score", 0.7))
            
            # Calculate summary metrics
            summary = self._calculate_summary(workflows, opportunities, time_breakdown)
            
            # Structure the final result
            result = {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "workflows": workflows,
                "automation_opportunities": opportunities,
                "time_analysis": time_breakdown,
                "insights": insights,
                "summary": summary,
                "confidence_score": confidence,
                "metadata": gpt_response.get("metadata", {}),
                "usage": gpt_response.get("usage", {}),
                # Include raw GPT-4V response for verification
                "raw_gpt_response": analysis
            }
            
            logger.info(f"Successfully parsed analysis with {len(workflows)} workflows and {len(opportunities)} opportunities")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse analysis result: {e}")
            return self._create_error_result(f"Parsing failed: {e}")
    
    def _parse_workflows(self, workflows_raw: List[Any]) -> List[Dict[str, Any]]:
        """
        Parse detected workflows
        
        Args:
            workflows_raw: Raw workflows from GPT-4V
            
        Returns:
            Structured workflow list
        """
        workflows = []
        
        for workflow in workflows_raw:
            if not isinstance(workflow, dict):
                continue
            
            # Detect or use existing workflow type
            workflow_type = workflow.get("type", "unknown")
            if workflow_type == "unknown":
                workflow_type = self.workflow_detector.detect_workflow_type(
                    applications=workflow.get("applications_involved", []),
                    description=workflow.get("description", ""),
                    steps=workflow.get("steps_observed", [])
                )
            
            # Calculate priority score using workflow detector
            repetitive_score = workflow.get("repetitive_score", 0.5)
            priority_score = self.workflow_detector.calculate_priority_score(
                workflow_type=workflow_type,
                repetitive_score=repetitive_score
            )
            
            parsed_workflow = {
                "type": workflow_type,
                "description": workflow.get("description", ""),
                "applications": workflow.get("applications_involved", []),
                "steps": workflow.get("steps_observed", []),
                "duration_seconds": workflow.get("estimated_duration_seconds", 0),
                "data_types": workflow.get("data_types_handled", []),
                "repetitive_score": repetitive_score,
                "priority_score": priority_score
            }
            
            workflows.append(parsed_workflow)
        
        # Sort by priority score (combines repetitive score with workflow type importance)
        workflows.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return workflows
    
    def _parse_opportunities(self, opportunities_raw: List[Any]) -> List[Dict[str, Any]]:
        """
        Parse automation opportunities
        
        Args:
            opportunities_raw: Raw opportunities from GPT-4V
            
        Returns:
            Structured opportunities list
        """
        opportunities = []
        
        for opp in opportunities_raw:
            if not isinstance(opp, dict):
                continue
            
            # Calculate daily and annual savings
            freq_daily = opp.get("frequency_daily", 1)
            time_per_occurrence = opp.get("time_per_occurrence_minutes", 0)
            daily_savings = freq_daily * time_per_occurrence
            
            parsed_opp = {
                "workflow_type": opp.get("workflow_type", "unknown"),
                "description": opp.get("description", ""),
                "frequency_daily": freq_daily,
                "time_per_occurrence_minutes": time_per_occurrence,
                "time_saved_daily_minutes": opp.get("total_time_saved_daily_minutes", daily_savings),
                "time_saved_weekly_hours": daily_savings * 5 / 60,  # 5 working days
                "time_saved_annually_hours": daily_savings * 250 / 60,  # 250 working days
                "cost_saved_annually": daily_savings * 250 / 60 * 25,  # $25/hour
                "automation_potential": opp.get("automation_potential", "medium"),
                "implementation_complexity": opp.get("implementation_complexity", "medium"),
                "recommendation": opp.get("specific_recommendation", ""),
                "priority_score": self._calculate_priority(
                    opp.get("automation_potential", "medium"),
                    opp.get("implementation_complexity", "medium"),
                    daily_savings
                )
            }
            
            opportunities.append(parsed_opp)
        
        # Sort by priority score
        opportunities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return opportunities
    
    def _parse_time_breakdown(self, time_raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse time breakdown analysis with dynamic application tracking
        
        Args:
            time_raw: Raw time breakdown from GPT-4V
            
        Returns:
            Structured time analysis
        """
        total_time = time_raw.get("total_time_analyzed_seconds", 0)
        idle_seconds = time_raw.get("idle_time_seconds", 0)
        
        # Handle both new and legacy formats
        application_breakdown = time_raw.get("application_time_breakdown", {})
        
        # Support legacy format for backwards compatibility
        if not application_breakdown:
            application_breakdown = {
                "primary_app": time_raw.get("email_time_seconds", time_raw.get("wms_time_seconds", 0)),
                "secondary_app": time_raw.get("excel_time_seconds", 0),
                "supporting_tools": time_raw.get("other_time_seconds", 0)
            }
        
        breakdown = {
            "total_seconds": total_time,
            "idle_seconds": idle_seconds,
            "application_breakdown": application_breakdown
        }
        
        # Calculate 'other' time from unaccounted time
        accounted_time = sum(application_breakdown.values()) + idle_seconds
        other_time = max(0, total_time - accounted_time)
        if other_time > 0:
            breakdown["application_breakdown"]["unaccounted"] = other_time
        
        # Calculate percentages
        if total_time > 0:
            breakdown["idle_percentage"] = round(100 * idle_seconds / total_time, 1)
            breakdown["productive_percentage"] = round(100 * (total_time - idle_seconds) / total_time, 1)
            
            # Calculate percentages for each application
            breakdown["application_percentages"] = {}
            for app_name, app_time in application_breakdown.items():
                breakdown["application_percentages"][app_name] = round(100 * app_time / total_time, 1)
        
        return breakdown
    
    def _parse_natural_format(self, analysis: Dict[str, Any], gpt_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse natural language format response from GPT-4V
        
        Args:
            analysis: Natural language analysis from GPT-4V
            gpt_response: Full GPT response with metadata
            
        Returns:
            Structured analysis results
        """
        # Extract total frame count from metadata if available
        total_frames = gpt_response.get("metadata", {}).get("frames_analyzed", 0)
        if total_frames == 0:
            # Try to get from analysis itself
            total_frames = self._estimate_total_frames(analysis)
        
        # Calculate time from frames for workflow steps
        workflow_steps = analysis.get("workflow_steps", [])
        if workflow_steps:
            workflow_steps = self._calculate_step_times(workflow_steps)
        
        # Calculate time from frames for applications
        applications_data = analysis.get("applications", {})
        if applications_data:
            applications_data = self._calculate_application_times(applications_data, total_frames)
        
        # Update workflow chart with calculated times
        workflow_chart = analysis.get("workflow_chart", {})
        if workflow_chart and "nodes" in workflow_chart:
            workflow_chart["nodes"] = self._calculate_node_times(workflow_chart["nodes"])
        
        # Parse applications into workflows
        workflows = self._parse_natural_workflows(analysis)
        
        # Parse automation opportunities
        opportunities = self._parse_natural_opportunities(
            analysis.get("automation_opportunities", [])
        )
        
        # Parse metrics into time breakdown
        time_breakdown = self._parse_natural_metrics(
            analysis.get("metrics", {})
        )
        
        # Enhance time breakdown with calculated application data
        if applications_data:
            time_breakdown = self._enhance_time_breakdown_with_applications(
                time_breakdown, applications_data
            )
        
        # Parse patterns as insights
        insights = analysis.get("patterns", [])
        if not isinstance(insights, list):
            insights = []
            
        # Workflow chart already processed above with calculated times
        
        # Extract confidence
        confidence = self._parse_confidence(
            analysis.get("confidence", 0.8)
        )
        
        # Calculate summary
        summary = self._calculate_natural_summary(
            workflows, opportunities, analysis
        )
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "workflows": workflows,
            "automation_opportunities": opportunities,
            "time_analysis": time_breakdown,
            "insights": insights[:5],  # Limit to 5
            "summary": summary,
            "confidence_score": confidence,
            "metadata": gpt_response.get("metadata", {}),
            "usage": gpt_response.get("usage", {}),
            "raw_gpt_response": analysis,
            "workflow_chart": workflow_chart,  # Chart data with calculated times for visualization
            "workflow_steps": workflow_steps,  # Steps with calculated times
            "format": "natural"  # Flag to indicate natural format
        }
    
    def _calculate_time_from_frames(self, frame_list: List[int]) -> Dict[str, Any]:
        """
        Calculate duration and statistics from frame numbers
        
        Args:
            frame_list: List of frame numbers where activity appears
            
        Returns:
            Time statistics dictionary
        """
        if not frame_list:
            return {
                "seconds": 0,
                "formatted": "0s",
                "frame_count": 0,
                "continuous_ranges": []
            }
        
        # Frames are 1 second apart
        duration_seconds = len(frame_list)
        
        # Find continuous ranges for better understanding
        continuous_ranges = self._find_continuous_ranges(frame_list)
        
        # Format time nicely
        formatted = self._format_duration(duration_seconds)
        
        return {
            "seconds": duration_seconds,
            "formatted": formatted,
            "frame_count": len(frame_list),
            "continuous_ranges": continuous_ranges
        }
    
    def _find_continuous_ranges(self, frames: List[int]) -> List[Dict[str, int]]:
        """
        Find continuous frame ranges
        
        Args:
            frames: List of frame numbers
            
        Returns:
            List of continuous ranges
        """
        if not frames:
            return []
        
        sorted_frames = sorted(frames)
        ranges = []
        start = sorted_frames[0]
        end = sorted_frames[0]
        
        for frame in sorted_frames[1:]:
            if frame == end + 1:
                end = frame
            else:
                ranges.append({"start": start, "end": end, "duration": end - start + 1})
                start = frame
                end = frame
        
        ranges.append({"start": start, "end": end, "duration": end - start + 1})
        return ranges
    
    def _format_duration(self, seconds: int) -> str:
        """
        Format duration in seconds to human-readable string
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string (e.g., "2m 30s")
        """
        if seconds < 60:
            return f"{seconds}s"
        
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        
        if remaining_seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {remaining_seconds}s"
    
    def _calculate_step_times(self, workflow_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate time for each workflow step from frame data
        
        Args:
            workflow_steps: Steps with visible_in_frames data
            
        Returns:
            Steps with calculated time_estimate_seconds
        """
        for step in workflow_steps:
            if isinstance(step, dict):
                frames = step.get("visible_in_frames", [])
                time_data = self._calculate_time_from_frames(frames)
                
                # Add calculated time
                step["time_estimate_seconds"] = time_data["seconds"]
                step["time_formatted"] = time_data["formatted"]
                step["frame_ranges"] = time_data["continuous_ranges"]
        
        return workflow_steps
    
    def _calculate_application_times(self, applications: Dict[str, Any], total_frames: int) -> Dict[str, Any]:
        """
        Calculate time and percentages for each application
        
        Args:
            applications: Application data with visible_in_frames
            total_frames: Total number of frames analyzed
            
        Returns:
            Applications with calculated timeSeconds and timePercentage
        """
        if total_frames == 0:
            total_frames = self._estimate_total_frames_from_apps(applications)
        
        for app_name, app_data in applications.items():
            if isinstance(app_data, dict):
                frames = app_data.get("visible_in_frames", [])
                time_data = self._calculate_time_from_frames(frames)
                
                # Add calculated times
                app_data["timeSeconds"] = time_data["seconds"]
                app_data["timeFormatted"] = time_data["formatted"]
                app_data["frameCount"] = time_data["frame_count"]
                
                # Calculate percentage
                if total_frames > 0:
                    app_data["timePercentage"] = round(100 * time_data["seconds"] / total_frames, 1)
                else:
                    app_data["timePercentage"] = 0
        
        return applications
    
    def _calculate_node_times(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate time for workflow chart nodes
        
        Args:
            nodes: Chart nodes with visible_in_frames in metadata
            
        Returns:
            Nodes with calculated time in metadata
        """
        for node in nodes:
            if isinstance(node, dict) and "metadata" in node:
                metadata = node["metadata"]
                if "visible_in_frames" in metadata:
                    frames = metadata["visible_in_frames"]
                    time_data = self._calculate_time_from_frames(frames)
                    
                    # Add formatted time
                    metadata["time"] = time_data["formatted"]
                    metadata["timeSeconds"] = time_data["seconds"]
        
        return nodes
    
    def _estimate_total_frames(self, analysis: Dict[str, Any]) -> int:
        """
        Estimate total frames from analysis data
        
        Args:
            analysis: Analysis data
            
        Returns:
            Estimated total frame count
        """
        max_frame = 0
        
        # Check workflow steps
        for step in analysis.get("workflow_steps", []):
            if isinstance(step, dict):
                frames = step.get("visible_in_frames", [])
                if frames:
                    max_frame = max(max_frame, max(frames))
        
        # Check applications
        for app_data in analysis.get("applications", {}).values():
            if isinstance(app_data, dict):
                frames = app_data.get("visible_in_frames", [])
                if frames:
                    max_frame = max(max_frame, max(frames))
        
        # Check workflow chart nodes
        for node in analysis.get("workflow_chart", {}).get("nodes", []):
            if isinstance(node, dict) and "metadata" in node:
                frames = node["metadata"].get("visible_in_frames", [])
                if frames:
                    max_frame = max(max_frame, max(frames))
        
        return max_frame
    
    def _estimate_total_frames_from_apps(self, applications: Dict[str, Any]) -> int:
        """
        Estimate total frames from application data
        
        Args:
            applications: Application data
            
        Returns:
            Estimated total frame count
        """
        max_frame = 0
        
        for app_data in applications.values():
            if isinstance(app_data, dict):
                frames = app_data.get("visible_in_frames", [])
                if frames:
                    max_frame = max(max_frame, max(frames))
        
        return max_frame
    
    def _parse_natural_workflows(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse workflows from natural language format
        
        Args:
            analysis: Natural language analysis
            
        Returns:
            List of workflows
        """
        workflows = []
        
        # Extract from applications
        applications = analysis.get("applications", {})
        for app_name, app_data in applications.items():
            if isinstance(app_data, dict):
                # Detect workflow type based on application usage
                actions = app_data.get("actions", [])
                purpose = app_data.get("purpose", "")
                workflow_type = self.workflow_detector.detect_workflow_type(
                    applications=[app_name],
                    description=purpose,
                    steps=actions
                )
                
                # Calculate priority score using workflow detector
                time_percentage = app_data.get("timePercentage", 0)
                repetitive_score = time_percentage / 100
                priority_score = self.workflow_detector.calculate_priority_score(
                    workflow_type=workflow_type,
                    repetitive_score=repetitive_score,
                    time_percentage=time_percentage
                )
                
                workflow = {
                    "type": workflow_type,
                    "description": f"{app_name}: {app_data.get('purpose', 'Workflow processing')}",
                    "applications": [app_name],
                    "steps": actions,
                    "duration_seconds": app_data.get("timeSeconds", 0),  # Now calculated from frames
                    "data_types": [],
                    "repetitive_score": time_percentage / 100 if time_percentage else 0,
                    "priority_score": priority_score
                }
                workflows.append(workflow)
        
        # Extract from workflow steps if present
        workflow_steps = analysis.get("workflow_steps", [])
        if workflow_steps:
            combined_workflow = {
                "type": "observed_workflow",
                "description": analysis.get("natural_description", "Observed workflow")[:200],
                "applications": list(applications.keys()),
                "steps": [step.get("action", "") for step in workflow_steps if isinstance(step, dict)],
                "duration_seconds": sum(
                    step.get("time_estimate_seconds", 0)  # Now calculated from frames
                    for step in workflow_steps 
                    if isinstance(step, dict)
                ),
                "data_types": [],
                "repetitive_score": 0.5,
                "priority_score": 0.5
            }
            workflows.append(combined_workflow)
        
        return workflows
    
    def _parse_natural_opportunities(self, opportunities_raw: List[Any]) -> List[Dict[str, Any]]:
        """
        Parse opportunities from natural language format
        
        Args:
            opportunities_raw: Raw opportunities from natural format
            
        Returns:
            List of opportunities
        """
        opportunities = []
        
        for opp in opportunities_raw:
            if isinstance(opp, dict):
                # Parse time saved (e.g., "30 minutes daily")
                time_saved = opp.get("timeSaved", "0 minutes")
                daily_minutes = self._extract_minutes(time_saved)
                
                parsed_opp = {
                    "workflow_type": "natural_opportunity",
                    "description": opp.get("what", "Automation opportunity"),
                    "frequency_daily": 1,  # Default assumption
                    "time_per_occurrence_minutes": daily_minutes,
                    "time_saved_daily_minutes": daily_minutes,
                    "time_saved_weekly_hours": daily_minutes * 5 / 60,
                    "time_saved_annually_hours": daily_minutes * 250 / 60,
                    "cost_saved_annually": daily_minutes * 250 / 60 * 25,
                    "automation_potential": self._complexity_to_potential(
                        opp.get("complexity", "moderate")
                    ),
                    "implementation_complexity": opp.get("complexity", "moderate"),
                    "recommendation": opp.get("how", ""),
                    "priority_score": 50  # Default medium priority
                }
                opportunities.append(parsed_opp)
        
        # Sort by time saved
        opportunities.sort(key=lambda x: x["time_saved_daily_minutes"], reverse=True)
        
        return opportunities
    
    def _parse_natural_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse metrics into time breakdown format
        Enhanced to extract application time data
        
        Args:
            metrics: Natural format metrics
            
        Returns:
            Time breakdown dict with application breakdown
        """
        total_seconds = metrics.get("totalTimeSeconds", 0)
        
        return {
            "total_seconds": total_seconds,
            "email_seconds": 0,  # Will be populated by applications parser
            "wms_seconds": 0,
            "excel_seconds": 0,
            "idle_seconds": 0,
            "other_seconds": total_seconds,
            "productive_percentage": 80,  # Default assumption
            "applications_used": metrics.get("applicationsUsed", 0),
            "repetitions_observed": metrics.get("repetitionsObserved", 0)
        }
    
    def _calculate_natural_summary(
        self,
        workflows: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate summary for natural format
        
        Args:
            workflows: Parsed workflows
            opportunities: Parsed opportunities
            analysis: Natural analysis data
            
        Returns:
            Summary metrics
        """
        total_daily_minutes = sum(opp["time_saved_daily_minutes"] for opp in opportunities)
        total_annual_savings = sum(opp["cost_saved_annually"] for opp in opportunities)
        
        metrics = analysis.get("metrics", {})
        
        # Count workflows by category
        workflow_type_counts = {}
        high_priority_count = 0
        
        for workflow in workflows:
            workflow_type = workflow.get("type", "other")
            workflow_type_counts[workflow_type] = workflow_type_counts.get(workflow_type, 0) + 1
            
            if workflow.get("priority_score", 0) > 0.7:
                high_priority_count += 1
        
        return {
            "total_workflows_detected": len(workflows),
            "high_priority_workflows": high_priority_count,
            "workflow_type_breakdown": workflow_type_counts,
            "total_opportunities": len(opportunities),
            "high_priority_opportunities": sum(
                1 for o in opportunities 
                if o["automation_potential"] == "high"
            ),
            "time_savings_daily_minutes": round(total_daily_minutes, 1),
            "time_savings_weekly_hours": round(total_daily_minutes * 5 / 60, 1),
            "cost_savings_annual_usd": round(total_annual_savings, 2),
            "highest_impact_opportunity": opportunities[0]["description"] if opportunities else None,
            "roi_multiplier": round(total_annual_savings / 5000, 1) if total_annual_savings > 0 else 0,
            "potential_hours_saved_daily": metrics.get("potentialTimeSavedDailyHours", 0)
        }
    
    def _extract_minutes(self, time_str: str) -> float:
        """
        Extract minutes from time string (e.g., "30 minutes daily")
        
        Args:
            time_str: Time string
            
        Returns:
            Minutes as float
        """
        import re
        
        # Try to extract number
        match = re.search(r'(\d+(?:\.\d+)?)', time_str)
        if match:
            value = float(match.group(1))
            
            # Check unit
            if 'hour' in time_str.lower():
                return value * 60
            elif 'minute' in time_str.lower():
                return value
            else:
                return value  # Assume minutes
        
        return 0
    
    def _complexity_to_potential(self, complexity: str) -> str:
        """
        Convert complexity to automation potential
        
        Args:
            complexity: Implementation complexity
            
        Returns:
            Automation potential
        """
        mapping = {
            "simple": "high",
            "moderate": "medium",
            "complex": "low"
        }
        return mapping.get(complexity.lower(), "medium")
    
    def _parse_insights(self, insights_raw: List[Any]) -> List[str]:
        """
        Parse key insights
        
        Args:
            insights_raw: Raw insights from GPT-4V
            
        Returns:
            List of insight strings
        """
        insights = []
        
        for insight in insights_raw:
            if isinstance(insight, str):
                insights.append(insight)
            elif isinstance(insight, dict):
                insights.append(insight.get("text", str(insight)))
        
        # Limit to top 5 insights
        return insights[:5]
    
    def _parse_confidence(self, confidence_raw: Any) -> float:
        """
        Parse and validate confidence score
        
        Args:
            confidence_raw: Raw confidence value
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            confidence = float(confidence_raw)
            return max(0.0, min(1.0, confidence))
        except (TypeError, ValueError):
            return 0.7  # Default confidence
    
    def _calculate_summary(
        self,
        workflows: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        time_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate summary metrics
        
        Args:
            workflows: Parsed workflows
            opportunities: Parsed opportunities
            time_breakdown: Parsed time analysis
            
        Returns:
            Summary metrics
        """
        # Calculate total savings
        total_daily_minutes = sum(opp["time_saved_daily_minutes"] for opp in opportunities)
        total_weekly_hours = sum(opp["time_saved_weekly_hours"] for opp in opportunities)
        total_annual_savings = sum(opp["cost_saved_annually"] for opp in opportunities)
        
        # Count workflows by type and priority
        high_priority_count = sum(1 for w in workflows if w["priority_score"] > 0.7)
        
        # Count workflows by category
        workflow_type_counts = {}
        for workflow in workflows:
            workflow_type = workflow.get("type", "other")
            workflow_type_counts[workflow_type] = workflow_type_counts.get(workflow_type, 0) + 1
        
        # Find highest impact opportunity
        highest_impact = opportunities[0] if opportunities else None
        
        summary = {
            "total_workflows_detected": len(workflows),
            "high_priority_workflows": high_priority_count,
            "workflow_type_breakdown": workflow_type_counts,
            "total_opportunities": len(opportunities),
            "high_priority_opportunities": sum(1 for o in opportunities if o["automation_potential"] == "high"),
            "time_savings_daily_minutes": round(total_daily_minutes, 1),
            "time_savings_weekly_hours": round(total_weekly_hours, 1),
            "cost_savings_annual_usd": round(total_annual_savings, 2),
            "highest_impact_opportunity": highest_impact["description"] if highest_impact else None,
            "roi_multiplier": round(total_annual_savings / 5000, 1) if total_annual_savings > 0 else 0  # Assuming $5k implementation
        }
        
        return summary
    
    def _calculate_priority(
        self,
        potential: str,
        complexity: str,
        daily_savings: float
    ) -> float:
        """
        Calculate priority score for opportunities
        
        Args:
            potential: Automation potential (high/medium/low)
            complexity: Implementation complexity (low/medium/high)
            daily_savings: Time saved daily in minutes
            
        Returns:
            Priority score (0-100)
        """
        # Map strings to scores
        potential_scores = {"high": 3, "medium": 2, "low": 1}
        complexity_scores = {"low": 3, "medium": 2, "high": 1}
        
        potential_score = potential_scores.get(potential.lower(), 2)
        complexity_score = complexity_scores.get(complexity.lower(), 2)
        
        # Calculate priority (higher is better)
        # Formula: potential * complexity * sqrt(daily_savings)
        import math
        priority = potential_score * complexity_score * math.sqrt(max(1, daily_savings))
        
        # Normalize to 0-100
        return min(100, priority * 10)
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Create error result structure
        
        Args:
            error_message: Error description
            
        Returns:
            Error result dict
        """
        return {
            "success": False,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "workflows": [],
            "automation_opportunities": [],
            "time_analysis": {},
            "insights": [],
            "summary": {
                "total_workflows_detected": 0,
                "total_opportunities": 0,
                "time_savings_daily_minutes": 0,
                "cost_savings_annual_usd": 0
            },
            "confidence_score": 0
        }
    
    def _enhance_time_breakdown_with_applications(
        self, 
        time_breakdown: Dict[str, Any], 
        applications_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance time breakdown with application-specific data
        
        Args:
            time_breakdown: Basic time breakdown
            applications_data: Application usage data from GPT-4V
            
        Returns:
            Enhanced time breakdown with application details
        """
        total_seconds = time_breakdown.get("total_seconds", 0)
        
        # Add application details to the breakdown
        for app_name, app_info in applications_data.items():
            if isinstance(app_info, dict):
                app_seconds = app_info.get("timeSeconds", 0)
                app_percentage = app_info.get("timePercentage", 0)
                
                # Use calculated timeSeconds if available
                if "timeSeconds" in app_info:
                    app_seconds = app_info["timeSeconds"]
                elif app_seconds == 0 and app_percentage > 0 and total_seconds > 0:
                    app_seconds = int((app_percentage / 100) * total_seconds)
                
                # Categorize applications
                app_lower = app_name.lower()
                if "gmail" in app_lower or "email" in app_lower:
                    time_breakdown["email_seconds"] += app_seconds
                elif "excel" in app_lower or "spreadsheet" in app_lower:
                    time_breakdown["excel_seconds"] += app_seconds
                elif "wms" in app_lower or "warehouse" in app_lower:
                    time_breakdown["wms_seconds"] += app_seconds
        
        # Calculate other_seconds (remaining time)
        accounted = (time_breakdown["email_seconds"] + 
                    time_breakdown["excel_seconds"] + 
                    time_breakdown["wms_seconds"])
        time_breakdown["other_seconds"] = max(0, total_seconds - accounted)
        
        # Calculate percentages if we have total time
        if total_seconds > 0:
            time_breakdown["email_percentage"] = round(100 * time_breakdown["email_seconds"] / total_seconds, 1)
            time_breakdown["excel_percentage"] = round(100 * time_breakdown["excel_seconds"] / total_seconds, 1) 
            time_breakdown["wms_percentage"] = round(100 * time_breakdown["wms_seconds"] / total_seconds, 1)
            time_breakdown["other_percentage"] = round(100 * time_breakdown["other_seconds"] / total_seconds, 1)
        
        return time_breakdown

    def validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate parsed result structure
        
        Args:
            result: Parsed result to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ["success", "workflows", "automation_opportunities", "summary"]
        
        for key in required_keys:
            if key not in result:
                logger.warning(f"Missing required key in result: {key}")
                return False
        
        if not isinstance(result["workflows"], list):
            logger.warning("Workflows is not a list")
            return False
        
        if not isinstance(result["automation_opportunities"], list):
            logger.warning("Opportunities is not a list")
            return False
        
        return True


# Singleton instance
_result_parser: Optional[ResultParser] = None

def get_result_parser() -> ResultParser:
    """Get singleton result parser instance"""
    global _result_parser
    if _result_parser is None:
        _result_parser = ResultParser()
    return _result_parser