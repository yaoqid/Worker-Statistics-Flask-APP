from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from datetime import datetime
from functools import wraps
from .models import (
    WorkerCategory,
    DisabilityStatus,
    AgeBand,
    SkillLevel,
    Sex,
    ModificationLog,
    Feedback,
)
from .forms import (
    DisabilityStatusForm,
    AgeBandForm,
    SkillLevelForm,
    SexForm,
    AdminLoginForm
)
from . import db
import http.client
import urllib.parse
import json

# Code is helped by ChatGPT
# Blueprint configuration
main = Blueprint('main', __name__)


# Custom decorator to require admin login
def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Admin access required.", "warning")
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# Routes for the main blueprint
@main.route('/')
def index():
    try:
        conn = http.client.HTTPConnection('api.mediastack.com')
        params = urllib.parse.urlencode({
            # fcff65b3328f8e67108097a1d802251f
            'access_key': 'fcff65b3328f8e67108097a1d802251f',  # Your API Key
            'keywords': 'London, worker',      # Search keywords
            'sort': 'published_desc',          # Sort by publication date
            'categories': 'business',          # Limit to business news
            'languages': 'en',                 # Only English news
            'limit': 10                         # Limit to 10 news articles
        })
        conn.request('GET', '/v1/news?{}'.format(params))
        res = conn.getresponse()
        news_data = res.read().decode('utf-8')
        # mediastack returns JSON with a "data" field containing news articles
        articles = json.loads(news_data).get('data', [])
    except Exception as e:
        flash(f"Error fetching news data: {e}", "danger")
        articles = []
    return render_template('index.html', news=articles)


# Admin routes for the log in
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        # For demonstration purposes, the admin credentials are hardcoded.
        # In production, retrieve credentials from the database and use
        # password hashing.
        # In production, retrieve credentials from the database and use
        # password hashing.
        if form.username.data == "admin" and form.password.data == "123456":
            session['admin_logged_in'] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("admin_login.html", form=form)


# Admin logout route
@main.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    """手动登出时，清除 Session"""
    session.clear()  # 清除所有登录状态

    if request.method == 'POST':
        return '', 204  # 204 无内容，防止页面刷新导致跳转

    flash("Logged out successfully.", "success")
    return redirect(url_for('main.index'))


# Admin dashboard route
@main.route('/admin/dashboard')
@require_admin
def admin_dashboard():
    # This page serves as a sub-navigation area for modifying data,
    # viewing logs, feedback,
    # and adding new admin users.
    return render_template("admin_dashboard.html")


# Admin route for viewing modification logs
@main.route('/admin/modification_log')
@require_admin
def modification_log():
    logs = ModificationLog.query.order_by(
        ModificationLog.timestamp.desc()
    ).all()
    return render_template("modification_log.html", logs=logs)


# Admin route for manage logs and feedbacks
@main.route('/admin/manage_entries')
@require_admin
def manage_entries():
    logs = ModificationLog.query.order_by(
        ModificationLog.timestamp.desc()
    ).all()
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template(
        "manage_entries.html", logs=logs, feedbacks=feedbacks
    )


# Admin route for deleting logs
@main.route('/admin/delete_log/<int:log_id>', methods=['POST'])
@require_admin
def delete_log(log_id):
    log = ModificationLog.query.get(log_id)
    if log:
        db.session.delete(log)
        db.session.commit()
        flash("Log deleted successfully.", "success")
    else:
        flash("Log not found.", "warning")
    return redirect(url_for('main.manage_entries'))


# Admin route for deleting feedbacks
@main.route('/admin/delete_feedback/<int:feedback_id>', methods=['POST'])
@require_admin
def delete_feedback(feedback_id):
    fb = Feedback.query.get(feedback_id)
    if fb:
        db.session.delete(fb)
        db.session.commit()
        flash("Feedback deleted successfully.", "success")
    else:
        flash("Feedback not found.", "warning")
    return redirect(url_for('main.manage_entries'))


# Admin route for modifying tables
@main.route('/admin/modify/<table_name>')
@require_admin
def modify_table(table_name):
    models_map = {
        'worker_category': WorkerCategory,
        'disability_status': DisabilityStatus,
        'age_band': AgeBand,
        'skill_level': SkillLevel,
        'sex': Sex
    }
    Model = models_map.get(table_name)
    if Model is None:
        flash('Invalid table name.', 'danger')
        return redirect(url_for('main.index'))
    data_entries = Model.query.all()
    return render_template(
        'modify_table.html',
        data_entries=data_entries,
        table_name=table_name
    )


