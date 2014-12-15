"""Convenience functions which interact with SQLAlchemy models."""

from sqlalchemy import func

from github_status.extensions import db


def count(column, value, glob=False):
    """Counts number of rows with value in a column. This function is case-insensitive.

    Positional arguments:
    column -- the SQLAlchemy column object to search in (e.g. Table.a_column).
    value -- the value to search for, any string.

    Keyword arguments:
    glob -- enable %globbing% search (default False).

    Returns:
    Number of rows that match. Equivalent of SELECT count(*) FROM.
    """
    query = db.session.query(func.count('*'))
    if glob:
        query = query.filter(column.ilike(value))
    else:
        query = query.filter(func.lower(column) == value.lower())
    return query.one()[0]
