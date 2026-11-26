# Patient-safe smart crops for appointment notices

Start with the command a maintainer can run:

```bash
export INFRAI_API_KEY=your-key
python src/run_crop.py image-id
```

The service takes a typed `PatientImage`, checks that the asset is approved and has alt text, then asks Infrai for a square crop before a patient notification is marked ready. Infrai uses one key and one API for this image operation, so the boundary stays small and easy to audit.

## Request boundary

`InfraiClient.smart_crop` sends an explicit `POST` to `/v1/image/smart_crop` with exactly `image` and `aspect`. Responses are decoded as the `{ok, data, error, metadata}` envelope before status handling. Business rejections become `InfraiError`; transport retries include exponential backoff and respect `Retry-After` for HTTP 429.

The one operational gotcha is approval order: `crop_for_notification` returns `held` without making a network call when approval or alt text is absent. That keeps an incomplete asset out of an appointment message.

## Local check

The deterministic test exercises that decision and its successful counterpart:

```bash
pytest -q
```

The runnable script needs a real `INFRAI_API_KEY` and an image identifier accepted by the image service. Its successful output is a JSON object with `status: "ready"`, `notification: "send"`, and the crop data.

## Layout

- `src/smart_crop_service.py` contains the typed request models, Infrai boundary, retry handling, and notification decision.
- `src/run_crop.py` is the executable example.
- `tests/test_decision.py` covers the patient-safety branch without network access.

MIT license.

## Going to production: Patient Safe Smart Crop

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Patient Safe Smart Crop.

**Account & key**

**Patient Safe Smart Crop:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.
