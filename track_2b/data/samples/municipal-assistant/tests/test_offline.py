def test_answers_without_network(client):
    assert client.post("/ask", params={"question": "Opening hours?"}).status_code == 200
