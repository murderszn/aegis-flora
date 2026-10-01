#!/usr/bin/env python3
"""Dependency-free checks for Aegis art manifest structure and local source paths.

This is a deliberately small project-specific validator, not a complete JSON
Schema implementation. See asset-manifest.schema.json for the fuller contract.
"""

import json
import re
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name("asset-manifest.json")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
ASSET_STATUSES = {
    "reference_only", "prototype_present", "staged_private", "cleanup",
    "review", "accepted", "rejected",
}
PRODUCTION_STATUSES = {
    "not_generated", "prototype_only", "generated_unreviewed",
    "cleanup_in_progress", "approved",
}
MATERIAL_STATUSES = {
    "reference_only", "not_acquired", "staged_private", "cleanup",
    "review", "accepted",
}


class ManifestError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ManifestError(message)


def require_object(value, where, keys):
    require(isinstance(value, dict), f"{where}: expected an object")
    missing = sorted(set(keys) - value.keys())
    require(not missing, f"{where}: missing required field(s): {', '.join(missing)}")


def require_string(value, where, nonempty=True):
    require(isinstance(value, str), f"{where}: expected a string")
    if nonempty:
        require(bool(value.strip()), f"{where}: must not be empty")


def require_id(value, where):
    require_string(value, where)
    require(ID_PATTERN.fullmatch(value) is not None, f"{where}: invalid stable ID {value!r}")


def require_choice(value, choices, where):
    require(isinstance(value, str) and value in choices,
            f"{where}: unsupported value {value!r}")


def validate_repo_path(value, where, must_exist):
    require_string(value, where)
    relative = PurePosixPath(value)
    require(not relative.is_absolute(), f"{where}: path must be repository-relative")
    require(".." not in relative.parts, f"{where}: parent traversal is not allowed")
    resolved = (ROOT / Path(*relative.parts)).resolve()
    require(resolved == ROOT or ROOT in resolved.parents, f"{where}: path escapes repository")
    if must_exist:
        require(resolved.is_file(), f"{where}: file does not exist: {value}")
    else:
        require(value.startswith("Unity/Assets/Aegis/Art/"),
                f"{where}: expected destination under Unity/Assets/Aegis/Art/")


def validate_asset(asset, index, seen_ids):
    where = f"assets[{index}]"
    required = (
        "id", "name", "category", "status", "productionStatus", "references",
        "existingPrototypeFiles", "targetPath", "meshSource", "license", "review",
    )
    require_object(asset, where, required)
    require_id(asset["id"], where + ".id")
    require(asset["id"] not in seen_ids, f"{where}: duplicate id {asset['id']!r}")
    seen_ids.add(asset["id"])
    require_string(asset["name"], where + ".name")
    require_choice(asset["status"], ASSET_STATUSES, where + ".status")
    require_choice(asset["productionStatus"], PRODUCTION_STATUSES, where + ".productionStatus")
    validate_repo_path(asset["targetPath"], where + ".targetPath", must_exist=False)

    for field in ("references", "existingPrototypeFiles"):
        values = asset[field]
        require(isinstance(values, list), f"{where}.{field}: expected an array")
        for path_index, value in enumerate(values):
            validate_repo_path(value, f"{where}.{field}[{path_index}]", must_exist=True)

    mesh = asset["meshSource"]
    require_object(mesh, where + ".meshSource", ("provider", "taskId", "promptRecord", "settingsRecord"))
    require_choice(mesh["provider"], {"Meshy", "Blender", "none"}, where + ".meshSource.provider")
    for key in ("taskId", "promptRecord", "settingsRecord", "rawExportPrivatePath"):
        if key in mesh:
            require(mesh[key] is None or isinstance(mesh[key], str),
                    f"{where}.meshSource.{key}: expected string or null")

    license_record = asset["license"]
    require_object(license_record, where + ".license",
                   ("provider", "record", "redistribution", "status"))
    require_choice(license_record["provider"], {
        "project_owned_reference", "Meshy", "Poliigon", "mixed", "unknown", "none",
    }, where + ".license.provider")
    require_choice(license_record["redistribution"], {
        "allowed", "restricted", "not_applicable", "unverified",
    }, where + ".license.redistribution")
    require_choice(license_record["status"], {
        "not_acquired", "needs_review", "verified", "not_applicable",
    }, where + ".license.status")
    require(license_record["record"] is None or isinstance(license_record["record"], str),
            f"{where}.license.record: expected string or null")

    review = asset["review"]
    require_object(review, where + ".review", ("owner", "notes", "approvedBy", "approvedDate"))
    require_string(review["owner"], where + ".review.owner", nonempty=False)
    require_string(review["notes"], where + ".review.notes", nonempty=False)
    require(review["approvedBy"] is None or isinstance(review["approvedBy"], str),
            f"{where}.review.approvedBy: expected string or null")
    require(review["approvedDate"] is None or isinstance(review["approvedDate"], str),
            f"{where}.review.approvedDate: expected date string or null")


