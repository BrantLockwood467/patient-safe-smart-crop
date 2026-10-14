import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from smart_crop_service import InfraiClient, PatientImage, crop_for_notification, notification_decision


def test_unapproved_asset_is_held_before_api_call():
    image = PatientImage(image_id="img-42", alt_text="Appointment", approved=False)
    assert notification_decision(image) == "hold_for_review"


def test_approved_asset_with_alt_text_can_be_sent():
    image = PatientImage(image_id="img-43", alt_text="Appointment reminder")
    assert notification_decision(image) == "send"


def test_structured_image_reference_reaches_request_boundary():
    client = InfraiClient(api_key="test-key")
    captured = {}

    def capture(method, path, payload):
        captured.update(payload)
        return {"crop": "ok"}

    client._request = capture
    image = PatientImage(image_id={"image_id": "img-43"}, alt_text="Appointment reminder")
    result = crop_for_notification(client, image, "1:1")

    assert captured == {"image": {"image_id": "img-43"}, "aspect": "1:1"}
    assert result["status"] == "ready"
