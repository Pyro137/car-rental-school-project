def register(client, **overrides):
    data = {
        "full_name": "Ayse Demir",
        "email": "ayse@example.com",
        "password": "secret123",
        "role": "company",
        "company_name": "Demir Rent",
    }
    data.update(overrides)
    return client.post("/register", data=data, follow_redirects=False)


def test_register_company(client):
    response = register(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/cars"
    # Every page extends base.html, so any page shows the menu.
    assert "My fleet" in client.get("/register").text


def test_register_duplicate_email(client, make_user):
    make_user(email="ayse@example.com")
    response = register(client)
    assert response.status_code == 400
    assert "This email is already registered." in response.text


def test_register_company_without_name(client):
    response = register(client, company_name="")
    assert response.status_code == 400
    assert "Company name is required." in response.text


def test_register_short_password(client):
    response = register(client, password="short")
    assert response.status_code == 422
    assert "Invalid input" in response.text


def test_login_wrong_password(client, make_user):
    user = make_user()
    response = client.post("/login", data={"email": user.email, "password": "wrong-password"})
    assert response.status_code == 400
    assert "Wrong email or password." in response.text


def test_logout(client, make_user, login):
    login(make_user())
    assert "Log in" not in client.get("/register").text
    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert "Log in" in client.get("/register").text
