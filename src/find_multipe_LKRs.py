"""
Finds records that have multiple related bibs (multiple LKR tags)
"""
from pymarc import MARCReader


def find_multi_lkr(marc_fh):
    with open(marc_fh, "rb") as marcfile:
        reader = MARCReader(marcfile)
        for bib in reader:
            lkrs = bib.get_fields("LKR")
            if len(lkrs) > 1:
                print(f"{bib['001'].data}")


if __name__ == "__main__":
    marc_fh = "../dump/kbhs_bib_all_20201016-utf8.mrc"
    find_multi_lkr(marc_fh)
