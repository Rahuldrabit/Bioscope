"""Hard-stop checks that a planner cannot override."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SafetyVerdict:
    status: str
    message: str


class EducationalSafetyPolicy:
    _urgent_terms = (
        "difficulty breathing",
        "cannot breathe",
        "rapidly spreading rash",
        "facial swelling",
        "blistering rash",
        "rash with fever",
    )
    _restricted_terms = ("diagnose", "dosage", "dose", "stop taking", "prescribe")

    def preflight(self, question: str) -> SafetyVerdict:
        normalized = question.lower()
        if any(term in normalized for term in self._urgent_terms):
            return SafetyVerdict(
                status="SAFETY_ESCALATION",
                message=(
                    "This may need urgent in-person medical assessment. "
                    "BioScope cannot assess it remotely."
                ),
            )
        if any(term in normalized for term in self._restricted_terms):
            return SafetyVerdict(
                status="LIMITED_ANSWER",
                message=(
                    "BioScope provides general education, not diagnosis, dosing, prescribing, "
                    "or medication-change advice."
                ),
            )
        return SafetyVerdict(status="ALLOWED", message="Educational exploration may proceed.")
