"""
This module parses Aleph item records (Z30) and outputs values into coma separated csv file for further analysis
"""

from collections import Counter, defaultdict

from pymarc import MARCReader

from utils import save2csv


STAGS = sorted(
    [
        "0",
        "1",
        "2",
        "4",
        "5",
        "7",
        "A",
        "a",
        "B",
        "b",
        "F",
        "f",
        "H",
        "h",
        "I",
        "i",
        "J",
        "j",
        "k",
        "m1",
        "m2",
        "P",
        "p",
        "Q",
        "R",
        "S",
        "w",
    ]
)


def find_number_of_subfields_per_item(marc_fh):
    with open(marc_fh, "rb") as marcfile:
        reader = MARCReader(marcfile)
        bcnt = Counter()
        for bib in reader:
            # find and iterate through Z30 - item record tags
            for field in bib.get_fields("Z30"):
                icnt = Counter()
                for stag, _ in field:
                    icnt[stag] += 1
                bcnt[len(icnt.keys())] += 1
                # print(icnt, len(icnt.keys()))
        print(bcnt)


def find_repeated_subfields(marc_fh):
    with open(marc_fh, "rb") as marcfile:
        reader = MARCReader(marcfile)
        rcnt = Counter()
        for bib in reader:
            # find and iterate through Z30 - item record tags
            for field in bib.get_fields("Z30"):
                icnt = Counter()
                for stag, _ in field:
                    icnt[stag] += 1
                    if icnt[stag] > 1:
                        rcnt[stag] += 1
        print(rcnt)


def run(marc_fh, output):
    # create a header in output csv file
    save2csv(output, STAGS)

    with open(marc_fh, "rb") as marcfile:
        reader = MARCReader(marcfile)
        for bib in reader:
            # find and iterate through Z30 - item record tags
            for field in bib.get_fields("Z30"):

                sd = dict()
                m_subs = field.get_subfields("m")
                m1 = m_subs[0]
                try:
                    m2 = m_subs[1]
                except IndexError:
                    m2 = None

                sd["m1"] = m1
                sd["m2"] = m2

                # rest of subfields
                for stag, value in field:
                    if stag != "m":
                        sd[stag] = value

                # missing subfields
                for s in STAGS:
                    if s not in sd:
                        sd[s] = None

                row = [sd[k] for k in sorted(sd.keys())]

                save2csv(output, row)


if __name__ == "__main__":
    # output file
    output_items = "./files/items.csv"
    output_repeatable_subs = "./files/repeat-subs.csv"

    # test file
    test_fh = "./files/kbhs_bib_sample_20201016.mrc"
    all_fh = "./files/kbhs_bib_all_20201016-utf8.mrc"
    run(all_fh, output_items)

    # find_number_of_subfields_per_item(all_fh)
    # find_repeated_subfields(all_fh)
