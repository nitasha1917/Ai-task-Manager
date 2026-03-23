"""
Memory Manager: Handles persistent storage of study plans in JSON format.
Provides robust load/save operations with error handling.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class MemoryManager:
    """Manages persistent storage of study plans."""
    
    def __init__(self, memory_file: str = "memory/memory.json"):
        """
        Initialize the memory manager.
        
        Args:
            memory_file: Path to the JSON memory file
        """
        self.memory_file = memory_file
        self._ensure_memory_file()
    
    def _ensure_memory_file(self) -> None:
        """Ensure the memory file and directory exist."""
        memory_path = Path(self.memory_file)
        
        # Create directory if it doesn't exist
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file if it doesn't exist
        if not memory_path.exists():
            self._save_data({"plans": [], "metadata": {"created_at": datetime.now().isoformat()}})
    
    def _load_data(self) -> Dict[str, Any]:
        """
        Load data from memory file.
        
        Returns:
            Dictionary containing all stored data
        """
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Warning: Could not load memory file: {e}")
            return {"plans": [], "metadata": {"created_at": datetime.now().isoformat()}}
    
    def _save_data(self, data: Dict[str, Any]) -> bool:
        """
        Save data to memory file.
        
        Args:
            data: Dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving memory: {e}")
            return False
    
    def save_plan(self, plan_data: Dict[str, Any]) -> bool:
        """
        Save a new study plan or update existing one.
        
        Args:
            plan_data: Dictionary containing plan information
                Required keys: goal, parsed_goal, schedule
                
        Returns:
            True if successful, False otherwise
        """
        data = self._load_data()
        
        # Add metadata
        plan_data["created_at"] = datetime.now().isoformat()
        plan_data["updated_at"] = datetime.now().isoformat()
        plan_data["id"] = len(data["plans"]) + 1
        
        # Check if plan with same goal exists
        existing_plan_idx = None
        for idx, plan in enumerate(data["plans"]):
            if plan.get("goal", "").strip().lower() == plan_data.get("goal", "").strip().lower():
                existing_plan_idx = idx
                break
        
        if existing_plan_idx is not None:
            # Update existing plan
            plan_data["id"] = data["plans"][existing_plan_idx]["id"]
            plan_data["created_at"] = data["plans"][existing_plan_idx]["created_at"]
            data["plans"][existing_plan_idx] = plan_data
            print(f"✅ Updated existing plan #{plan_data['id']}")
        else:
            # Add new plan
            data["plans"].append(plan_data)
            print(f"✅ Saved new plan #{plan_data['id']}")
        
        return self._save_data(data)
    
    def get_all_plans(self) -> List[Dict[str, Any]]:
        """
        Get all stored plans.
        
        Returns:
            List of plan dictionaries
        """
        data = self._load_data()
        return data.get("plans", [])
    
    def get_plan_by_id(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific plan by ID.
        
        Args:
            plan_id: The plan ID to retrieve
            
        Returns:
            Plan dictionary or None if not found
        """
        plans = self.get_all_plans()
        for plan in plans:
            if plan.get("id") == plan_id:
                return plan
        return None
    
    def get_latest_plan(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently created/updated plan.
        
        Returns:
            Latest plan dictionary or None if no plans exist
        """
        plans = self.get_all_plans()
        if not plans:
            return None
        
        # Sort by updated_at timestamp
        sorted_plans = sorted(
            plans,
            key=lambda p: p.get("updated_at", ""),
            reverse=True
        )
        return sorted_plans[0]
    
    def update_plan_schedule(self, plan_id: int, updated_schedule: List[Dict[str, Any]]) -> bool:
        """
        Update the schedule of a specific plan.
        
        Args:
            plan_id: The plan ID to update
            updated_schedule: New schedule array
            
        Returns:
            True if successful, False otherwise
        """
        data = self._load_data()
        
        for plan in data["plans"]:
            if plan.get("id") == plan_id:
                plan["schedule"] = updated_schedule
                plan["updated_at"] = datetime.now().isoformat()
                return self._save_data(data)
        
        print(f"❌ Plan #{plan_id} not found")
        return False
    
    def delete_plan(self, plan_id: int) -> bool:
        """
        Delete a plan by ID.
        
        Args:
            plan_id: The plan ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        data = self._load_data()
        
        initial_count = len(data["plans"])
        data["plans"] = [p for p in data["plans"] if p.get("id") != plan_id]
        
        if len(data["plans"]) < initial_count:
            print(f"✅ Deleted plan #{plan_id}")
            return self._save_data(data)
        
        print(f"❌ Plan #{plan_id} not found")
        return False
    
    def get_plan_statistics(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Calculate statistics for a plan.
        
        Args:
            plan_id: The plan ID
            
        Returns:
            Dictionary with statistics or None
        """
        plan = self.get_plan_by_id(plan_id)
        if not plan:
            return None
        
        schedule = plan.get("schedule", [])
        total_days = len(schedule)
        completed_days = sum(1 for day in schedule if day.get("status") == "done")
        pending_days = sum(1 for day in schedule if day.get("status") == "pending")
        
        total_hours = sum(day.get("duration_hours", 0) for day in schedule)
        completed_hours = sum(
            day.get("duration_hours", 0) 
            for day in schedule 
            if day.get("status") == "done"
        )
        
        progress_percentage = (completed_days / total_days * 100) if total_days > 0 else 0
        
        return {
            "total_days": total_days,
            "completed_days": completed_days,
            "pending_days": pending_days,
            "total_hours": round(total_hours, 2),
            "completed_hours": round(completed_hours, 2),
            "progress_percentage": round(progress_percentage, 2)
        }


# Convenience function for global instance
_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    """Get or create the global MemoryManager instance."""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance