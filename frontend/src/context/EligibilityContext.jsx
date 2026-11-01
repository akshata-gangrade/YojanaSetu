import {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
  useMemo,
  useEffect,
} from 'react';
import { useTranslation } from 'react-i18next';
import { extractIntake, matchSchemes, ApiError } from '../lib/api';

const EligibilityContext = createContext(null);

function getQuickRepliesForField(fieldName, t) {
  if (!fieldName) return [];

  switch (fieldName) {
    case 'gender':
      return [
        { field: 'gender', value: 'female', label: t('criteria.values.female', 'Female') },
        { field: 'gender', value: 'male', label: t('criteria.values.male', 'Male') },
        { field: 'gender', value: 'transgender', label: t('criteria.values.transgender', 'Transgender') },
        { field: 'gender', value: 'prefer_not_to_say', label: t('intake.details.preferNotToSay', 'Prefer not to say') },
      ];
    case 'residence_type':
      return [
        { field: 'residence_type', value: 'rural', label: t('criteria.values.rural', 'Rural') },
        { field: 'residence_type', value: 'urban', label: t('criteria.values.urban', 'Urban') },
        { field: 'residence_type', value: 'prefer_not_to_say', label: t('intake.details.preferNotToSay', 'Prefer not to say') },
      ];
    case 'marital_status':
      return [
        { field: 'marital_status', value: 'single', label: t('intake.details.single', 'Single') },
        { field: 'marital_status', value: 'married', label: t('intake.details.married', 'Married') },
        { field: 'marital_status', value: 'widowed', label: t('intake.details.widowed', 'Widowed') },
        { field: 'marital_status', value: 'prefer_not_to_say', label: t('intake.details.preferNotToSay', 'Prefer not to say') },
      ];
    case 'is_student':
      return [
        { field: 'is_student', value: true, label: t('intake.details.yes', 'Yes') },
        { field: 'is_student', value: false, label: t('intake.details.no', 'No') },
      ];
    case 'social_category':
      return [
        { field: 'social_category', value: 'general', label: t('criteria.values.general', 'General') },
        { field: 'social_category', value: 'obc', label: t('criteria.values.obc', 'OBC') },
        { field: 'social_category', value: 'sc', label: t('criteria.values.sc', 'SC') },
        { field: 'social_category', value: 'st', label: t('criteria.values.st', 'ST') },
        { field: 'social_category', value: 'prefer_not_to_say', label: t('intake.details.preferNotToSay', 'Prefer not to say') },
      ];
    case 'occupation':
      return [
        { field: 'occupation', value: 'farmer', label: t('criteria.values.farmer', 'Farmer') },
        { field: 'occupation', value: 'student', label: t('criteria.values.student', 'Student') },
        { field: 'occupation', value: 'salaried', label: t('criteria.values.salaried', 'Salaried') },
        { field: 'occupation', value: 'self_employed', label: t('criteria.values.self_employed', 'Self Employed') },
        { field: 'occupation', value: 'daily_wage', label: t('criteria.values.daily_wage', 'Daily Wage') },
      ];
    default:
      return [];
  }
}

