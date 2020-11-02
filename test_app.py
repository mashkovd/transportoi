from app import app as app


# Is apidocs working?
def test_apidocs():
    res = app.test_client().get('/apidocs/')
    assert res.status_code == 200


# Is links working?
def test_links():
    res = app.test_client().get('/link')
    assert res.status_code == 200
    assert isinstance(res.json, list)


# Is add short link working?
def test_post():
    res = app.test_client().post(
        '/long_to_short',
        json={"long_link": 'https://yandex.ru/news/?clid=1955454&win=368'},
        content_type='application/json',
    )

    assert res.status_code == 200
    assert isinstance(res.json, dict)
    assert res.json.get('short_link').split('/')[-1:][0] == 'ce762c9569'


# Is redirect working?
def test_redirect():
    res = app.test_client().get('/ce762c9569')
    assert res.status_code == 302


# Is statistics working?
def test_statistics():
    res = app.test_client().get('statistics/ce762c9569')
    assert res.status_code == 200
    assert isinstance(res.json, dict)
    assert isinstance(res.json.get('count'), int)
