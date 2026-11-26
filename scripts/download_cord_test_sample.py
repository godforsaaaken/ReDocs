import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DATASET = "naver-clova-ix/cord-v2"
SPLIT = "test"
SAMPLE_COUNT = 25
OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "pairs"
    / "datasets"
    / "cord-v2-test-sample-25"
    / "data"
)


def fetch_json(url):
    request = Request(url, headers={"User-Agent": "ReDocs-dataset-sample/1.0"})
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def fetch_bytes(url):
    request = Request(url, headers={"User-Agent": "ReDocs-dataset-sample/1.0"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def main():
    params = urlencode(
        {
            "dataset": DATASET,
            "config": "default",
            "split": SPLIT,
            "offset": 0,
            "length": SAMPLE_COUNT,
        }
    )
    payload = fetch_json(f"https://datasets-server.huggingface.co/rows?{params}")
    rows = payload.get("rows", [])
    if len(rows) != SAMPLE_COUNT:
        raise RuntimeError(
            f"Expected {SAMPLE_COUNT} rows from {SPLIT}, got {len(rows)}"
        )

    image_dir = OUTPUT_DIR / "images"
    record_dir = OUTPUT_DIR / "records"
    image_dir.mkdir(parents=True, exist_ok=True)
    record_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = OUTPUT_DIR / "manifest.jsonl"

    with manifest_path.open("w", encoding="utf-8") as manifest:
        for sample in rows:
            row_idx = sample["row_idx"]
            row = sample["row"]
            image = row["image"]
            image_name = f"{row_idx:05d}.jpg"
            image_bytes = fetch_bytes(image["src"])
            image_path = image_dir / image_name
            image_path.write_bytes(image_bytes)

            ground_truth = json.loads(row["ground_truth"])
            record = {
                "dataset": DATASET,
                "split": SPLIT,
                "row_idx": row_idx,
                "image": {
                    "file": f"images/{image_name}",
                    "width": image["width"],
                    "height": image["height"],
                },
                "ground_truth": ground_truth,
            }
            record_path = record_dir / f"{row_idx:05d}.json"
            record_path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            manifest.write(
                json.dumps(
                    {
                        "row_idx": row_idx,
                        "image": f"images/{image_name}",
                        "record": f"records/{row_idx:05d}.json",
                        "image_sha256": hashlib.sha256(image_bytes).hexdigest(),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            print(f"Downloaded test row {row_idx}: {image_name}")

    print(f"Saved {len(rows)} samples under {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
