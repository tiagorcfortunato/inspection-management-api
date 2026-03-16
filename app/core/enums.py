from enum import Enum


class DamageType(str, Enum):
    pothole = "pothole"
    crack = "crack"
    rutting = "rutting"
    surface_wear = "surface_wear"


class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class InspectionStatus(str, Enum):
    reported = "reported"
    verified = "verified"
    scheduled = "scheduled"
    repaired = "repaired"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"