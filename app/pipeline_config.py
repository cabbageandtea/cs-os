"""Pipeline stage definitions and workflow rules. Single source of truth."""

from dataclasses import dataclass
from enum import Enum

from app.models import PipelineStatus


class RollbackPolicy(str, Enum):
    """Operational law for pipeline stage movement."""

    # Option B — declared policy for CS-OS
    CONTROLLED_ONE_STEP = "controlled_one_step"


# Option B: forward advance max 1 stage; backward rollback max 1 stage; no skipping.
ROLLBACK_POLICY = RollbackPolicy.CONTROLLED_ONE_STEP


@dataclass(frozen=True)
class StageDefinition:
    status: PipelineStatus
    done_criteria: str
    task_titles: tuple[str, ...]


PIPELINE_ORDER: tuple[PipelineStatus, ...] = (
    PipelineStatus.INTAKE,
    PipelineStatus.ANALYSIS,
    PipelineStatus.BUILD,
    PipelineStatus.QA,
    PipelineStatus.REVIEW,
    PipelineStatus.DELIVERED,
)

STAGE_DEFINITIONS: dict[PipelineStatus, StageDefinition] = {
    PipelineStatus.INTAKE: StageDefinition(
        status=PipelineStatus.INTAKE,
        done_criteria=(
            "All required intake fields collected and validated. "
            "Client name, target role, structured experience, and skills are on file."
        ),
        task_titles=("Review intake data",),
    ),
    PipelineStatus.ANALYSIS: StageDefinition(
        status=PipelineStatus.ANALYSIS,
        done_criteria=(
            "LinkedIn and GitHub audited. Portfolio template selected. "
            "Gap analysis and delivery plan documented."
        ),
        task_titles=(
            "Audit LinkedIn profile",
            "Audit GitHub profile",
            "Select portfolio template",
        ),
    ),
    PipelineStatus.BUILD: StageDefinition(
        status=PipelineStatus.BUILD,
        done_criteria=(
            "Portfolio site built. Resume rewritten. "
            "All build-phase deliverables drafted."
        ),
        task_titles=(
            "Build portfolio site",
            "Resume rewrite",
        ),
    ),
    PipelineStatus.QA: StageDefinition(
        status=PipelineStatus.QA,
        done_criteria=(
            "Internal QA checklist complete. Links verified. "
            "Copy, formatting, and deployment readiness confirmed."
        ),
        task_titles=("QA checklist",),
    ),
    PipelineStatus.REVIEW: StageDefinition(
        status=PipelineStatus.REVIEW,
        done_criteria=(
            "Client has reviewed deliverables. Revisions captured and resolved."
        ),
        task_titles=("Client review + revisions",),
    ),
    PipelineStatus.DELIVERED: StageDefinition(
        status=PipelineStatus.DELIVERED,
        done_criteria=(
            "Final assets deployed. Handoff complete. "
            "Client has live URLs and documentation."
        ),
        task_titles=("Deploy + handoff",),
    ),
}

BUILD_WIP_WARNING_THRESHOLD = 2
UNKNOWN_STAGE = StageDefinition(
    status=PipelineStatus.INTAKE,
    done_criteria="Stage definition unavailable. Verify project status.",
    task_titles=(),
)


def stage_index(status: PipelineStatus) -> int:
    return PIPELINE_ORDER.index(status)


def is_rollback(current: PipelineStatus, new: PipelineStatus) -> bool:
    """True when moving exactly one stage backward (Option B rollback)."""
    return stage_index(new) == stage_index(current) - 1


def can_transition(current: PipelineStatus, new: PipelineStatus) -> bool:
    """Single gatekeeper for all pipeline status changes.

    Policy (Option B — controlled_one_step):
    - Same stage: allowed (no-op)
    - Forward: exactly one stage
    - Backward: exactly one stage (controlled rollback)
    - Anything else: blocked
    """
    if current == new:
        return True
    return abs(stage_index(current) - stage_index(new)) == 1


def allowed_next_statuses(current: PipelineStatus) -> list[PipelineStatus]:
    """Statuses reachable from current — derived only from can_transition."""
    return [status for status in PIPELINE_ORDER if can_transition(current, status)]


def transition_error(current: PipelineStatus, new: PipelineStatus) -> str | None:
    """Return user-facing error when transition is blocked, else None."""
    if can_transition(current, new):
        return None

    cur_idx = stage_index(current)
    new_idx = stage_index(new)

    if new_idx > cur_idx + 1:
        return (
            f"Cannot skip forward from {current.value}. "
            f"Allowed: {', '.join(s.value for s in allowed_next_statuses(current))}."
        )
    if new_idx < cur_idx - 1:
        return (
            f"Cannot skip backward from {current.value}. "
            f"Rollback policy ({ROLLBACK_POLICY.value}): one stage back only. "
            f"Allowed: {', '.join(s.value for s in allowed_next_statuses(current))}."
        )
    return (
        f"Invalid transition from {current.value} to {new.value}. "
        f"Allowed: {', '.join(s.value for s in allowed_next_statuses(current))}."
    )


def log_state_label(current: PipelineStatus, new: PipelineStatus) -> str:
    """Audit log label for a successful transition."""
    if is_rollback(current, new):
        return f"{new.value} (rollback)"
    return new.value


def safe_stage_definition(status: PipelineStatus | None) -> StageDefinition:
    if status is None:
        return UNKNOWN_STAGE
    return STAGE_DEFINITIONS.get(status, UNKNOWN_STAGE)


def default_tasks_for_project() -> list[tuple[str, PipelineStatus]]:
    tasks: list[tuple[str, PipelineStatus]] = []
    for status in PIPELINE_ORDER:
        definition = STAGE_DEFINITIONS[status]
        for title in definition.task_titles:
            tasks.append((title, status))
    return tasks
