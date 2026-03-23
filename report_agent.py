"""
Report Agent: Generates comprehensive progress reports.
Creates human-readable summaries of study progress.
"""

import json
from typing import Dict, Any, List
import google.generativeai as genai
from utils.prompts import REPORT_PROMPT


class ReportAgent:
    """Agent responsible for generating progress reports."""
    
    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize the Report Agent.
        
        Args:
            model: Configured Gemini model instance
        """
        self.model = model
    
    def generate_report(self, schedule: List[Dict[str, Any]], use_ai: bool = True) -> str:
        """
        Generate a comprehensive progress report.
        
        Args:
            schedule: Current schedule
            use_ai: Whether to use AI for report generation
            
        Returns:
            Formatted progress report string
        """
        print(f"\n📊 Report Agent: Generating progress report...")
        
        if use_ai:
            try:
                return self._generate_ai_report(schedule)
            except Exception as e:
                print(f"⚠️ AI report generation failed: {e}")
                print("🔄 Falling back to template report...")
        
        return self._generate_template_report(schedule)
    
    def _generate_ai_report(self, schedule: List[Dict[str, Any]]) -> str:
        """
        Generate report using AI.
        
        Args:
            schedule: Current schedule
            
        Returns:
            AI-generated report
        """
        # Generate prompt
        prompt = REPORT_PROMPT.format(
            current_plan=json.dumps(schedule, indent=2)
        )
        
        # Call Gemini API
        response = self.model.generate_content(prompt)
        report = response.text.strip()
        
        print("✅ AI report generated")
        return report
    
    def _generate_template_report(self, schedule: List[Dict[str, Any]]) -> str:
        """
        Generate report using template.
        
        Args:
            schedule: Current schedule
            
        Returns:
            Template-based report
        """
        # Calculate statistics
        stats = self._calculate_statistics(schedule)
        
        # Build report
        report = []
        report.append("=" * 60)
        report.append("📊 STUDY PROGRESS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overview section
        report.append("📈 OVERVIEW")
        report.append("-" * 60)
        report.append(f"Total Days:        {stats['total_days']}")
        report.append(f"Completed Days:    {stats['completed_days']} ✅")
        report.append(f"Pending Days:      {stats['pending_days']} ⏳")
        report.append(f"Progress:          {stats['progress_percentage']:.1f}%")
        report.append("")
        report.append(f"Total Hours:       {stats['total_hours']:.1f} hours")
        report.append(f"Completed Hours:   {stats['completed_hours']:.1f} hours")
        report.append(f"Remaining Hours:   {stats['remaining_hours']:.1f} hours")
        report.append("")
        
        # Progress bar
        progress_bar = self._create_progress_bar(stats['progress_percentage'])
        report.append(f"Progress Bar: {progress_bar}")
        report.append("")
        
        # Completed tasks section
        if stats['completed_tasks']:
            report.append("✅ COMPLETED TASKS")
            report.append("-" * 60)
            for task in stats['completed_tasks']:
                report.append(f"Day {task['day']:2d}: {task['topic']}")
                report.append(f"         ({task['duration_hours']:.1f}h) - {task['notes']}")
            report.append("")
        
        # Pending tasks section
        if stats['pending_tasks']:
            report.append("⏳ PENDING TASKS")
            report.append("-" * 60)
            # Show next 5 pending tasks
            for task in stats['pending_tasks'][:5]:
                report.append(f"Day {task['day']:2d}: {task['topic']}")
                report.append(f"         ({task['duration_hours']:.1f}h) - {task['notes']}")
            
            if len(stats['pending_tasks']) > 5:
                report.append(f"... and {len(stats['pending_tasks']) - 5} more pending tasks")
            report.append("")
        
        # Next task highlight
        if stats['next_task']:
            report.append("🎯 NEXT UP")
            report.append("-" * 60)
            next_task = stats['next_task']
            report.append(f"Day {next_task['day']}: {next_task['topic']}")
            report.append(f"Duration: {next_task['duration_hours']:.1f} hours")
            report.append(f"Focus: {next_task['notes']}")
            report.append("")
        
        # Insights section
        report.append("💡 INSIGHTS & RECOMMENDATIONS")
        report.append("-" * 60)
        
        # Progress assessment
        if stats['progress_percentage'] >= 75:
            report.append("🌟 Excellent progress! You're almost there!")
        elif stats['progress_percentage'] >= 50:
            report.append("👍 Great work! You're over halfway through!")
        elif stats['progress_percentage'] >= 25:
            report.append("💪 Keep going! You're making steady progress!")
        else:
            report.append("🚀 Just getting started! Stay consistent!")
        
        report.append("")
        
        # Pace assessment
        if stats['completed_days'] > 0:
            avg_hours_per_completed_day = stats['completed_hours'] / stats['completed_days']
            report.append(f"Average study time: {avg_hours_per_completed_day:.1f} hours/day")
        
        # Motivational message
        report.append("")
        report.append("Remember: Consistency is key! Keep up the great work! 🎓")
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _calculate_statistics(self, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics from schedule.
        
        Args:
            schedule: Current schedule
            
        Returns:
            Dictionary with statistics
        """
        total_days = len(schedule)
        completed_tasks = [day for day in schedule if day.get("status") == "done"]
        pending_tasks = [day for day in schedule if day.get("status") == "pending"]
        
        completed_days = len(completed_tasks)
        pending_days = len(pending_tasks)
        
        total_hours = sum(day.get("duration_hours", 0) for day in schedule)
        completed_hours = sum(day.get("duration_hours", 0) for day in completed_tasks)
        remaining_hours = total_hours - completed_hours
        
        progress_percentage = (completed_days / total_days * 100) if total_days > 0 else 0
        
        # Get next pending task
        next_task = None
        if pending_tasks:
            next_task = sorted(pending_tasks, key=lambda x: x.get("day", 999))[0]
        
        return {
            "total_days": total_days,
            "completed_days": completed_days,
            "pending_days": pending_days,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "total_hours": total_hours,
            "completed_hours": completed_hours,
            "remaining_hours": remaining_hours,
            "progress_percentage": progress_percentage,
            "next_task": next_task
        }
    
    def _create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """
        Create a visual progress bar.
        
        Args:
            percentage: Progress percentage (0-100)
            width: Width of progress bar in characters
            
        Returns:
            Progress bar string
        """
        filled = int(width * percentage / 100)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percentage:.1f}%"
    
    def get_summary_stats(self, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for display.
        
        Args:
            schedule: Current schedule
            
        Returns:
            Dictionary with summary statistics
        """
        return self._calculate_statistics(schedule)