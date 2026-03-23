"""
Export Utilities: Handle PDF and CSV export features
Provides functions to export study plans and reports
"""

import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
import base64
from io import BytesIO


class ExportManager:
    """Manages all export functionality."""
    
    @staticmethod
    def schedule_to_csv(schedule: List[Dict[str, Any]], plan_goal: str = "") -> str:
        """
        Convert schedule to CSV format.
        
        Args:
            schedule: List of daily tasks
            plan_goal: Optional goal description
            
        Returns:
            CSV string
        """
        df = pd.DataFrame(schedule)
        
        # Reorder columns
        column_order = ['day', 'topic', 'duration_hours', 'status', 'notes']
        df = df[column_order]
        
        # Rename columns for better readability
        df.columns = ['Day', 'Topic', 'Hours', 'Status', 'Notes']
        
        # Add header row with goal
        header = f"# Study Plan Export - {datetime.now().strftime('%Y-%m-%d')}\n"
        if plan_goal:
            header += f"# Goal: {plan_goal}\n"
        header += "\n"
        
        return header + df.to_csv(index=False)
    
    @staticmethod
    def stats_to_csv(stats: Dict[str, Any]) -> str:
        """
        Convert statistics to CSV format.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            CSV string
        """
        data = {
            'Metric': [
                'Total Days',
                'Completed Days',
                'Pending Days',
                'Total Hours',
                'Completed Hours',
                'Progress Percentage'
            ],
            'Value': [
                stats.get('total_days', 0),
                stats.get('completed_days', 0),
                stats.get('pending_days', 0),
                f"{stats.get('total_hours', 0):.1f}",
                f"{stats.get('completed_hours', 0):.1f}",
                f"{stats.get('progress_percentage', 0):.1f}%"
            ]
        }
        
        df = pd.DataFrame(data)
        
        header = f"# Study Plan Statistics - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        return header + df.to_csv(index=False)
    
    @staticmethod
    def create_download_link(data: str, filename: str, link_text: str = "Download") -> str:
        """
        Create an HTML download link for data.
        
        Args:
            data: Data to download
            filename: Name of the download file
            link_text: Text for the link
            
        Returns:
            HTML string with download link
        """
        b64 = base64.b64encode(data.encode()).decode()
        return f'''
        <a href="data:text/csv;base64,{b64}" 
           download="{filename}"
           style="display: inline-block; padding: 0.75rem 1.5rem; 
                  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                  color: white; text-decoration: none; border-radius: 10px;
                  font-weight: 600; box-shadow: 0 4px 8px rgba(67, 233, 123, 0.3);
                  transition: all 0.3s ease;">
            📥 {link_text}
        </a>
        '''
    
    @staticmethod
    def report_to_text(report: str, plan_goal: str = "") -> str:
        """
        Format report for text export.
        
        Args:
            report: Report string
            plan_goal: Optional goal description
            
        Returns:
            Formatted text string
        """
        header = f"""
{'='*70}
AGENTIC AI STUDY PLANNER - PROGRESS REPORT
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Goal: {plan_goal}
{'='*70}

"""
        return header + report
    
    @staticmethod
    def export_complete_plan(
        plan: Dict[str, Any], 
        stats: Dict[str, Any]
    ) -> str:
        """
        Export complete plan with all details.
        
        Args:
            plan: Complete plan dictionary
            stats: Statistics dictionary
            
        Returns:
            Formatted CSV string with all information
        """
        # Plan header
        header = f"""# Complete Study Plan Export
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Goal: {plan.get('goal', 'N/A')}
# Created: {plan.get('created_at', 'N/A')[:10]}

# === PLAN STATISTICS ===
Total Days,{stats.get('total_days', 0)}
Completed Days,{stats.get('completed_days', 0)}
Pending Days,{stats.get('pending_days', 0)}
Total Hours,{stats.get('total_hours', 0):.1f}
Completed Hours,{stats.get('completed_hours', 0):.1f}
Progress,{stats.get('progress_percentage', 0):.1f}%

# === DAILY SCHEDULE ===
"""
        
        # Schedule data
        schedule = plan.get('schedule', [])
        df = pd.DataFrame(schedule)
        df.columns = ['Day', 'Topic', 'Hours', 'Status', 'Notes']
        
        return header + df.to_csv(index=False)


# Convenience functions
def export_schedule_csv(schedule: List[Dict[str, Any]], goal: str = "") -> str:
    """Export schedule to CSV."""
    return ExportManager.schedule_to_csv(schedule, goal)


def export_stats_csv(stats: Dict[str, Any]) -> str:
    """Export statistics to CSV."""
    return ExportManager.stats_to_csv(stats)


def create_download_button(data: str, filename: str, button_text: str = "Download") -> str:
    """Create download button HTML."""
    return ExportManager.create_download_link(data, filename, button_text)


def export_report_txt(report: str, goal: str = "") -> str:
    """Export report to text format."""
    return ExportManager.report_to_text(report, goal)


def export_full_plan(plan: Dict[str, Any], stats: Dict[str, Any]) -> str:
    """Export complete plan with all details."""
    return ExportManager.export_complete_plan(plan, stats)