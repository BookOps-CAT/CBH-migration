"""
This module splits marc file into finding aid bibs and the rest
"""

from pymarc import MARCReader

from utils import save2csv


def create_finding_aids_list(marcfile, csvfile):
    with open(marcfile, "rb") as file:
        reader = MARCReader(file)
        for bib in reader:
            if "960" in bib:
                scode = bib["960"]["l"][2:]
                if scode == "aam":
                    control_no = bib["001"].data
                    aleph_no = bib["029"]["b"]
                    author = bib.author()
                    title = bib.title()
                    call_no = bib["099"].value()
                    url = bib["856"]["u"]
                    save2csv(
                        csvfile, [control_no, aleph_no, call_no, title, author, url]
                    )

            else:
                print(f"bib {bib['001'].data} has no items!!")


if __name__ == "__main__":
    marcfile = "../dump/kbhs_bib_all_20201016-utf8.mrc"
    csvfile = "../dump/finding_aids_list.cvs"
    create_finding_aids_list(marcfile, csvfile)
