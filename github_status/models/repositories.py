"""Holds all metadata for each GitHub repository being tracked."""

from sqlalchemy import Column, Integer, String, Text

from github_status.extensions import db


class Repository(db.Model):
    """Holds all metadata for each GitHub repository being tracked."""

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    url = Column(String(255), unique=True, nullable=False)
    line_count = Column(Integer)
    top_committers = Column(String(255))
    last_commit = Column(Text)
