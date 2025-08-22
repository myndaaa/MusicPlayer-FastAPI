from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator
import enum


# Audit action types enum
class AuditActionType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    SUBSCRIPTION_CHANGE = "subscription_change"
    PAYMENT = "payment"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SHARE = "share"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    LIKE = "like"
    UNLIKE = "unlike"
    SYSTEM_CONFIG = "system_config"
    ADMIN_ACTION = "admin_action"


# Base schema for audit log
class AuditLogBase(BaseModel):
    user_id: int
    action_type: AuditActionType
    target_table: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
    target_id: Optional[int] = None
    action_details: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(BaseModel):
    action_details: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogOut(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


# Nested schemas for relationships
class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True


# Audit log output with relationships
class AuditLogWithRelations(AuditLogOut):
    user: UserMinimal


# Audit log with additional context
class AuditLogWithContext(AuditLogWithRelations):
    target_object: Optional[dict] = None  
    changes: Optional[dict] = None  # What changed (for updates)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# List schemas for pagination
class AuditLogList(BaseModel):
    audit_logs: List[AuditLogOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class AuditLogListWithRelations(BaseModel):
    audit_logs: List[AuditLogWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    action_type: Optional[AuditActionType] = None
    target_table: Optional[str] = None
    target_id: Optional[int] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None


class AuditLogSearch(BaseModel):
    query: str  # search in action_details or target_table
    user_id: Optional[int] = None
    action_type: Optional[AuditActionType] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Audit log statistics
class AuditLogStats(BaseModel):
    total_logs: int
    logs_today: int
    logs_this_week: int
    logs_this_month: int
    most_active_user: Optional[UserMinimal] = None
    most_common_action: Optional[AuditActionType] = None
    most_common_table: Optional[str] = None


# User activity summary
class UserActivitySummary(BaseModel):
    user_id: int
    total_actions: int
    actions_today: int
    actions_this_week: int
    actions_this_month: int
    last_activity: Optional[datetime] = None
    most_common_action: Optional[AuditActionType] = None


# System activity summary
class SystemActivitySummary(BaseModel):
    period: str  # "day", "week", "month"
    total_actions: int
    unique_users: int
    action_breakdown: dict  # {action_type: count}
    table_breakdown: dict  # {table_name: count}
    peak_activity_hour: Optional[int] = None


# Audit log export
class AuditLogExport(BaseModel):
    format: str = "json"  # json, csv, etc.
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[int] = None
    action_type: Optional[AuditActionType] = None
    target_table: Optional[str] = None
    include_user_details: bool = True
    include_context: bool = False


# Audit log cleanup
class AuditLogCleanup(BaseModel):
    older_than_days: int = Field(gt=0)
    dry_run: bool = True  # if True, show what would be deleted
    action_types: Optional[List[AuditActionType]] = None
    target_tables: Optional[List[str]] = None


# Audit log retention policy
class AuditLogRetentionPolicy(BaseModel):
    retention_days: int = Field(gt=0)
    action_types_to_retain: List[AuditActionType]
    tables_to_retain: List[str]
    enabled: bool = True


# Audit log monitoring
class AuditLogAlert(BaseModel):
    alert_type: str  # "suspicious_activity", "high_volume", "failed_actions"
    threshold: int
    time_window_minutes: int
    action_types: Optional[List[AuditActionType]] = None
    users: Optional[List[int]] = None
    enabled: bool = True


# Audit log dashboard
class AuditLogDashboard(BaseModel):
    recent_activity: List[AuditLogWithRelations]
    activity_stats: AuditLogStats
    top_users: List[UserActivitySummary]
    system_summary: SystemActivitySummary
    alerts: List[AuditLogAlert] 
