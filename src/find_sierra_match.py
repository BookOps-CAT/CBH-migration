"""
This module uses BPL Solr to query for matches in Sierra
"""
import csv
import json
import os
import time

from bookops_bpl_solr import SolrSession

from utils import save2csv


def make_request(control_no, client_id, endpoint):
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


def parse_response(response, control_no):
    print(f"{response.url} = {response.status_code}")
    if response.status_code == 200:
        jres = response.json()
        hits = jres["response"]["numFound"]
        if hits > 0:
            doc = jres["response"]["docs"][0]
            title = doc["title"]
            author = doc["author_raw"]
            matType = doc["material_type"]
            callNumber = doc["call_number"]
            try:
                isbn = ",".join(doc["isbn"])
            except KeyError:
                isbn = ""
            publisher = doc["publisher"]
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
                res = make_request(control_no, cred["client_key"], cred["endpoint"])
                parse_response(res, control_no)
                time.sleep(0.5)
            # if i >= 5:
            #     break


if __name__ == "__main__":
    fh = "../dump/oclc-controlNos.csv"

    query_control_nos(fh)
