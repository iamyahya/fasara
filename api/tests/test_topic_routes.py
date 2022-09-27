from app.models import User, Topic
from app.models.topic import TopicStatus

from tests.conftest import generate_access_token


# TODO: Test actions with not TopicStatus.PUBLIC


async def test__create_draft_success(client):
    access_token = await generate_access_token(client)
    response = await client.post(
        "/topic",
        json={"text": "text"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    response_json = response.json()
    assert "status" in response_json
    assert response_json["status"] == TopicStatus.DRAFT.value
    assert response_json["text"] == "text"


async def test__create_no_auth(client):
    response = await client.post(
        "/topic",
        json={"text": "text"},
    )
    assert response.status_code == 401
    assert await Topic().count() == 0


async def test__list_empty(client):
    response = await client.get("/topic")
    response_json = response.json()
    assert "results" in response_json
    assert not len(response_json["results"])


async def test__list_filled_one(client):
    access_token = await generate_access_token(client)
    await client.post(
        "/topic",
        json={
            "text": "text",
            "status": TopicStatus.PUBLIC.value
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response = await client.get("/topic")
    response_json = response.json()
    assert response_json["results"][0]["text"] == "text"
    response = await client.get(
        "/user/topic", 
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert len(response.json().get("results")) == 1


async def test__list_filled_30(client):
    access_token = await generate_access_token(client)
    for _ in range(30):
        await client.post(
            "/topic",
            json={
                "text": "text",
                "status": TopicStatus.PUBLIC.value
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
    response = await client.get("/topic")
    response_json = response.json()
    assert response_json["total"] == 30
    assert len(response_json["results"]) == 25
    response = await client.get("/topic?page=2")
    response_json = response.json()
    assert response_json["page"] == 2
    assert len(response_json["results"]) == 5


async def test__list_search(client):
    access_token = await generate_access_token(client)
    await client.post(
        "/topic",
        json={
            "text": "text",
            "status": TopicStatus.PUBLIC.value
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response = await client.get("/topic?q=text1")
    response_json = response.json()
    assert len(response_json["results"]) == 0
    response = await client.get("/topic?q=text")
    response_json = response.json()
    assert len(response_json["results"]) == 1


async def test__update_success(client):
    access_token = await generate_access_token(client)
    response = await client.post(
        "/topic",
        json={"text": "text"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    id_ = response.json().get("id")
    response = await client.put(
        f"/topic/{id_}",
        json={
            "text": "text-updated"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response_json = response.json()
    assert response_json["text"] == "text-updated"


async def test__update_no_auth(client):
    access_token = await generate_access_token(client)
    response = await client.post(
        "/topic",
        json={"text": "text"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    id_ = response.json().get("id")
    response = await client.put(
        f"/topic/{id_}",
        json={
            "text": "text-updated"
        },
    )
    assert response.status_code == 401
    response_json = response.json()
    assert "text" not in response_json


async def test__update_after_publish(client):
    access_token = await generate_access_token(client)
    response = await client.post(
        "/topic",
        json={"text": "text", "status": TopicStatus.PUBLIC.value},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    id_ = response.json().get("id")
    response = await client.put(
        f"/topic/{id_}",
        json={
            "text": "text-updated"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404
    response_json = response.json()
    assert "text" not in response_json


async def test__delete_success(client):
    access_token = await generate_access_token(client)
    response = await client.post(
        "/topic",
        json={"text": "text", "status": TopicStatus.PUBLIC.value},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    id_ = response.json().get("id")
    response = await client.delete(
        f"/topic/{id_}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    response = await client.get("/topic")
    response_json = response.json()
    assert not len(response_json["results"])
    response = await client.get(f"/topic/{id_}")
    assert response.status_code == 404
    response = await client.get(
        "/user/topic",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert len(response.json().get("results")) == 0
    response = await client.get(
        f"/user/topic/{id_}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404


async def test__get_success(client):
    access_token = await generate_access_token(client)
    response = await client.post(
        "/topic",
        json={"text": "text", "status": TopicStatus.PUBLIC.value},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    id_ = response.json().get("id")
    response = await client.get(f"/topic/{id_}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["text"] == "text"


async def test__get_draft(client):
    access_token = await generate_access_token(client)
    response = await client.post(
        "/topic",
        json={"text": "text"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    id_ = response.json().get("id")
    response = await client.get(f"/topic/{id_}")
    assert response.status_code == 404
    response_json = response.json()
    assert "text" not in response_json
    response = await client.get(
        f"/user/topic/{id_}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response_json = response.json()
    assert "text" in response_json
