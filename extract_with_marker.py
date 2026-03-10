import argparse
import json
import os
import re

import pypdfium2 as pdfium
from marker.config.parser import parse_range_str


DEFAULT_PDF_PATH = "dmd_rl2.pdf"


def resolve_output_dir(pdf_path, output_dir):
    if output_dir:
        return output_dir

    pdf_name = os.path.basename(pdf_path)
    pdf_stem = os.path.splitext(pdf_name)[0]
    parent_dir = os.path.dirname(pdf_path) or "."
    return os.path.join(parent_dir, pdf_stem)


def resolve_page_indices(page_range, total_pages):
    if not page_range:
        return list(range(total_pages))
    indices = sorted(set(parse_range_str(page_range)))
    return [idx for idx in indices if 0 <= idx < total_pages]


def extract_page_text(page):
    textpage = page.get_textpage()
    try:
        return (textpage.get_text_bounded() or "").strip()
    finally:
        textpage.close()


def extract_caption_snippet(page_text):
    if not page_text:
        return ""

    normalized = " ".join(page_text.split())
    match = re.search(
        r'((?:Figure|Fig\.|Table)\s*\d+[^\n]{0,320})',
        normalized,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return ""


def select_page_figure(page, page_number):
    page_w, page_h = page.get_size()
    page_area = max(page_w * page_h, 1.0)
    candidates = []
    seen = set()

    for obj_idx, obj in enumerate(page.get_objects()):
        if type(obj).__name__ != "PdfImage":
            continue

        try:
            img_w, img_h = obj.get_size()
            left, bottom, right, top = obj.get_pos()
        except Exception:
            continue

        bbox_w = max(right - left, 0.0)
        bbox_h = max(top - bottom, 0.0)
        bbox_area = bbox_w * bbox_h
        bbox_ratio = bbox_area / page_area
        pixel_area = img_w * img_h

        if img_w < 180 or img_h < 180:
            continue
        if bbox_w < 100 or bbox_h < 80:
            continue
        if pixel_area < 60000:
            continue
        if bbox_ratio < 0.03:
            continue

        key = (
            round(left, 1),
            round(bottom, 1),
            round(right, 1),
            round(top, 1),
            img_w,
            img_h,
        )
        if key in seen:
            continue
        seen.add(key)

        candidates.append(
            {
                "page": page_number,
                "object_index": obj_idx,
                "bbox_ratio": bbox_ratio,
                "pixel_area": pixel_area,
                "bbox": [left, bottom, right, top],
                "size": [img_w, img_h],
                "obj": obj,
            }
        )

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item["bbox_ratio"], item["pixel_area"]), reverse=True)
    return candidates[0]


def extract_pdfium_assets(pdf_path, output_dir, page_indices, max_figures=10):
    pdf = pdfium.PdfDocument(pdf_path)
    assets = []

    try:
        for page_index in page_indices:
            page = pdf[page_index]
            try:
                chosen = select_page_figure(page, page_index + 1)
                if not chosen:
                    continue

                if len(assets) >= max_figures:
                    break

                filename = f"_page_{page_index + 1}_Figure_0.png"
                save_path = os.path.join(output_dir, filename)
                bitmap = None
                try:
                    bitmap = chosen["obj"].get_bitmap(render=True)
                except Exception:
                    try:
                        bitmap = chosen["obj"].get_bitmap(render=False)
                    except Exception:
                        print(f"  Skipping figure candidate on page {page_index + 1}: bitmap extraction failed")
                        continue

                bitmap.to_pil().save(save_path)

                assets.append(
                    {
                        "filename": filename,
                        "path": save_path,
                        "page": page_index + 1,
                        "bbox_ratio": chosen["bbox_ratio"],
                        "pixel_area": chosen["pixel_area"],
                        "bbox": chosen["bbox"],
                        "size": chosen["size"],
                    }
                )
                print(f"  Saved figure asset: {filename} (page {page_index + 1})")
            finally:
                page.close()
    finally:
        pdf.close()

    return assets