def validate_material_family(material, index, seen_ids):
    where = f"materialFamilies[{index}]"
    required = (
        "id", "name", "provider", "status", "searchBrief", "licenseStatus",
        "stagingPolicy", "targetPath",
    )
    require_object(material, where, required)
    require_id(material["id"], where + ".id")
    require(material["id"] not in seen_ids, f"{where}: duplicate id {material['id']!r}")
    seen_ids.add(material["id"])
    require_string(material["name"], where + ".name")
    require_choice(material["provider"], {"Poliigon", "project_authored", "mixed"}, where + ".provider")
    require_choice(material["status"], MATERIAL_STATUSES, where + ".status")
    require_choice(material["licenseStatus"], {"not_acquired", "needs_review", "verified"}, where + ".licenseStatus")
    require_choice(material["stagingPolicy"], {
        "private_only", "license_permits_runtime_files", "project_authored",
    }, where + ".stagingPolicy")
    require(isinstance(material["searchBrief"], list), f"{where}.searchBrief: expected an array")
    for brief_index, brief in enumerate(material["searchBrief"]):
        require_string(brief, f"{where}.searchBrief[{brief_index}]")
    validate_repo_path(material["targetPath"], where + ".targetPath", must_exist=False)


def validate(data):
    require_object(data, "manifest", ("manifestVersion", "policy", "assets", "materialFamilies"))
    require(data["manifestVersion"] == 1, "manifest.manifestVersion: expected 1")
    policy = data["policy"]
    require_object(policy, "manifest.policy", ("noPaidCalls", "allowRestrictedRawFilesInPublicRepo", "unityArtRoot"))
    require(policy["noPaidCalls"] is True, "manifest.policy.noPaidCalls must remain true")
    require(policy["allowRestrictedRawFilesInPublicRepo"] is False,
            "manifest.policy.allowRestrictedRawFilesInPublicRepo must remain false")
    require(policy["unityArtRoot"] == "Unity/Assets/Aegis/Art",
            "manifest.policy.unityArtRoot must point to Unity/Assets/Aegis/Art")
    if "privateStagingRoot" in policy:
        require_string(policy["privateStagingRoot"], "manifest.policy.privateStagingRoot")

    assets = data["assets"]
    materials = data["materialFamilies"]
    require(isinstance(assets, list) and assets, "manifest.assets: expected a non-empty array")
    require(isinstance(materials, list) and materials,
            "manifest.materialFamilies: expected a non-empty array")
    ids = set()
    for index, asset in enumerate(assets):
        validate_asset(asset, index, ids)
    for index, material in enumerate(materials):
        validate_material_family(material, index, ids)
    return len(assets), len(materials)


def main():
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        assets, materials = validate(data)
    except (OSError, json.JSONDecodeError, ManifestError) as exc:
        print(f"Manifest validation failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Manifest checks passed: {assets} assets and {materials} material families; "
        "required fields, selected values, repository-safe paths, and local reference/prototype files verified."
    )
    print("This command performs project-specific checks; it does not fully evaluate JSON Schema.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
