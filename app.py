"""
🎓 AGENTIC AI STUDY PLANNER & TASK MANAGER - ULTIMATE EDITION
Complete Production Application - Main Entry Point
Run with: streamlit run ui/app.py
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.goal_agent import GoalAgent
from agents.planner_agent import PlannerAgent
from agents.task_manager import TaskManagerAgent
from agents.report_agent import ReportAgent
from memory.memory_manager import MemoryManager

# Import page render functions
try:
    from ui.app_pages import (
        render_create_plan_page,
        render_schedule_page,
        render_mark_complete_page,
        render_analytics_page,
        render_all_plans_page,
        render_export_page
    )
    PAGES_IMPORTED = True
except:
    PAGES_IMPORTED = False
    pass

try:
    from cnn.cnn_page import render_cnn_page
    CNN_IMPORTED = True
except Exception:
    CNN_IMPORTED = False
# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Agentic AI Study Planner | Ultimate Edition",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)




# ==================== UTILITY FUNCTIONS ====================
def get_achievement_badges(stats: Dict[str, Any]) -> List[str]:
    """Generate achievement badges."""
    badges = []
    completed = stats.get('completed_days', 0)
    progress = stats.get('progress_percentage', 0)
    
    if completed >= 1: badges.append("🌟 First Steps")
    if completed >= 7: badges.append("🔥 Week Warrior")
    if completed >= 30: badges.append("💪 Month Master")
    if progress >= 25: badges.append("🎯 Quarter Champion")
    if progress >= 50: badges.append("⭐ Halfway Hero")
    if progress >= 75: badges.append("🏆 Almost There")
    if progress >= 100: badges.append("👑 Goal Crusher")
    
    return badges


def create_progress_gauge(percentage: float) -> go.Figure:
    """Create progress gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Progress", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 25], 'color': '#ffcccb'},
                {'range': [25, 50], 'color': '#ffeaa7'},
                {'range': [50, 75], 'color': '#74b9ff'},
                {'range': [75, 100], 'color': '#55efc4'}
            ]
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def create_heatmap(schedule: List[Dict[str, Any]]) -> go.Figure:
    """Create study heatmap."""
    days = [f"Day {d.get('day', 0)}" for d in schedule[:30]]
    statuses = [1 if d.get('status') == 'done' else 0 for d in schedule[:30]]
    topics = [d.get('topic', 'N/A') for d in schedule[:30]]
    
    fig = go.Figure(data=go.Heatmap(
        z=[statuses],
        x=days,
        y=['Progress'],
        colorscale=[[0, '#ffcccb'], [1, '#55efc4']],
        text=[topics],
        hovertemplate='%{x}<br>%{text}<extra></extra>',
        showscale=False
    ))
    fig.update_layout(title='Study Progress Heatmap', height=150)
    return fig


