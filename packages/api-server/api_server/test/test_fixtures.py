import asyncio
import inspect
import os
import os.path
import time
import unittest
import unittest.mock
from typing import Awaitable, Callable, Optional, TypeVar, Union
from uuid import uuid4

from api_server.app import app, on_sio_connect

from .mocks import patch_sio
from .test_client import client

T = TypeVar("T")


def try_until(
    action: Callable[[], T],
    predicate: Callable[[T], bool],
    timeout=5,
    interval=0.5,
) -> T:
    """
    Do action until an expected result is received.
    Returns the last result.
    """
    end_time = time.time() + timeout

    result = action()
    success = predicate(result)
    if success:
        return result

    time.sleep(interval)
    while time.time() < end_time:
        try:
            result = action()
            success = predicate(result)
            if success:
                return result
        except Exception:  # pylint: disable=broad-except
            pass
        time.sleep(interval)
    return result


async def async_try_until(
    action: Callable[[], Awaitable[T]],
    predicate: Union[Callable[[T], Awaitable[bool]], Callable[[T], bool]],
    timeout=5,
    interval=0.5,
) -> T:
    """
    Do action until an expected result is received.
    Returns the last result, or throws if the last result raises an exception.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            result = await action()
            success = predicate(result)
            if inspect.isawaitable(success):
                success = await success
            if success:
                return result
        except Exception:  # pylint: disable=broad-except
            pass
        await asyncio.sleep(interval)
    return await action()


here = os.path.dirname(__file__)
with open(f"{here}/../../scripts/test.key", "br") as f:
    jwt_key = f.read()


class AppFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = client()
        cls.client.set_user("admin")

    def subscribe_sio(self, room: str, *, user="admin"):
        """
        Subscribes to a socketio room and return a generator of messages
        Returns a tuple of (success: bool, messages: Any).
        """

        def impl():
            with patch_sio() as mock_sio:
                msgs = []
                condition = asyncio.Condition()

                async def handle_resp(emit_room, msg, *_args, **_kwargs):
                    if emit_room == "subscribe" and not msg["success"]:
                        raise Exception("Failed to subscribe")
                    if emit_room == room:
                        async with condition:
                            msgs.append(msg)
                            condition.notify()

                mock_sio.emit.side_effect = handle_resp

                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    on_sio_connect("test", {}, {"token": self.client.token(user)})
                )
                # pylint: disable=protected-access
                loop.run_until_complete(app._on_subscribe("test", {"room": room}))

                yield

                async def wait_for_msgs():
                    async with condition:
                        if len(msgs) == 0:
                            await condition.wait()
                        return msgs.pop(0)

                try:
                    while True:
                        yield loop.run_until_complete(
                            asyncio.wait_for(wait_for_msgs(), 5)
                        )
                finally:
                    loop.run_until_complete(app._on_disconnect("test"))

        gen = impl()
        next(gen)
        return gen

    def setUp(self):
        self.test_time = 0

    def create_user(self, admin: bool = False):
        username = f"user_{uuid4().hex}"
        resp = self.client.post(
            "/admin/users",
            json={"username": username, "is_admin": admin},
        )
        self.assertEqual(200, resp.status_code)
        return username

    def create_role(self):
        role_name = f"role_{uuid4().hex}"
        resp = self.client.post("/admin/roles", json={"name": role_name})
        self.assertEqual(200, resp.status_code)
        return role_name

    def add_permission(self, role: str, action: str, authz_grp: Optional[str] = ""):
        resp = self.client.post(
            f"/admin/roles/{role}/permissions",
            json={"action": action, "authz_grp": authz_grp},
        )
        self.assertEqual(200, resp.status_code)

    def assign_role(self, username: str, role: str):
        resp = self.client.post(f"/admin/users/{username}/roles", json={"name": role})
        self.assertEqual(200, resp.status_code)

    def now(self) -> int:
        """
        Returns the current time in the testing clock in unix millis.
        """
        return self.test_time
