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


def has_related_bib(bib):
    if bib.get_fields("LKR") == []:
        return False
    else:
        return True


def process_analytic_bibs(marc_fh):
    with open(marc_fh, "rb") as marcfile:
        reader = MARCReader(marcfile)
        abibs = 0
        for bib in reader:
            if has_analytic_item(bib):
                abibs += 1
                # print(bib["001"].data)
                found_regular = False
                found_analytic = False
                for tag in bib.get_fields("Z30"):
                    if tag["0"].upper() == "N":
                        found_regular = True
                    elif tag["0"].upper() == "Y":
                        found_analytic = True
                if not found_regular and found_analytic:
                    print(bib["001"].data)

        print(f"found {abibs} analytic bibs")


def create_960_tag(z30, controlNo):
    # new subfields
    subfields = []

    # analytic item record?
    if z30["0"].upper() == "Y":
        analytic = True
    else:
        analytic = False
    if analytic:
        subfields.extend(["j", "analytic item"])

    # location and shelf code
    ccode = z30["2"].upper()
    if ccode == "MAIN":
        scode = "mos"
    elif ccode == "CSTAC":
        scode = "cst"
    elif ccode == "SPCL":
        scode = "spc"
    elif ccode == "FLMAP":
        scode = "flm"
    elif ccode == "ARMS":
        scode = "aam"
    elif ccode == "REF":
        scode = "arf"
    elif ccode == "MFORM":
        scode = "mfo"
    elif ccode == "REFD":
        scode = "drf"
    elif ccode == "ATLAS":
        scode = "atl"
    elif ccode == "STAFR":
        scode = "srf"
    elif ccode == "RARE":
        scode = "rbk"
    elif ccode == "FDMAP":
        scode = "fdm"
    elif ccode == "FOLIO":
        scode = "fol"
    elif ccode == "CBDSK":
        scode = "cbd"
    else:
        print(f"shelf code error: {controlNo}")
        scode = None

    subfields.extend(["l", f"91{scode}"])

    # subfield $4
    if "4" in z30:
        value = z30["4"].strip()
        subfields.extend(["n", value])

    # subfield $5 - barcode
    value = z30["5"].strip()
    subfields.extend(["i", value])

    # subfield $7 - OPAC note
    if "7" in z30:
        value = z30["7"].strip()
        subfields.extend(["n", value])

    # Sierra status field
    if "p" in z30:
        value = z30["p"].strip().upper()
        if value == "AR":
            status = "g"
        elif value == "LB":
            status = "g"
        elif value == "MI":
            status = "m"
        elif value == "RP":
            status = "r"
    else:
        status = "4"
    subfields.extend(["s", status])

    # Sierra stat categroy
    subfields.extend(["q", "40"])

    # Sierra price
    subfields.extend(["p", "20.00"])

    # Sierra OPAC label
    if scode == "fol":
        value = "q"
    elif scode == "rbk":
        value = "5"
    else:
        value = "4"
    subfields.extend(["o", value])

    # item call number
    icall = []
    if "h" in z30:
        icall.append(f"|h{z30['h'].strip()}")
    if "i" in z30:
        icall.append(f"|i{z30['i'].strip()}")
    if "j" in z30:
        icall.append(f"|j{z30['j'].strip()}")
    if "k" in z30:
        icall.append(f"|k{z30['k'].strip()}")
    if "m" in z30:
        icall.append(f"|m{z30['m'].strip()}")
    subfields.extend(["g", "".join(icall)])

    if "Q" in z30:
        value = f"issue date: {z30['Q'].strip()}"
        subfields.extend(["n", value])
    if "R" in z30:
        value = f"expected arrival date: {z30['R'].strip()}"
        subfields.extend(["n", value])
    if "S" in z30:
        value = f"arrival date: {z30['S'].strip()}"
        subfields.extend(["n", value])

    # volume fields
    if "w" in z30:
        value = z30["w"].strip()
        subfields.extend(["v", value])

    return Field(tag="960", indicators=[" ", " "], subfields=subfields)


def is_analytic_item(z30):
    if z30["0"].upper().strip() == "Y":
        return True
    else:
        return False


def call_number(z30):
    subfields = []
    if "h" in z30:
        subfields.extend(["a", z30["h"].strip()])
    if "i" in z30:
        subfields.extend(["b", z30["i"].strip()])
    if "j" in z30:
        subfields.extend(["a", z30["j"].strip()])
    if subfields:
        return Field(tag="099", indicators=[" ", " "], subfields=subfields)


def create_call_number_tag(z30s):
    # evaluate item records to select best LC classification

    deter = dict()

    for z30 in reversed(z30s):
        analytic = is_analytic_item(z30)
        deter[analytic] = z30

    if False in deter:
        call_tag = call_number(deter[False])
    else:
        call_tag = call_number(deter[True])

    return call_tag


def add_item_records(marc_in, marc_out):
    with open(marc_in, "rb") as marcfile:
        reader = MARCReader(marcfile)
        no_call = 0
        no_call_ids = []
        for bib in reader:
            controlNo = bib["001"].data
            z30s = bib.get_fields("Z30")

            for z30 in z30s:
                item_tag = create_960_tag(z30, controlNo)
                # print(z30)
                # item
                bib.add_ordered_field(item_tag)

            calltag = create_call_number_tag(z30s)
            try:
                bib.add_ordered_field(calltag)
            except:
                no_call += 1
                no_call_ids.append((bib["001"].data))

            bib.remove_fields("Z30")

            save2marc(marc_out, bib)

        print(f"Unable to create call number for {no_call} bibs")
        print(no_call_ids)


if __name__ == "__main__":
    src = "../dump/kbhs_bib_all_20201016-utf8.mrc"
    out = "../dump/kbhs_bib_all_20201016-utf8_call-item.mrc"
    # add_missing_001(fh)
    # process_analytic_bibs(fh)
    add_item_records(src, out)
