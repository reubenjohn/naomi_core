from naomi_core.db.webhook import WebhookEvent


def test_webhook_event_model(db_session):
    # Create a new event
    event = WebhookEvent(event_type="test_event", payload='{"key": "value"}', status="pending")
    db_session.add(event)
    db_session.commit()

    # Verify event was saved correctly
    saved_event = db_session.query(WebhookEvent).filter_by(event_type="test_event").one()
    assert saved_event.payload == '{"key": "value"}'
    assert saved_event.status == "pending"

    # Update event status
    saved_event.status = "processed"
    db_session.commit()

    # Verify update
    updated_event = db_session.query(WebhookEvent).filter_by(event_type="test_event").one()
    assert updated_event.status == "processed"
