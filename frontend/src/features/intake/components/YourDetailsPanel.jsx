import { useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEligibility } from '../../../context/EligibilityContext';
import { Card, Button } from '../../../components/ui';
import { formatCurrencyINR } from '../../../lib/formatters';
import {
  INDIAN_STATES,
  GENDER_OPTIONS,
  SOCIAL_CATEGORY_OPTIONS,
  RESIDENCE_TYPE_OPTIONS,
  MARITAL_STATUS_OPTIONS,
  DISABILITY_STATUS_OPTIONS,
  OCCUPATION_OPTIONS,
  EDUCATION_LEVEL_OPTIONS,
  IS_STUDENT_OPTIONS,
} from '../constants';

export function YourDetailsPanel() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const {
    profile,
    setProfileField,
    clearAllDetails,
    evaluateEligibility,
    hasAtLeastOneField,
    focusedField,
    setFocusedField,
    isLoading,
  } = useEligibility();

  const ageRef = useRef(null);
  const annualIncomeRef = useRef(null);
  const stateRef = useRef(null);
  const genderRef = useRef(null);
  const occupationRef = useRef(null);
  const socialCategoryRef = useRef(null);
  const educationLevelRef = useRef(null);
  const residenceTypeRef = useRef(null);
  const maritalStatusRef = useRef(null);
  const disabilityStatusRef = useRef(null);
  const isStudentRef = useRef(null);

  const fieldRefs = useMemo(
    () => ({
      age: ageRef,
      annual_income: annualIncomeRef,
      state: stateRef,
      gender: genderRef,
      occupation: occupationRef,
      social_category: socialCategoryRef,
      education_level: educationLevelRef,
      residence_type: residenceTypeRef,
      marital_status: maritalStatusRef,
      disability_status: disabilityStatusRef,
      is_student: isStudentRef,
    }),
    []
  );

  // Programmatically focus field if returning from "Add missing detail" button
  useEffect(() => {
    if (focusedField && fieldRefs[focusedField]?.current) {
      const el = fieldRefs[focusedField].current;
      el.focus();
      if (typeof el.scrollIntoView === 'function') {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      setFocusedField(null);
    }
  }, [focusedField, setFocusedField, fieldRefs]);

  const handleMatchClick = async () => {
    try {
      await evaluateEligibility();
      navigate('/check-eligibility/results');
    } catch {
      // Error is caught and surfaced in context/UI
    }
  };

  return (
    <Card className="flex h-[620px] flex-col p-4 shadow-soft sm:p-5" data-your-details-panel>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border-card pb-3">
        <div>
          <h3 className="text-base font-bold text-navy sm:text-lg">
            {t('intake.details.title', 'Your Details')}
          </h3>
          <p className="text-xs text-text-muted">
            {t(
              'intake.details.subtitle',
              'Editable source of truth. You can adjust any field directly.'
            )}
          </p>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={clearAllDetails}
          className="text-xs text-[#B3261E] hover:bg-[#FDF2F2]"
        >
          {t('intake.details.clearAll', 'Clear my details')}
        </Button>
      </div>

      {/* Fields Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (hasAtLeastOneField) handleMatchClick();
        }}
        className="flex-1 space-y-3.5 overflow-y-auto py-3 pr-1 text-sm"
      >
        {/* Age */}
        <div className="space-y-1">
          <label htmlFor="field-age" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.age', 'Age')}
          </label>
          <input
            id="field-age"
            ref={fieldRefs.age}
            type="number"
            min={0}
            max={125}
            value={profile.age ?? ''}
            onChange={(e) => {
              const val = e.target.value === '' ? undefined : parseInt(e.target.value, 10);
              setProfileField('age', Number.isNaN(val) ? undefined : val);
            }}
            placeholder={t('intake.details.agePlaceholder', 'e.g. 32')}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          />
        </div>

        {/* State */}
        <div className="space-y-1">
          <label htmlFor="field-state" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.state', 'State / Union Territory')}
          </label>
          <select
            id="field-state"
            ref={fieldRefs.state}
            value={profile.state ?? ''}
            onChange={(e) => setProfileField('state', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {INDIAN_STATES.map((st) => (
              <option key={st.value} value={st.value}>
                {st.label}
              </option>
            ))}
            <option value="prefer_not_to_say">
              {t('intake.details.preferNotToSay', 'Prefer not to say')}
            </option>
          </select>
        </div>

        {/* Annual Income */}
        <div className="space-y-1">
          <label htmlFor="field-annual-income" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.annual_income', 'Annual Household Income (₹)')}
          </label>
          <input
            id="field-annual-income"
            ref={fieldRefs.annual_income}
            type="number"
            min={0}
            step={1000}
            value={profile.annual_income ?? ''}
            onChange={(e) => {
              const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
              setProfileField('annual_income', Number.isNaN(val) ? undefined : val);
            }}
            placeholder={t('intake.details.incomePlaceholder', 'e.g. 150000')}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          />
          {typeof profile.annual_income === 'number' && (
            <p className="text-[11px] text-text-muted">
              {formatCurrencyINR(profile.annual_income)} / year
            </p>
          )}
        </div>

        {/* Occupation */}
        <div className="space-y-1">
          <label htmlFor="field-occupation" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.occupation', 'Occupation')}
          </label>
          <select
            id="field-occupation"
            ref={fieldRefs.occupation}
            value={profile.occupation ?? ''}
            onChange={(e) => setProfileField('occupation', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {OCCUPATION_OPTIONS.map((occ) => (
              <option key={occ} value={occ}>
                {t(`criteria.values.${occ}`, occ.replace(/_/g, ' '))}
              </option>
            ))}
          </select>
        </div>

        {/* Gender */}
        <div className="space-y-1">
          <label htmlFor="field-gender" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.gender', 'Gender')}
          </label>
          <select
            id="field-gender"
            ref={fieldRefs.gender}
            value={profile.gender ?? ''}
            onChange={(e) => setProfileField('gender', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {GENDER_OPTIONS.map((g) => (
              <option key={g} value={g}>
                {t(`criteria.values.${g}`, g.replace(/_/g, ' '))}
              </option>
            ))}
          </select>
        </div>

        {/* Social Category (Sensitive, Optional) */}
        <div className="space-y-1">
          <label htmlFor="field-social-category" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.social_category', 'Social Category (Optional)')}
          </label>
          <select
            id="field-social-category"
            ref={fieldRefs.social_category}
            value={profile.social_category ?? ''}
            onChange={(e) => setProfileField('social_category', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {SOCIAL_CATEGORY_OPTIONS.map((cat) => (
              <option key={cat} value={cat}>
                {t(`criteria.values.${cat}`, cat.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        {/* Residence Type */}
        <div className="space-y-1">
          <label htmlFor="field-residence-type" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.residence_type', 'Habitation / Area')}
          </label>
          <select
            id="field-residence-type"
            ref={fieldRefs.residence_type}
            value={profile.residence_type ?? ''}
            onChange={(e) => setProfileField('residence_type', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {RESIDENCE_TYPE_OPTIONS.map((res) => (
              <option key={res} value={res}>
                {t(`criteria.values.${res}`, res.replace(/_/g, ' '))}
              </option>
            ))}
          </select>
        </div>

        {/* Marital Status */}
        <div className="space-y-1">
          <label htmlFor="field-marital-status" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.marital_status', 'Marital Status')}
          </label>
          <select
            id="field-marital-status"
            ref={fieldRefs.marital_status}
            value={profile.marital_status ?? ''}
            onChange={(e) => setProfileField('marital_status', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {MARITAL_STATUS_OPTIONS.map((mar) => (
              <option key={mar} value={mar}>
                {t(`intake.details.${mar}`, mar.replace(/_/g, ' '))}
              </option>
            ))}
          </select>
        </div>

        {/* Education Level */}
        <div className="space-y-1">
          <label htmlFor="field-education-level" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.education_level', 'Highest Education Completed')}
          </label>
          <select
            id="field-education-level"
            ref={fieldRefs.education_level}
            value={profile.education_level ?? ''}
            onChange={(e) => setProfileField('education_level', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {EDUCATION_LEVEL_OPTIONS.map((edu) => (
              <option key={edu} value={edu}>
                {t(`intake.details.${edu}`, edu.replace(/_/g, ' '))}
              </option>
            ))}
          </select>
        </div>

        {/* Disability Status (Sensitive, Optional) */}
        <div className="space-y-1">
          <label htmlFor="field-disability-status" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.disability_status', 'Disability Status (Optional)')}
          </label>
          <select
            id="field-disability-status"
            ref={fieldRefs.disability_status}
            value={profile.disability_status ?? ''}
            onChange={(e) => setProfileField('disability_status', e.target.value || undefined)}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {DISABILITY_STATUS_OPTIONS.map((dis) => (
              <option key={dis} value={dis}>
                {t(`intake.details.${dis}`, dis.replace(/_/g, ' '))}
              </option>
            ))}
          </select>
        </div>

        {/* Enrolled Student */}
        <div className="space-y-1">
          <label htmlFor="field-is-student" className="block text-xs font-bold text-text-primary">
            {t('criteria.fields.is_student', 'Currently a Student')}
          </label>
          <select
            id="field-is-student"
            ref={fieldRefs.is_student}
            value={profile.is_student === undefined || profile.is_student === null ? '' : String(profile.is_student)}
            onChange={(e) => {
              const val = e.target.value;
              setProfileField('is_student', val === '' ? undefined : val === 'true');
            }}
            className="h-10 w-full rounded-lg border border-border-card bg-surface-card px-3 text-sm focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy"
          >
            <option value="">{t('intake.details.notGiven', 'Not given')}</option>
            {IS_STUDENT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {t(opt.labelKey, opt.value === 'true' ? 'Yes' : 'No')}
              </option>
            ))}
          </select>
        </div>
      </form>

      {/* Footer Match Action Button */}
      <div className="border-t border-border-card pt-3">
        <Button
          type="button"
          variant="primary"
          size="md"
          className="w-full"
          disabled={!hasAtLeastOneField || isLoading}
          isLoading={isLoading}
          onClick={handleMatchClick}
        >
          {t('intake.details.seeMatchingSchemes', 'See my matching schemes')} &rarr;
        </Button>
      </div>
    </Card>
  );
}

export default YourDetailsPanel;
