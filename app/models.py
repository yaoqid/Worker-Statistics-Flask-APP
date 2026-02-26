from . import db
from datetime import datetime

# Code is helped by ChatGPT
# Define the database models
class WorkerCategory(db.Model):
    __tablename__ = 'WORKER_CATEGORY'
    # Composite primary key: category_name and year uniquely identify a record.
    category_name = db.Column(db.String, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    # Relationships to other tables
    disability_statuses = db.relationship(
        'DisabilityStatus', backref='worker_category', lazy=True
    )
    age_bands = db.relationship(
        'AgeBand', backref='worker_category', lazy=True
    )
    skill_levels = db.relationship(
        'SkillLevel', backref='worker_category', lazy=True
    )
    sexes = db.relationship('Sex', backref='worker_category', lazy=True)

    def __repr__(self):
        return f"<WorkerCategory {self.year} - {self.category_name}>"


# Define the DisabilityStatus model
class DisabilityStatus(db.Model):
    __tablename__ = 'DISABILITY_STATUS'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # The status description, e.g., "Equality Act Disabled"
    disability_status = db.Column(db.String)
    weighted_count = db.Column(db.Integer)
    year = db.Column(db.Integer, nullable=False)
    category_name = db.Column(db.String, nullable=False)
    # Define a composite foreign key that references WORKER_CATEGORY
    # table's primary key
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['year', 'category_name'],
            [
                'WORKER_CATEGORY.year',
                'WORKER_CATEGORY.category_name'
            ]
        ),
    )

    def __repr__(self):
        return f"<DisabilityStatus {self.id}: {self.disability_status}>"


# Define the AgeBand model
class AgeBand(db.Model):
    __tablename__ = 'AGE_BAND'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # The age band, e.g., "16-21"
    age_band = db.Column(db.String)
    year = db.Column(db.Integer, nullable=False)
    category_name = db.Column(db.String, nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['year', 'category_name'],
                                [
                                    'WORKER_CATEGORY.year',
                                    'WORKER_CATEGORY.category_name'
                                ]),
    )

    def __repr__(self):
        return f"<AgeBand {self.id}: {self.age_band}>"


# Define the SkillLevel model
class SkillLevel(db.Model):
    __tablename__ = 'SKILL_LEVEL'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # The skill level, e.g., "Level 1"
    skill_level = db.Column(db.String)
    weighted_count = db.Column(db.Integer)
    year = db.Column(db.Integer, nullable=False)
    category_name = db.Column(db.String, nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['year', 'category_name'],
                                [
                                    'WORKER_CATEGORY.year',
                                    'WORKER_CATEGORY.category_name'
                                ]),
    )

    def __repr__(self):
        return f"<SkillLevel {self.id}: {self.skill_level}>"


# Define the sex model
class Sex(db.Model):
    __tablename__ = 'SEX'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # The gender, e.g., "Male" or "Female"
    sex = db.Column(db.String)
    weighted_count = db.Column(db.Integer)
    year = db.Column(db.Integer, nullable=False)
    category_name = db.Column(db.String, nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['year', 'category_name'],
                                [
                                    'WORKER_CATEGORY.year',
                                    'WORKER_CATEGORY.category_name'
                                ]),
    )

    def __repr__(self):
        return f"<Sex {self.id}: {self.sex}>"


# Define the log model
class ModificationLog(db.Model):
    __tablename__ = 'modification_log'
    id = db.Column(db.Integer, primary_key=True)
    # Timestamp of the modification
    timestamp = db.Column(db.DateTime, nullable=False)
    # Which table was modified
    table_name = db.Column(db.String, nullable=False)
    # Type of modification, e.g., 'Add' or 'Delete'
    modification_type = db.Column(db.String, nullable=False)
    # Optional description of the modification
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return (
            f"<ModificationLog {self.table_name} {self.modification_type} "
            f"at {self.timestamp}>"
        )


# Define the feedback model
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    # The timestamp when feedback is submitted (default to current UTC time)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Which chart type this feedback is about
    chart_type = db.Column(db.String, nullable=False)
    # The year associated with the chart (if applicable)
    chart_year = db.Column(db.Integer, nullable=True)
    # The feedback text provided by the user
    feedback_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return (
            f"<Feedback {self.chart_type} {self.chart_year} "
            f"at {self.timestamp}>"
        )
