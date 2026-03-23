"""
Goal Agent - Parses user study goals using Gemini AI dynamically.
"""

import json
import re


class GoalAgent:
    """Parses and structures user study goals using Gemini."""

    def __init__(self, model):
        self.model = model

    def parse_goal(self, user_goal: str) -> dict:
        """
        Use Gemini to extract structured info from any study goal.
        Returns a dict with goal_summary, total_days, hours_per_day, topics, difficulty.
        """

        prompt = f"""
You are an expert study planner. A user has given you the following study goal:

"{user_goal}"

Your job is to extract structured information from this goal and return ONLY a valid JSON object — no explanation, no markdown, no code fences.

Rules:
- "goal_summary": A concise 1-sentence summary of what the user wants to achieve.
- "subject": The exact subject/technology/skill they want to learn (e.g., "Python", "AWS Solutions Architect", "Calculus", "Guitar").
- "total_days": How many days the plan should span. Extract from the goal if mentioned, otherwise estimate reasonably (e.g., 30 for beginner topics, 60-90 for complex ones).
- "hours_per_day": Hours per day. Extract if mentioned, otherwise default to 1.5.
- "difficulty_level": "beginner", "intermediate", or "advanced" — infer from context.
- "topics": A list of 8-15 SPECIFIC, CONCRETE topic names for THIS subject. 
  - DO NOT use generic names like "Core Concepts" or "Intermediate Concepts".
  - Use real topic names like "Python List Comprehensions", "AWS EC2 and IAM", "Calculus Derivatives", etc.
  - Topics should flow logically from beginner to advanced.
- "prerequisites": List of things the user should already know (can be empty list).
- "learning_outcomes": List of 3-5 things the user will be able to do after completing the plan.

Return ONLY the JSON. Example format:
{{
  "goal_summary": "Learn Python programming from scratch in 30 days",
  "subject": "Python",
  "total_days": 30,
  "hours_per_day": 1.5,
  "difficulty_level": "beginner",
  "topics": [
    "Python Installation and Setup",
    "Variables, Data Types, and Operators",
    "Conditional Statements and Loops",
    "Functions and Scope",
    "Lists, Tuples, and Dictionaries",
    "File I/O and Exception Handling",
    "Object-Oriented Programming",
    "Modules and Packages",
    "List Comprehensions and Generators",
    "Working with APIs and JSON"
  ],
  "prerequisites": [],
  "learning_outcomes": [
    "Write Python scripts for automation",
    "Build simple applications",
    "Understand OOP principles"
  ]
}}

Now parse this goal: "{user_goal}"
"""

        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()

            # Strip markdown code fences if present
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            raw = raw.strip()

            parsed = json.loads(raw)

            # Validate required fields
            required = ["goal_summary", "subject", "total_days", "hours_per_day", "topics"]
            for field in required:
                if field not in parsed:
                    raise ValueError(f"Missing field: {field}")

            if not isinstance(parsed["topics"], list) or len(parsed["topics"]) < 3:
                raise ValueError("Topics must be a list with at least 3 items")

            print(f"✅ Goal parsed: {parsed['goal_summary']}")
            print(f"   Subject: {parsed['subject']} | Days: {parsed['total_days']} | Topics: {len(parsed['topics'])}")
            return parsed

        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Gemini response parse error: {e}")
            print(f"   Raw response: {response.text[:300] if 'response' in locals() else 'No response'}")
            # Fallback: return a minimal but still dynamic structure
            return self._fallback_parse(user_goal)

    def _fallback_parse(self, user_goal: str) -> dict:
        """Fallback if JSON parsing fails — try simpler prompt."""
        print("🔄 Trying fallback parse...")
        simple_prompt = f"""
Given this study goal: "{user_goal}"

List exactly 10 specific topics to study for this subject, one per line, numbered 1-10.
Be specific to the subject — no generic names like "Core Concepts".
After the list, on a new line write: DAYS: <number> HOURS: <number>
"""
        try:
            response = self.model.generate_content(simple_prompt)
            lines = response.text.strip().split("\n")

            topics = []
            days = 30
            hours = 1.5

            for line in lines:
                line = line.strip()
                if line and line[0].isdigit() and "." in line:
                    topic = re.sub(r"^\d+\.\s*", "", line).strip()
                    if topic:
                        topics.append(topic)
                if line.startswith("DAYS:"):
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "DAYS:" and i + 1 < len(parts):
                            try:
                                days = int(parts[i + 1])
                            except ValueError:
                                pass
                        if p == "HOURS:" and i + 1 < len(parts):
                            try:
                                hours = float(parts[i + 1])
                            except ValueError:
                                pass

            if not topics:
                topics = [f"Getting Started with {user_goal}",
                          f"Core Skills in {user_goal}",
                          f"Advanced {user_goal} Techniques"]

            return {
                "goal_summary": user_goal,
                "subject": user_goal,
                "total_days": days,
                "hours_per_day": hours,
                "difficulty_level": "beginner",
                "topics": topics,
                "prerequisites": [],
                "learning_outcomes": [f"Gain proficiency in {user_goal}"]
            }
        except Exception as e:
            print(f"❌ Fallback also failed: {e}")
            return {
                "goal_summary": user_goal,
                "subject": user_goal,
                "total_days": 30,
                "hours_per_day": 1.5,
                "difficulty_level": "beginner",
                "topics": [user_goal],
                "prerequisites": [],
                "learning_outcomes": []
            }