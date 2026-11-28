# Progress

**Last updated:** 2026-11-26

## Government document scraper

- Reviewed `scripts/scraper.py`; added domain-limited redirect handling,
  HTTPS-downgrade rejection, robots checks on redirect targets, fail-closed
  handling for unavailable/unexpected robots responses, and CLI input checks.
- Added four unit tests for redirect scope, HTTPS downgrade, and robots
  enforcement.
- All four unit tests pass; Pylance reports no syntax errors or diagnostics
  for the scraper or its tests.
- A crawl of BPK-hosted detail pages was skipped because the scraper could not
  obtain an allowed robots decision from that host; it did not attempt to
  bypass the restriction.
- The Cirebon DPRD JDIH endpoint returned HTTP 502 and `jdihn.go.id` failed TLS
  certificate verification during access checks; neither was bypassed.
- Dry-ran and then retrieved three public regulations from the official
  `peraturan.go.id` portal: one Kemendagri and one ANRI regulation plus a
  second Kemendagri regulation. The PDFs and their provenance/checksum
  manifest are local under `pairs/gov-docs/`, which is Git-ignored.
- Confirmed all three PDFs have extractable text on page 1 (74, 111, and 131
  pages respectively), so they are useful public layout/legal-document
  examples but are not verified as scanned-image OCR samples.
- This is a small targeted sample, not the complete 20–30 document benchmark.

## Repository setup

- Added a root `.gitignore` rule to exclude `templates/` from version control.
- Added a root `.gitignore` rule to exclude the entire `pairs/` folder from
  version control; local dataset files are preserved.
- Configured the `origin` remote and this repository's Git author identity.
- Verified `templates/` and `pairs/` are ignored.
- Reviewed [redocs_dataset_sourcing_budget_explorer.html](./redocs_dataset_sourcing_budget_explorer.html)
  for terminal download feasibility. Public Hugging Face sources can generally
  be fetched via `hf`/`huggingface_hub`; Kaggle requires account/API setup;
  government PDF and template links need source URL and terms verification.
- Added a Python-standard-library downloader for the first 25 CORD v2 test
  rows and acquired their images and ground-truth JSON (2.6 MB total).
- Verified all 25 JPEGs and annotations exist and all manifest SHA-256 hashes
  match. The downloaded data is excluded from Git; the downloader and
  retrieval notes remain separate from the data files.
- The explorer's generated script contains placeholder actions and unverified
  size/license claims, so it should not be run wholesale without checking each
  source.

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
- The initial catalog pass did not download dataset files; the CORD test
  sample was acquired afterward as recorded above.

## Current scope and constraints

- Initial dataset interest: general Indonesian scanned documents.
- Handwriting is excluded from the initial benchmark.
- Public datasets only; keep data local and verify rights and provenance.
- The project brief targets a small 20–30 document benchmark and an offline
  Windows prototype with CPU-only operation.
- No broad public Indonesian scanned-document dataset with image-level OCR
  and layout ground truth has been verified so far.

## Next

- Decide whether receipt-specific CORD is acceptable for the first local
  experiment, or whether to investigate a narrower document type.
- Recheck dataset terms before redistribution and keep the sample's
  receipt-specific limitation explicit.
- Other explorer datasets remain unacquired where they require Kaggle
  credentials, have unclear licensing, or lack a verified direct download
  source.
- Update this log whenever a project milestone is completed.
