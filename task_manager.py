"""
Task Manager Agent: Manages and updates study tasks.
Handles marking tasks as complete and adjusting schedules.
"""

import json
import re
from typing import Dict, Any, List
import google.generativeai as genai
from utils.prompts import TASK_MANAGER_PROMPT


class TaskManagerAgent:
    """Agent responsible for managing study tasks and schedules."""
    
    def __init__(self, model: genai.GenerativeModel):
        """
        Initialize the Task Manager Agent.
        
        Args:
            model: Configured Gemini model instance
        """
        self.model = model
    
    def mark_day_complete(self, schedule: List[Dict[str, Any]], day_number: int) -> List[Dict[str, Any]]:
        """
        Mark a specific day as complete in the schedule.
        
        Args:
            schedule: Current study schedule
            day_number: Day number to mark as complete
            
        Returns:
            Updated schedule with day marked as done
        """
        print(f"\n✅ Task Manager: Marking Day {day_number} as complete...")
        
        updated_schedule = []
        
        for day in schedule:
            if day.get("day") == day_number:
                day["status"] = "done"
                print(f"✅ Day {day_number} ({day.get('topic', 'N/A')}) marked as done")
            updated_schedule.append(day)
        
        return updated_schedule
    
    def mark_multiple_days_complete(
        self,
        schedule: List[Dict[str, Any]],
        day_numbers: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Mark multiple days as complete.
        
        Args:
            schedule: Current study schedule
            day_numbers: List of day numbers to mark as complete
            
        Returns:
            Updated schedule with days marked as done
        """
        print(f"\n✅ Task Manager: Marking {len(day_numbers)} days as complete...")
        
        updated_schedule = []
        
        for day in schedule:
            if day.get("day") in day_numbers:
                day["status"] = "done"
                print(f"✅ Day {day.get('day')} ({day.get('topic', 'N/A')}) marked as done")
            updated_schedule.append(day)
        
        return updated_schedule
    
    def update_schedule_with_ai(
        self,
        schedule: List[Dict[str, Any]],
        completed_day: int
    ) -> List[Dict[str, Any]]:
        """
        Update schedule using AI for intelligent adjustments.
        
        Args:
            schedule: Current study schedule
            completed_day: Day that was just completed
            
        Returns:
            Intelligently updated schedule
        """
        print(f"\n🤖 Task Manager: AI-powered schedule update for Day {completed_day}...")
        
        try:
            # Generate prompt
            prompt = TASK_MANAGER_PROMPT.format(
                current_plan=json.dumps(schedule, indent=2),
                completed_day=completed_day
            )
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            updated_schedule = self._extract_json(response_text)
            
            # Validate the updated schedule
            validated_schedule = self._validate_schedule(updated_schedule, schedule)
            
            print(f"✅ Schedule updated successfully")
            
            return validated_schedule
            
        except Exception as e:
            print(f"⚠️ Error updating schedule with AI: {e}")
            print("🔄 Using simple completion...")
            return self.mark_day_complete(schedule, completed_day)
    
    def _extract_json(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract JSON array from LLM response text.
        
        Args:
            text: Response text that may contain JSON
            
        Returns:
            Parsed JSON array
        """
        # Try to find JSON in code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        # Try to find JSON array
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
        
        # Parse JSON
        return json.loads(text)
    
    def _validate_schedule(
        self,
        updated_schedule: List[Dict[str, Any]],
        original_schedule: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate updated schedule against original.
        
        Args:
            updated_schedule: Updated schedule from AI
            original_schedule: Original schedule for reference
            
        Returns:
            Validated schedule
        """
        if not isinstance(updated_schedule, list) or len(updated_schedule) == 0:
            return original_schedule
        
        validated = []
        
        for day_data in updated_schedule:
            # Ensure required fields
            day = {
                "day": day_data.get("day", 0),
                "topic": day_data.get("topic", "Study"),
                "duration_hours": day_data.get("duration_hours", 2.0),
                "status": day_data.get("status", "pending"),
                "notes": day_data.get("notes", "")
            }
            
            # Validate duration
            if not isinstance(day["duration_hours"], (int, float)) or day["duration_hours"] <= 0:
                day["duration_hours"] = 2.0
            day["duration_hours"] = float(min(max(day["duration_hours"], 0.5), 12.0))
            
            # Validate status
            if day["status"] not in ["pending", "done"]:
                day["status"] = "pending"
            
            validated.append(day)
        
        return validated
    
    def get_next_task(self, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get the next pending task.
        
        Args:
            schedule: Current study schedule
            
        Returns:
            Next pending task or empty dict if none
        """
        pending_tasks = [day for day in schedule if day.get("status") == "pending"]
        
        if pending_tasks:
            return min(pending_tasks, key=lambda x: x.get("day", 999))
        
        return {}
    
    def get_completed_count(self, schedule: List[Dict[str, Any]]) -> int:
        """
        Get count of completed tasks.
        
        Args:
            schedule: Current study schedule
            
        Returns:
            Number of completed tasks
        """
        return sum(1 for day in schedule if day.get("status") == "done")
    
    def get_pending_count(self, schedule: List[Dict[str, Any]]) -> int:
        """
        Get count of pending tasks.
        
        Args:
            schedule: Current study schedule
            
        Returns:
            Number of pending tasks
        """
        return sum(1 for day in schedule if day.get("status") == "pending")
    
    def get_progress_percentage(self, schedule: List[Dict[str, Any]]) -> float:
        """
        Get overall progress percentage.
        
        Args:
            schedule: Current study schedule
            
        Returns:
            Progress percentage (0-100)
        """
        if not schedule:
            return 0.0
        
        completed = self.get_completed_count(schedule)
        total = len(schedule)
        
        return (completed / total * 100) if total > 0 else 0.0
