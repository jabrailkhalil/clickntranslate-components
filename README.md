# ClicknTranslate components

Verified optional engine runtimes and model manifests for [ClicknTranslate](https://github.com/jabrailkhalil/clickntranslate).

Install and update components from **Language packages** inside the application. Application downloads remain in the main project's releases.

## Publication

- `public/metadata/`: signed TUF metadata. The application embeds the initial public root.
- `public/targets/`: authenticated compatibility catalogs.
- Releases: immutable, prepared runtime archives. Models can retain their original pinned upstream URL and digest.
- `recipes/`: maintainer inputs and exact dependency locks.
- `scripts/`: publisher and upstream discovery. Root/targets private keys are never stored here or uploaded to CI.

The Windows x64 stable catalog now contains five tested component packages. This publication does not release or update the ClicknTranslate application itself. It is available to compatible component-aware clients, including the signed Windows test build from commit `193dff1`. The older RapidOCR preview profiles remain available.

| Component | Published Windows runtime |
| --- | --- |
| RapidOCR | 3.10.0 with explicit PP-OCRv5 models |
| Tesseract | 5.5.3, source-built PNG/TSV executable |
| EasyOCR | 1.7.2 with CPU Torch 2.14.1 and 14 model families |
| Argos | 1.11.0 with pinned EN↔RU / EN↔AR directions |
| Hy-MT | HY-MT1.5-1.8B Q4_K_M with llama.cpp b11899 |

Tesseract is compiled from pinned Tesseract, Leptonica, libpng and zlib sources. It includes format configs required by fullscreen TSV recognition. Its native executable imports only Windows system libraries; the older candidate with a third-party DLL closure is not published. Corresponding source archives and the build recipe accompany its component Release. Recognition models remain separate selected downloads.

Python-based runtimes use private interpreters and pinned wheels. Original vendor licenses/notices and Microsoft runtime terms are retained; publication adds notices without changing the previously tested code or DLLs. All final archives are hash-verified and natively validated. Prepared candidates are never promoted automatically, and published runtime bytes are never overwritten.

Argos uses the application's sentence splitter without Torch/Stanza/SpaCy. Hy-MT's runner and 1.13 GB GGUF model are separate authenticated objects, so runner updates reuse an unchanged model. EasyOCR preserves its original shared model families and validates each selected recognizer before activation. Removal, cancellation, rollback and selected-model preservation use the same transactional store for all engines.

[Publication verification](verification/windows-publication-20261026/approval.json) and [frozen client checks](verification/windows-publication-20261026/frozen-client.json) record the final hashes, cold installation from actual public runtime/model URLs, real inference through all five engines and production module equality with the delivered Windows test build. The isolated QA executable changes only the explicit smoke-test harness. No native engine SDK is imported into the Qt process. UI checks use Qt offscreen with Windows fonts.

[Earlier candidate verification](verification/all-engines-windows-20261026.json) retains preparation history, 355 source tests, 72 rendered UI states, lifecycle tests and exact OCR samples. Synthetic OCR checks establish runtime viability and do not guarantee accuracy on every image. macOS/Linux candidates remain separate from this Windows publication.

## Maintenance

Daily automation refreshes short-lived snapshot/timestamp metadata using restricted online keys. Approval of a new catalog requires the author's targets key. Targets approval expires after 90 days and must be renewed by the maintainer; refresh automation fails visibly before it can serve an expired approval.

Upstream discovery produces a report; it never silently publishes untested dependencies or models. Runtime recipes must be prepared and tested natively for each OS/architecture. A Python virtual environment copied from a development machine is not a portable runtime.

Discovery reads the prepared recipe pins and watches the Windows CPU `bNNNN` llama.cpp track and the Hy-MT model repository revision. Unrelated stable tags or rolling builds without a Windows CPU archive are not reported as ready. A failed source is shown as unavailable; other source results are retained and the workflow fails visibly, with its partial report attached.

No secrets, user API keys, OCR text, histories or private signing certificates belong in this repository.
