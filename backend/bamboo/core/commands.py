import click
from flask import Flask

from bamboo.database import db


@click.command(name="create-tables")
def create_tables() -> None:
    """Create all tables."""
    db.create_all()
    click.echo("Tables created")


@click.command(name="drop-tables")
def drop_tables() -> None:
    """Drop all tables."""
    db.drop_all()
    click.echo("Tables dropped")


def init_app(app: Flask) -> None:
    app.cli.add_command(create_tables)
    app.cli.add_command(drop_tables)
