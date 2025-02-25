from python_template.sanity import sanity_check
import pytest  # type: ignore[import]


def test_entity_creation():
    with pytest.raises(ValueError, match="Sanity check"):
        sanity_check()
