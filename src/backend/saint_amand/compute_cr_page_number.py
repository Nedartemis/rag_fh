import re

import pandas as pd
from tqdm import tqdm

from backend.saint_amand import TYPE_PAGES


def compute_cr_page_numbers(pages: TYPE_PAGES) -> pd.DataFrame:

    # extract cr number from text
    numbers_cr = {}
    for num_page, text in tqdm(
        enumerate(pages, start=1),
        total=len(pages),
        desc="Extracting num cr from text page",
    ):
        # search cr number
        nums = re.findall(r"CR( [A-Z]{3})? (N° )?(\d\d)", text)

        # not found
        if len(nums) == 0:
            print(f"Page {num_page} does not have a cr number")
            continue

        # found

        # check consistency
        num_cr = nums[0][2]
        if not all(num_iter == num_cr for _, _, num_iter in nums):
            # fix inconsistency
            nums = [e for e in nums if e[0]]

        # store it with by taking the updated list
        numbers_cr[num_page] = nums[0][0], int(nums[0][2])

    # compute start and end pages of each CR
    cr_begin_end = {}
    num_previous_cr = 0
    start = 0
    types_cr = []

    for page, (type_cr, num_cr) in numbers_cr.items():

        # if same, we are not at the end of the cr, continue
        if num_cr == num_previous_cr:
            if type_cr not in types_cr:
                types_cr.append(type_cr)
            continue

        # end cr :

        # store start and end
        cr_begin_end[num_previous_cr] = (start, page - 1, types_cr)

        # update vars
        start = page
        num_previous_cr += 1
        types_cr = [type_cr]

    # store the last
    cr_begin_end[num_previous_cr] = (start, page, types_cr)
    # remove the first false one
    cr_begin_end.pop(0)

    # store into a df
    return pd.DataFrame(
        [
            {"num_cr": num_cr, "page_start": p1, "page_end": p2, "types": types_cr}
            for num_cr, (p1, p2, types_cr) in cr_begin_end.items()
        ]
    )


if __name__ == "__main__":
    from read_pdf import read_pdf

    from vars import PATH_DOCS

    pages = read_pdf(
        PATH_DOCS / "intégrale CR chantier Saint Amand.pdf", pages=range(1, 20)
    )
    df = compute_cr_page_numbers(pages)
    print(df)
