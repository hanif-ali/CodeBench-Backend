from flask import Flask, jsonify
from models import db

app = Flask(__name__)
app.config['SECRET_KEY']='thisissecretkey'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)


@app.route("/", methods=["GET"])
def root():
    return jsonify(name="hanif")

if __name__=="__main___":
    app.run()