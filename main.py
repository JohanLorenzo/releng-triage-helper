#!/usr/bin/env python3


import requests

from collections import defaultdict


_BMO_REST_ENDPOINT = "https://bugzilla.mozilla.org/rest"
_PRODUCT_COMPONENTS_TO_MONITOR = (
    {"product": "Release Engineering"}, # All components
    {"product": "Firefox Build System", "component": "Task Configuration"},
)


def main():
    bugs = _fetch_bugs()
    triage_owners_per_component = _fetch_triage_owners()

    bug_ids_per_component = defaultdict(list)
    for bug in bugs:
        bug_ids_per_component[bug["component"]].append(bug["id"])
    number_of_bugs_per_component = {
        component: len(bug_ids_per_component[component])
        for component in bug_ids_per_component.keys()
    }
    print(number_of_bugs_per_component)

    number_of_bugs_per_owner = defaultdict(int)
    for component in number_of_bugs_per_component:
        owner = triage_owners_per_component[component]
        number_of_bugs_per_owner[owner] += number_of_bugs_per_component[component]
    print(number_of_bugs_per_owner)


def _fetch_bugs():
    bugs = []
    for product_component in _PRODUCT_COMPONENTS_TO_MONITOR:
        query_params = {
            "limit": 0,
            "include_fields": "id,summary,product,component",
            "resolution": "---",
        }
        query_params.update(product_component)
        req = requests.get(f"{_BMO_REST_ENDPOINT}/bug", params=query_params)
        req.raise_for_status()
        bugs.extend(req.json()["bugs"])

    return bugs


def _fetch_triage_owners():
    triage_owners_per_component = {}
    for product_component in _PRODUCT_COMPONENTS_TO_MONITOR:
        req = requests.get(f"{_BMO_REST_ENDPOINT}/bmo/triage_owners", params=product_component)
        req.raise_for_status()
        resp = req.json()
        for product in resp.keys():
            for component in resp[product].keys():
                triage_owners_per_component[component] = resp[product][component]["triage_owner"]

    return triage_owners_per_component


__name__ == "__main__" and main()
