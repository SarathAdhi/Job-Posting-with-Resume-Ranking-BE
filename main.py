from application import app

from flask_cors import CORS

from views import *


# middleware
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
