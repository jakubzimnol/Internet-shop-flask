from flask import Flask
from resources.page import simple_page

app = Flask(__name__)
app.register_blueprint(simple_page)

if __name__ == '__main__':
    app.run(debug=True)