from uuid import uuid4
from datetime import datetime

from app.models import User, Invite


async def test__sign_up_first_user(client, userform):
    userform.update({
        "code": str(uuid4())
    })
    response = await client.post("/sign-up", json=userform)
    assert response.status_code == 200
    response_json = response.json()
    assert await User().count() == 1
    assert await Invite(from_id=1).count() == 1
    assert await Invite(to_id=1).count() == 1
    assert await Invite().count() == 2


async def test__sign_up_first_user_no_code(client, userform):
    response = await client.post("/sign-up", json=userform)
    assert response.status_code == 200
    assert await User().count() == 1


async def test__sign_up_only_first_without_code(client, userform):
    await client.post("/sign-up", json=userform)
    assert await User().count() == 1
    response = await client.post("/sign-up", json=userform)
    assert response.status_code == 422
    assert await User().count() == 1
    userform.update({
        "code": str(uuid4())
    })
    response = await client.post("/sign-up", json=userform)
    assert response.status_code == 422
    assert await User().count() == 1


async def test__sign_up_username_not_unique(client, userform):
    await client.post("/sign-up", json=userform)
    response = await client.post("/sign-in", data=userform)
    access_token = response.json().get("access_token")
    invite = await Invite(from_id=1).one()
    invite.created_at = datetime.utcnow()
    await invite.save()
    response = await client.get("/user/invite", headers={
        "Authorization": f"Bearer {access_token}"
    })
    userform.update({
        "code": response.json().get("results").pop().get("code")
    })
    response = await client.post("/sign-up", json=userform)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Username already used"


async def test__sign_in_success(client, userform):
    await client.post("/sign-up", json=userform)
    response = await client.post("/sign-in", data=userform)
    assert response.status_code == 200


async def test__sign_in_not_success(client, userform):
    await client.post("/sign-up", json=userform)
    userform.update({
        "password": "worng-password"
    })
    response = await client.post("/sign-in", data=userform)
    assert response.status_code == 422


async def test__me_without_token(client):
    response = await client.get("/user")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


async def test__me_fake_token(client):
    response = await client.get("/user", headers={
        "Authorization": f"Bearer tokenlikestring.FfTW1i8_gxKVqi3Iv1QlhwXFEhpO_XYb5HCmJLbVJXo"
    })
    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"


async def test__me_success(client, userform):
    await client.post("/sign-up", json=userform)
    response = await client.post("/sign-in", data=userform)
    access_token = response.json().get("access_token")
    assert access_token is not None
    response = await client.get("/user", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    assert "username" in response.json()


async def test__invites_count_after_signup(client, userform):
    assert await Invite().count() == 0
    await client.post("/sign-up", json=userform)
    response = await client.post("/sign-in", data=userform)
    assert await Invite(from_id=1).count() == 1
    access_token = response.json().get("access_token")
    response = await client.get("/user/invite", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert not len(response.json().get("results"))
    invite = await Invite(from_id=1).one()
    invite.created_at = datetime.utcnow()
    await invite.save()
    response = await client.get("/user/invite", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert len(response.json().get("results")) == 1


async def test__sign_up_reuse_code(client, userform):
    await client.post("/sign-up", json=userform)
    response = await client.post("/sign-in", data=userform)
    access_token = response.json().get("access_token")
    invite = await Invite(from_id=1).one()
    invite.created_at = datetime.utcnow()
    await invite.save()
    response = await client.get("/user/invite", headers={
        "Authorization": f"Bearer {access_token}"
    })
    userform.update({
        "username": "newusername",
        "code": response.json().get("results").pop().get("code")
    })
    await client.post("/sign-up", json=userform)
    response = await client.post("/sign-up", json=userform)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Invite already used"


async def test__invite_is_used_after_use(client, userform):
    await client.post("/sign-up", json=userform)
    response = await client.post("/sign-in", data=userform)
    access_token = response.json().get("access_token")
    invite = await Invite(from_id=1).one()
    invite.created_at = datetime.utcnow()
    await invite.save()
    response = await client.get("/user/invite", headers={
        "Authorization": f"Bearer {access_token}"
    })
    userform.update({
        "username": "newusername",
        "code": response.json().get("results").pop().get("code")
    })
    await client.post("/sign-up", json=userform)
    response = await client.get("/user/invite", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.json().get("results").pop().get("used") == True
