"""
Use to create an index of Sierra bib # & original Aleph's control numbers (001)
During the migration the load table stripped out 029 tag where the control number was mapped.
This script uses original, prepped for migration MARC file and export from Sierra to create
an index of bib #, Aleph's control #, call numbers, and titles
"""

import csv

from pymarc import MARCReader

from utils import save2csv


def control_no_parser(fh: str) -> str:
    """
    Yields oclc & aleph control number as tuple
    """

    with open(fh, "rb") as marcfile:
        reader = MARCReader(marcfile)
        for bib in reader:
            oclc_no = bib["001"].data
            aleph_no = bib["029"]["b"]

            yield (oclc_no, aleph_no)


def find_record(fh: str, oclc_no: str) -> None:
    """
    finds Sierra bib #, call #, title for provided
    oclc control no
    """
    with open(fh, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter="^")
        # reader.__next__()
        for row in reader:
            if oclc_no == row[1]:
                return row


if __name__ == "__main__":
    prepped_file = "../dump/cbh-bibs-migration.mrc"
    sierra_export = "../dump/cbh-idx-all.txt"
    out_report = "../dump/chd-aleph-number-idx.csv"

    control_nos = control_no_parser(prepped_file)

    n = 0
    v = 0
    for oclc_no, aleph_no in control_nos:
        n += 1

        sierra_data = find_record(sierra_export, oclc_no)

        if sierra_data is not None:
            v += 1
            sierra_data.append(aleph_no)
            save2csv(out_report, sierra_data)
        else:
            print(f"Unable to find match for {oclc_no}, {aleph_no}")


print(f"Processed {n} control nos, found {v} matches")
