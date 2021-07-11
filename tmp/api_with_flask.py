import flask
from flask import jsonify, request
from flask import render_template


app = flask.Flask(__name__)
app.config["DEBUG"] = True

# test data
aladdin = {
    "id":1,
    "Leader":"Tony",
    "nickname":"iron man",
    "nationality":"American",
    "gender":"M",
    "superpower":"n"
}

elpis = {
    "id":2,
    "Leader":"Peter",
    "nickname":"spider man",
    "nationality":"American",
    "gender":"M",
    "superpower":"y"
}

lapras = {
    "id":3,
    "Leader":"Natasha",
    "nickname":"Block Widow",
    "nationality":"Russia",
    "gender":"F",
    "superpower":"n"
}

avengers =[aladdin, elpis, lapras]


@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello, I am here !</h1>"


@app.route('/template', methods=['GET'])
def template_home():
    return render_template('upload_sample.txt')


@app.route('/get/avengers/all', methods=['GET'])
def avengers_all():
    return jsonify(avengers)


@app.route('/get/avengers', methods=['GET'])
def avengers_properties():
    results = []
    nationality = ""
    if 'nationality' in request.args:
        nationality = request.args['nationality']
    else:
        print("no hero")    

    for avenger in avengers:
        if avenger['nationality'] == nationality:
            results.append(avenger)

    return jsonify(results)


@app.route('/post/avengers', methods=['POST'])
def create_avengers():
    request_data = request.get_json()
    leader = request_data['Leader']
    gender = request_data['gender']
    new_avenger = {
        "Leader": leader, 
        "gender": gender, 
    }
    avengers.append(new_avenger)
    return jsonify(new_avenger)


def init_api():
    app.run(debug=False, use_reloader=False)


if __name__ == '__main__':
    init_api()
