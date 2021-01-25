"""
MARC manipulation functions
"""


from pymarc import MARCReader, Field
import os


def save2marc(dst_fh, bib):
    with open(dst_fh, "ab") as marcfile:
        marcfile.write(bib.as_marc())


def add_missing_001(marcfile):
    """
    adds 001 with OCLC control # if missing based on 035$a value
    """

    with open(marcfile, "rb") as file:
        missing = 0
        cbhNo = 0
        reader = MARCReader(file)
        for bib in reader:
            controlNo = bib.get_fields("001")
            if not controlNo:
                missing += 1
                found = False
                t035 = bib.get_fields("035")
                for t in t035:
                    if "(OCoLC)" in t["a"]:
                        value = t["a"][7:].strip()
                        if "ocm" in value.lower() or "ocn" in value.lower():
                            # prefix exists
                            found = True
                            controlNo = value[3:]
                            break
                        elif "on" in value.lower():
                            controlNo = value[2:]
                            found = True
                            break
                        else:
                            controlNo = value
                            found = True
                            break

                if found is False:
                    # no oclc # found, create one
                    cbhNo += 1
                    cbh_digits = f"{cbhNo}".zfill(6)
                    controlNo = f"cbh-{cbh_digits}"

                    nyuNo = bib["029"]["b"]
                    # print(f"{found}-{controlNo}-{nyuNo}")
                bib.add_ordered_field(Field(tag="001", data=controlNo))

            # add prefixes
            try:
                controlNo = bib["001"].data
            except AttributeError:
                print(bib)
            if "cbh" not in controlNo:
                new_value = None
                lengh = len(controlNo)
                c_digits = controlNo.isdigit()
                if not c_digits:
                    print(f"Found invalid oclc #: {bib['029']['b']}")
                if lengh < 8:
                    controlNo = controlNo.zfill(8)
                    # print(f"zfill: {controlNo}")
                    new_value = f"ocm{controlNo}"
                elif lengh == 8:
                    new_value = f"ocm{controlNo}"
                elif lengh == 9:
                    new_value = f"ocn{controlNo}"
                elif lengh >= 10:
                    new_value = f"on{controlNo}"

                if not new_value:
                    print(f"Error adding prefix on bib: {bib['29']['b']}")

                bib["001"].data = new_value

            # save new control number
            save2marc("../dump/kbhs_bib_all_20201016-utf8-t001.mrc", bib)


if __name__ == "__main__":
    fh = "../dump/kbhs_bib_all_20201016-utf8.mrc"
    add_missing_001(fh)
