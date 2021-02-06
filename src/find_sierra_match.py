"""
This module uses BPL Solr to query for matches in Sierra
"""
import csv
import json
import os
import time

from bookops_bpl_solr import SolrSession

from utils import save2csv


def make_control_no_request(control_no, client_id, endpoint):
    """
    returns author, title, publication, and Sierra bib number
    """

    with SolrSession(authorization=client_id, endpoint=endpoint) as session:
        payload = {
            "q": f'ss_marc_tag_001:{control_no} AND collection:"Brooklyn Collection"',
            "fq": "ss_type:catalog",
            "start": 0,
            "rows": 5,
        }
        response = session._send_request(payload=payload)
        return response


def make_isbns_request(isbns, client_id, endpoint):
    """
    returns author, title, publication, and Sierra bib number
    """

    with SolrSession(authorization=client_id, endpoint=endpoint) as session:
        isbn_list = " OR  ".join(isbns)
        payload = {
            "q": f'isbn:({isbn_list}) AND collection:"Brooklyn Collection"',
            "fq": "ss_type:catalog",
            "start": 0,
            "rows": 5,
        }
        response = session._send_request(payload=payload)
        return response


def parse_response(response, control_no):
    print(f"{response.url} = {response.status_code}")
    if response.status_code == 200:
        jres = response.json()
        hits = jres["response"]["numFound"]
        if hits > 0:
            doc = jres["response"]["docs"][0]
            title = doc["title"]
            try:
                author = doc["author_raw"]
            except KeyError:
                author = ""
            matType = doc["material_type"]
            try:
                callNumber = doc["call_number"]
            except KeyError:
                callNumber = ""
            try:
                isbn = ",".join(doc["isbn"])
            except KeyError:
                isbn = ""
            try:
                publisher = doc["publisher"]
            except KeyError:
                publisher = ""
            bid = f"b{doc['id']}a"

            save2csv(
                "../dump/oclc-match.csv",
                [
                    control_no,
                    bid,
                    hits,
                    title,
                    author,
                    publisher,
                    isbn,
                    callNumber,
                    matType,
                ],
            )
        else:
            save2csv("../dump/oclc-no-match.csv", [control_no])

    else:
        print(f"Error on {control_no}. Status code {response.status_code}")
        raise


def query_control_nos(control_nos_fh):
    creds_fh = os.path.join(os.environ["USERPROFILE"], ".bpl-solr/bpl-solr-prod.json")
    with open(creds_fh, "r") as credfile:
        cred = json.load(credfile)
    with open(control_nos_fh, "r") as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for r in reader:
            i += 1
            control_no = r[0]
            if control_no:
                res = make_control_no_request(
                    control_no, cred["client_key"], cred["endpoint"]
                )
                parse_response(res, control_no)
                time.sleep(0.5)
            # if i >= 5:
            #     break


def query_isbns(isbn_fh):
    creds_fh = os.path.join(os.environ["USERPROFILE"], ".bpl-solr/bpl-solr-prod.json")
    with open(creds_fh, "r") as credfile:
        cred = json.load(credfile)
    with open(isbn_fh, "r") as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for r in reader:
            i += 1
            control_no = r[0]
            isbns = r[1].split(";")
            res = make_isbns_request(isbns, cred["client_key"], cred["endpoint"])
            parse_response(res, control_no)
            time.sleep(0.5)

            # if i >= 5:
            #     break


if __name__ == "__main__":
    # fh = "../dump/oclc-controlNos.csv"
    # query_control_nos(fh)
    fh = "../dump/isbns_prepped.csv"
    query_isbns(fh)
