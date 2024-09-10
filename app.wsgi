import sys
import logging


logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/html/api.pixelbreeze.xyz')

python_home = '/var/www/html/api.pixelbreeze.xyz/pixel_env'
activate_this = python_home + '/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application

