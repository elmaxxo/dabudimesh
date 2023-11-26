from dabudimesh.message import Message


def test_message():
    msg = Message("message", "1000", "2000", {"text": "Message to 2000"})

    assert Message.decode(msg.encode()) == msg
