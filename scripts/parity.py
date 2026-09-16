#!/usr/bin/env python3
"""Run concrete compatibility cases; never promote host/model claims from unit tests."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

CASES={
    'loopy.native-save': ['test_loopy_native_text_roundtrip_without_schema','test_save_preserves_foreign_crlf_bytes','test_stale_native_save_does_not_write','test_native_explicit_update_preserves_sibling','test_save_rejects_secret_shaped_input'],
    'loopy.native-reuse': ['test_legacy_markdown_quotes_read_and_search','test_structured_and_native_saved_loops_coexist','test_prompt_cannot_inject_structured_loop_entry'],
    'loopy.find-client': ['test_live_discovery_matches_body_and_limits_three','test_provider_failure_is_not_published_absence','test_catalog_cannot_supply_other_origin','test_catalog_invalid_shape_and_duplicates_rejected'],
    'loopy.compare-client':['test_compare_exposes_unknowns_without_inventing_authority'],
    'loopy.publish-client':['test_publish_preview_checks_live_overlap_but_never_submits','test_publish_permission_cannot_be_smuggled_into_candidate','test_publish_unavailable_provider_blocks_before_submission','test_publication_readback_binds_exact_prompt'],
    'eog.observation-admission':['test_actual_command_observation_and_stale_subject','test_failed_command_never_becomes_success','test_fake_or_tampered_observations_fail_closed','test_observation_admission_binds_current_git_and_work_owner','test_read_only_library_stdin_rejects_write_and_root_override'],
    'eog.initialization':['test_init_preview_preserves_existing_owner','test_init_stale_write_rejected','test_policy_crlf_and_bom_are_semantically_equal'],
    'eog.native-launcher':['test_native_launcher_runs_real_cli'],
    'eog.procedure-delivery':['test_preserved_reference_integrity_and_no_missing_fallback','test_all_original_operation_routes_reach_detailed_procedures','test_legacy_command_alias_reaches_same_operation','test_refresh_is_bounded_not_full_procedure_dump'],
}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
    rows=[]
    for capability,names in CASES.items():
        ids=['test_absorption.AbsorptionTests.'+n for n in names]
        suite=unittest.defaultTestLoader.loadTestsFromNames(ids)
        result=unittest.TextTestRunner(stream=sys.stderr,verbosity=0).run(suite)
        rows.append({'capability':capability,'tests':ids,'result':'passed' if result.wasSuccessful() else 'failed',
                     'kind':'local_operation_or_provider_fixture', 'native_host_verified':False,'model_behavior_verified':False})
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('*.py'))}
    report={'schema':'eog-parity-run-1','source_sha256':sources,'results':rows,
            'upstream_local_runtime_imported':False,
            'replacement_ready':False,
            'limits':'Client semantics under explicit local/provider fixtures. Procedure delivery is not model behavior; actual host loading and service publication are separate observations.'}
    raw=json.dumps(report,indent=2)+'\n'
    if args.output:args.output.write_text(raw,encoding='utf-8')
    else:print(raw,end='')
    return 0 if all(r['result']=='passed' for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