def build_pdfium_markdown(pdf_path, page_indices, assets_by_page):
    pdf = pdfium.PdfDocument(pdf_path)
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    parts = [f"# Extracted Content: {stem}", ""]

    try:
        for page_index in page_indices:
            page = pdf[page_index]
            try:
                page_text = extract_page_text(page)
                parts.append(f"## Page {page_index + 1}")
                parts.append("")

                page_assets = assets_by_page.get(page_index + 1, [])
                if page_assets:
                    caption = extract_caption_snippet(page_text)
                    for asset in page_assets:
                        parts.append(f'<span id="page-{page_index + 1}-0"></span>![]({asset["filename"]})')
                        parts.append("")
                        if caption:
                            parts.append(caption)
                            parts.append("")

                if page_text:
                    parts.append(page_text)
                    parts.append("")
            finally:
                page.close()
    finally:
        pdf.close()

    return "\n".join(parts).strip() + "\n"


def extract_with_pdfium(pdf_path, output_dir, page_indices):
    print("Using PDFium extraction engine...")
    assets = extract_pdfium_assets(pdf_path, output_dir, page_indices)
    assets_by_page = {}
    for asset in assets:
        assets_by_page.setdefault(asset["page"], []).append(asset)

    markdown_text = build_pdfium_markdown(pdf_path, page_indices, assets_by_page)
    return markdown_text, assets


def extract_with_marker(pdf_path, output_dir, page_range, disable_ocr):
    from marker.models import create_model_dict
    from marker.converters.pdf import PdfConverter

    print("Using Marker extraction engine...")
    model_dict = create_model_dict()
    config = {}
    if page_range:
        config["page_range"] = parse_range_str(page_range)
        print(f"Extraction limited to pages: {page_range}")
    if disable_ocr:
        config["disable_ocr"] = True
        print("OCR disabled; using embedded PDF text only.")

    converter = PdfConverter(artifact_dict=model_dict, config=config)
    rendered = converter(pdf_path)

    images = getattr(rendered, "images", {})
    assets = []
    for filename, image in images.items():
        save_path = os.path.join(output_dir, filename)
        image.save(save_path)
        assets.append({"filename": filename, "path": save_path})
        print(f"  Saved: {filename}")

    full_text = getattr(rendered, "markdown", "") or getattr(rendered, "text", "")
    return full_text, assets


def main():
    parser = argparse.ArgumentParser(description="Extract content from PDF and save text plus figure assets.")
    parser.add_argument("--pdf_path", default=DEFAULT_PDF_PATH, help="Path to input PDF")
    parser.add_argument("--output_dir", default=None, help="Directory for output assets (default: same as PDF)")
    parser.add_argument("--page_range", default=None, help="Page range to extract (0-based, e.g. 0-5, 10, 12-14)")
    parser.add_argument("--disable_ocr", action="store_true", help="Disable OCR and rely on embedded PDF text")
    parser.add_argument(
        "--engine",
        choices=["pdfium", "marker"],
        default="marker",
        help="Deprecated compatibility flag. Extraction always uses 'marker' to avoid missing figures.",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path
    output_dir = resolve_output_dir(pdf_path, args.output_dir)

    print(f"--- Starting Extraction for {pdf_path} ---")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    pdf = pdfium.PdfDocument(pdf_path)
    try:
        total_pages = len(pdf)
    finally:
        pdf.close()

    page_indices = resolve_page_indices(args.page_range, total_pages)
    print(f"Pages selected: {[idx + 1 for idx in page_indices]}")

    if args.engine != "marker":
        print(f"Ignoring --engine={args.engine}; Marker extraction is always used to avoid missing figures.")

    markdown_text, assets = extract_with_marker(
        pdf_path,
        output_dir,
        args.page_range,
        args.disable_ocr,
    )

    md_path = os.path.join(output_dir, "extracted_content.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    print(f"Saved Markdown content to {md_path}")

    json_path = os.path.join(output_dir, "assets_map.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, indent=2)
    print(f"Saved asset metadata to {json_path}")

    print(f"Found {len(assets)} extracted assets.")
    print("--- Extraction Complete ---")


if __name__ == "__main__":
    main()
