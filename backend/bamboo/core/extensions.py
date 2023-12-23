from flask_migrate import Migrate
from flask_rq2 import RQ
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
rq = RQ()
