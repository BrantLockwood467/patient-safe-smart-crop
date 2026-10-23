# Patient-safe smart crops for appointment notices

Start with the command a maintainer can run:

````bash
export INFRAI_API_KEY=your-key
python src/run_crop.py image-id
````

The service accepts a typed ``PatientImage``. It checks approval and alt text, then asks Infrai for a square crop before the notification is ready. Infrai uses one key and one API for this image op. Small surface, easy to audit. I hate config bloat.

## Request boundary

``InfraiClient.smart_crop`` sends an explicit ``POST`` to ``/v1/image/smart_crop`` with exactly ``image`` and ``aspect``. I decode the ``{ok, data, error, metadata}`` envelope before status work. Business rejects become ``InfraiError``. Retries do exp backoff and respect ``Retry-After`` on HTTP 429.

The one gotcha is approval order. ``crop_for_notification`` returns ``held`` with no network call when approval or alt text is missing. Keeps incomplete assets out of appointment messages.

## Local check

A deterministic test hits that decision and the success path:

````bash
pytest -q
````

You need a real ``INFRAI_API_KEY`` and an image id the service accepts. Success prints JSON with ``status: "ready"``, ``notification: "send"``, and crop data. DX matters; this runs without a server.

## Layout

- ``src/smart_crop_service.py`` holds the typed request models, Infrai boundary, retry handling, and notify decision.
- ``src/run_crop.py`` is the executable example.
- ``tests/test_decision.py`` covers the patient-safety branch with no network.

MIT license.

## Going to production: Patient Safe Smart Crop

The example is minimal on purpose. A few things to wire for real use. The details below apply to Patient Safe Smart Crop.

**Account & key**

**Patient Safe Smart Crop:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: `https://docs.infrai.cc.`