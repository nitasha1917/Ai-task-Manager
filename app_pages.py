"""
Page Render Functions for Streamlit App
Contains all page rendering logic separated for maintainability
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.export_utils import (
    export_schedule_csv, export_stats_csv,
    create_download_button, export_report_txt, export_full_plan
)


# ==================== HELPER ====================

def safe_df(schedule: list) -> pd.DataFrame:
    """
    Convert schedule list to DataFrame with ALL expected columns guaranteed.
    Any missing column is filled with a safe default so no KeyError ever occurs.
    """
    if not schedule:
        return pd.DataFrame(columns=['day', 'topic', 'subtopic', 'duration_hours',
                                     'activity', 'status', 'status_icon', 'notes'])

    df = pd.DataFrame(schedule)

    defaults = {
        'day': 0,
        'topic': 'N/A',
        'subtopic': '',
        'duration_hours': 0.0,
        'activity': 'learn',
        'status': 'pending',
        'notes': '',
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    # Always recompute status_icon from status
    df['status_icon'] = df['status'].apply(lambda x: '✅' if x == 'done' else '⏳')

    return df


# ==================== PAGES ====================

def render_create_plan_page(goal_agent, planner_agent, memory):
    """Render the create plan page."""
    st.markdown('<h1 class="main-header">📝 Create Your Study Plan</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Let AI transform your goals into actionable plans</p>', unsafe_allow_html=True)

    with st.expander("💡 See Examples", expanded=False):
        st.markdown("""
        **Vague Goals** (AI figures it out):
        - "learn web development"
        - "get better at coding"
        - "prepare for interviews"

        **Specific Goals** (AI optimizes):
        - "Master Python in 30 days, 2 hours daily"
        - "AWS certification prep, 60 days, 3 hours/day"
        - "Learn React and build 3 projects in 45 days"
        """)

    with st.form("create_plan_form", clear_on_submit=False):
        st.markdown("### 🎯 Describe Your Learning Goal")

        goal_input = st.text_area(
            "What do you want to learn?",
            placeholder="Examples:\n• Learn Python programming in 30 days\n• Master machine learning fundamentals in 60 days, studying 2 hours daily\n• Prepare for AWS certification exam",
            height=150,
            help="Be as specific or vague as you like - our AI will figure it out!"
        )

        st.markdown("### ⚙️ Customization (Optional)")

        col1, col2 = st.columns(2)
        with col1:
            custom_days = st.number_input(
                "Duration (days)",
                min_value=0, max_value=365, value=0,
                help="Leave as 0 to let AI decide"
            )
        with col2:
            custom_hours = st.number_input(
                "Daily study hours",
                min_value=0.0, max_value=12.0, value=0.0, step=0.5,
                help="Leave as 0 to let AI suggest"
            )

        submitted = st.form_submit_button("🚀 Create My Study Plan", type="primary", use_container_width=True)

    if submitted:
        if not goal_input.strip():
            st.error("❌ Please enter your study goal")
            return

        with st.spinner("🤖 AI agents are working on your personalized plan..."):
            try:
                with st.status("🎯 Analyzing your goal...", expanded=True) as status:
                    st.write("Goal Agent is understanding your requirements...")
                    parsed_goal = goal_agent.parse_goal(goal_input)

                    if custom_days > 0:
                        parsed_goal['total_days'] = custom_days
                    if custom_hours > 0:
                        parsed_goal['hours_per_day'] = custom_hours

                    st.write("✅ Goal analyzed successfully!")
                    status.update(label="✅ Goal Analysis Complete", state="complete")

                with st.status("📅 Creating your personalized schedule...", expanded=True) as status:
                    st.write("Planner Agent is designing your learning path...")
                    schedule = planner_agent.create_schedule(parsed_goal)
                    st.write("✅ Schedule created successfully!")
                    status.update(label="✅ Schedule Creation Complete", state="complete")

                with st.status("💾 Saving your plan...", expanded=True) as status:
                    plan_data = {
                        "goal": goal_input,
                        "parsed_goal": parsed_goal,
                        "schedule": schedule
                    }

                    if memory.save_plan(plan_data):
                        st.write("✅ Plan saved successfully!")
                        status.update(label="✅ Save Complete", state="complete")
                    else:
                        st.error("Failed to save plan")
                        return

                st.balloons()

                st.markdown("""
                <div class="success-box">
                    <h3>🎉 Your Study Plan is Ready!</h3>
                    <p>Your personalized learning journey has been created.</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📅 Duration", f"{parsed_goal.get('total_days', '?')} days")
                with col2:
                    st.metric("⏰ Daily Hours", f"{parsed_goal.get('hours_per_day', '?')} hours")
                with col3:
                    st.metric("📚 Topics", len(parsed_goal.get('topics', [])))

                st.markdown("### 🎯 Topics Covered")
                for i, topic in enumerate(parsed_goal.get('topics', []), 1):
                    st.write(f"{i}. {topic}")

            except Exception as e:
                st.error(f"❌ Error creating plan: {e}")
                st.exception(e)  # shows full traceback in UI for easier debugging