export function EligibilityProvider({ children }) {
  const { t, i18n } = useTranslation();

  // In-memory profile state only (never in storage)
  const [consentGiven, setConsentGiven] = useState(false);
  const [profile, setProfile] = useState({});
  const [matchResults, setMatchResults] = useState(null);
  const [focusedField, setFocusedField] = useState(null);

  // Chat state
  const [chatMessages, setChatMessages] = useState([
    {
      id: 'msg-welcome',
      sender: 'assistant',
      text: t(
        'intake.chat.welcomeMessage',
        'Namaste! Describe your situation in English or Hindi (e.g., "I am a 28-year-old farmer from Uttar Pradesh with an annual income of ₹1.5 lakh"). You can also edit your details directly in the panel.'
      ),
      quickReplies: [],
      timestamp: new Date().toISOString(),
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [isSlow, setIsSlow] = useState(false);
  const [error, setError] = useState(null);

  const abortControllerRef = useRef(null);
  const requestCounterRef = useRef(0);

  // Abort pending request on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Updates single or multiple profile fields directly and invalidates previous match
  const updateProfile = useCallback((updates) => {
    setProfile((prev) => {
      const next = { ...prev, ...updates };
      // Clean up undefined or empty strings
      Object.keys(next).forEach((key) => {
        if (next[key] === undefined || next[key] === '') {
          delete next[key];
        }
      });
      return next;
    });
    // Invalidate stale match results whenever profile changes
    setMatchResults(null);
  }, []);

  // Sets single profile field
  const setProfileField = useCallback(
    (field, value) => {
      updateProfile({ [field]: value });
    },
    [updateProfile]
  );

  // Clears all citizen details, chat history, match results, focusedField, and aborts in-flight calls
  const clearAllDetails = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    requestCounterRef.current += 1;

    setProfile({});
    setMatchResults(null);
    setFocusedField(null);
    setIsLoading(false);
    setIsSlow(false);
    setError(null);

    setChatMessages([
      {
        id: `msg-welcome-${Date.now()}`,
        sender: 'assistant',
        text: t(
          'intake.chat.welcomeMessage',
          'Namaste! Describe your situation in English or Hindi (e.g., "I am a 28-year-old farmer from Uttar Pradesh with an annual income of ₹1.5 lakh"). You can also edit your details directly in the panel.'
        ),
        quickReplies: [],
        timestamp: new Date().toISOString(),
      },
    ]);
  }, [t]);

  // Sends citizen message to POST /intake/extract with current profile
  const sendMessage = useCallback(
    async (text, chipOverride = null) => {
      const trimmed = text?.trim();
      if (!trimmed || isLoading) return;

      // Abort previous in-flight request if any
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const currentReqId = ++requestCounterRef.current;

      // Add user message to transcript
      const userMsg = {
        id: `user-${Date.now()}`,
        sender: 'user',
        text: trimmed,
        timestamp: new Date().toISOString(),
      };
      setChatMessages((prev) => [...prev, userMsg]);

      // If triggered by quick-reply chip, apply chip value directly (chip value wins!)
      let activeProfile = { ...profile };
      if (chipOverride?.field) {
        activeProfile[chipOverride.field] = chipOverride.value;
        setProfile((prev) => ({ ...prev, [chipOverride.field]: chipOverride.value }));
        setMatchResults(null);
      }

      setIsLoading(true);
      setIsSlow(false);
      setError(null);

      try {
        const response = await extractIntake({
          message: trimmed,
          currentProfile: activeProfile,
          language: i18n.language || 'en',
          signal: controller.signal,
          onSlow: () => {
            if (requestCounterRef.current === currentReqId) {
              setIsSlow(true);
            }
          },
        });

        // If request was superseded or cleared, ignore response
        if (requestCounterRef.current !== currentReqId) {
          return;
        }

        // Merge profile updates, ensuring chip override takes precedence over LLM conflicts
        const updates = response.profile_updates || {};
        if (chipOverride?.field) {
          updates[chipOverride.field] = chipOverride.value;
        }

        if (Object.keys(updates).length > 0) {
          updateProfile(updates);
        }

        // Determine quick replies for next question
        let replies = [];
        if (response.missing_fields && response.missing_fields.length > 0) {
          replies = getQuickRepliesForField(response.missing_fields[0], t);
        }

        // Add assistant message with next question and any PII notice
        const assistantText =
          response.next_question ||
          t(
            'intake.chat.detailsUpdated',
            'I have updated your details in the panel. You can answer further questions or click "See my matching schemes" to view results.'
          );

        const assistantMsg = {
          id: `assistant-${Date.now()}`,
          sender: 'assistant',
          text: assistantText,
          quickReplies: replies,
          piiNotice: response.pii_notice || null,
          timestamp: new Date().toISOString(),
        };

        setChatMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        // Discard aborted errors
        if (err.name === 'AbortError' || requestCounterRef.current !== currentReqId) {
          return;
        }

        if (err instanceof ApiError && err.status === 429) {
          setError(
            t(
              'apiErrors.rateLimit',
              'Too many requests, please wait a minute.'
            )
          );
        } else {
          setError(err.message || t('common.error', 'An error occurred'));
        }
      } finally {
        if (requestCounterRef.current === currentReqId) {
          setIsLoading(false);
          setIsSlow(false);
        }
      }
    },
    [profile, isLoading, i18n.language, t, updateProfile]
  );

  // Evaluates profile deterministically in Python rule engine via POST /api/v1/match
  const evaluateEligibility = useCallback(async () => {
    if (isLoading) return null;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setIsSlow(false);
    setError(null);

    try {
      const response = await matchSchemes({
        profile,
        language: i18n.language || 'en',
        signal: controller.signal,
        onSlow: () => setIsSlow(true),
      });

      setMatchResults(response);
      return response;
    } catch (err) {
      if (err.name === 'AbortError') return null;

      if (err instanceof ApiError && err.status === 429) {
        setError(t('apiErrors.rateLimit', 'Too many requests, please wait a minute.'));
      } else {
        setError(err.message || t('common.error', 'An error occurred'));
      }
      throw err;
    } finally {
      setIsLoading(false);
      setIsSlow(false);
    }
  }, [profile, isLoading, i18n.language, t]);

  const hasAtLeastOneField = useMemo(() => {
    return Object.values(profile).some(
      (v) => v !== undefined && v !== null && v !== ''
    );
  }, [profile]);

  const value = {
    consentGiven,
    setConsentGiven,
    profile,
    updateProfile,
    setProfileField,
    clearAllDetails,
    chatMessages,
    sendMessage,
    matchResults,
    setMatchResults,
    evaluateEligibility,
    hasAtLeastOneField,
    focusedField,
    setFocusedField,
    isLoading,
    isSlow,
    error,
  };

  return (
    <EligibilityContext.Provider value={value}>
      {children}
    </EligibilityContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useEligibility() {
  const context = useContext(EligibilityContext);
  if (!context) {
    throw new Error('useEligibility must be used within an EligibilityProvider');
  }
  return context;
}

export default EligibilityContext;
