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

    bug_ids_per_component = defaultdict(list)
    for bug in bugs:
        bug_ids_per_component[bug["component"]].append(bug["id"])
    number_of_bugs_per_component = {
        component: len(bug_ids_per_component[component])
        for component in bug_ids_per_component.keys()
    }
    print(number_of_bugs_per_component)



def _fetch_bugs():
    bugs = []
    for product_component in _PRODUCT_COMPONENTS_TO_MONITOR:
        query_params = {
            "limit": 0,
            "include_fields": "id,summary,product,component,severity",
            "resolution": "---",
            "bug_severity": ["--", "normal", "N/A"],
        }
        query_params.update(product_component)
        req = requests.get(f"{_BMO_REST_ENDPOINT}/bug", params=query_params)
        req.raise_for_status()
        bugs.extend(req.json()["bugs"])

    return bugs


__name__ == "__main__" and main()
