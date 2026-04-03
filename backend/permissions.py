from enum import Enum


class AccessLevel(str, Enum):
    FULL = "FULL"
    RESTRICTED = "RESTRICTED"
    HIDDEN = "HIDDEN"


# Role-based default access levels per category.
# GP has no HIDDEN fields — they always know every category exists.
# HIDDEN means the category is silently omitted for that role.
# RESTRICTED means the role sees the category exists but not the value.

ROLE_DEFAULTS = {
    "GP": {
        "medications":     AccessLevel.FULL,
        "allergies":       AccessLevel.FULL,
        "mental_health":   AccessLevel.FULL,
        "musculoskeletal": AccessLevel.FULL,
        "nutrition":       AccessLevel.FULL,
        "substance_use":   AccessLevel.FULL,
        "sexual_health":   AccessLevel.FULL,
    },
    "PHYSIO": {
        "medications":     AccessLevel.FULL,
        "allergies":       AccessLevel.FULL,
        "musculoskeletal": AccessLevel.FULL,
        "nutrition":       AccessLevel.RESTRICTED,
        "mental_health":   AccessLevel.RESTRICTED,
        "substance_use":   AccessLevel.HIDDEN,
        "sexual_health":   AccessLevel.HIDDEN,
    },
    "DIETITIAN": {
        "medications":     AccessLevel.FULL,
        "allergies":       AccessLevel.FULL,
        "nutrition":       AccessLevel.FULL,
        "musculoskeletal": AccessLevel.RESTRICTED,
        "mental_health":   AccessLevel.RESTRICTED,
        "substance_use":   AccessLevel.RESTRICTED,
        "sexual_health":   AccessLevel.HIDDEN,
    },
    "PSYCHOLOGIST": {
        "medications":     AccessLevel.FULL,
        "allergies":       AccessLevel.FULL,
        "mental_health":   AccessLevel.FULL,
        "substance_use":   AccessLevel.FULL,
        "sexual_health":   AccessLevel.RESTRICTED,
        "nutrition":       AccessLevel.RESTRICTED,
        "musculoskeletal": AccessLevel.HIDDEN,
    },
}

# Human-readable labels for each category — included in unavailable field responses
# so SensitiveField.jsx can render the label without its own lookup table.
CATEGORY_LABELS = {
    "medications":     "Medications",
    "allergies":       "Allergies",
    "mental_health":   "Mental Health",
    "musculoskeletal": "Musculoskeletal",
    "nutrition":       "Nutrition & Dietetics",
    "substance_use":   "Substance Use",
    "sexual_health":   "Sexual Health",
}


def filter_summary(raw_summary: dict, role: str, opted_out_categories: set, practitioner_restricted_categories: set) -> dict:
    """
    Apply permission logic to a raw summary and return only what this role is allowed to see.

    raw_summary: dict mapping category -> value (value is None if no record exists)
    role: practitioner role string (GP, PHYSIO, DIETITIAN, PSYCHOLOGIST)
    opted_out_categories: set of categories the patient has opted out of sharing
    practitioner_restricted_categories: set of categories where the practitioner has allow_summary=False

    Check order per field:
      1. no_record — nothing to restrict if data doesn't exist
      2. practitioner_restricted — active privacy decision by the practitioner
      3. patient_restricted — patient consent, except for roles with FULL access
         (e.g. PSYCHOLOGIST and GP can see mental_health even if patient opts out)
      4. role access level — HIDDEN skips silently, RESTRICTED returns reason
      5. FULL — return value
    """
    role_defaults = ROLE_DEFAULTS.get(role, {})
    result = {}

    for category, value in raw_summary.items():
        label = CATEGORY_LABELS.get(category, category)
        access_level = role_defaults.get(category, AccessLevel.HIDDEN)

        # 1. No record
        if value is None:
            if access_level == AccessLevel.HIDDEN:
                continue
            result[category] = {"visible": False, "reason": "no_record", "label": label}
            continue

        # 2. Practitioner restricted
        if category in practitioner_restricted_categories:
            if access_level == AccessLevel.HIDDEN:
                continue
            result[category] = {"visible": False, "reason": "practitioner_restricted", "label": label}
            continue

        # 3. Patient restricted — FULL access roles bypass this check
        if category in opted_out_categories and access_level != AccessLevel.FULL:
            if access_level == AccessLevel.HIDDEN:
                continue
            result[category] = {"visible": False, "reason": "patient_restricted", "label": label}
            continue

        # 4. Role access level
        if access_level == AccessLevel.HIDDEN:
            continue
        if access_level == AccessLevel.RESTRICTED:
            result[category] = {"visible": False, "reason": "role_restricted", "label": label}
            continue

        # 5. FULL
        result[category] = {"visible": True, "value": value, "label": label}

    return result
