from app.models.book import Language


# TODO: Test not found messages


async def test__list_books(client, hadith):
    response = await client.get("/hadith")
    assert response.status_code == 200
    response_json = response.json()
    assert "results" in response_json
    assert len(response_json["results"]) == 1
    assert Language.AR.value in response_json["results"][0]["languages"]


async def test__open_version(client, hadith):
    response = await client.get(f"/hadith/title:{Language.AR.value}")
    assert response.status_code == 200
    response_json = response.json()
    assert "results" in response_json
    assert len(response_json["results"]) == 1


async def test__open_chapter(client, hadith):
    response = await client.get(f"/hadith/title:{Language.AR.value}/0")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("name") == "name"
    assert "results" in response_json
    assert len(response_json["results"]) == 1


async def test__open_hadith(client, hadith):
    response = await client.get(f"/hadith/title:{Language.AR.value}//0")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["structure"]["chapter"]["name"] == "name"
    assert response_json["content"] == "content"