# Admin route for adding records
@main.route('/admin/add/<table_name>', methods=['GET', 'POST'])
@require_admin
def add_record(table_name):
    form = None
    if table_name == 'disability_status':
        form = DisabilityStatusForm()
    elif table_name == 'age_band':
        form = AgeBandForm()
    elif table_name == 'skill_level':
        form = SkillLevelForm()
    elif table_name == 'sex':
        form = SexForm()
    else:
        flash('This table does not support adding records.', 'danger')
        return redirect(url_for('main.index'))
    # If the form is submitted and validated, add the record to the database
    if form.validate_on_submit():
        new_record = None
        if table_name == 'disability_status':
            new_record = DisabilityStatus(
                disability_status=form.disability_status.data,
                weighted_count=form.weighted_count.data,
                year=form.year.data,
                category_name=form.category_name.data
            )
        elif table_name == 'age_band':
            new_record = AgeBand(
                age_band=form.age_band.data,
                year=form.year.data,
                category_name=form.category_name.data
            )
        elif table_name == 'skill_level':
            new_record = SkillLevel(
                skill_level=form.skill_level.data,
                weighted_count=form.weighted_count.data,
                year=form.year.data,
                category_name=form.category_name.data
            )
        elif table_name == 'sex':
            new_record = Sex(
                sex=form.sex.data,
                weighted_count=form.weighted_count.data,
                year=form.year.data,
                category_name=form.category_name.data
            )
        db.session.add(new_record)
        # Record the add operation in ModificationLog
        log_entry = ModificationLog(
            timestamp=datetime.utcnow(),
            table_name=table_name,
            modification_type='Add',  # "Add"
            description=f"Added record: {new_record}"
        )
        db.session.add(log_entry)
        db.session.commit()
        flash('Record added successfully.', 'success')
        return redirect(url_for('main.modify_table', table_name=table_name))
    return render_template('add_record.html', form=form, table_name=table_name)


# Admin route for deleting records
@main.route('/admin/delete/<table_name>/<int:record_id>', methods=['POST'])
@require_admin
def delete_record(table_name, record_id):
    models_map = {
        'disability_status': DisabilityStatus,
        'age_band': AgeBand,
        'skill_level': SkillLevel,
        'sex': Sex
    }
    Model = models_map.get(table_name)
    if Model is None:
        flash(
            (
                'Invalid table name or deletion not supported for this table.',
                'danger'
            )
        )
        return redirect(url_for('main.index'))
    record = Model.query.get(record_id)
    if record:
        db.session.delete(record)
        # Record the delete operation in ModificationLog
        log_entry = ModificationLog(
            timestamp=datetime.utcnow(),
            table_name=table_name,
            modification_type='Delet',  # "Delete"
            description=f"Deleted record ID: {record_id}"
        )
        db.session.add(log_entry)
        db.session.commit()
        flash('Record deleted successfully.', 'success')
    else:
        flash('Record not found.', 'warning')
    return redirect(url_for('main.modify_table', table_name=table_name))


# Route for viewing tables
# This route is public and does not require admin login.
@main.route('/view/<table_name>')
def view_table(table_name):
    # This route is public and does not require admin login.
    models_map = {
        'worker_category': WorkerCategory,
        'disability_status': DisabilityStatus,
        'age_band': AgeBand,
        'skill_level': SkillLevel,
        'sex': Sex
    }
    Model = models_map.get(table_name)
    # If the table name is invalid, redirect to the home page.
    if Model is None:
        flash('Invalid table name.', 'danger')
        return redirect(url_for('main.index'))
    data_entries = Model.query.all()
    return render_template(
        'view_table.html',
        data_entries=data_entries,
        table_name=table_name
    )