def get_streak_info(schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate streak information."""
    completed = sorted([d for d in schedule if d.get('status') == 'done'], 
                      key=lambda x: x.get('day', 0))
    
    if not completed:
        return {'current_streak': 0, 'longest_streak': 0, 'last_study': None}
    
    longest_streak = current_streak = 1
    temp_streak = 1
    
    for i in range(1, len(completed)):
        if completed[i]['day'] == completed[i-1]['day'] + 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    current_streak = 1
    for i in range(len(completed) - 1, 0, -1):
        if completed[i]['day'] == completed[i-1]['day'] + 1:
            current_streak += 1
        else:
            break
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_study': completed[-1].get('topic', 'N/A')
    }


def create_cumulative_hours_chart(schedule: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """Create cumulative study hours line chart."""
    completed = [d for d in schedule if d.get('status') == 'done']
    completed = sorted(completed, key=lambda x: x.get('day', 0))
    
    if not completed:
        return None
    
    days = [d.get('day', 0) for d in completed]
    cumulative_hours = []
    total = 0
    for d in completed:
        total += d.get('duration_hours', 0)
        cumulative_hours.append(total)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days,
        y=cumulative_hours,
        mode='lines+markers',
        name='Cumulative Hours',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    fig.update_layout(
        title='Cumulative Study Hours Over Time',
        xaxis_title='Day',
        yaxis_title='Total Hours',
        height=400,
        font={'family': 'Poppins'},
        hovermode='x unified'
    )
    
    return fig


def create_topic_distribution_chart(schedule: List[Dict[str, Any]]) -> go.Figure:
    """Create topic distribution pie chart."""
    topic_counts = {}
    for day in schedule:
        topic = day.get('topic', 'Unknown')
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(topic_counts.keys()),
        values=list(topic_counts.values()),
        hole=0.4,
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title='Topic Distribution',
        height=400,
        showlegend=True,
        font={'family': 'Poppins'}
    )
    
    return fig


# ==================== CSS ====================
def load_css():
    """Load custom CSS."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Poppins', sans-serif; }
        
        .main-header {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .sub-header {
            font-size: 1.3rem;
            color: #6c757d;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.8rem;
            border-radius: 15px;
            color: white;
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        }
        
        .stat-value {
            font-size: 3rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }
        
        .stat-label {
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .info-box {
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            border-left: 5px solid #17a2b8;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .success-box {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left: 5px solid #28a745;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .achievement-badge {
            display: inline-block;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            margin: 0.3rem;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)


# ==================== MAIN APP CLASS ====================
class StudyPlannerApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize app."""
        load_css()
        self.initialize_session_state()
        self.initialize_agents()
    
    def initialize_session_state(self):
        """Initialize session state."""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.memory = MemoryManager()
    
    def initialize_agents(self):
        """Initialize AI agents."""
        if 'agents_initialized' not in st.session_state:
            load_dotenv()
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                st.error("❌ **GEMINI_API_KEY not configured!**")
                st.info("Please add your Gemini API key to the `.env` file")
                st.code("GEMINI_API_KEY=your_actual_key_here", language="bash")
                st.stop()
            
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"))
                
                st.session_state.goal_agent = GoalAgent(model)
                st.session_state.planner_agent = PlannerAgent(model)
                st.session_state.task_manager = TaskManagerAgent(model)
                st.session_state.report_agent = ReportAgent(model)
                st.session_state.agents_initialized = True
            except Exception as e:
                st.error(f"❌ Error initializing AI agents: {e}")
                st.stop()
    
    def render_sidebar(self) -> str:
        """Render sidebar."""
        with st.sidebar:
            st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h1 style='color: white; font-size: 2rem;'>🎓</h1>
                <h2 style='color: white; font-size: 1.3rem;'>Study Planner</h2>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.8rem;'>Ultimate Edition</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            page = st.radio(
                "📍 Navigation",
                [
                    "🏠 Dashboard",
                    "📝 Create Plan",
                    "📅 View Schedule",
                    "✅ Mark Complete",
                    "📊 Analytics",
                    "🎯 All Plans",
                    "📥 Export Data",
                    "🧠 Distraction Detector", 
                ]
            )
            
            st.markdown("---")
            
            # Quick stats
            plan = st.session_state.memory.get_latest_plan()
            if plan:
                stats = st.session_state.memory.get_plan_statistics(plan['id'])
                if stats:
                    st.markdown("### 📈 Quick Stats")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("✅ Done", stats['completed_days'])
                    with col2:
                        st.metric("⏳ Left", stats['pending_days'])
                    
                    st.progress(stats['progress_percentage'] / 100)
                    
                    # Streak
                    streak_info = get_streak_info(plan.get('schedule', []))
                    if streak_info['current_streak'] > 0:
                        st.markdown(f"""
                        <div style='background: rgba(255,255,255,0.1); padding: 0.8rem; 
                                    border-radius: 10px; margin-top: 1rem;'>
                            <p style='color: white; margin: 0; font-size: 0.9rem;'>
                                🔥 Streak: <b>{streak_info['current_streak']}</b> days
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            
            return page
    
    def render_dashboard(self):
        """Render dashboard."""
        st.markdown('<h1 class="main-header">🎓 Agentic AI Study Planner</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Your Intelligent Learning Companion</p>', unsafe_allow_html=True)
        
        plan = st.session_state.memory.get_latest_plan()
        
        if not plan:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div class="info-box">
                    <h2 style='text-align: center;'>👋 Welcome!</h2>
                    <p style='text-align: center;'>Transform your learning goals into structured plans with AI.</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 Create Your First Plan", type="primary", use_container_width=True):
                    st.rerun()
            return
        
        # Display stats
        stats = st.session_state.memory.get_plan_statistics(plan['id'])
        schedule = plan.get('schedule', [])
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Days</div>
                <div class="stat-value">{stats['total_days']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="stat-label">Completed</div>
                <div class="stat-value">{stats['completed_days']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div class="stat-label">Remaining</div>
                <div class="stat-value">{stats['pending_days']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <div class="stat-label">Progress</div>
                <div class="stat-value">{stats['progress_percentage']:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Visualizations
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = create_progress_gauge(stats['progress_percentage'])
            st.plotly_chart(fig, use_container_width=True)
            
            if schedule:
                fig = create_heatmap(schedule)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Your Goal")
            st.info(plan.get('goal', 'N/A'))
            
            # Achievements
            badges = get_achievement_badges(stats)
            if badges:
                st.markdown("### 🏆 Achievements")
                for badge in badges:
                    st.markdown(f'<span class="achievement-badge">{badge}</span>', unsafe_allow_html=True)
            
            # Next task
            pending = [d for d in schedule if d.get('status') == 'pending']
            if pending:
                next_task = sorted(pending, key=lambda x: x.get('day', 999))[0]
                st.markdown("### 📌 Next Up")
                st.markdown(f"""
                **Day {next_task['day']}: {next_task['topic']}**  
                ⏰ {next_task['duration_hours']} hours
                """)
    
    def run(self):
        """Run the application."""
        page = self.render_sidebar()
        
        # Route to pages
        if page == "🏠 Dashboard":
            self.render_dashboard()
        
        elif page == "📝 Create Plan":
            if PAGES_IMPORTED:
                render_create_plan_page(
                    st.session_state.goal_agent,
                    st.session_state.planner_agent,
                    st.session_state.memory
                )
            else:
                # Inline fallback
                st.markdown('<h1 class="main-header">📝 Create Plan</h1>', unsafe_allow_html=True)
                
                with st.form("create_form"):
                    goal = st.text_area("Enter your study goal:", height=150)
                    col1, col2 = st.columns(2)
                    with col1:
                        custom_days = st.number_input("Duration (days)", 0, 365, 0)
                    with col2:
                        custom_hours = st.number_input("Hours/day", 0.0, 12.0, 0.0)
                    
                    if st.form_submit_button("Create", type="primary"):
                        if goal:
                            with st.spinner("Creating plan..."):
                                parsed = st.session_state.goal_agent.parse_goal(goal)
                                if custom_days > 0:
                                    parsed['total_days'] = custom_days
                                if custom_hours > 0:
                                    parsed['hours_per_day'] = custom_hours
                                schedule = st.session_state.planner_agent.create_schedule(parsed)
                                st.session_state.memory.save_plan({
                                    "goal": goal,
                                    "parsed_goal": parsed,
                                    "schedule": schedule
                                })
                                st.success("Plan created!")
                                st.balloons()
        
        elif page == "📅 View Schedule":
            if PAGES_IMPORTED:
                render_schedule_page(st.session_state.memory)
            else:
                st.markdown('<h1 class="main-header">📅 Schedule</h1>', unsafe_allow_html=True)
                plan = st.session_state.memory.get_latest_plan()
                if plan:
                    df = pd.DataFrame(plan.get('schedule', []))
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No plan found")
        
        elif page == "✅ Mark Complete":
            if PAGES_IMPORTED:
                render_mark_complete_page(
                    st.session_state.task_manager,
                    st.session_state.memory
                )
            else:
                st.markdown('<h1 class="main-header">✅ Mark Complete</h1>', unsafe_allow_html=True)
                plan = st.session_state.memory.get_latest_plan()
                if plan:
                    pending = [d for d in plan['schedule'] if d.get('status') == 'pending']
                    for day in pending[:5]:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**Day {day['day']}: {day['topic']}**")
                        with col2:
                            if st.button(f"✅", key=f"c_{day['day']}"):
                                updated = st.session_state.task_manager.mark_day_complete(
                                    plan['schedule'], day['day']
                                )
                                st.session_state.memory.update_plan_schedule(plan['id'], updated)
                                st.success("Complete!")
                                st.rerun()
                else:
                    st.warning("No plan found")
        
        elif page == "📊 Analytics":
            if PAGES_IMPORTED:
                render_analytics_page(st.session_state.memory)
            else:
                st.markdown('<h1 class="main-header">📊 Analytics</h1>', unsafe_allow_html=True)
                plan = st.session_state.memory.get_latest_plan()
                if plan:
                    stats = st.session_state.memory.get_plan_statistics(plan['id'])
                    schedule = plan.get('schedule', [])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Days", stats['total_days'])
                    with col2:
                        st.metric("Completed", stats['completed_days'])
                    with col3:
                        st.metric("Progress", f"{stats['progress_percentage']:.0f}%")
                    
                    # Charts
                    fig = create_cumulative_hours_chart(schedule)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    fig = create_topic_distribution_chart(schedule)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No plan found")
        
        elif page == "🎯 All Plans":
            if PAGES_IMPORTED:
                render_all_plans_page(st.session_state.memory)
            else:
                st.markdown('<h1 class="main-header">🎯 All Plans</h1>', unsafe_allow_html=True)
                plans = st.session_state.memory.get_all_plans()
                for plan in plans:
                    stats = st.session_state.memory.get_plan_statistics(plan['id'])
                    with st.expander(f"Plan #{plan['id']}: {plan.get('goal', 'N/A')[:40]}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Progress", f"{stats['progress_percentage']:.0f}%")
                        with col2:
                            st.metric("Days", f"{stats['completed_days']}/{stats['total_days']}")
        
        elif page == "📥 Export Data":
            if PAGES_IMPORTED:
                render_export_page(st.session_state.memory, st.session_state.report_agent)
            else:
                st.markdown('<h1 class="main-header">📥 Export</h1>', unsafe_allow_html=True)
                plan = st.session_state.memory.get_latest_plan()
                if plan:
                    csv = pd.DataFrame(plan['schedule']).to_csv(index=False)
                    st.download_button("Download CSV", csv, "schedule.csv", "text/csv")
                else:
                    st.warning("No plan found")

        elif page == "🧠 Distraction Detector":
            try:
               from cnn.cnn_page import render_cnn_page
               CNN_IMPORTED = True
            except Exception as e:
                CNN_IMPORTED = False
                st.error(f"❌ CNN Import Failed: {e}")
        else:
            st.error("❌ CNN module not found. Make sure cnn/cnn_page.py exists.")
            st.code("pip install tensorflow opencv-python pillow", language="bash")


# ==================== MAIN ====================
def main():
    """Main entry point."""
    app = StudyPlannerApp()
    app.run()


if __name__ == "__main__":
    main()