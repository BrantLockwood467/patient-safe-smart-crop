import json
import sys

from smart_crop_service import InfraiClient, PatientImage, crop_for_notification


def main() -> None:
    image_id = sys.argv[1] if len(sys.argv) > 1 else "uploaded-image-id"
    if image_id.startswith("{"):
        image_id = json.loads(image_id)
        if not isinstance(image_id, dict):
            raise ValueError("image reference must be a JSON object")
    image = PatientImage(image_id=image_id, alt_text="Clinic appointment reminder")
    output = crop_for_notification(InfraiClient(), image, "1:1")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