def render_schedule_page(memory):
    """Render the schedule view page."""
    st.markdown('<h1 class="main-header">📅 Study Schedule</h1>', unsafe_allow_html=True)

    plan = memory.get_latest_plan()

    if not plan:
        st.warning("No study plan found. Create one first!")
        return

    schedule = plan.get('schedule', [])

    st.markdown(f"### 🎯 {plan.get('goal', 'Study Plan')}")
    st.caption(f"Created: {str(plan.get('created_at', 'N/A'))[:10]}")

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
    with col2:
        sort_by = st.selectbox("Sort by", ["Day (Ascending)", "Day (Descending)", "Topic"])

    # Filter
    if status_filter == "Pending":
        filtered = [d for d in schedule if d.get("status") == "pending"]
    elif status_filter == "Completed":
        filtered = [d for d in schedule if d.get("status") == "done"]
    else:
        filtered = schedule

    # Sort
    if sort_by == "Day (Ascending)":
        filtered = sorted(filtered, key=lambda x: x.get('day', 0))
    elif sort_by == "Day (Descending)":
        filtered = sorted(filtered, key=lambda x: x.get('day', 0), reverse=True)
    elif sort_by == "Topic":
        filtered = sorted(filtered, key=lambda x: x.get('topic', ''))

    if filtered:
        df = safe_df(filtered)

        # Only show columns that make sense to the user
        display_cols = ['day', 'topic', 'duration_hours', 'status_icon']

        # Optionally show subtopic/notes if they have real content
        if df['subtopic'].str.strip().ne('').any():
            display_cols.append('subtopic')
        if df['notes'].str.strip().ne('').any():
            display_cols.append('notes')
        if 'activity' in df.columns:
            display_cols.append('activity')

        df_display = df[display_cols].copy()
        df_display.columns = [c.replace('_', ' ').title()
                               .replace('Status Icon', 'Status')
                               .replace('Duration Hours', 'Hours')
                               for c in display_cols]

        st.dataframe(df_display, use_container_width=True, height=400)

        try:
            csv = export_schedule_csv(filtered, plan.get('goal', ''))
            st.markdown(
                create_download_button(
                    csv,
                    f"study_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                    "📥 Export Schedule as CSV"
                ),
                unsafe_allow_html=True
            )
        except Exception:
            pass  # Export is non-critical
    else:
        st.info("No tasks match the selected filter")


