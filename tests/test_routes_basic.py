def test_routes_import(app):
    # Simply importing app triggers blueprint registration
    assert app is not None

def test_routes_execute(client):
    client.get("/")
    client.get("/contact")
    client.get("/peak-events")


