from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
import json

app = Flask("__main__", static_url_path='/static')
CORS(app)

@app.route("/")
def my_index():
    return render_template("index.html", flask_token="Hello world")

@app.route('/back/nextWater', methods=['GET'])
def nextWater():
    lastWater = 1584416537
    timeBetweenWatering = 50

    waterNext = lastWater + (timeBetweenWatering * 60)

    response = json.dumps({"nextWater": waterNext})
    return Response(response = response, status = 200, mimetype = "application/json")

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', threaded = True)
        while True: # run so that when the program is interrupted, the sensors thread can be stopped
            None
    except KeyboardInterrupt:
        None