def render_mark_complete_page(task_manager, memory):
    """Render the mark complete page."""
    st.markdown('<h1 class="main-header">✅ Mark Day Complete</h1>', unsafe_allow_html=True)

    plan = memory.get_latest_plan()

    if not plan:
        st.warning("No study plan found. Create one first!")
        return

    schedule = plan.get('schedule', [])
    pending = [d for d in schedule if d.get("status") == "pending"]

    if not pending:
        st.success("🎉 Congratulations! All days are complete!")
        st.balloons()
        return

    st.markdown("### ⏳ Pending Tasks")

    for day in pending[:5]:
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                topic = day.get('topic', 'N/A')
                hours = day.get('duration_hours', 0)
                subtopic = day.get('subtopic', '')
                notes = day.get('notes', '')

                detail = subtopic or notes or ''
                st.markdown(
                    f"**Day {day.get('day', '?')}: {topic}**  \n"
                    f"⏰ {hours} hours"
                    + (f"  \n📝 {detail}" if detail else "")
                )

            with col2:
                if st.button("✅ Complete", key=f"complete_{day.get('day', 0)}"):
                    try:
                        updated_schedule = task_manager.mark_day_complete(schedule, day['day'])

                        if memory.update_plan_schedule(plan['id'], updated_schedule):
                            st.success(f"✅ Day {day['day']} marked as complete!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Failed to update schedule")
                    except Exception as e:
                        st.error(f"Error: {e}")

            st.markdown("---")

    if len(pending) > 5:
        st.info(f"... and {len(pending) - 5} more pending tasks")

    # Bulk complete
    st.markdown("### 🔢 Bulk Complete")

    with st.form("bulk_complete_form"):
        day_numbers_input = st.text_input(
            "Enter day numbers (comma-separated)",
            placeholder="e.g., 1, 2, 3"
        )

        if st.form_submit_button("✅ Mark Multiple Days Complete"):
            try:
                day_numbers = [int(d.strip()) for d in day_numbers_input.split(",") if d.strip()]

                # Use mark_multiple_days_complete if available, else loop
                if hasattr(task_manager, 'mark_multiple_days_complete'):
                    updated_schedule = task_manager.mark_multiple_days_complete(schedule, day_numbers)
                else:
                    updated_schedule = schedule
                    for dn in day_numbers:
                        updated_schedule = task_manager.mark_day_complete(updated_schedule, dn)

                if memory.update_plan_schedule(plan['id'], updated_schedule):
                    st.success(f"✅ Marked {len(day_numbers)} days as complete!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to update schedule")

            except ValueError:
                st.error("Invalid day numbers. Use format: 1, 2, 3")
            except Exception as e:
                st.error(f"Error: {e}")


def render_analytics_page(memory):
    """Render the advanced analytics page."""
    st.markdown('<h1 class="main-header">📊 Advanced Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Deep insights into your learning journey</p>', unsafe_allow_html=True)

    plan = memory.get_latest_plan()

    if not plan:
        st.warning("No study plan found. Create one first!")
        return

    schedule = plan.get('schedule', [])
    stats = memory.get_plan_statistics(plan['id'])

    st.markdown("### 📈 Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Days", stats.get('total_days', 0))
    with col2:
        st.metric("Completed", stats.get('completed_days', 0),
                  f"{stats.get('progress_percentage', 0):.0f}%")
    with col3:
        st.metric("Pending", stats.get('pending_days', 0))
    with col4:
        st.metric("Total Hours", f"{stats.get('total_hours', 0):.1f}h")

    st.markdown("### 📊 Visualizations")

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Progress", "🎯 Topics", "⏰ Time Analysis", "🔥 Streaks"])

    with tab1:
        try:
            from ui.app import create_cumulative_hours_chart
            fig = create_cumulative_hours_chart(schedule)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Complete some days to see progress chart")
        except Exception as e:
            st.warning(f"Chart unavailable: {e}")

    with tab2:
        try:
            from ui.app import create_topic_distribution_chart
            fig = create_topic_distribution_chart(schedule)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Chart unavailable: {e}")

    with tab3:
        try:
            completed_hours = stats.get('completed_hours', 0)
            total_hours = stats.get('total_hours', 0)
            remaining_hours = max(0, total_hours - completed_hours)

            fig = go.Figure(data=[
                go.Bar(name='Completed', x=['Hours'], y=[completed_hours], marker_color='#55efc4'),
                go.Bar(name='Remaining', x=['Hours'], y=[remaining_hours], marker_color='#ffcccb')
            ])
            fig.update_layout(title='Study Hours Breakdown', yaxis_title='Hours', height=400)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Chart unavailable: {e}")

    with tab4:
        try:
            from ui.app import get_streak_info
            streak_info = get_streak_info(schedule)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔥 Current Streak", f"{streak_info.get('current_streak', 0)} days")
            with col2:
                st.metric("🏆 Best Streak", f"{streak_info.get('longest_streak', 0)} days")

            last = streak_info.get('last_study')
            if last:
                st.info(f"📚 Last studied: {last}")
        except Exception as e:
            st.warning(f"Streak info unavailable: {e}")


