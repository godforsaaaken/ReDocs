# Offline Document Reconstruction Studio

## Project Discussion Brief and Exploration Base

**Document purpose:** A reusable project brief for discussing,
researching, scoping, and planning a potential software project with
other LLMs, developers, or technical reviewers.

**Status:** Early concept / requirements discovery
**Target platform:** Windows desktop
**Deployment model:** Fully offline after installation
**Initial time budget:** Approximately one month
**Primary constraint:** Must remain usable on older,
modest-specification office computers

---

## 1. The idea in one paragraph

Explore building a lightweight, offline Windows desktop application that
takes scanned documents (images or scanned PDFs), extracts their
content, infers their structure, and reconstructs them into genuinely
editable digital documents. The goal is not merely to place OCR text
over an image or create a searchable PDF. The application should recover
document elements such as headings, paragraphs, tables, rows, columns,
cells, labels, fields, and basic layout, then let a human review and
correct the result before exporting to formats such as DOCX, XLSX, HTML,
or JSON.

A local small language model (LLM) may assist with semantic
interpretation and OCR review, but should not be required for the core
processing pipeline.

## 2. Problem statement

Many offices and organizations still hold information in scanned paper
documents. A scan is essentially an image: the original text, table
structure, formatting metadata, and editable objects are no longer
available.

Basic OCR can recover text, but often loses the relationships and layout
that make a document useful. For example:

- Text from separate table cells may be extracted in the wrong order.
- Headings, labels, and body text may become indistinguishable.
- Merged cells and multi-column layouts can be difficult to recover.
- Handwriting and low-quality scans can produce uncertain results.
- Exported text may be editable but no longer resemble the original
  document.

The proposed application would bridge the gap between a scanned image
and a structured, editable document.

## 3. Intended users and document types

The initial audience is not yet finalized. Plausible users include:

- Administrative and government offices.
- Small businesses.
- Schools and educational institutions.
- Records and archive staff.
- People who need to digitize batches of paper forms.

A promising initial specialization is Indonesian administrative
documents, particularly structured forms and tables. This is a
hypothesis to validate, not a confirmed product requirement.

Potential document types:

- Administrative forms.
- Registration forms.
- Data tables and lists.
- Letters and reports.
- Scanned PDFs containing multiple pages.
- Documents containing both printed and handwritten entries.

The first release should deliberately support a narrow set of document
types well rather than promise universal reconstruction.

## 4. Core product goals

### Must-have goals for a first usable version

1. Import scanned PDF, PNG, and JPEG files.
2. Process documents locally without internet access.
3. Improve scan quality through basic image preprocessing.
4. Extract printed text using OCR.
5. Detect basic document regions and table structure.
6. Represent extracted content in a structured intermediate format.
7. Provide a way to review and correct OCR output.
8. Export useful editable results, initially DOCX and/or XLSX.
9. Run without requiring a dedicated GPU.
10. Handle errors gracefully and avoid losing work.

### Later or stretch goals

- Better reconstruction of original visual formatting.
- Handwriting recognition.
- Batch processing of large document collections.
- Multiple document templates.
- Confidence indicators and uncertainty highlighting.
- Optional local LLM assistance.
- Searchable PDF output.
- More export formats.
- Automatic document classification.

### Explicit non-goals for the first month

Unless early testing proves them unusually easy, do not promise:

- Perfect recreation of every original document.
- Pixel-perfect reproduction of arbitrary scans.
- Reliable recognition of all handwriting.
- Support for every language and document type.
- A general-purpose AI agent.
- Cloud synchronization or online APIs.
- Training a custom OCR or language model from scratch.

## 5. What "editable reconstruction" means

The project should distinguish three levels of output.

### Level 1: Text recovery

Recognize text and make it selectable and editable.

Examples: TXT, searchable PDF, or text placed into a document.

### Level 2: Structural reconstruction

Recover document semantics and relationships:

- Headings and paragraphs.
- Tables, rows, columns, and cells.
- Labels and corresponding values.
- Sections and basic hierarchy.
- Reading order.

This is the recommended primary target for the first version.

### Level 3: Visual reconstruction

Attempt to reproduce the original appearance:

- Positioning and alignment.
- Fonts and font sizes.
- Borders and shading.
- Margins and spacing.
- Page breaks.
- Signatures, stamps, and other visual elements.

This is substantially harder. It should be treated as a later
enhancement, not a condition for declaring the first version successful.

A scan does not contain the original Word formatting metadata. The
software must infer the layout, so exact recovery is not always
possible.

## 6. Proposed processing pipeline

A possible pipeline is:

1. **Import**
   - Load PDF or image files.
   - Convert PDF pages into images when necessary.
   - Preserve the original source for comparison.
