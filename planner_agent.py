"""
Planner Agent - Creates a day-by-day study schedule dynamically using Gemini AI.
"""

import json
import re
import math


class PlannerAgent:
    """Creates detailed study schedules using Gemini."""

    def __init__(self, model):
        self.model = model

    def create_schedule(self, parsed_goal: dict) -> list:
        """
        Use Gemini to create a detailed day-by-day schedule.
        Falls back to a smart algorithmic schedule if Gemini fails.
        """
        subject = parsed_goal.get("subject", "the subject")
        total_days = parsed_goal.get("total_days", 30)
        hours_per_day = parsed_goal.get("hours_per_day", 1.5)
        topics = parsed_goal.get("topics", [])
        difficulty = parsed_goal.get("difficulty_level", "beginner")

        print(f"📅 Creating {total_days}-day schedule for: {subject}")

        # For schedules up to 30 days, ask Gemini for a full schedule
        # For longer schedules, use smart topic distribution
        if total_days <= 45:
            schedule = self._gemini_full_schedule(
                subject, total_days, hours_per_day, topics, difficulty
            )
        else:
            schedule = self._smart_topic_distribution(
                subject, total_days, hours_per_day, topics, difficulty
            )

        if schedule and len(schedule) > 0:
            print(f"✅ Schedule created: {len(schedule)} days")
            return schedule

        # Final fallback
        print("⚠️  Using algorithmic schedule fallback")
        return self._algorithmic_schedule(total_days, hours_per_day, topics, subject)

    def _gemini_full_schedule(self, subject, total_days, hours_per_day, topics, difficulty):
        """Ask Gemini to generate the full day-by-day schedule as JSON."""

        topics_str = "\n".join(f"- {t}" for t in topics)

        prompt = f"""
You are an expert study planner. Create a detailed {total_days}-day study schedule for:

Subject: {subject}
Daily Hours: {hours_per_day}
Difficulty: {difficulty}
Topics to cover:
{topics_str}

Return ONLY a valid JSON array. Each element must have:
- "day": integer (1 to {total_days})
- "topic": specific topic name for that day (use the topics above, break them into sub-topics as needed)
- "subtopic": a more specific description of what to study that day
- "duration_hours": float (should be {hours_per_day} for most days; use 0.5-1.0 for review days)
- "activity": one of "learn", "practice", "review", "project", "quiz"
- "status": "pending"

Guidelines:
- Distribute topics logically from easy to hard
- Include review days every 7 days
- End with a project or assessment
- Every topic name must be SPECIFIC to {subject}, not generic

Return ONLY the JSON array, no explanation.
"""

        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            raw = raw.strip()

            schedule = json.loads(raw)

            if not isinstance(schedule, list):
                raise ValueError("Response is not a list")

            # Validate and clean each day
            cleaned = []
            for item in schedule:
                if not isinstance(item, dict):
                    continue
                cleaned.append({
                    "day": int(item.get("day", len(cleaned) + 1)),
                    "topic": str(item.get("topic", f"Study {subject}")),
                    "subtopic": str(item.get("subtopic", "")),
                    "duration_hours": float(item.get("duration_hours", hours_per_day)),
                    "activity": str(item.get("activity", "learn")),
                    "status": "pending"
                })

            if len(cleaned) < total_days * 0.8:  # Less than 80% of expected days
                raise ValueError(f"Too few days returned: {len(cleaned)}")

            return cleaned

        except Exception as e:
            print(f"⚠️  Gemini full schedule failed: {e}")
            return None

    def _smart_topic_distribution(self, subject, total_days, hours_per_day, topics, difficulty):
        """
        For longer plans: ask Gemini for sub-topics per main topic,
        then distribute them across days algorithmically.
        """
        topics_str = ", ".join(topics)

        prompt = f"""
For a {total_days}-day study plan on "{subject}", I have these main topics:
{topics_str}

For each topic, give me 2-4 specific sub-topics or learning activities.
Return ONLY a JSON object where keys are topic names and values are arrays of sub-topic strings.
Be specific to {subject}.

Example format:
{{
  "Python Basics": ["Installing Python and IDEs", "Variables and data types", "Basic operators"],
  "Control Flow": ["if/elif/else statements", "for and while loops", "break and continue"]
}}
"""

        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            subtopics_map = json.loads(raw)

            # Flatten into a list of (topic, subtopic) pairs
            all_subtopics = []
            for topic, subs in subtopics_map.items():
                for sub in subs:
                    all_subtopics.append((topic, sub))

            # Distribute across days
            return self._distribute_subtopics(
                all_subtopics, total_days, hours_per_day, subject
            )

        except Exception as e:
            print(f"⚠️  Smart distribution failed: {e}")
            return self._algorithmic_schedule(total_days, hours_per_day, topics, subject)

    def _distribute_subtopics(self, subtopics, total_days, hours_per_day, subject):
        """Distribute a list of (topic, subtopic) tuples across days."""
        schedule = []
        n = len(subtopics)

        for day_num in range(1, total_days + 1):
            # Every 7th day is a review day
            if day_num % 7 == 0:
                topic = f"Review & Practice"
                subtopic = f"Review last 6 days of {subject} study"
                activity = "review"
                duration = max(0.5, hours_per_day * 0.75)
            else:
                # Pick subtopic proportionally
                idx = min(int((day_num - 1) / total_days * n), n - 1)
                topic, subtopic = subtopics[idx]
                activity = "learn" if day_num % 5 != 0 else "practice"
                duration = hours_per_day

            schedule.append({
                "day": day_num,
                "topic": topic,
                "subtopic": subtopic,
                "duration_hours": duration,
                "activity": activity,
                "status": "pending"
            })

        return schedule

    def _algorithmic_schedule(self, total_days, hours_per_day, topics, subject):
        """
        Pure algorithmic fallback — distributes topics evenly across days.
        No hardcoded names; uses the actual topics from GoalAgent.
        """
        if not topics:
            topics = [f"{subject} Fundamentals", f"{subject} Practice", f"{subject} Advanced Topics"]

        schedule = []
        days_per_topic = math.ceil(total_days / len(topics))

        day_num = 1
        for i, topic in enumerate(topics):
            for d in range(days_per_topic):
                if day_num > total_days:
                    break

                is_review = (day_num % 7 == 0)
                is_practice = (d == days_per_topic - 1)  # Last day of each topic = practice

                if is_review:
                    activity = "review"
                    actual_topic = f"Review: {topic}"
                    duration = max(0.5, hours_per_day * 0.75)
                elif is_practice:
                    activity = "practice"
                    actual_topic = f"Practice: {topic}"
                    duration = hours_per_day
                else:
                    activity = "learn"
                    actual_topic = topic
                    duration = hours_per_day

                schedule.append({
                    "day": day_num,
                    "topic": actual_topic,
                    "subtopic": f"Day {d + 1} of {topic}",
                    "duration_hours": duration,
                    "activity": activity,
                    "status": "pending"
                })
                day_num += 1

        return schedule