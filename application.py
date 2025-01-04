"""

"""

import sys
from app import create_app

path = "/home/Mushfique/read-my-mind"
if path not in sys.path:
    sys.path.insert(0, path)

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
