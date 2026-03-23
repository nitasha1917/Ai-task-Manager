"""
Constants: Application-wide constants and fixed values.
Provides centralized configuration for reusable values.
"""

# Study Plan Constants
MIN_STUDY_DAYS = 1
MAX_STUDY_DAYS = 365
DEFAULT_STUDY_DAYS = 30

MIN_HOURS_PER_DAY = 0.5
MAX_HOURS_PER_DAY = 12.0
DEFAULT_HOURS_PER_DAY = 2.0

MIN_TOPICS = 1
MAX_TOPICS = 20
RECOMMENDED_TOPICS = 5

# Text Limits
MIN_GOAL_LENGTH = 5
MAX_GOAL_LENGTH = 2000
DEFAULT_GOAL_LENGTH = 100

MIN_TOPIC_LENGTH = 2
MAX_TOPIC_LENGTH = 200

MIN_NOTES_LENGTH = 1
MAX_NOTES_LENGTH = 1000

# API Constants
DEFAULT_API_TIMEOUT = 30
MAX_API_RETRIES = 3
API_RETRY_DELAY = 1.0
MAX_API_RETRY_DELAY = 60.0

# Memory Constants
MEMORY_FILE_PATH = "memory/memory.json"
MAX_PLANS = 100
BACKUP_INTERVAL = 86400  # 24 hours in seconds

# UI Constants
STREAMLIT_PAGE_TITLE = "Agentic AI Study Planner"
STREAMLIT_PAGE_ICON = "🎓"
STREAMLIT_LAYOUT = "wide"

# Theme Colors
PRIMARY_COLOR = "#667eea"
SECONDARY_COLOR = "#764ba2"
SUCCESS_COLOR = "#43e97b"
WARNING_COLOR = "#f5576c"
INFO_COLOR = "#4facfe"
ERROR_COLOR = "#ff6b6b"

# Status Constants
STATUS_PENDING = "pending"
STATUS_DONE = "done"
STATUS_IN_PROGRESS = "in_progress"
STATUS_SKIPPED = "skipped"

VALID_STATUSES = [STATUS_PENDING, STATUS_DONE, STATUS_IN_PROGRESS, STATUS_SKIPPED]

# Progress Thresholds (percentages)
PROGRESS_JUST_STARTED = 10  # 0-10%
PROGRESS_STARTED = 25       # 10-25%
PROGRESS_HALFWAY = 50       # 25-50%
PROGRESS_MAJORITY = 75      # 50-75%
PROGRESS_NEARLY_DONE = 90   # 75-90%
PROGRESS_COMPLETE = 100     # 90-100%

# Error Messages
ERROR_INVALID_GOAL = "Study goal must be between {min} and {max} characters"
ERROR_INVALID_DURATION = "Study duration must be between {min} and {max} days"
ERROR_INVALID_HOURS = "Daily study hours must be between {min} and {max}"
ERROR_INVALID_TOPICS = "Number of topics must be between {min} and {max}"
ERROR_API_FAILED = "API request failed after {retries} retries"
ERROR_MEMORY_SAVE = "Failed to save plan to memory"
ERROR_MEMORY_LOAD = "Failed to load plans from memory"
ERROR_PLAN_NOT_FOUND = "Plan with ID {plan_id} not found"

# Success Messages
SUCCESS_PLAN_CREATED = "Study plan created successfully"
SUCCESS_PLAN_UPDATED = "Study plan updated successfully"
SUCCESS_DAY_COMPLETED = "Day {day} marked as complete"
SUCCESS_REPORT_GENERATED = "Progress report generated successfully"

# Log Messages
LOG_APP_START = "Application started"
LOG_APP_SHUTDOWN = "Application shutting down"
LOG_PLAN_CREATE = "Creating new study plan: {goal}"
LOG_PLAN_DELETE = "Deleting plan ID: {plan_id}"
LOG_GOAL_PARSE = "Parsing study goal: {goal}"
LOG_SCHEDULE_CREATE = "Creating schedule for {days} days"
LOG_DAY_COMPLETE = "Marking day {day} as complete"

# Emoji Constants
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_LOADING = "🔄"
EMOJI_CALENDAR = "📅"
EMOJI_CLOCK = "⏰"
EMOJI_BOOK = "📚"
EMOJI_CHART = "📊"
EMOJI_GOAL = "🎯"
EMOJI_ROCKET = "🚀"
EMOJI_STAR = "⭐"
EMOJI_FIRE = "🔥"
EMOJI_CHECK = "✔️"
EMOJI_CROSS = "✖️"

# AI Model Parameters
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TOP_P = 0.95
DEFAULT_TOP_K = 40