2. **Preprocessing**
   - Deskew rotated pages.
   - Denoise.
   - Improve contrast.
   - Correct orientation.
   - Optionally remove borders, shadows, or background artifacts.
3. **OCR**
   - Detect text regions.
   - Recognize printed text.
   - Preserve word or line coordinates where available.
   - Record OCR confidence when supported.
4. **Layout analysis**
   - Identify paragraphs, headings, columns, tables, and other
     regions.
   - Determine reading order.
   - Detect table boundaries, rows, columns, and cells.
5. **Structure reconstruction**
   - Convert OCR and layout results into a normalized internal
     document representation.
   - Preserve links between recognized text and its original page
     coordinates.
   - Track uncertain or missing elements.
6. **Optional semantic assistance**
   - Use a local LLM to suggest field classification, terminology
     normalization, or possible OCR corrections.
   - Never silently replace source text with an LLM guess.
7. **Human review**
   - Show the source scan alongside reconstructed content.
   - Let users edit text and correct table structure.
   - Highlight low-confidence or ambiguous elements.
8. **Export**
   - Generate DOCX, XLSX, HTML, JSON, and potentially searchable PDF.
   - Export only formats that the first version can generate
     reliably.

## 7. Candidate technology stack

These are candidates to evaluate, not final decisions.

---

  Area                    Candidate               Reason to investigate

---

  Programming language    Python                  Broad OCR, image
                                                  processing, and
                                                  document-generation
                                                  ecosystem

  Desktop GUI             PySide6 / Qt            Native desktop-style
                                                  interface and Python
                                                  integration

  Image processing        OpenCV                  Deskewing,
                                                  thresholding,
                                                  denoising, geometry

  OCR                     Tesseract               Local operation,
                                                  established ecosystem,
                                                  Indonesian language
                                                  data

  Alternative OCR         PaddleOCR               Detection and
                                                  recognition models;
                                                  investigate CPU and
                                                  Windows deployment

  Document parsing        Docling                 Existing document
                                                  understanding and
                                                  structured extraction
                                                  capabilities

  Layout analysis         OpenCV + custom logic;  Avoid overengineering
                          possibly pretrained     the first release
                          layout models

  Local LLM runtime       llama.cpp               Local inference and
                                                  quantized GGUF model
                                                  support

  Internal representation JSON / Python data      Separate extraction
                          classes                 from output generation

  DOCX export             python-docx             Editable Word documents

  XLSX export             openpyxl                Editable spreadsheets

Packaging               PyInstaller             Windows executable
                                                  packaging
-----------------------------------------------------------

### Important implementation principle

Do not tie OCR directly to DOCX or XLSX generation.

Create a stable intermediate representation first. Multiple export
formats should consume that same representation. This makes it possible
to replace an OCR engine or improve layout analysis without rewriting
every exporter.

Example conceptual representation:

```json
{
  "document": {
    "type": "administrative_form",
    "pages": [
      {
        "elements": [
          {
            "type": "heading",
            "text": "DATA PENDUDUK",
            "confidence": 0.99
          },
          {
            "type": "table",
            "rows": [
              ["Nama", "Fawaiz"],
              ["Alamat", "Cirebon"]
            ]
          }
        ]
      }
    ]
  }
}
```

This is illustrative only. A real schema should also preserve page
number, bounding boxes, source text, confidence, cell spans, and review
status.

## 8. Should a lightweight LLM be included?

Potentially, yes. It should be an optional assistant rather than the
central document-processing engine.

### Good candidate tasks

- Suggesting likely corrections for OCR mistakes.
- Classifying a detected region as a heading, label, address, or other
  field.
- Interpreting Indonesian administrative terminology.
- Suggesting relationships between labels and values.
- Flagging text that appears inconsistent with surrounding context.
- Normalizing output when the user explicitly requests it.

### Poor candidate tasks

- Detecting exact table borders from pixels.
- Recovering precise geometry.
- Reconstructing original fonts and spacing.
- Replacing OCR or image-processing algorithms.
- Making unverified changes to official records.

### Models and runtimes to investigate

- Qwen 2.5 0.5B Instruct.
- Qwen 2.5 1.5B Instruct.
- llama.cpp with quantized GGUF models.

Model availability, licensing, language performance, memory use, and
Windows compatibility must be checked before selecting one. Small models
may perform poorly on Indonesian administrative terminology, so test
them against real examples.

### Safety and data-integrity rule

The original OCR result must remain recoverable. An LLM suggestion
should be displayed as a suggestion, with the original text retained and
user approval required before replacement. Do not invent missing names,
identification numbers, addresses, dates, or other official information.

