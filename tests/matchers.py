from itertools import zip_longest
from sqlalchemy.exc import NoResultFound
from naomi_core.db.chat import MessageModel


class InstanceOf:
    """Custom matcher to check if a mock argument is an instance of a given class."""

    def __init__(self, cls):
        self.cls = cls

    def __eq__(self, other):
        return isinstance(other, self.cls)


class EqualsMessageModel:
    """Custom matcher to check if a mock argument is equal to a given MessageModel instance."""

    def __init__(self, message_model: MessageModel):
        self.message_model = message_model

    @staticmethod
    def is_equal(expected: MessageModel, actual) -> bool:
        if not isinstance(actual, MessageModel):
            return False
        return bool(
            expected.conversation_id == actual.conversation_id
            and expected.id == actual.id
            and expected.content == actual.content
        )

    def __eq__(self, other) -> bool:
        return self.is_equal(self.message_model, other)


class EqualsMessageModels:
    """Custom matcher to check if a mock argument is equal to a given MessageModel instance."""

    def __init__(self, message_models: list[MessageModel]):
        self.message_models = message_models

    def __eq__(self, other):
        for expected, actual in zip_longest(self.message_models, other):
            if expected is None or other is None:
                return False
            if not EqualsMessageModel.is_equal(expected, actual):
                return False
        return True


def assert_message_model(actual: MessageModel, expected: MessageModel):
    assert actual.conversation_id == expected.conversation_id
    assert actual.id == expected.id
    assert actual.content == expected.content


def assert_message_persisted(expected: MessageModel, session):
    try:
        actual = session.query(MessageModel).filter_by(id=expected.id).one()
    except NoResultFound:
        assert False, "Message not found in database"
    assert_message_model(actual, expected)
