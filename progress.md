# Progress

**Last updated:** 2026-11-25

## Repository setup

- Added a root `.gitignore` rule to exclude `templates/` from version control.
- Configured the `origin` remote and this repository's Git author identity.
- Verified `templates/` is ignored and not staged.
- The GitHub host rejected access because this environment has no accepted Git
  credentials; pushing is pending authentication.

## Completed

- Reviewed the project brief in [main_draft.md](./main_draft.md) and the
  guidance in [AGENTS/](./AGENTS/).
- Confirmed the workspace had no dataset assets.
- Created a metadata-only dataset source inventory at
  [pairs/datasets/README.md](./pairs/datasets/README.md).
- Shortlisted CORD v2 as the closest public Indonesian-language image dataset,
  while recording its receipt-only limitation and license.
- Recorded auxiliary layout/table benchmarks and sources requiring further
  license, provenance, privacy, or size review.
- Did not download or copy any dataset files.

## Current scope and constraints

- Initial dataset interest: general Indonesian scanned documents.
- Handwriting is excluded from the initial benchmark.
- Public datasets only; keep data local and verify rights and provenance.
- The project brief targets a small 20–30 document benchmark and an offline
  Windows prototype with CPU-only operation.
- No broad public Indonesian scanned-document dataset with image-level OCR
  and layout ground truth has been verified so far.

## Next

- Push the local commit to GitHub after valid authentication is available.
- Decide whether receipt-specific CORD is acceptable for the first local
  experiment, or whether to investigate a narrower document type.
- Confirm dataset permissions and sample selection before acquiring any files.
- Update this log whenever a project milestone is completed.
