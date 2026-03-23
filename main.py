#!/usr/bin/env python3
"""
Agentic AI Study Planner & Task Manager - CLI Interface
Main entry point for command-line interaction.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.goal_agent import GoalAgent
from agents.planner_agent import PlannerAgent
from agents.task_manager import TaskManagerAgent
from agents.report_agent import ReportAgent
from memory.memory_manager import MemoryManager


class StudyPlannerCLI:
    """Command-line interface for the Study Planner."""
    
    def __init__(self):
        """Initialize the CLI and all agents."""
        # Load environment variables
        load_dotenv()
        
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY not found in .env file")
            print("Please create a .env file with your Gemini API key:")
            print("GEMINI_API_KEY=your_api_key_here")
            sys.exit(1)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        try:
            self.model = genai.GenerativeModel(model_name)
            print(f"✅ Initialized Gemini model: {model_name}")
        except Exception as e:
            print(f"❌ Error initializing Gemini model: {e}")
            sys.exit(1)
        
        # Initialize agents
        self.goal_agent = GoalAgent(self.model)
        self.planner_agent = PlannerAgent(self.model)
        self.task_manager = TaskManagerAgent(self.model)
        self.report_agent = ReportAgent(self.model)
        
        # Initialize memory manager
        self.memory = MemoryManager()
        
        print("✅ All agents initialized successfully\n")
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 70)
        print(" " * 15 + "🎓 AGENTIC AI STUDY PLANNER & TASK MANAGER")
        print("=" * 70)
        print("\n📋 MAIN MENU:")
        print("  ┌─ CREATE PLAN")
        print("  │  1️⃣  Create New Study Plan")
        print("  ├─ VIEW & MANAGE")
        print("  │  2️⃣  View Current Plan")
        print("  │  3️⃣  View All Plans")
        print("  ├─ TRACK PROGRESS")
        print("  │  4️⃣  Mark Day as Complete")
        print("  │  5️⃣  Generate Progress Report")
        print("  ├─ MAINTENANCE")
        print("  │  6️⃣  Delete Plan")
        print("  └─ EXIT")
        print("  0️⃣  Exit Application")
        print("\n" + "=" * 70)
    
    def create_new_plan(self):
        """Create a new study plan."""
        print("\n" + "=" * 70)
        print("📝 CREATE NEW STUDY PLAN")
        print("=" * 70)
        print("\n💡 TIPS FOR BETTER PLANS:")
        print("  ✓ Be specific: 'Learn Python basics in 30 days, 1 hour daily'")
        print("  ✓ Include details: current level, time commitment, duration")
        print("  ✓ Mention goals: 'Master data science', 'Pass certification'")
        print("\n📌 EXAMPLES:")
        print("  • 'I want to learn Python in 30 days'")
        print("  • 'Master machine learning basics in 60 days, 2 hours daily'")
        print("  • 'Prepare for AWS certification, 90 days'")
        print("\n" + "-" * 70)
        
        user_goal = input("\n🎯 Enter your study goal: ").strip()
        
        if not user_goal:
            print("❌ Goal cannot be empty")
            return
        
        print("\n🚀 Creating your personalized study plan...\n")
        
        # Step 1: Parse goal
        parsed_goal = self.goal_agent.parse_goal(user_goal)
        
        # Step 2: Create schedule
        schedule = self.planner_agent.create_schedule(parsed_goal)
        
        # Step 3: Save to memory
        plan_data = {
            "goal": user_goal,
            "parsed_goal": parsed_goal,
            "schedule": schedule
        }
        
        if self.memory.save_plan(plan_data):
            print("\n" + "=" * 70)
            print("✅ STUDY PLAN CREATED SUCCESSFULLY!")
            print("=" * 70)
            print(f"📚 Goal: {parsed_goal['goal_summary']}")
            print(f"📅 Duration: {parsed_goal['total_days']} days")
            print(f"⏰ Daily commitment: {parsed_goal['hours_per_day']} hours")
            print(f"🎯 Topics: {', '.join(parsed_goal['topics'][:3])}{'...' if len(parsed_goal['topics']) > 3 else ''}")
            print("\n💡 Next Steps:")
            print("  1. View your schedule to see the day-by-day breakdown")
            print("  2. Start studying according to the plan")
            print("  3. Mark days as complete as you finish them")
            print("  4. Check your progress report regularly")
            print("\n" + "=" * 70)
        else:
            print("\n❌ Failed to save plan to memory")
    
    def view_current_plan(self):
        """View the current study plan."""
        plan = self.memory.get_latest_plan()
        
        if not plan:
            print("\n❌ No study plan found. Create one first!")
            return
        
        schedule = plan.get("schedule", [])
        parsed_goal = plan.get("parsed_goal", {})
        
        print("\n" + "=" * 70)
        print("📚 YOUR CURRENT STUDY PLAN")
        print("=" * 70)
        print(f"📝 Goal: {plan.get('goal', 'N/A')}")
        print(f"📅 Duration: {parsed_goal.get('total_days', 0)} days")
        print(f"⏰ Daily Hours: {parsed_goal.get('hours_per_day', 0)}")
        print("=" * 70)
        print()
        
        # Display schedule with better formatting
        print(f"{'Day':<5} {'Topic':<30} {'Hours':<8} {'Status':<10}")
        print("-" * 70)
        
        for day in schedule[:10]:  # Show first 10 days
            status_icon = "✅" if day.get("status") == "done" else "⏳"
            print(
                f"{day.get('day', 0):<5} "
                f"{day.get('topic', 'N/A')[:28]:<30} "
                f"{day.get('duration_hours', 0):<8.1f} "
                f"{status_icon} {day.get('status', 'N/A'):<10}"
            )
        
        if len(schedule) > 10:
            print(f"... and {len(schedule) - 10} more days")
        
        # Show statistics
        stats = self.memory.get_plan_statistics(plan['id'])
        if stats:
            print("\n" + "=" * 70)
            print("📊 PROGRESS STATISTICS")
            print("-" * 70)
            print(f"✅ Completed: {stats['completed_days']}/{stats['total_days']} days ({stats['progress_percentage']:.1f}%)")
            print(f"⏳ Pending: {stats['pending_days']} days")
            print(f"📈 Hours completed: {stats['completed_hours']:.1f}/{stats['total_hours']:.1f}")
            print("=" * 70)
    
    def mark_day_complete(self):
        """Mark a day as complete."""
        plan = self.memory.get_latest_plan()
        
        if not plan:
            print("\n❌ No study plan found. Create one first!")
            return
        
        print("\n" + "=" * 70)
        print("✅ MARK DAY AS COMPLETE")
        print("=" * 70)
        
        # Show pending days
        schedule = plan.get("schedule", [])
        pending = [d for d in schedule if d.get("status") == "pending"]
        
        if not pending:
            print("🎉 All days are already complete!")
            return
        
        print("\n📋 Next Pending Days:")
        for day in pending[:5]:
            print(f"  Day {day.get('day')}: {day.get('topic')} ({day.get('duration_hours')} hours)")
        
        if len(pending) > 5:
            print(f"  ... and {len(pending) - 5} more")
        
        print()
        try:
            day_num = int(input("📌 Enter day number to mark as complete: "))
            
            # Update schedule
            updated_schedule = self.task_manager.mark_day_complete(schedule, day_num)
            
            # Save updated schedule
            if self.memory.update_plan_schedule(plan['id'], updated_schedule):
                print(f"\n✅ Day {day_num} marked as complete! 🎉")
                stats = self.memory.get_plan_statistics(plan['id'])
                print(f"   Progress: {stats['completed_days']}/{stats['total_days']} days ({stats['progress_percentage']:.1f}%)")
            else:
                print("\n❌ Failed to save changes")
                
        except ValueError:
            print("❌ Invalid day number. Please enter a number.")
    
    def generate_report(self):
        """Generate a progress report."""
        plan = self.memory.get_latest_plan()
        
        if not plan:
            print("\n❌ No study plan found. Create one first!")
            return
        
        print("\n" + "=" * 70)
        print("📊 GENERATING YOUR PROGRESS REPORT")
        print("=" * 70)
        
        schedule = plan.get("schedule", [])
        
        print("\n🤖 Generating comprehensive analysis...\n")
        
        report = self.report_agent.generate_report(schedule, use_ai=True)
        print(report)
        print("\n" + "=" * 70)
    
    def view_all_plans(self):
        """View all saved plans."""
        plans = self.memory.get_all_plans()
        
        if not plans:
            print("\n❌ No plans found")
            return
        
        print("\n" + "=" * 70)
        print("📚 ALL YOUR STUDY PLANS")
        print("=" * 70)
        
        for idx, plan in enumerate(plans, 1):
            stats = self.memory.get_plan_statistics(plan['id'])
            print(f"\n📌 Plan #{idx} (ID: {plan['id']})")
            print(f"  📝 Goal: {plan.get('goal', 'N/A')[:60]}")
            print(f"  📅 Created: {plan.get('created_at', 'N/A')[:10]}")
            if stats:
                print(f"  📊 Progress: {stats['completed_days']}/{stats['total_days']} days ({stats['progress_percentage']:.1f}%)")
                print(f"  ⏰ Hours: {stats['completed_hours']:.1f}/{stats['total_hours']:.1f}")
        
        print("\n" + "=" * 70)
    
    def delete_plan(self):
        """Delete a study plan."""
        plans = self.memory.get_all_plans()
        
        if not plans:
            print("\n❌ No plans found")
            return
        
        print("\n" + "=" * 70)
        print("🗑️  DELETE STUDY PLAN")
        print("=" * 70)
        print("\n⚠️  WARNING: This action cannot be undone!")
        print("\nAvailable Plans:")
        
        for idx, plan in enumerate(plans, 1):
            print(f"  #{idx} (ID: {plan['id']}): {plan.get('goal', 'N/A')[:50]}")
        
        print()
        try:
            plan_id = int(input("📌 Enter plan ID to delete (0 to cancel): "))
            
            if plan_id == 0:
                print("❌ Deletion cancelled.")
                return
            
            confirm = input(f"🔴 Are you absolutely sure you want to delete plan #{plan_id}? (type 'yes' to confirm): ")
            if confirm.lower() == 'yes':
                if self.memory.delete_plan(plan_id):
                    print(f"\n✅ Plan #{plan_id} has been successfully deleted.")
                else:
                    print("❌ Failed to delete plan")
            else:
                print("❌ Deletion cancelled.")
        except ValueError:
            print("❌ Invalid plan ID. Please enter a number.")
    
    def run(self):
        """Run the CLI application."""
        print("\n" + "=" * 70)
        print("🎓 Welcome to Agentic AI Study Planner!")
        print("=" * 70)
        print("Your intelligent learning companion powered by Google Gemini AI")
        print("=" * 70)
        
        while True:
            try:
                self.display_menu()
                choice = input("\n👉 Enter your choice (0-6): ").strip()
                
                if choice == "1":
                    self.create_new_plan()
                elif choice == "2":
                    self.view_current_plan()
                elif choice == "3":
                    self.mark_day_complete()
                elif choice == "4":
                    self.generate_report()
                elif choice == "5":
                    self.view_all_plans()
                elif choice == "6":
                    self.delete_plan()
                elif choice == "0":
                    print("\n" + "=" * 70)
                    print("👋 Thank you for using Agentic AI Study Planner!")
                    print("Good luck with your studies! 🎓")
                    print("=" * 70 + "\n")
                    break
                else:
                    print("\n❌ Invalid choice. Please enter a number between 0 and 6.")
                
                input("\n⏸️  Press Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n" + "=" * 70)
                print("👋 Goodbye! Keep learning!")
                print("=" * 70 + "\n")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("\n⏸️  Press Enter to continue...")


def main():
    """Main entry point."""
    cli = StudyPlannerCLI()
    cli.run()


if __name__ == "__main__":
    main()