import requests
import pytest
from requests.auth import HTTPBasicAuth

url = 'http://127.0.0.1:5000/'
datakeys = ['description', 'done', 'id', 'title']
username = 'john'
password = 'doe'

tdata = [
    ((username, 'no'), 401),
    (('no', password), 401),
    ((username, password), 200)]


class Request:
    def get(self, urld=None, user=username, passwd=password):
        response = requests.get('{}{}'.format(url, urld), auth=HTTPBasicAuth(user, passwd))
        return response

    def post(self, **kwargs):
        response = requests.post(url + 'tasks/add', json=kwargs)
        return response

    def delete(self, id1):
        response = requests.delete(url + 'tasks/{}'.format(id1), auth=HTTPBasicAuth(username, password))
        return response


@pytest.fixture()
def request_cls():
    return Request()


@pytest.fixture()
def get_ids_to_delete(request_cls):
    def delete_ids(post_key, post_value, gen_data=False):
        if gen_data:
            for i in range(5):
                response = request_cls.post(title=post_key, description=post_value)
                assert response.status_code == 201
        response = request_cls.get('tasks')
        resp = response.json().get('tasks')
        # getting ids with data to delete
        idnums = [i['id'] for i in resp if i[post_key] == post_value]
        if idnums:
            return idnums
        else: pytest.skip("No ids to delete, dude")
    return delete_ids


def test_0_clean_data(request_cls, get_ids_to_delete):
    idlist = get_ids_to_delete('title', 'post testing')
    for id1 in idlist:
        response = request_cls.delete(id1)
        assert response.status_code == 200


@pytest.mark.parametrize('authd, code', tdata)
def test_1_access_check(authd, code, request_cls):
    response = request_cls.get('', authd[0], authd[1])
    assert response.status_code == code
    if code == 401:
        assert response.json().get('error') == 'Unauthorized access'
    elif code == 200:
        assert response.text == 'Hello, dolly'
        assert not response.is_redirect
        assert response.headers['Server'] == 'Werkzeug/1.0.1 Python/3.7.7'


def test_2_get_one(request_cls):
    response = request_cls.get('tasks/1')
    assert response.status_code == 200
    resp = response.json().get('task')
    assert datakeys == list(resp.keys())
    assert resp['title'] == 'Test title 1'
    for k, v in resp.items():
        if k == 'done': assert not v
        else: assert v


def test_3_get_all(request_cls):
    response = request_cls.get('tasks')
    resp = response.json().get('tasks')
    assert response.status_code == 200
    assert len(resp) >= 2


def test_4_post_data(request_cls):
    post_title = 'post testing'
    title_descr = 'post request test'
    response = request_cls.post(title=post_title, description=title_descr)
    assert response.status_code == 201
    idd = response.json().get('task')['id']
    print(idd)
    # put new id to get data request
    response = request_cls.get('tasks/{}'.format(idd))
    assert response.status_code == 200
    #print(response.json())
    resp = response.json().get('task')['title']
    assert resp == post_title


def test_5_exception():
    with pytest.raises(TypeError):
        response = requests.post()


def test_6_delete_data(request_cls, get_ids_to_delete):
    idlist = get_ids_to_delete('description', 'test delete descr', True)
    for id1 in idlist:
        response = request_cls.delete(id1)
        assert response.status_code == 200
