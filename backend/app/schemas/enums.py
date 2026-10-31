"""Standard enumeration types across database models and API schemas."""

from enum import Enum


class SchemeLevel(str, Enum):
    """Administrative tier of the scheme."""

    CENTRAL = "central"
    STATE = "state"


class SchemeStatus(str, Enum):
    """Lifecycle status for scheme records."""

    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    VERIFIED = "verified"
    ARCHIVED = "archived"


class ChunkSection(str, Enum):
    """Categorized knowledge chunk sections for vector retrieval."""

    ELIGIBILITY = "eligibility"
    BENEFITS = "benefits"
    DOCUMENTS = "documents"
    HOW_TO_APPLY = "how_to_apply"
    OTHER = "other"


class AdminRole(str, Enum):
    """Role-based authorization for administrative access."""

    ADMIN = "admin"
    REVIEWER = "reviewer"


class FeedbackVote(str, Enum):
    """Anonymous helpfulness sentiment."""

    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


class CriterionField(str, Enum):
    """Allowed user profile and eligibility evaluation criteria fields."""

    AGE = "age"
    GENDER = "gender"
    STATE = "state"
    ANNUAL_INCOME = "annual_income"
    SOCIAL_CATEGORY = "social_category"
    OCCUPATION = "occupation"
    EDUCATION_LEVEL = "education_level"
    RESIDENCE_TYPE = "residence_type"
    MARITAL_STATUS = "marital_status"
    DISABILITY_STATUS = "disability_status"
    IS_STUDENT = "is_student"


class CriterionOperator(str, Enum):
    """Deterministic comparison operators for criteria evaluation."""

    EQ = "eq"
    IN = "in"
    NOT_IN = "not_in"
    GTE = "gte"
    LTE = "lte"
    BETWEEN = "between"


class Gender(str, Enum):
    """Citizen gender categories."""

    FEMALE = "female"
    MALE = "male"
    TRANSGENDER = "transgender"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class SocialCategory(str, Enum):
    """Affirmative action / social category classifications."""

    GENERAL = "general"
    OBC = "obc"
    SC = "sc"
    ST = "st"
    EBC = "ebc"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ResidenceType(str, Enum):
    """Locality classification."""

    RURAL = "rural"
    URBAN = "urban"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class MaritalStatus(str, Enum):
    """Citizen marital status."""

    SINGLE = "single"
    MARRIED = "married"
    WIDOWED = "widowed"
    DIVORCED = "divorced"
    SEPARATED = "separated"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class DisabilityStatus(str, Enum):
    """Disability status classification (sensitive, optional)."""

    NONE = "none"
    LOCOMOTOR = "locomotor"
    VISUAL = "visual"
    HEARING = "hearing"
    SPEECH_AND_LANGUAGE = "speech_and_language"
    INTELLECTUAL = "intellectual"
    MENTAL_ILLNESS = "mental_illness"
    MULTIPLE = "multiple"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class Occupation(str, Enum):
    """Primary economic occupation."""

    FARMER = "farmer"
    ARTISAN = "artisan"
    STUDENT = "student"
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    DAILY_WAGE = "daily_wage"
    UNEMPLOYED = "unemployed"
    HOMEMAKER = "homemaker"
    RETIRED = "retired"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class EducationLevel(str, Enum):
    """Highest level of formal education."""

    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGHER_SECONDARY = "higher_secondary"
    DIPLOMA = "diploma"
    GRADUATE = "graduate"
    POST_GRADUATE = "post_graduate"
    DOCTORATE = "doctorate"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class IndianState(str, Enum):
    """States and Union Territories of India."""

    ANDHRA_PRADESH = "andhra_pradesh"
    ARUNACHAL_PRADESH = "arunachal_pradesh"
    ASSAM = "assam"
    BIHAR = "bihar"
    CHHATTISGARH = "chhattisgarh"
    GOA = "goa"
    GUJARAT = "gujarat"
    HARYANA = "haryana"
    HIMACHAL_PRADESH = "himachal_pradesh"
    JHARKHAND = "jharkhand"
    KARNATAKA = "karnataka"
    KERALA = "kerala"
    MADHYA_PRADESH = "madhya_pradesh"
    MAHARASHTRA = "maharashtra"
    MANIPUR = "manipur"
    MEGHALAYA = "meghalaya"
    MIZORAM = "mizoram"
    NAGALAND = "nagaland"
    ODISHA = "odisha"
    PUNJAB = "punjab"
    RAJASTHAN = "rajasthan"
    SIKKIM = "sikkim"
    TAMIL_NADU = "tamil_nadu"
    TELANGANA = "telangana"
    TRIPURA = "tripura"
    UTTAR_PRADESH = "uttar_pradesh"
    UTTARAKHAND = "uttarakhand"
    WEST_BENGAL = "west_bengal"
    ANDAMAN_AND_NICOBAR = "andaman_and_nicobar"
    CHANDIGARH = "chandigarh"
    DADRA_AND_NAGAR_HAVELI_AND_DAMAN_AND_DIU = (
        "dadra_and_nagar_haveli_and_daman_and_diu"
    )
    DELHI = "delhi"
    JAMMU_AND_KASHMIR = "jammu_and_kashmir"
    LADAKH = "ladakh"
    LAKSHADWEEP = "lakshadweep"
    PUDUCHERRY = "puducherry"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
