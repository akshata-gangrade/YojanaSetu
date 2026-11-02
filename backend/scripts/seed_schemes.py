"""Seed clearly labelled FICTIONAL sample schemes for dev and offline testing.

Invariants:
- All sample schemes are marked is_sample: true and excluded from production.
- Explicit --confirm flag is strictly required to execute database writes.
- Never invoke this script or database purging from automated test suites.
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Ensure backend root is on sys.path for direct script execution
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.core.logging import logger, setup_logging  # noqa: E402
from app.db.mongo import MongoDBManager  # noqa: E402
from app.repositories.scheme_repo import SchemeRepository  # noqa: E402
from app.schemas.criteria import Criterion, EligibilityCriteria  # noqa: E402
from app.schemas.enums import (  # noqa: E402
    CriterionField,
    CriterionOperator,
    SchemeLevel,
    SchemeStatus,
)
from app.schemas.scheme import SchemeCreate, SchemeUpdate  # noqa: E402

# 5 Clearly labelled FICTIONAL sample schemes for development and manual evaluation
SAMPLE_SCHEMES: list[SchemeCreate] = [
    SchemeCreate(
        slug="fictional-pm-yuva-swarojgar",
        name="Pradhan Mantri Yuva Swarojgar Yojana (FICTIONAL TEST SAMPLE)",
        name_hi="प्रधानमंत्री युवा स्वरोजगार योजना (काल्पनिक परीक्षण नमूना)",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["employment", "youth", "entrepreneurship"],
        benefit_summary=(
            "Provides subsidized collateral-free seed loans up to Rs 2,00,000 with a "
            "3% annual interest subvention for first-time youth entrepreneurs."
        ),
        benefit_summary_hi=(
            "18-35 वर्ष के युवा उद्यमियों के लिए 3% वार्षिक ब्याज अनुदान के साथ "
            "₹2,00,000 तक का संपार्श्विक-मुक्त रियायती ऋण प्रदान करता है।"
        ),
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.AGE,
                    op=CriterionOperator.BETWEEN,
                    value=[18, 35],
                ),
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=300000.0,
                ),
            ],
            any_of=[
                Criterion(
                    field=CriterionField.OCCUPATION,
                    op=CriterionOperator.IN,
                    value=["unemployed", "student", "artisan"],
                )
            ],
        ),
        required_documents=[
            "Identity Proof (Voter ID / Driving License)",
            "Age Verification Certificate",
            "Self-declared Income Certificate",
            "Project Proposal Brief",
        ],
        application_steps=[
            "Submit online application form at the portal",
            "Upload project summary and self-declaration",
            "Verification by district nodal agency within 15 days",
            "Loan disbursement through designated partner banks",
        ],
        apply_url="https://sample-schemes.example.gov.in/pm-yuva/apply",
        source_url="https://sample-schemes.example.gov.in/docs/pm-yuva-guidelines.pdf",
        source_hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@yojanasetu.internal",
        verified_at=datetime(2026, 10, 1, 10, 0, 0),
        last_verified=datetime(2026, 10, 1, 10, 0, 0),
        is_sample=True,
    ),
    SchemeCreate(
        slug="fictional-kanya-shiksha-protsahan",
        name="National Kanya Shiksha Protsahan Fellowship (FICTIONAL TEST SAMPLE)",
        name_hi="राष्ट्रीय कन्या शिक्षा प्रोत्साहन फ़ेलोशिप (काल्पनिक परीक्षण नमूना)",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["education", "women", "scholarship"],
        benefit_summary=(
            "Annual scholarship grant of Rs 50,000 for female students "
            "enrolled in full-time recognized undergraduate degree programs."
        ),
        benefit_summary_hi=(
            "पूर्णकालिक मान्यता प्राप्त स्नातक डिग्री कार्यक्रमों में नामांकित छात्राओं "
            "को सीधे ₹50,000 का वार्षिक छात्रवृत्ति अनुदान प्रदान किया जाता है।"
        ),
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.GENDER,
                    op=CriterionOperator.EQ,
                    value="female",
                ),
                Criterion(
                    field=CriterionField.IS_STUDENT,
                    op=CriterionOperator.EQ,
                    value=True,
                ),
                Criterion(
                    field=CriterionField.AGE,
                    op=CriterionOperator.BETWEEN,
                    value=[17, 26],
                ),
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=450000.0,
                ),
            ],
            any_of=[],
        ),
        required_documents=[
            "College Enrollment ID / Admission Receipt",
            "Class 12 Passing Marksheet",
            "Family Income Certificate",
        ],
        application_steps=[
            "Register on National Scholarship sample portal",
            "Enter academic enrollment details and upload marksheets",
            "Institute verification and merit validation",
            "Direct Benefit Transfer to student account",
        ],
        apply_url="https://sample-schemes.example.gov.in/kanya-shiksha/apply",
        source_url="https://sample-schemes.example.gov.in/docs/kanya-shiksha.pdf",
        source_hash="1123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@yojanasetu.internal",
        verified_at=datetime(2026, 10, 1, 10, 0, 0),
        last_verified=datetime(2026, 10, 1, 10, 0, 0),
        is_sample=True,
    ),
    SchemeCreate(
        slug="fictional-krishi-solar-pump-maharashtra",
        name="Maharashtra Krishi Solar Pump Sahayata (FICTIONAL TEST SAMPLE)",
        name_hi="महाराष्ट्र कृषि सौर पंप सहायता (काल्पनिक परीक्षण नमूना)",
        level=SchemeLevel.STATE,
        state="maharashtra",
        category_tags=["agriculture", "energy", "farmers"],
        benefit_summary=(
            "90% capital subsidy on off-grid 3HP to 7.5HP solar agricultural pump sets "
            "for small and marginal farmers in drought-prone areas."
        ),
        benefit_summary_hi=(
            "सूखा प्रभावित क्षेत्रों में छोटे और सीमांत किसानों के लिए 3HP से 7.5HP "
            "ऑफ-ग्रिड सौर कृषि पंप सेट पर 90% पूंजीगत सब्सिडी।"
        ),
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.STATE,
                    op=CriterionOperator.EQ,
                    value="maharashtra",
                ),
                Criterion(
                    field=CriterionField.OCCUPATION,
                    op=CriterionOperator.EQ,
                    value="farmer",
                ),
                Criterion(
                    field=CriterionField.RESIDENCE_TYPE,
                    op=CriterionOperator.EQ,
                    value="rural",
                ),
            ],
            any_of=[],
        ),
        required_documents=[
            "Land 7/12 Extract showing ownership",
            "Electricity Non-Availability / NOC Certificate",
            "Water Source Verification Proof",
        ],
        application_steps=[
            "Submit online application with 7/12 land extract",
            "Pay 10% farmer beneficiary contribution",
            "Site inspection by district renewable energy officer",
            "Installation and commissioning of solar pump within 45 days",
        ],
        apply_url="https://sample-schemes.example.gov.in/maha-solar/apply",
        source_url="https://sample-schemes.example.gov.in/docs/maha-solar-guidelines.pdf",
        source_hash="2123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@yojanasetu.internal",
        verified_at=datetime(2026, 10, 1, 10, 0, 0),
        last_verified=datetime(2026, 10, 1, 10, 0, 0),
        is_sample=True,
    ),
    SchemeCreate(
        slug="fictional-divyangjan-kaushal-vikas",
        name="National Divyangjan Kaushal Vikas Anudan (FICTIONAL TEST SAMPLE)",
        name_hi="राष्ट्रीय दिव्यांगजन कौशल विकास अनुदान (काल्पनिक परीक्षण नमूना)",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["disability", "skills", "vocational"],
        benefit_summary=(
            "Free 6-month certified vocational IT skill courses "
            "with a monthly stipend of Rs 4,000 and accessible toolkit grant."
        ),
        benefit_summary_hi=(
            "₹4,000 के मासिक वजीफे और सुलभ टूलकिट अनुदान के साथ 6 महीने का "
            "निःशुल्क प्रमाणित व्यावसायिक कौशल विकास कार्यक्रम।"
        ),
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.DISABILITY_STATUS,
                    op=CriterionOperator.NOT_IN,
                    value=["none", "prefer_not_to_say"],
                ),
                Criterion(
                    field=CriterionField.AGE,
                    op=CriterionOperator.BETWEEN,
                    value=[18, 55],
                ),
            ],
            any_of=[],
        ),
        required_documents=[
            "Disability Certificate / UDID Card",
            "Age Certificate",
            "Education Proof (Minimum Class 8)",
        ],
        application_steps=[
            "Register at regional skill training center",
            "Counselor assessment and trade allocation",
            "Commence classroom and practical hands-on module",
            "Job placement assistance upon course completion",
        ],
        apply_url="https://sample-schemes.example.gov.in/divyangjan-skills/apply",
        source_url="https://sample-schemes.example.gov.in/docs/divyangjan-skills.pdf",
        source_hash="3123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@yojanasetu.internal",
        verified_at=datetime(2026, 10, 1, 10, 0, 0),
        last_verified=datetime(2026, 10, 1, 10, 0, 0),
        is_sample=True,
    ),
    SchemeCreate(
        slug="fictional-vridha-pension-uttar-pradesh",
        name="UP Vridha Pension Sahayata (FICTIONAL TEST SAMPLE)",
        name_hi="यूपी वृद्ध पेंशन सहायता (काल्पनिक परीक्षण नमूना)",
        level=SchemeLevel.STATE,
        state="uttar_pradesh",
        category_tags=["senior_citizens", "social_security", "pension"],
        benefit_summary=(
            "Direct monthly pension of Rs 1,500 transferred to senior citizens "
            "residing in Uttar Pradesh living below poverty line."
        ),
        benefit_summary_hi=(
            "उत्तर प्रदेश में गरीबी रेखा से नीचे रहने वाले निराश्रित वरिष्ठ नागरिकों को "
            "₹1,500 की प्रत्यक्ष मासिक पेंशन सहायता।"
        ),
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.STATE,
                    op=CriterionOperator.EQ,
                    value="uttar_pradesh",
                ),
                Criterion(
                    field=CriterionField.AGE,
                    op=CriterionOperator.GTE,
                    value=60,
                ),
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=120000.0,
                ),
            ],
            any_of=[],
        ),
        required_documents=[
            "Age Proof (Voter ID or Birth Certificate)",
            "BPL Card or Rural Gram Sabha Income Verification",
            "Bank Passbook photocopy (first page)",
        ],
        application_steps=[
            "Submit online application through Social Welfare portal or CSC",
            "Block Development Officer (BDO) field verification within 21 days",
            "Sanction order issuance and Direct Benefit Transfer activation",
        ],
        apply_url="https://sample-schemes.example.gov.in/up-vridha/apply",
        source_url="https://sample-schemes.example.gov.in/docs/up-vridha.pdf",
        source_hash="4123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@yojanasetu.internal",
        verified_at=datetime(2026, 10, 1, 10, 0, 0),
        last_verified=datetime(2026, 10, 1, 10, 0, 0),
        is_sample=True,
    ),
]


async def seed_samples(repo: SchemeRepository) -> None:
    """Insert the 5 sample schemes, updating them if they already exist."""
    logger.info("Seeding %d fictional sample schemes...", len(SAMPLE_SCHEMES))
    inserted_count = 0
    updated_count = 0

    for sample in SAMPLE_SCHEMES:
        existing = await repo.get_by_slug(sample.slug)
        if existing:
            logger.info("Updating existing sample scheme '%s'...", sample.slug)
            update_data = SchemeUpdate.model_validate(
                sample.model_dump(exclude={"created_at"})
            )
            await repo.update_scheme(sample.slug, update_data)
            updated_count += 1
        else:
            logger.info("Inserting sample scheme '%s'...", sample.slug)
            await repo.create_scheme(sample)
            inserted_count += 1

    logger.info(
        "Seeding complete: %d inserted, %d updated.", inserted_count, updated_count
    )


async def purge_samples(repo: SchemeRepository) -> None:
    """Purge all schemes marked is_sample: true."""
    logger.info("Purging all sample schemes from database...")
    deleted = await repo.delete_sample_schemes()
    logger.info("Purge complete: %d sample schemes removed.", deleted)


def main() -> None:
    """CLI entry point for seeding or purging sample schemes."""
    setup_logging("INFO")
    parser = argparse.ArgumentParser(
        description="Seed or purge FICTIONAL test schemes in YojanaSetu database."
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Explicit confirmation required to perform database writes.",
    )
    parser.add_argument(
        "--purge-samples",
        action="store_true",
        help="Purge all sample schemes (is_sample: true) instead of inserting.",
    )

    args = parser.parse_args()

    if not args.confirm:
        print(
            "ERROR: Missing required flag --confirm.\n"
            "This script modifies database. Pass --confirm to proceed.\n"
            "Example:\n"
            "  python scripts/seed_schemes.py --confirm\n"
            "  python scripts/seed_schemes.py --purge-samples --confirm",
            file=sys.stderr,
        )
        sys.exit(1)

    async def _run() -> None:
        db = MongoDBManager.get_database()
        repo = SchemeRepository(db)
        try:
            if args.purge_samples:
                await purge_samples(repo)
            else:
                await seed_samples(repo)
        finally:
            await MongoDBManager.close_client()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
