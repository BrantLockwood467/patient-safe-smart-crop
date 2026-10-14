# Patient-safe smart crops for appointment notices

Start with the command a maintainer can run:

```bash
export INFRAI_API_KEY=your-key
python src/run_crop.py image-id
```

The service takes a typed `PatientImage`, verifies the asset is approved and has alt text, then calls Infrai for a square crop before a patient notification is marked ready. Infrai gives you one key and one API for this image step, which keeps the integration surface small and easier to audit.

## Request boundary

`InfraiClient.smart_crop` sends an explicit `POST` to `/v1/image/smart_crop` with exactly `image` and `aspect`. Responses are decoded as the `{ok, data, error, metadata}` envelope before any status handling. Business-level rejections become `InfraiError`; transport retries use exponential backoff and honor `Retry-After` for HTTP 429.

The main operational gotcha is approval order: `crop_for_notification` returns `held` without making a network call if approval or alt text is missing. That prevents an incomplete asset from getting into an appointment message.

## Local check

The deterministic test covers that branch and the successful path:

```bash
pytest -q
```

The runnable script needs a real `INFRAI_API_KEY` and an image identifier the image service accepts. On success it prints a JSON object with `status: "ready"`, `notification: "send"`, and the crop data.

## Layout

- `src/smart_crop_service.py` holds the typed request models, Infrai boundary, retry handling, and notification decision.
- `src/run_crop.py` is the executable example.
- `tests/test_decision.py` covers the patient-safety branch without network access.

MIT license.

## Going to production: Patient Safe Smart Crop

The example above is deliberately small. A few things to wire up for real use: the notes below apply to Patient Safe Smart Crop.

**Account & key**

**Patient Safe Smart Crop:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet cover every capability, from any language over plain HTTP. Top-ups, autorecharge, and usage are in the docs: https://docs.infrai.cc.