## 9. Hardware and offline constraints

The intended environment is older Windows office computers. Exact
minimum specifications are not yet known.

Provisional engineering targets:

- CPU-only operation.
- No dedicated GPU requirement.
- 8 GB RAM as a preferred baseline, with testing on 4 GB if that
  hardware is in scope.
- SSD recommended, but test HDD behavior if relevant.
- No internet connection required during normal operation.
- Process pages sequentially where possible.
- Avoid loading multiple large models simultaneously.
- Make LLM functionality optional and independently disableable.

Do not claim that a particular model or pipeline will run acceptably
until it has been benchmarked on the actual target hardware.

## 10. One-month development plan

A month is plausible for a constrained prototype, not a polished
universal reconstruction product.

### Week 1: Foundation and OCR

- Create the PySide6 application shell.
- Implement PDF and image import.
- Implement basic preprocessing.
- Integrate one OCR engine.
- Display extracted text and source images.
- Test on representative scans.

**Deliverable:** A Windows desktop prototype that imports scans and
extracts text offline.

### Week 2: Layout and structure

- Detect basic regions.
- Implement reading order.
- Detect simple tables and cells.
- Define the internal JSON representation.
- Preserve links to source coordinates.

**Deliverable:** Structured extraction for a limited set of document
types.

### Week 3: Editing and export

- Build a basic review interface.
- Support text correction.
- Support basic table correction.
- Generate DOCX and/or XLSX.
- Experiment with optional LLM assistance only if the core pipeline is
  stable.

**Deliverable:** A user can review, correct, and export a reconstructed
document.

### Week 4: Testing and packaging

- Test poor-quality and rotated scans.
- Test multi-page PDFs.
- Test batch processing if time permits.
- Profile CPU and RAM use.
- Improve error handling.
- Package the application for Windows.
- Test on a clean machine without internet access.

**Deliverable:** A distributable offline prototype with documented
limitations.

### Scope-control rule

If the core OCR and table reconstruction are not working by the end of
Week 2, postpone the LLM and advanced visual reconstruction. A reliable
basic application is better than a collection of unfinished AI features.

## 11. Existing products and projects to benchmark

The following names have been identified as starting points for
research. Their current capabilities, licensing, availability, offline
behavior, and hardware requirements must be independently verified. Do
not treat this list as a completed competitive analysis.

### Commercial products

- ABBYY FineReader PDF --- OCR, PDF editing, and conversion to
  editable formats.
- OCRtoWord --- scanned document conversion to editable Word
  documents.
- ScanLex --- described as an offline OCR and document conversion
  product; verify current product details.
- Adobe Acrobat Pro --- scanned PDF OCR and editing.

### Open-source projects and frameworks

- Docling --- document conversion and structural extraction.
- PaddleOCR --- OCR, text detection, and document analysis.
- Tesseract --- established OCR engine.
- NAPS2 --- desktop scanning and OCR workflow.
- llama.cpp --- local LLM inference runtime.

### Benchmark questions

For each relevant product, test:

1. Does it operate completely offline?
2. Does it support Indonesian OCR?
3. Can it reconstruct tables rather than merely extract their text?
4. Can users edit the resulting document?
5. Does it preserve merged cells?
6. How does it handle handwritten entries?
7. Can it process batches?
8. How much RAM and CPU does it use?
9. Can it run on the actual target Windows machines?
10. What are its licensing and distribution restrictions?

Useful starting links:

- Tesseract: https://github.com/tesseract-ocr/tesseract
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
- Docling: https://github.com/docling-project/docling
- NAPS2: https://github.com/cyanfish/naps2
- llama.cpp: https://github.com/ggml-org/llama.cpp
- PySide6: https://doc.qt.io/qtforpython-6/
- OpenCV: https://opencv.org/
- python-docx: https://python-docx.readthedocs.io/

## 12. Evaluation plan

Build a small, representative test set before making major architecture
decisions.

Suggested initial set: 20--30 documents, including:

- Clean printed documents.
- Low-resolution scans.
- Rotated or skewed scans.
- Tables with simple cells.
- Tables with merged cells.
- Multi-column layouts.
- Indonesian terminology and abbreviations.
- Documents with handwritten fields.
- Multi-page PDFs.

If documents contain personal or sensitive information, use authorized
samples, anonymize them where appropriate, and keep test data local.

### Suggested evaluation metrics

  Area               Possible measurement

---

  OCR accuracy       Character error rate (CER) and word error rate (WER)
  Table extraction   Cell and row reconstruction accuracy
  Layout             Correct region classification and reading order
  Export             Whether text and tables remain editable
  Visual fidelity    Human comparison against the source
  Performance        Processing time per page
  Resource use       Peak RAM and CPU utilization
  Reliability        Failed pages, crashes, and incomplete exports

