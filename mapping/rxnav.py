from collections import namedtuple
from typing import List, Optional
import requests
from requests import Response
import time
import logging

logger = logging.getLogger("approx_match")

Candidate = namedtuple('Candidate', ['rxcui', 'score'])


class RxNavResponse:
    def __init__(self, query: str, candidates: List[Candidate]):
        self.query = query
        self.candidates = candidates

    def __repr__(self):
        return f"Query: {self.query} -- Candidates: {self.candidates}"

    def csv_format(self):
        return f"{self.query},{self.candidates[0].rxcui},{self.candidates[0].score}\n"


def approx_match(query: str, max_entries=1, sleep_time=1) -> RxNavResponse:
    candidates: List[Candidate] = []

    # Ensure valid URL for RxNav
    query = query.replace("\n", "").strip()
    url_query: str = query.replace(" ", "%")

    response = None
    while response is None:
        try:
            response: Optional[Response] = requests.get(
                f"http://localhost:4000/REST/approximateTerm.json?term={url_query}&maxEntries={max_entries}")
            break
        except ConnectionRefusedError:
            print(f"Connection refused by server, sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            continue

    if response.status_code != 200:
        print(f"Something went wrong... Status code = {response.status_code}")
    j_res = response.json()
    try:
        j_candidates = j_res["approximateGroup"]["candidate"]
    except KeyError:
        logger.info(f"Could not find any candidates for query: {query}.")
        return RxNavResponse(query=query, candidates=[Candidate("NULL", 0)])
    for j_candidate in j_candidates:
        candidates.append(Candidate(j_candidate["rxcui"], int(j_candidate["score"])))
    return RxNavResponse(query=query, candidates=candidates)
