# 🎓 Agentic AI Study Planner & Task Manager
## **ULTIMATE EDITION** ⚡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> **Transform your vague learning goals into structured, AI-powered study plans in seconds.** The most advanced agentic AI study planner with beautiful UI, smart analytics, and zero configuration hassle.

---

## 🌟 Why This is The ULTIMATE Study Planner

### 🎯 **What Makes It Special**

| Feature | Basic Tool | **Our Ultimate Edition** |
|---------|-----------|--------------------------|
| Goal Understanding | Manual input required | ✅ **AI parses ANY goal** - vague or detailed |
| Schedule Creation | Templates only | ✅ **Personalized AI curriculum** for you |
| Progress Tracking | Simple checkboxes | ✅ **Advanced analytics + streaks** |
| User Experience | Plain forms | ✅ **Stunning animated UI** |
| Insights | Basic stats | ✅ **AI-powered recommendations** |
| Motivation | None | ✅ **Achievements & gamification** |
| Error Handling | Crashes easily | ✅ **Never breaks - intelligent fallbacks** |

### ⚡ **Core Superpowers**

🤖 **4 Intelligent AI Agents**
- 🎯 **Goal Parser**: Understands "learn Python" to "Master AWS" - extracts perfect structure
- 📅 **Smart Planner**: Creates optimal day-by-day schedules based on learning science
- ✅ **Task Manager**: Tracks progress and adapts dynamically
- 📊 **Report Generator**: Provides insights, encouragement, and actionable advice

💎 **Production-Grade Quality**
- ✨ **Beautiful Modern UI** with animations and gradients
- 📊 **Advanced Analytics** with heatmaps, gauges, and trend charts
- 🏆 **Gamification** with achievements, streaks, and milestones
- 📱 **Responsive Design** works perfectly on any device
- 🎨 **Dark Mode Support** (coming soon)
- 💾 **Auto-save** every action
- 🚀 **Blazing Fast** with optimized caching

---

## 🎬 See It In Action

### 📸 Screenshots

<table>
  <tr>
    <td width="50%">
      <img src="docs/images/dashboard.png" alt="Dashboard" />
      <p align="center"><b>📊 Beautiful Dashboard</b></p>
    </td>
    <td width="50%">
      <img src="docs/images/create-plan.png" alt="Create Plan" />
      <p align="center"><b>📝 AI-Powered Plan Creation</b></p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="docs/images/analytics.png" alt="Analytics" />
      <p align="center"><b>📈 Advanced Analytics</b></p>
    </td>
    <td width="50%">
      <img src="docs/images/achievements.png" alt="Achievements" />
      <p align="center"><b>🏆 Gamification & Achievements</b></p>
    </td>
  </tr>
</table>

### 🎥 Demo Video

