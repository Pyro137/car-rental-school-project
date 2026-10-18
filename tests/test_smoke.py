def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_factories(make_user, make_car):
    car = make_car(make_user("company"))
    assert car.is_active
