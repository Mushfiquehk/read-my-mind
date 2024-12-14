import sys
path = '/home/Mushfique/read-my-mind'
if path not in sys.path:
   sys.path.insert(0, path)

from flask_app import app as application


if __name__ == "__main__":
    application.run(debug=False)
    