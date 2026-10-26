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

Tesseract Windows has a pinned **candidate recipe** and a manual native-validation workflow. Candidate artifacts are not published to the trusted catalog automatically. Tesseract language files remain separate: the application downloads only selected languages and preserves them across engine updates. Public promotion requires the native/frozen checks and the bundled DLL license/source inventory.

Argos Windows has a private-runtime **candidate** and four pinned EN↔RU/EN↔AR model directions. Its manual workflow checks real translation, the English pivot, streaming, update preservation, offline removal, cancellation and rollback. It uses the application sentence splitter without Torch/Stanza/SpaCy. Original model archives retain upstream notices.

New RapidOCR/Argos candidates include pinned Microsoft runtime files and audit native imports instead of depending on the developer's global Visual C++ installation. Candidate locks and CI artifacts do not approve publication: redistribution review and frozen-application checks remain explicit gates. Published runtime assets and the existing catalog are never overwritten by preparation.

Hy-MT Windows has a native **candidate** with a separately authenticated GGUF model, its matching license/document revision, and a curated llama.cpp CPU runner. The manual workflow compares b9048 and b11899 using the same model, verifies loaded private DLL paths and tests update without another model download, rollback, cancellation, invalid GGUF rejection and removal while a worker holds a lease. Candidate preparation does not publish a new model or runtime.

## Maintenance

Daily automation refreshes short-lived snapshot/timestamp metadata using restricted online keys. Approval of a new catalog requires the author's targets key. Targets approval expires after 90 days and must be renewed by the maintainer; refresh automation fails visibly before it can serve an expired approval.

Upstream discovery produces a report; it never silently publishes untested dependencies or models. Runtime recipes must be prepared and tested natively for each OS/architecture. A Python virtual environment copied from a development machine is not a portable runtime.

Discovery reads the prepared recipe pins and watches the Windows CPU `bNNNN` llama.cpp track and the Hy-MT model repository revision. Unrelated stable tags or rolling builds without a Windows CPU archive are not reported as ready. A failed source is shown as unavailable; other source results are retained and the workflow fails visibly, with its partial report attached.

No secrets, user API keys, OCR text, histories or private signing certificates belong in this repository.
