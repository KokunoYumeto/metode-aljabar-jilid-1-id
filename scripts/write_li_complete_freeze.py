#!/usr/bin/env python3
"""Write the one exact complete-Li translation freeze after final promotion."""

from __future__ import annotations

import json
import os
from collections import Counter

from check_li_complete_translation import (
    AUTHORITY,
    FILES,
    FREEZE,
    HAN,
    TARGET,
    active_text,
    balanced_braces,
    identity,
    require,
    topology,
)


def main() -> int:
    files: list[dict[str, object]] = []
    aggregate = Counter()
    for filename in FILES:
        source = AUTHORITY / filename
        target = TARGET / filename
        require(source.is_file() and target.is_file(), f"missing source pair: {filename}")
        source_active = active_text(source.read_text(encoding="utf-8"))
        target_active = active_text(target.read_text(encoding="utf-8"))
        require(not HAN.search(target_active), f"active Han residue: {filename}")
        require(balanced_braces(target_active), f"unbalanced braces: {filename}")
        source_topology = topology(source_active)
        target_topology = topology(target_active)
        require(
            target_topology["environment_starts"] == target_topology["environment_ends"],
            f"unbalanced target environments: {filename}",
        )
        aggregate.update(target_topology)
        files.append(
            {
                "filename": filename,
                "authority": identity(source),
                "target": identity(target),
                "authority_topology": source_topology,
                "target_topology": target_topology,
            }
        )
    require(aggregate["top_level_exercises"] == 161, "exercise census drift")
    require(aggregate["hints"] == 51, "hint census drift")
    record = {
        "schema": "o013.li-complete-translation-freeze.v1",
        "result": "pass",
        "authority_commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "authority_tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
        "files": files,
        "target_aggregate_topology": dict(aggregate),
    }
    payload = (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = FREEZE.with_name(FREEZE.name + ".tmp")
    require(not temporary.exists(), f"stale temporary: {temporary}")
    temporary.write_bytes(payload)
    require(temporary.read_bytes() == payload, "freeze write verification failed")
    os.replace(temporary, FREEZE)
    print(json.dumps({"result": "PASS", "path": str(FREEZE), "bytes": len(payload)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