[![Watch Demo](https://img.shields.io/badge/▶️-Watch%20Demo-red?style=for-the-badge)](https://youtu.be/your-demo-link)

---

## 🚀 Quick Start (60 Seconds)

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/agentic-study-planner.git
cd agentic-study-planner

# Run magic setup script
chmod +x quick_start.sh
./quick_start.sh

# Add your Gemini API key to .env
echo "GEMINI_API_KEY=your_key_here" > .env

# Launch! 🚀
streamlit run ui/app.py
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your Gemini API key

# Run the app
streamlit run ui/app.py
```

### 🔑 Get Your Free Gemini API Key

1. Visit: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file

**That's it!** Your AI study planner is ready! 🎉

---

## 💡 Features Deep Dive

### 🎯 1. Intelligent Goal Parsing

**Input anything, get perfect structure:**

```
User: "learn web development"
AI: 60-day plan with HTML, CSS, JS, React, projects
```

```
User: "prepare for AWS certification"
AI: 90-day focused prep with practice exams
```

```
User: "get better at algorithms"
AI: 45-day LeetCode-style progression
```

### 📅 2. Smart Schedule Creation

- **Learning Science Based**: Spaced repetition, interleaving, progressive difficulty
- **Adaptive Pacing**: Adjusts to your progress
- **Variety**: Balances theory, practice, and projects
- **Momentum Builders**: Strategic "quick win" days
- **Review Points**: Consolidation at key milestones

### 📊 3. Advanced Analytics Dashboard

#### Progress Tracking
- 📈 **Visual Progress Gauge** with color-coded milestones
- 🗓️ **Study Heatmap** showing daily activity
- 🔥 **Streak Counter** with best streak tracking
- ⏰ **Time Analysis** with hourly breakdowns

#### Insights
- 🎯 **Pace Assessment**: On track / Ahead / Needs boost
- 📊 **Topic Distribution** charts
- 📈 **Cumulative Progress** over time
- 🏆 **Achievement System** with unlock notifications

### 🏆 4. Gamification & Motivation

**Achievements:**
- 🌟 **First Steps** - Complete Day 1
- 🔥 **Week Warrior** - 7-day streak
- 💪 **Month Master** - 30 days completed
- 🎯 **Quarter Champion** - 25% progress
- ⭐ **Halfway Hero** - 50% progress
- 🏆 **Almost There** - 75% progress
- 👑 **Goal Crusher** - 100% completion

**Streaks:**
- Current streak with fire emoji 🔥
- Best streak tracking
- Streak protection reminders

### 📱 5. Beautiful, Modern UI

- **Gradient Designs** for visual appeal
- **Smooth Animations** on interactions
- **Custom Progress Bars** that celebrate wins
- **Responsive Layout** for any screen size
- **Interactive Charts** using Plotly
- **Color-Coded Status** for quick scanning

---

## 🛠️ Technology Stack

### Core Technologies
```
Frontend:  Streamlit 1.29+ (Python-based web framework)
AI:        Google Gemini 2.0 Flash (Advanced LLM)
Storage:   JSON-based persistent memory
Charts:    Plotly (Interactive visualizations)
UI:        Custom CSS3 with animations
```

### AI Architecture
```
┌─────────────────────────────────────────────────┐
│              User Input (Any Goal)              │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │  🤖 Goal Agent  │  ← Parses & structures
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ 📅 Planner Agent│  ← Creates schedule
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ 💾 Memory Store │  ← Saves persistently
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ ✅ Task Manager │  ← Tracks progress
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ 📊 Report Agent │  ← Generates insights
        └─────────────────┘
```

---

## 📂 Project Structure

```
agentic-study-planner/
│
├── 📱 ui/
│   └── app.py                 # Ultimate Streamlit interface
│
├── 🤖 agents/
│   ├── goal_agent.py          # AI goal parser
│   ├── planner_agent.py       # Schedule creator
│   ├── task_manager.py        # Progress tracker
│   └── report_agent.py        # Insight generator
│
├── 💾 memory/
│   ├── memory_manager.py      # JSON persistence
│   └── memory.json            # Data storage
│
├── 🛠️ utils/
│   ├── prompts.py             # Enhanced AI prompts
│   └── config.py              # Configuration management
│
├── 📄 Documentation
│   ├── README.md              # This file
│   ├── SETUP_GUIDE.md         # Detailed setup
│   ├── API_DOCS.md            # API documentation
│   └── CONTRIBUTING.md        # Contribution guide
│
├── ⚙️ Configuration
│   ├── .env                   # Environment variables
│   ├── requirements.txt       # Python dependencies
│   └── config.py              # App configuration
│
└── 🚀 Scripts
    ├── main.py                # CLI interface
    ├── quick_start.sh         # Automated setup (Unix)
    └── quick_start.bat        # Automated setup (Windows)
```

---

## 🎯 Use Cases

### 🎓 **Students**
- Plan semester coursework
- Prepare for exams
- Learn new subjects systematically
- Track assignment progress

### 💼 **Professionals**
- Upskill for career growth
- Prepare for certifications (AWS, Azure, Google Cloud)
- Learn new programming languages/frameworks
- Structured self-improvement

### 👨‍💻 **Developers**
- Master new technologies
- Prepare for coding interviews
- Learn system design
- Build portfolio projects

### 🏢 **Teams**
- Coordinate learning initiatives
- Track team skill development
- Share study schedules
- Measure learning ROI

---

## 🎨 Customization Guide

### 🎨 Change UI Theme

Edit `ui/app.py` CSS section:

```python
# Change primary gradient
.stat-card {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

### 🤖 Adjust AI Behavior

Edit `utils/prompts.py`:

```python
GOAL_PARSING_PROMPT = """
Your custom instructions here...
Adjust tone, strictness, creativity...
"""
```

### ⚙️ Configure Defaults

Edit `config.py`:

```python
class StudyPlanConfig:
    default_duration_days: int = 30  # Your default
    default_hours_per_day: float = 2.0  # Your default
```

---

## 📊 Performance & Limits

| Metric | Value |
|--------|-------|
| Max Plan Duration | 365 days |
| Max Daily Hours | 12 hours |
| Max Topics per Plan | 20 topics |
| API Response Time | 3-10 seconds |
| Concurrent Users | Unlimited (local) |
| Storage | JSON (upgradeable to DB) |

---

## 🤝 Contributing

We love contributions! Here's how you can help:

### 🐛 **Report Bugs**
Open an [issue](https://github.com/yourusername/study-planner/issues) with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

### ✨ **Suggest Features**
Create a [feature request](https://github.com/yourusername/study-planner/issues/new?template=feature_request.md) with:
- Use case description
- Proposed solution
- Alternative solutions considered

### 💻 **Submit Pull Requests**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

### 📝 **Improve Documentation**
- Fix typos
- Add examples
- Clarify instructions
- Translate to other languages

---

## 🗺️ Roadmap

### 🚧 **Coming Soon** (v2.0)

- [ ] 🌙 **Dark Mode** - Easy on the eyes
- [ ] 📱 **Mobile App** - iOS & Android
- [ ] 🔗 **Calendar Integration** - Google Calendar, Outlook
- [ ] 👥 **Multi-User** - Team collaboration
- [ ] 🔔 **Smart Notifications** - Email & push
- [ ] 🗄️ **Database Support** - PostgreSQL, MongoDB
- [ ] 🌐 **Multi-Language** - i18n support
- [ ] 🎮 **More Gamification** - Leaderboards, challenges
- [ ] 📚 **Resource Library** - Curated learning materials
- [ ] 🤖 **AI Tutor** - Chatbot for questions
- [ ] 📊 **Team Analytics** - For organizations
- [ ] 💳 **Premium Features** - Advanced insights

### 💡 **Future Ideas** (v3.0+)

- Spaced repetition flashcards
- Pomodoro timer integration
- Study buddy matching
- AI-generated quizzes
- Voice commands
- AR/VR study environments
- Blockchain certificates

---

## ❓ FAQ

<details>
<summary><b>Q: Is this free to use?</b></summary>
<br>
Yes! The app is 100% free and open-source. You only need a free Gemini API key from Google.
</details>

<details>
<summary><b>Q: Do I need programming knowledge?</b></summary>
<br>
No! Just follow the setup instructions. If you can copy-paste commands, you can run this.
</details>

<details>
<summary><b>Q: Can I use this offline?</b></summary>
<br>
Partially. Once plans are created, you can view and track them offline. Creating new plans requires internet for AI features.
</details>

<details>
<summary><b>Q: How is my data stored?</b></summary>
<br>
All data is stored locally in `memory/memory.json`. Nothing is sent to external servers except API calls to Gemini for AI features.
</details>

<details>
<summary><b>Q: Can multiple people use this?</b></summary>
<br>
Currently it's single-user. Multi-user support is planned for v2.0. For now, each user should have their own installation.
</details>

<details>
<summary><b>Q: What if I want to change my plan mid-way?</b></summary>
<br>
You can create a new plan anytime. The old plan is saved and you can switch between them in the "All Plans" page.
</details>

---

## 🏆 Showcase

### 📢 **Built With This**

Share your success stories! Create a PR to add your story:

- 🎓 **John D.** - "Learned React in 30 days and got hired!"
- 💼 **Sarah M.** - "Passed AWS Solutions Architect with this plan"
- 👨‍💻 **Mike T.** - "100+ LeetCode problems in 60 days"

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Agentic Study Planner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Powering the intelligence
- **Streamlit** - Amazing web framework
- **Plotly** - Beautiful visualizations
- **Open Source Community** - For inspiration and support

---

## 📞 Support & Contact

### 💬 **Get Help**

- 📧 **Email**: support@studyplanner.com
- 💬 **Discord**: [Join our community](https://discord.gg/studyplanner)
- 🐦 **Twitter**: [@AgenticPlanner](https://twitter.com/agenticplanner)
- 📖 **Documentation**: [docs.studyplanner.com](https://docs.studyplanner.com)

### 🐛 **Report Issues**

Found a bug? [Create an issue](https://github.com/yourusername/study-planner/issues/new)

### 💡 **Feature Requests**

Have an idea? [Suggest a feature](https://github.com/yourusername/study-planner/discussions/new)

---

## ⭐ Star History

If this project helped you, please consider giving it a ⭐ on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/agentic-study-planner&type=Date)](https://star-history.com/#yourusername/agentic-study-planner&Date)

---

## 💖 Support the Project

Love this project? Here's how you can support:

1. ⭐ **Star** the repository
2. 🔀 **Fork** and contribute
3. 📢 **Share** with friends and colleagues
4. 🐛 **Report bugs** to help improve
5. 💡 **Suggest features** for future versions
6. 📝 **Write tutorials** or blog posts
7. ☕ **Buy us a coffee** (coming soon)

---

<div align="center">

**Made with ❤️ and 🤖 AI**

**Transform Your Learning Journey Today! 🚀**

[⬆ Back to Top](#-agentic-ai-study-planner--task-manager)

---

**© 2024 Agentic Study Planner | [Website](https://studyplanner.com) | [Docs](https://docs.studyplanner.com) | [Blog](https://blog.studyplanner.com)**

</div>