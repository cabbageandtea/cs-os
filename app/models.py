import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PipelineStatus(str, enum.Enum):
    INTAKE = "Intake"
    ANALYSIS = "Analysis"
    BUILD = "Build"
    QA = "QA"
    REVIEW = "Review"
    DELIVERED = "Delivered"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class DeliverableStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class PurchaseStatus(str, enum.Enum):
    CREATED = "created"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class CustomerLifecycle(str, enum.Enum):
    PURCHASED = "purchased"
    INTAKE_PENDING = "intake_pending"
    ACTIVE = "active"
    DELIVERED = "delivered"
    ARCHIVED = "archived"


class IntakeStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETE = "complete"


class LeadStatus(str, enum.Enum):
    NEW_LEAD = "new_lead"
    CONTACTED = "contacted"
    PURCHASED = "purchased"
    LOST = "lost"


LEAD_PIPELINE_ORDER = list(LeadStatus)


PIPELINE_ORDER = list(PipelineStatus)  # re-export for templates; canonical order in pipeline_config


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"), nullable=True, index=True)
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    package_slug: Mapped[str] = mapped_column(String(50), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default=PurchaseStatus.PAYMENT_PENDING.value, index=True)
    customer_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    intake_link_delivered: Mapped[bool] = mapped_column(Boolean, default=False)

    client: Mapped[Optional["Client"]] = relationship(
        "Client",
        foreign_keys=[client_id],
        primaryjoin="Purchase.client_id==Client.id",
    )


class StripeWebhookEvent(Base):
    __tablename__ = "stripe_webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    stripe_event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LifecycleEvent(Base):
    __tablename__ = "lifecycle_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    previous_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_state: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), index=True)
    target_role: Mapped[str] = mapped_column(String(200))
    current_status: Mapped[str] = mapped_column(String(200))
    interested_package: Mapped[str] = mapped_column(String(50))
    lead_status: Mapped[str] = mapped_column(
        String(50), default=LeadStatus.NEW_LEAD.value, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    target_role: Mapped[str] = mapped_column(String(200))
    experience_summary: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    package_tier: Mapped[str] = mapped_column(String(50), default="Basic")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True, index=True)
    public_id: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True)
    package_slug: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    customer_lifecycle: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    intake_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    intake_token_hash: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True)
    intake_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    purchase_id: Mapped[Optional[int]] = mapped_column(ForeignKey("purchases.id"), nullable=True, unique=True)
    intake_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="client", uselist=False)
    purchase: Mapped[Optional[Purchase]] = relationship(
        "Purchase",
        foreign_keys=[purchase_id],
        primaryjoin="Client.purchase_id==Purchase.id",
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), unique=True)
    status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus), default=PipelineStatus.INTAKE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    client: Mapped[Client] = relationship(back_populates="project")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    deliverables: Mapped[list["Deliverable"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(300))
    stage_name: Mapped[str] = mapped_column(String(50), default=PipelineStatus.INTAKE.value)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    project: Mapped[Project] = relationship(back_populates="tasks")


class Deliverable(Base):
    __tablename__ = "deliverables"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(300))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[DeliverableStatus] = mapped_column(
        Enum(DeliverableStatus), default=DeliverableStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    project: Mapped[Project] = relationship(back_populates="deliverables")


class TimestampLog(Base):
    __tablename__ = "timestamp_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column()
    previous_state: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    new_state: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class BusinessMetrics(Base):
    __tablename__ = "business_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[Optional[int]] = mapped_column(ForeignKey("leads.id"), nullable=True, unique=True)
    purchase_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("purchases.id"), nullable=True, unique=True
    )
    client_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("clients.id"), nullable=True, unique=True
    )
    lead_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    checkout_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    purchased_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    intake_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    package_slug: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    revenue_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class ClientOutcome(Base):
    __tablename__ = "client_outcomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), unique=True, index=True)
    before_problem: Mapped[str] = mapped_column(Text)
    after_result: Mapped[str] = mapped_column(Text)
    testimonial: Mapped[str] = mapped_column(Text)
    display_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


def new_public_id() -> str:
    return str(uuid.uuid4())
