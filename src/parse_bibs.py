"""
This modules parses Aleph's bibliographic records and outputs selected values into a csv file
"""


from pymarc import MARCReader

from utils import save2csv


TAGS = sorted(["090", "092", "099", "539", "590", "699", "796", "797", "LKR"])


def run(src_marc, out_file):
    save2csv(out_file, TAGS)

    with open(src_marc, "rb") as marcfile:
        reader = MARCReader(marcfile)
        for bib in reader:
            sb = dict()
            for tag in TAGS:
                fields = bib.get_fields(tag)
                for f in fields:
                    sb[tag] = str(f)

                    for t in TAGS:
                        if t not in sb:
                            sb[t] = None
                    row = [sb[t] for t in sorted(sb.keys())]
                    save2csv(out_file, row)


if __name__ == "__main__":
    # src_marc = "./files/kbhs_bib_sample_20201016.mrc"
    src_marc = "./files/kbhs_bib_all_20201016-utf8.mrc"
    out_file = "./files/bib-selected-values.csv"
    run(src_marc, out_file)
