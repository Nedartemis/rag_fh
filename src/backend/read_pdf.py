from pathlib import Path
from typing import List, Optional

import pymupdf
from tqdm import tqdm

from helper import cache


def read_pdf(path_pdf: Path, pages: Optional[List[int]] = None) -> List[str]:

    filename_cache = path_pdf.stem + "_text_pages.json"

    # load from cache
    if text_pages := cache.load(filename_cache):
        print(f"Load '{path_pdf}' from cache")
        return text_pages

    # open doc
    with pymupdf.open(path_pdf) as doc:

        # filters pages
        text_pages_to_read = [doc[page - 1] for page in pages] if pages else doc

        # get pages
        text_pages = [
            page.get_text()
            for page in tqdm(text_pages_to_read, desc=f"Reading pdf : '{path_pdf}'")
        ]

    # save in cache
    cache.save(filename_cache, text_pages)

    return text_pages


if __name__ == "__main__":
    import fire

    fire.Fire(read_pdf)
