#!/usr/bin/env python3


import requests

from collections import defaultdict
from itertools import cycle


_BMO_REST_ENDPOINT = "https://bugzilla.mozilla.org/rest"
_PRODUCT_COMPONENTS_TO_MONITOR = (
    {"product": "Release Engineering"}, # All components
    {"product": "Firefox Build System", "component": "Task Configuration"},
)

_TRIAGE_OWNERS_PER_COMPONENT = {
    "Task Configuration": ["ahalberstadt", "jcristau"],
    "Applications: MozharnessCore": ["gbrown"],
    "Applications: Shipit": ["gbustamente"],
    "Firefox-CI Administration": ["bhearsum", "gbrown"],
    "General": ["bhearsum", "jlorenzo", "hneiva"],
    "Release Automation: Bouncer": ["jcristau"],
    "Release Automation: L10N": ["gbustamente"],
    "Release Automation: Other": ["gbrown", "hneiva", "ahalberstadt", "gbrown", "hneiva", "jlorenzo", "gbrown"],
    "Release Automation: Signing": ["gbustamente"],
    "Release Automation: Snap": ["jcristau"],
    "Release Automation: Updates": ["gbustamente"],
    "Release Automation: Uploading": ["jlorenzo"],
    "Release Requests": ["jcristau"],
}
_TRIAGE_OWNERS_PER_COMPONENT = {
    component: cycle(owners)
    for component, owners in _TRIAGE_OWNERS_PER_COMPONENT.items()
}


def main():
    bugs = _fetch_bugs()

    bug_ids_per_triage_owner = defaultdict(list)
    for bug in bugs:
        owner = next(_TRIAGE_OWNERS_PER_COMPONENT[bug["component"]])
        bug_ids_per_triage_owner[owner].append(str(bug["id"]))

    bug_ids_per_component = defaultdict(list)
    for bug in bugs:
        bug_ids_per_component[bug["component"]].append(bug["id"])

    number_of_bugs_per_component = {
        component: len(bug_ids_per_component[component])
        for component in bug_ids_per_component.keys()
    }
    print(number_of_bugs_per_component)


    bugzilla_request_url_per_triage_owner = {
        owner:
        f"https://bugzilla.mozilla.org/buglist.cgi?query_format=advanced&bug_severity=--&bug_severity=normal&bug_severity=N%2FA&bug_id={'%2C'.join(bug_ids)}"
        for owner, bug_ids in bug_ids_per_triage_owner.items()
    }

    for owner, url in bugzilla_request_url_per_triage_owner.items():
        print(owner, url)


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
