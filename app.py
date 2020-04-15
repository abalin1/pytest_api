from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': 'Test title 1',
        'description': 'test description 1',
        'done': False
    },
    {
        'id': 2,
        'title': 'Test title 2',
        'description': 'test description 2',
        'done': False
    }
]


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


# auth
auth = HTTPBasicAuth()

users = {
    'john': 'doe',
    'sue': 'mcdowel'
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        if users[username] == password:
            return username, password
    return False
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
@auth.login_required
def index():
    return 'Hello, dolly'

@app.route('/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    #return jsonify({'tasks': list(map(make_public_task, tasks))})
    return jsonify({'tasks': tasks})


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    print(task)
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/tasks/add', methods=['POST'])
#@auth.login_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
