"""
Prepares isbn data for Sorl queries
"""

import csv

from utils import save2csv


def normalize_isbn(value):
    return value.split(" ")[0]


def prep_isbns(src, dst):
    with open(src, "r") as src_file:
        reader = csv.reader(src_file)
        for row in reader:
            controlNo = row[0]
            isbns = row[1].split(";")
            norm_isbns = []
            for i in isbns:
                isbn = normalize_isbn(i)
                if isbn:
                    norm_isbns.append(isbn)
            if norm_isbns:
                save2csv(dst, [controlNo, ";".join(norm_isbns)])


if __name__ == "__main__":
    src = "../dump/isbns.csv"
    dst = "../dump/isbns_prepped.csv"
    prep_isbns(src, dst)
