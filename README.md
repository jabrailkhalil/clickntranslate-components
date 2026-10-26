# ClicknTranslate components

Verified optional engine runtimes and model manifests for [ClicknTranslate](https://github.com/jabrailkhalil/clickntranslate).

Install and update components from **Language packages** inside the application. Application downloads remain in the main project's releases.

## Publication

- `public/metadata/`: signed TUF metadata. The application embeds the initial public root.
- `public/targets/`: authenticated compatibility catalogs.
- Releases: immutable, prepared runtime archives. Models can retain their original pinned upstream URL and digest.
- `recipes/`: maintainer inputs and exact dependency locks.
- `scripts/`: publisher and upstream discovery. Root/targets private keys are never stored here or uploaded to CI.

The initial Windows x64 RapidOCR runtime is a **preview**. It is tested separately from the application and does not declare frozen-app, macOS or Linux validation complete. The stable channel remains empty until those release checks are completed. Existing installed engines continue to work.

## Maintenance

Daily automation refreshes short-lived snapshot/timestamp metadata using restricted online keys. Approval of a new catalog requires the author's targets key. Targets approval expires after 90 days and must be renewed by the maintainer; refresh automation fails visibly before it can serve an expired approval.

Upstream discovery produces a report; it never silently publishes untested dependencies or models. Runtime recipes must be prepared and tested natively for each OS/architecture. A Python virtual environment copied from a development machine is not a portable runtime.

No secrets, user API keys, OCR text, histories or private signing certificates belong in this repository.
