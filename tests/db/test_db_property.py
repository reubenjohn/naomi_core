from naomi_core.db.property import PropertyModel


def test_property_model(db_session):
    # Create a new property
    prop = PropertyModel(key="testKey", value="testValue")
    db_session.add(prop)
    db_session.commit()

    # Verify property was saved correctly
    saved_prop = db_session.query(PropertyModel).filter_by(key="testKey").one()
    assert saved_prop.value == "testValue"

    # Update property
    saved_prop.value = "updatedValue"
    db_session.commit()

    # Verify update
    updated_prop = db_session.query(PropertyModel).filter_by(key="testKey").one()
    assert updated_prop.value == "updatedValue"
