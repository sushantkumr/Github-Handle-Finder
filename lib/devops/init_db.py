import os
import sys
from datetime import datetime

sys.path.append(os.getcwd())

from lib.core.config import get_config # noqa
from lib.models import db # noqa
from lib.models.users import User # noqa
from lib.models.searched_results import SearchResults # noqa


try:
    os.remove(get_config()['connection_string'][10:])
except:  # noqa
    # If it doesn't exist already
    pass

db.init_db()
