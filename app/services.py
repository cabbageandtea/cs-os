from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import Session



from app.intake_validation import (

    IntakeValidationError,

    compose_experience_summary,

    normalize_skills,

    normalize_url,

    validate_name,

    validate_target_role,

)

from app.intake_tokens import invalidate_intake_token, verify_intake_token

from app.lifecycle import transition_customer_lifecycle

from app.models import (

    Client,

    CustomerLifecycle,

    Deliverable,

    DeliverableStatus,

    IntakeStatus,

    PipelineStatus,

    Project,

    Task,

    TaskStatus,

    TimestampLog,

    utcnow,

)

from app.package_config import get_package
from app.metrics_service import record_delivered, record_intake_completed
from app.pipeline_config import default_tasks_for_project, log_state_label, transition_error





class WorkflowError(ValueError):

    pass





class PersistenceError(RuntimeError):

    pass





class IntakeAccessError(ValueError):

    pass





def log_change(

    db: Session,

    *,

    entity_type: str,

    entity_id: int,

    previous_state: str | None,

    new_state: str,

) -> None:

    db.add(

        TimestampLog(

            entity_type=entity_type,

            entity_id=entity_id,

            previous_state=previous_state,

            new_state=new_state,

        )

    )





def _commit_or_rollback(db: Session) -> None:

    try:

        db.commit()

    except SQLAlchemyError as exc:

        db.rollback()

        raise PersistenceError("Database write failed.") from exc





def _ensure_client_not_archived(client: Client) -> None:

    if client.customer_lifecycle == CustomerLifecycle.ARCHIVED.value:

        raise WorkflowError("This client is archived and cannot be updated.")





def seed_project_defaults(db: Session, project: Project, *, package_slug: str | None = None) -> None:

    for title, stage in default_tasks_for_project():

        db.add(

            Task(

                project_id=project.id,

                title=title,

                stage_name=stage.value,

            )

        )



    deliverable_names: tuple[str, ...]

    if package_slug:

        deliverable_names = get_package(package_slug).deliverables

    else:

        deliverable_names = (

            "Portfolio website",

            "Resume (PDF)",

            "LinkedIn optimization notes",

            "Deployment URL",

        )



    for deliverable_name in deliverable_names:

        db.add(Deliverable(project_id=project.id, name=deliverable_name, url=None))





def create_client_with_project(

    db: Session,

    *,

    name: str,

    target_role: str,

    experience_education: str,

    experience_projects: str,

    experience_work: str,

    skills: str,

    linkedin_url: str | None,

    github_url: str | None,

    package_tier: str,

) -> Client:

    client = Client(

        name=validate_name(name),

        target_role=validate_target_role(target_role),

        experience_summary=compose_experience_summary(

            education=experience_education,

            projects=experience_projects,

            work=experience_work,

        ),

        skills=normalize_skills(skills),

        linkedin_url=normalize_url(linkedin_url),

        github_url=normalize_url(github_url),

        package_tier=package_tier or "Basic",

    )

    db.add(client)

    db.flush()



    project = Project(client_id=client.id, status=PipelineStatus.INTAKE)

    db.add(project)

    db.flush()



    log_change(

        db,

        entity_type="project",

        entity_id=project.id,

        previous_state=None,

        new_state=PipelineStatus.INTAKE.value,

    )



    seed_project_defaults(db, project)

    record_intake_completed(db, client)

    _commit_or_rollback(db)

    db.refresh(client)

    return client





def complete_token_intake(

    db: Session,

    client: Client,

    *,

    token: str,

    name: str,

    target_role: str,

    experience_education: str,

    experience_projects: str,

    experience_work: str,

    skills: str,

    linkedin_url: str | None,

    github_url: str | None,

) -> Client:

    token_error = verify_intake_token(client, token)

    if token_error:

        raise IntakeAccessError(token_error)



    if client.intake_status == IntakeStatus.COMPLETE.value:

        raise IntakeAccessError("Intake has already been submitted.")



    client.name = validate_name(name)

    client.target_role = validate_target_role(target_role)

    client.experience_summary = compose_experience_summary(

        education=experience_education,

        projects=experience_projects,

        work=experience_work,

    )

    client.skills = normalize_skills(skills)

    client.linkedin_url = normalize_url(linkedin_url)

    client.github_url = normalize_url(github_url)

    client.intake_status = IntakeStatus.COMPLETE.value

    client.intake_completed_at = utcnow()

    invalidate_intake_token(client)

    transition_customer_lifecycle(db, client, CustomerLifecycle.ACTIVE.value)

    record_intake_completed(db, client)

    _commit_or_rollback(db)

    db.refresh(client)

    return client





def update_project_status(db: Session, project: Project, new_status: PipelineStatus) -> Project:

    if project.client:

        _ensure_client_not_archived(project.client)



    if project.status == new_status:

        return project



    error = transition_error(project.status, new_status)

    if error:

        raise WorkflowError(error)



    old_status = project.status

    old = old_status.value

    project.status = new_status

    log_change(

        db,

        entity_type="project",

        entity_id=project.id,

        previous_state=old,

        new_state=log_state_label(old_status, new_status),

    )

    if new_status == PipelineStatus.DELIVERED:
        delivery_client = project.client
        if delivery_client is None and project.client_id:
            delivery_client = db.get(Client, project.client_id)
        if delivery_client:
            record_delivered(db, delivery_client)

    _commit_or_rollback(db)

    db.refresh(project)

    return project





def update_task_status(db: Session, task: Task, new_status: TaskStatus) -> Task:

    if task.status == new_status:

        return task



    old = task.status.value

    task.status = new_status

    log_change(

        db,

        entity_type="task",

        entity_id=task.id,

        previous_state=old,

        new_state=new_status.value,

    )

    _commit_or_rollback(db)

    db.refresh(task)

    return task





def update_deliverable_status(

    db: Session, deliverable: Deliverable, new_status: DeliverableStatus

) -> Deliverable:

    if deliverable.status == new_status:

        return deliverable



    old = deliverable.status.value

    deliverable.status = new_status

    log_change(

        db,

        entity_type="deliverable",

        entity_id=deliverable.id,

        previous_state=old,

        new_state=new_status.value,

    )

    _commit_or_rollback(db)

    db.refresh(deliverable)

    return deliverable





def update_deliverable_url(db: Session, deliverable: Deliverable, url: str | None) -> Deliverable:

    deliverable.url = url

    _commit_or_rollback(db)

    db.refresh(deliverable)

    return deliverable


