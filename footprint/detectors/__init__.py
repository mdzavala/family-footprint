"""Detector registry. Each detector takes a Context and returns a list of Findings.

Add your own detector by writing a function and appending it to DETECTORS.
"""
from . import baseline, challenge

DETECTORS = [
    # Working baseline detectors
    baseline.credential_leak,
    baseline.personal_data_leak,
    baseline.contact_exposed,
    baseline.home_location,
    baseline.account_linkage,
    # Challenge detectors: stubs for you to build (they return [] today)
    challenge.child_identifiable,
    challenge.routine_pattern,
    challenge.voice_clone_risk,
    challenge.impersonation_target,
]


def run_all(ctx):
    findings = []
    for detect in DETECTORS:
        findings.extend(detect(ctx))
    return findings
