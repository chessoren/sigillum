def test_answers_without_network(client):
    assert client.post("/ask", params={"question": "Öffnungszeiten?"}).status_code == 200