A useful benchmark must measure both recognition accuracy and structural
correctness. High OCR accuracy alone does not mean a document was
reconstructed successfully.

## 13. Key risks and unresolved questions

1. **Document scope:** Which specific document types should be
   supported first?
2. **Target hardware:** What are the minimum CPU, RAM, Windows version,
   and storage specifications?
3. **OCR quality:** Which engine performs best on the actual scans,
   especially Indonesian text?
4. **Table reconstruction:** Can basic geometry-based methods handle
   the target forms, or is a pretrained model needed?
5. **Handwriting:** Is handwriting required in the first release, or
   can it be marked for manual entry?
6. **Output priority:** Is DOCX, XLSX, or both essential?
7. **Visual fidelity:** Is editable structure sufficient, or must the
   output resemble the original page?
8. **LLM value:** Does a small local model measurably improve results
   enough to justify its memory and packaging cost?
9. **Packaging:** Can all model files, language data, and dependencies
   be distributed legally and reliably?
10. **Privacy:** What safeguards are needed for administrative or
    personally identifiable information?

## 14. Current working hypothesis

The most defensible first version is:

> A lightweight, fully offline Windows desktop application that
> reconstructs a limited range of Indonesian administrative scans into
> editable, structured DOCX/XLSX documents, with human verification and
> optional local AI assistance.

The core should use conventional OCR, image processing, layout analysis,
and document-generation libraries. A small LLM should be an optional
layer for semantic suggestions, not a dependency for basic operation.

The main differentiator to investigate is not simply offline OCR. It is
the combination of:

- Practical Indonesian document support.
- Usability on older office hardware.
- Structured, editable output.
- Human-verifiable corrections.
- Batch processing.
- Fully local operation.

This is a hypothesis, not a claim that no competing product offers these
features.

---

# Discussion prompts for other LLMs and technical reviewers

Use these prompts to get critical feedback rather than generic
encouragement.

## A. Product and scope review

- Is this problem sufficiently distinct from existing OCR and PDF
  software?
- Which user group and document type should be the first target?
- What is the smallest useful product that can be completed in four
  weeks?
- Which proposed features should be removed from the first release?
- What would make this genuinely useful to a small administrative
  office?

## B. Architecture review

- Propose a robust architecture for a fully offline Windows desktop
  application.
- Compare PySide6 with other suitable desktop GUI options.
- Compare Tesseract, PaddleOCR, and Docling for this specific
  workload.
- Recommend a document intermediate representation that preserves
  text, page coordinates, table structure, confidence, and review
  history.
- Identify dependency conflicts and Windows packaging risks.
- Explain which components should run sequentially and which can run
  concurrently.

## C. Lightweight LLM review

- Is a 0.5B--1.5B quantized model useful for this workload?
- Which local models perform reasonably on Indonesian text?
- Which tasks genuinely benefit from an LLM rather than deterministic
  code?
- Estimate RAM requirements and CPU performance on older hardware.
- Recommend a safe correction workflow that never silently changes
  official information.
- Explain whether an LLM should receive OCR text, layout metadata,
  cropped images, or some combination.

## D. One-month feasibility review

- Create a realistic four-week implementation plan for one developer.
- Identify the highest-risk technical components.
- Define measurable acceptance criteria for each week.
- Recommend what to prototype first.
- Identify features that should be postponed.
- Account for debugging, testing, and packaging time.

## E. Critical review

- What assumptions in this proposal are weak or unsupported?
- Which existing tools already solve most of the problem?
- Where would a new application have a defensible advantage?
- What is likely to fail on 4--8 GB RAM machines?
- What is the simplest architecture that could still deliver
  meaningful reconstruction?
- If you had to cut 50% of the proposed scope, what would you retain?

## F. Benchmark design

- Design a reproducible benchmark for Indonesian scanned
  administrative documents.
- Recommend metrics for OCR, table reconstruction, layout, and export
  quality.
- Explain how to compare output against source scans.
- Propose a small test corpus that covers realistic document quality
  without exposing private information.

---

## Instructions for whoever reviews this brief

Treat this as an early-stage proposal, not a fixed specification.

Be skeptical. Separate verified facts from assumptions. Check current
project documentation, licenses, supported platforms, model
availability, and deployment requirements. Do not invent benchmark
results or claim that a model is lightweight without specifying its
quantization, memory requirements, and hardware context.

Prefer practical recommendations that can be implemented and tested by
one developer within approximately one month. Explain trade-offs and
identify what should be postponed.

**The immediate objective is to turn this concept into a technically
defensible, realistically scoped prototype plan.**
