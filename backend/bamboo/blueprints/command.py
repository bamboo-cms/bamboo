from flask import Blueprint

from bamboo.database import db

command = Blueprint("command", __name__, cli_group=None)


@command.cli.command(name="create-tables")
def create_tables() -> None:
    """Create all tables."""
    db.create_all()
    print("Tables created.")


@command.cli.command(name="drop-tables")
def drop_tables() -> None:
    """Drop all tables."""
    db.drop_all()
    print("Tables dropped.")
