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


def has_oclc_controlNo(bib):
    """
    identifies if 001 is oclc control number or not
    """
    controlNo = bib["001"].data
    if "ocn" in controlNo or "ocm" in controlNo or "on" in controlNo:
        return True
    else:
        return False


def remove_oclc_prefix_from_035(marcfile):
    with open(marcfile, "rb") as file:
        reader = MARCReader(file)
        manip_count = 0
        for bib in reader:
            t035 = bib.get_fields("035")
            for t in t035:
                value = None
                if "a" in t:
                    if "(OCoLC)" in t["a"]:
                        # print("trigger")
                        if "ocm" in t["a"].lower() or "ocn" in t["a"].lower():
                            manip_count += 1
                            value = t["a"][10:]
                            bib[""]
                        elif "on" in t["a"].lower():
                            manip_count += 1
                            value = t["a"][9:]
                            print(f"{value}-{bib['029']['b']}")
        print(f"Finished fixing {manip_count} bibs.")


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


def find_related_bib(marc_src, aleph_control_no):
    with open(marc_src, "rb") as marcfile:
        reader = MARCReader(marcfile)
        for bib in reader:
            if aleph_control_no == bib["029"]["b"]:
                return bib


def construct_related_title(title_tag):
    ind2 = int(title_tag.indicator2)
    main_title = title_tag["a"][ind2:]
    main_title = main_title.replace("/", "").replace(":", "").strip()
    if main_title[-1] == ".":
        main_title = main_title[:-1].strip()
    first_letter = main_title[0].upper()
    main_title = f"{first_letter}{main_title[1:]}"
    return main_title


def construct_publishing_data(bib):
    if "260" in bib:
        return bib["260"].value()
    elif "264" in bib:
        return bib["264"].value()
    else:
        return None


def add_787_tag(bib, marc_src, marc_dst):
    """
    Creates relationship between analytic item records and "main" bibs using 787 tag
    """
    if has_related_bib(bib):
        lkrs = bib.get_fields("LKR")
        for lkr in lkrs:
            aleph_control_no = lkr["b"]
            related_bib = find_related_bib(marc_src, aleph_control_no)
            if related_bib is not None:
                subfields = []
                related_author = related_bib.author()
                if related_author is not None:
                    subfields.extend(["a", related_author])
                related_title = construct_related_title(related_bib["245"])
                subfields.extend(["t", related_title])
                publishing_data = construct_publishing_data(bib)
                if publishing_data:
                    subfields.extend(["d", publishing_data])
                subfields.extend(["w", related_bib["001"].data])
                t787 = Field(tag="787", indicators=["1", " "], subfields=subfields)
                bib.add_ordered_field(t787)

            else:
                print(f"Error: unable to find aleph control no: {aleph_control_no}")

        bib.remove_fields("LKR")
        save2marc(marc_dst, bib)
    else:
        # simply save record as is
        save2marc(marc_dst, bib)


def add_949_command_line(marc_src, marc_dst):
    with open(marc_src, "rb") as marcfile:
        reader = MARCReader(marcfile)
        for bib in reader:
            scode = bib["960"]["l"]
            jcode = bib["960"]["g"]
            if "mfo" in scode:
                bibformat = "n"
            elif "BOOK" in jcode:
                bibformat = "a"
            elif "MAP" in jcode:
                bibformat = "e"
            elif "MIXED" in jcode:
                bibformat = "p"
            elif "ISSUE" in jcode:
                bibformat = "q"
            elif "ISSMX" in jcode:
                bibformat = "p"
            elif "ISSBD" in jcode:
                bibformat = "q"
            elif "SCORE" in jcode:
                bibformat = "c"
            elif "GRAPH" in jcode:
                bibformat = "p"
            elif "ERES" in jcode:
                bibformat = "x"
            elif "SOUND" in jcode:
                bibformat = "i"
            elif "VIDEO" in jcode:
                bibformat = "h"

            command_tag = Field(
                tag="949",
                indicators=[" ", " "],
                subfields=["a", f"*b2={bibformat};bn=91;"],
            )
            bib.add_ordered_field(command_tag)
            save2marc(marc_dst, bib)


def determine_item_format(bib_format):
    if bib_format == "a":
        return "a"
    elif bib_format in ("nepc"):
        return "i"
    elif bib_format == "q":
        return "f"
    elif bib_format == "x":
        return "1"
    elif bib_format in ("ihv"):
        return "d"
    else:
        print(bib_format)


def add_item_format(src, out):
    with open(src, "rb") as marcfile:
        reader = MARCReader(marcfile)
        n = 0
        for bib in reader:
            n += 1
            bib_format = bib["949"]["a"][4]
            item_format = determine_item_format(bib_format)
            for i in bib.get_fields("960"):
                i.add_subfield("r", item_format)
            save2marc(out, bib)
            # print(bib)
            # if n > 5:
            #     break


# def populate_internal_note(marc_src, marc_dst):
#     """
#     Fixes carried over data from Aleph that is not mapped correctly by Sierra load table.
#     This elements were previously recorded in $j and $g, will be moved into $n ($x in Sierra).
#     """
#     with open(marc_src, "rb") as marcfile:
#         reader = MARCReader(marcfile)
#         for bib in reader:
#             items = bib.get_fields("960")
#             for item in items:
#                 subJ = None
#                 subG = None
#                 subN = None
#                 if "j" in item:
#                     subJ = item["j"]
#                 if "g" in item:
#                     subG = item["g"]
#                 if "n" in item:
#                     subN = item["n"]
#                 if any(subJ, subG, subN):
#                     item["n"] =


if __name__ == "__main__":
    src = "../dump/kbhs_bib_all_20201016-utf8.mrc"
    out = "../dump/kbhs_bib_all_20201016-utf8-item_format_fix.mrc"
    # out = "../dump/kbhs_bib_all_20201016-utf8_command_tag.mrc"
    # add_missing_001(src)
    # process_analytic_bibs(fh)
    # add_item_records(src, out)

    # with open(src, "rb") as marcfile:
    #     reader = MARCReader(marcfile)
    #     for bib in reader:
    #         add_787_tag(bib, src, out)

    # add_949_command_line(src, out)
    add_item_format(src, out)
