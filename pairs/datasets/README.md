# Dataset source inventory

**Status:** Source shortlist only. No dataset files have been downloaded.
**Reviewed:** 2026-11-25
**Project brief:** [../../main_draft.md](../../main_draft.md)

## Intended benchmark scope

The current selection is for general Indonesian scanned documents, with
handwriting excluded from the first benchmark. The project brief calls for a
small, representative set of roughly 20–30 documents and evaluation of OCR,
structure, editability, processing time, resource use, and reliability. Keep
any sensitive data local and use only material whose use is authorized.

The workspace has no existing dataset assets. In the public sources checked,
I did not verify a broad Indonesian scanned-document dataset with image-level
OCR and layout ground truth. CORD is the closest direct match, but it contains
receipts rather than general forms, letters, and reports.

## Candidate sources

| Dataset | Contents and scale | Language / fit | License and provenance | Recommendation |
|---|---|---|---|---|
| [CORD v2](https://github.com/clovaai/cord) · [Hugging Face](https://huggingface.co/datasets/naver-clova-ix/cord-v2) | 1,000 receipt images; 800 train / 100 dev / 100 test. Includes OCR text and box annotations plus hierarchical receipt labels. | Indonesian. Strongest direct source for printed Indonesian OCR and structured extraction, but receipt-specific. Handwriting is not its intended focus. | The source repository states CC BY 4.0. Attribute the source and preserve the applicable license notice. | **Use as the initial public benchmark source.** Select a small, documented subset; do not treat receipt results as representative of all document types. |
| [IDX Financial Statements](https://huggingface.co/datasets/Azzindani/IDX_Financial_Statements) | Dataset card describes PDFs, spreadsheets, and XBRL; reports total size of 128 GB. | Indonesian and English financial disclosures. Potential source of real-world pages and tables, but not verified as scanned-image data and much broader/larger than needed. | Card declares CC BY 4.0. The source documents are issuer filings; check document-level rights and provenance before reuse or redistribution. | **Hold for a later, small-sample audit.** Do not download the full collection. Check whether PDFs are scans, whether the files are accessible, and whether their source terms permit the intended use. |
| [DocLayNet](https://github.com/DS4SD/DocLayNet) · [Hugging Face](https://huggingface.co/datasets/docling-project/DocLayNet) | 80,863 pages, 11 layout classes, COCO bounding boxes; PNG pages, with optional PDFs and text-cell JSON. The source README lists 28 GiB for core data and 7.5 GiB for extra files. | Broad document-layout benchmark, not an Indonesian-language benchmark; includes finance, science, law, tenders, manuals, and patents. | Dataset card lists CDLA-Permissive-1.0. Review the agreement and source/provenance terms for underlying documents before redistribution. | **Optional layout benchmark only.** Useful for understanding layout classes, but too large to acquire for this small local prototype benchmark. |
| [PubTabNet](https://github.com/ibm-aur-nlp/PubTabNet) · [Hugging Face](https://huggingface.co/datasets/ajimeno/PubTabNet) | More than 568,000 scientific-paper table images with HTML structure annotations and cell boxes for non-empty cells. | Table-structure benchmark, not Indonesian or administrative forms. | IBM states the annotations use CDLA-Permissive-1.0; images come from the PubMed Central Open Access Subset and remain subject to its terms. | **Optional table-only reference.** Do not download the full corpus; source-specific image terms apply. |

## Not selected for acquisition

- [FUNSD](https://guillaumejaume.github.io/FUNSD/) has 199 annotated noisy
  scanned forms, but is English-language and the official page checked did not
  establish dataset reuse terms. Revisit only after confirming the license.
- [XFUND](https://github.com/doc-analysis/XFUND) has form annotations in seven
  languages, none Indonesian, and states CC BY-NC-SA 4.0. It is not a suitable
  default for a project whose eventual distribution/licensing needs are not
  yet specified.
- [Indonesian tax document classification](https://huggingface.co/datasets/Hadisawara/indonesian-tax-document-classification)
  is a CSV of metadata/labels, not document images or OCR ground truth. Its
  preview includes names and tax identifiers, and the checked card did not
  establish a license. Do not use it as an image benchmark.
- Indonesian legal-text datasets found during the search provide extracted
  text rather than scanned-page image/structure pairs; source and reuse terms
  also need separate review.

## Dataset handling rules for this project

1. Prefer CORD v2 for an initial local experiment, but keep the benchmark
   limitation explicit: it tests Indonesian receipts, not broad document
   reconstruction.
2. Before adding any corpus, record its source URL, version/split, license,
   attribution requirements, provenance, file types, and intended use.
3. Do not copy sensitive identifiers or personal records into this workspace.
   A public URL alone does not establish that the data is safe or authorized
   for this use.
4. Keep public benchmark data separate from any future authorized internal
   samples. Do not mix train and evaluation examples; record the exact sample
   selection so results can be reproduced.
5. Defer handwriting, large downloads, and any dataset with unresolved reuse
   terms. The draft's first-month target is a constrained offline prototype,
   not a universal reconstruction system.

## Working rules and project constraints

The relevant guidance in [AGENTS/AGENTS.md](../../AGENTS/AGENTS.md) is:

- Surface assumptions and ambiguity before proceeding.
- Prefer the simplest solution that satisfies the stated scope.
- Make only changes directly required by the task.
- Define verifiable goals and check the result.

The project brief additionally sets these provisional constraints:

- Windows desktop; fully offline after installation.
- CPU-only operation, no dedicated GPU; 8 GB RAM preferred, with 4 GB to be
  tested only if that hardware is in scope.
- First-version emphasis is structural reconstruction, human review, and
  editable output; pixel-perfect visual reproduction and reliable handwriting
  recognition are non-goals for the first month.
- A local LLM is optional and must not silently overwrite OCR or invent
  official information.
- Final document types and target hardware are still open decisions.

## Source links

- [CORD v2 source README and download information](https://github.com/clovaai/cord)
- [CORD v2 dataset card](https://huggingface.co/datasets/naver-clova-ix/cord-v2)
- [IDX Financial Statements dataset card](https://huggingface.co/datasets/Azzindani/IDX_Financial_Statements)
- [DocLayNet source README and download sizes](https://github.com/DS4SD/DocLayNet)
- [DocLayNet dataset card and license](https://huggingface.co/datasets/docling-project/DocLayNet)
- [PubTabNet source README](https://github.com/ibm-aur-nlp/PubTabNet)
- [PubTabNet license notes](https://github.com/ibm-aur-nlp/PubTabNet/blob/master/LICENSE.md)
- [PubMed Central Open Access Subset terms](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/)