def render_all_plans_page(memory):
    """Render all plans management page."""
    st.markdown('<h1 class="main-header">🎯 All Plans</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage all your study plans</p>', unsafe_allow_html=True)

    plans = memory.get_all_plans()

    if not plans:
        st.info("No plans found. Create your first plan!")
        return

    st.markdown(f"### 📊 You have {len(plans)} study plan(s)")

    for plan in plans:
        try:
            stats = memory.get_plan_statistics(plan['id'])

            with st.expander(f"📚 Plan #{plan['id']}: {str(plan.get('goal', 'N/A'))[:50]}", expanded=False):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Progress", f"{stats.get('progress_percentage', 0):.0f}%")
                    st.metric("Total Days", stats.get('total_days', 0))

                with col2:
                    st.metric("Completed", stats.get('completed_days', 0))
                    st.metric("Pending", stats.get('pending_days', 0))

                with col3:
                    st.metric("Hours Done", f"{stats.get('completed_hours', 0):.1f}h")
                    remaining = stats.get('total_hours', 0) - stats.get('completed_hours', 0)
                    st.metric("Hours Left", f"{max(0, remaining):.1f}h")

                col1, col2, col3 = st.columns(3)

                with col2:
                    try:
                        csv = export_full_plan(plan, stats)
                        st.markdown(
                            create_download_button(csv, f"plan_{plan['id']}.csv", "📥 Export"),
                            unsafe_allow_html=True
                        )
                    except Exception:
                        pass

                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{plan['id']}"):
                        if memory.delete_plan(plan['id']):
                            st.success(f"Plan #{plan['id']} deleted")
                            st.rerun()

        except Exception as e:
            st.warning(f"Could not load plan #{plan.get('id', '?')}: {e}")


def render_export_page(memory, report_agent):
    """Render the export data page."""
    st.markdown('<h1 class="main-header">📥 Export Data</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Download your study data in various formats</p>', unsafe_allow_html=True)

    plan = memory.get_latest_plan()

    if not plan:
        st.warning("No study plan found. Create one first!")
        return

    schedule = plan.get('schedule', [])
    stats = memory.get_plan_statistics(plan['id'])

    st.markdown("### 📊 Available Exports")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📅 Schedule Data")

        try:
            csv_schedule = export_schedule_csv(schedule, plan.get('goal', ''))
            st.markdown(
                create_download_button(
                    csv_schedule,
                    f"schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                    "📥 Download Schedule (CSV)"
                ),
                unsafe_allow_html=True
            )
        except Exception as e:
            st.warning(f"Schedule export unavailable: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        try:
            csv_stats = export_stats_csv(stats)
            st.markdown(
                create_download_button(
                    csv_stats,
                    f"statistics_{datetime.now().strftime('%Y%m%d')}.csv",
                    "📥 Download Statistics (CSV)"
                ),
                unsafe_allow_html=True
            )
        except Exception as e:
            st.warning(f"Statistics export unavailable: {e}")

    with col2:
        st.markdown("#### 📊 Reports")

        if st.button("📝 Generate AI Report", type="primary"):
            with st.spinner("Generating report..."):
                try:
                    report = report_agent.generate_report(schedule, use_ai=True)
                    txt_report = export_report_txt(report, plan.get('goal', ''))
                    st.markdown(
                        create_download_button(
                            txt_report,
                            f"report_{datetime.now().strftime('%Y%m%d')}.txt",
                            "📥 Download Report (TXT)"
                        ),
                        unsafe_allow_html=True
                    )
                    st.success("Report generated!")
                except Exception as e:
                    st.error(f"Report generation failed: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        try:
            csv_full = export_full_plan(plan, stats)
            st.markdown(
                create_download_button(
                    csv_full,
                    f"complete_plan_{datetime.now().strftime('%Y%m%d')}.csv",
                    "📥 Download Complete Plan (CSV)"
                ),
                unsafe_allow_html=True
            )
        except Exception as e:
            st.warning(f"Full plan export unavailable: {e}")

    # Preview
    st.markdown("### 👀 Data Preview")

    tab1, tab2 = st.tabs(["📅 Schedule", "📊 Statistics"])

    with tab1:
        try:
            df = safe_df(schedule)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.warning(f"Preview unavailable: {e}")

    with tab2:
        st.json(stats)