# Route for get data from database to show in charts
@main.route('/charts', methods=['GET', 'POST'])
def charts():
    import pandas as pd
    import plotly.express as px
    from pathlib import Path
    import sqlite3
    from .models import Feedback  # Ensure Feedback is imported

    # Get parameters: chart type and (for most charts) year.
    # For "skill_trend", use a skill filter.
    chart_type = request.args.get("chart_type", "disability")
    if chart_type == "skill_trend":
        selected_skill = request.args.get("skill", None)
    else:
        chart_year = request.form.get('chart_year') or \
                     request.args.get('year', None)
    # If POST, save feedback information.
    if request.method == 'POST':
        feedback_text = request.form.get('feedback')
        if chart_type == "skill_trend":
            new_feedback = Feedback(
                chart_type=chart_type,
                chart_year=None,
                feedback_text=f"Skill: {selected_skill} - {feedback_text}"
            )
        else:
            chart_year_int = int(chart_year) if chart_year else None
            new_feedback = Feedback(
                chart_type=chart_type,
                chart_year=chart_year_int,
                feedback_text=feedback_text
            )
        db.session.add(new_feedback)
        db.session.commit()
        flash("Thank you for your feedback, it has been saved.", "success")
        if chart_type == "skill_trend":
            return redirect(
                url_for(
                    'main.charts', chart_type=chart_type, skill=selected_skill
                )
            )
        else:
            return redirect(
                url_for('main.charts', chart_type=chart_type, year=chart_year)
            )
    # Use sqlite3 to fetch data based on chart_type.
    file_path = Path(__file__).parent.joinpath(
        '..', 'data', 'night_worker_normalised.db'
    )
    conn = sqlite3.connect(file_path)
    if chart_type == "disability":
        df_all = pd.read_sql_query("SELECT * FROM DISABILITY_STATUS", conn)
    elif chart_type == "skill":
        df_all = pd.read_sql_query("SELECT * FROM SKILL_LEVEL", conn)
    elif chart_type == "gender":
        df_all = pd.read_sql_query("SELECT * FROM SEX", conn)
    elif chart_type == "skill_trend":
        df_all = pd.read_sql_query("SELECT * FROM SKILL_LEVEL", conn)
    else:
        df_all = pd.read_sql_query("SELECT * FROM DISABILITY_STATUS", conn)
    conn.close()
    # Filter data based on chart_type and year.
    if chart_type in ["disability", "skill", "gender"]:
        distinct_years = (
            sorted(df_all['year'].unique()) if not df_all.empty else []
        )
        # If no year is selected, default to the first year in the data.
        if not chart_year and distinct_years:
            chart_year = distinct_years[0]
        if chart_year:
            df = df_all[df_all['year'] == int(chart_year)]
        else:
            df = df_all
    # Filter data based on chart_type and skill for "skill_trend".
    elif chart_type == "skill_trend":
        distinct_skills = (
            sorted(df_all['skill_level'].unique())
            if not df_all.empty
            else []
        )
        if not selected_skill and distinct_skills:
            selected_skill = distinct_skills[0]
        df = df_all[df_all['skill_level'] == selected_skill]
    # Default to all data for unknown chart types.
    else:
        df = df_all
    # Generate the chart based on the chart_type.
    if chart_type == "disability":
        title = (
            f"Worker Distribution by Disability Status in {chart_year}"
            if chart_year
            else "Worker Distribution by Disability Status"
        )
        fig = px.pie(
            df,
            names="disability_status",
            values="weighted_count",
            title=title
        )
    # Generate the chart based on the chart_type.
    elif chart_type == "skill":
        title = (
            f"Worker Counts by Skill Level in {chart_year}"
            if chart_year
            else "Worker Counts by Skill Level"
        )
        fig = px.bar(df, x="skill_level", y="weighted_count", title=title)
    elif chart_type == "gender":
        title = (
            f"Gender Distribution in {chart_year}"
            if chart_year
            else "Gender Distribution"
        )
        fig = px.pie(df, names="sex", values="weighted_count", title=title)
    elif chart_type == "skill_trend":
        title = f"Trend for {selected_skill} Over Years"
        fig = px.line(
            df,
            x="year",
            y="weighted_count",
            title=title,
            labels={"weighted_count": "Count", "year": "Year"}
        )
    else:
        title = (
            f"Worker Distribution by Disability Status in {chart_year}"
            if chart_year
            else "Worker Distribution by Disability Status"
        )
        fig = px.pie(
            df,
            names="disability_status",
            values="weighted_count",
            title=title
        )

    chart_html = fig.to_html(full_html=False)

    if chart_type == "skill_trend":
        return render_template(
            "charts.html",
            chart_html=chart_html,
            chart_type=chart_type,
            skills=distinct_skills,
            selected_skill=selected_skill
        )
    else:
        return render_template(
            "charts.html",
            chart_html=chart_html,
            chart_year=chart_year,
            years=distinct_years,
            chart_type=chart_type
        )


# Route for viewing feedback
@main.route('/feedback')
def feedback_list():
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('feedback_list.html', feedbacks=feedbacks)
