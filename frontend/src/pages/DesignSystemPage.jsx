import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Badge,
  Alert,
  Stepper,
  ChatBubble,
  TextInput,
  Checklist,
  Tabs,
  Modal,
  useToast,
} from '../components/ui';

export function DesignSystemPage() {
  const { t } = useTranslation();
  const { addToast } = useToast();

  const [modalOpen, setModalOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(1);
  const [activeTab, setActiveTab] = useState('overview');
  const [inputText, setInputText] = useState('Uttar Pradesh');
  const [inputError, setInputError] = useState('');
  const [isButtonLoading, setIsButtonLoading] = useState(false);
  const [cardState, setCardState] = useState('normal');

  const [checklistItems, setChecklistItems] = useState([
    {
      id: 1,
      label: 'Aadhaar Card (Self-verification at official portal)',
      description: 'Used only at the time of final application on the ministry portal.',
      checked: true,
      status: 'eligible',
    },
    {
      id: 2,
      label: 'Land Ownership Records (Khatauni / RoR)',
      description: 'Required for agricultural machinery and solar pump subsidies.',
      checked: false,
      status: 'warning',
      note: 'Required if applying under Farmer category',
    },
    {
      id: 3,
      label: 'Income Certificate (Issued by Tehsildar)',
      description: 'Annual family income must be below ₹2,50,000.',
      checked: true,
      status: 'eligible',
    },
    {
      id: 4,
      label: 'Commercial Electricity Connection',
      description: 'Beneficiary must not hold an active commercial grid connection.',
      checked: false,
      status: 'error',
      note: 'Criterion met: No commercial connection',
    },
  ]);

  const handleToggleChecklist = (id, checked) => {
    setChecklistItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, checked } : item))
    );
  };

  const handleSimulateToast = (variant) => {
    addToast({
      title: `${variant.toUpperCase()} Notification`,
      message:
        variant === 'success'
          ? t('components.toastSuccess', 'Preferences saved successfully.')
          : `Sample ${variant} toast notification demonstrating accessible aria-live delivery.`,
      variant,
    });
  };

  return (
    <div className="space-y-8 py-8">
      <div className="flex flex-col justify-between gap-4 border-b border-[#D9E0EA] pb-6 sm:flex-row sm:items-center">
        <div>
          <div className="mb-2 inline-flex items-center gap-1.5 rounded bg-[#EBF1FA] px-2.5 py-1 text-xs font-bold text-[#0B2A5B]">
            <span>Development Mode Only • WCAG 2.1 AA</span>
          </div>
          <h1 className="text-3xl font-black tracking-tight text-[#0B2A5B]">
            Design System & Component Showcase
          </h1>
          <p className="mt-1 text-sm text-[#55627A]">
            Live, accessible component library built strictly with the YojanaSetu color
            tokens and typography scale.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setModalOpen(true)}>
            Open Native Modal
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleSimulateToast('success')}
          >
            Trigger Toast
          </Button>
        </div>
      </div>

      {/* Stepper Demo */}
      <Card className="p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>Stepper Component</CardTitle>
          <CardDescription>
            Accessible multi-step workflow progress with interactive clickability for
            completed steps.
          </CardDescription>
        </CardHeader>
        <div className="py-2">
          <Stepper
            steps={[
              {
                id: 'profile',
                title: t('components.stepperStep1', 'Citizen Profile'),
                description: 'State, occupation, family',
              },
              {
                id: 'rules',
                title: t('components.stepperStep2', 'Eligibility Engine'),
                description: 'Rule evaluation',
              },
              {
                id: 'results',
                title: t('components.stepperStep3', 'Verified Results'),
                description: 'Official portals',
              },
            ]}
            currentStep={activeStep}
            onStepClick={(step) => setActiveStep(step)}
          />
          <div className="mt-4 flex justify-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              disabled={activeStep === 0}
              onClick={() => setActiveStep((prev) => Math.max(0, prev - 1))}
            >
              Previous Step
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={activeStep === 2}
              onClick={() => setActiveStep((prev) => Math.min(2, prev + 1))}
            >
              Next Step
            </Button>
          </div>
        </div>
      </Card>

      {/* Badges & Status Tokens */}
      <Card className="space-y-4 p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>Status Tokens & Badges</CardTitle>
          <CardDescription>
            Status colours strictly tested for WCAG 2.1 AA (4.5:1 ratio): Eligible =
            green, Maybe eligible = saffron on light tint, Not eligible = neutral grey
            with reason text in #B3261E.
          </CardDescription>
        </CardHeader>
        <div className="flex flex-wrap items-center gap-4">
          <Badge status="eligible">{t('status.eligible', 'Eligible')}</Badge>
          <Badge status="maybe">{t('status.maybeEligible', 'Maybe Eligible')}</Badge>
          <Badge status="not-eligible" reason="Income exceeds ₹2.5L limit">
            {t('status.notEligible', 'Not Eligible')}
          </Badge>
          <Badge variant="navy">Central Ministry Scheme</Badge>
          <Badge variant="neutral">Verified Oct 2026</Badge>
        </div>
      </Card>

      {/* Buttons & Input Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card className="space-y-4 p-6">
          <CardHeader className="px-0 pt-0">
            <CardTitle>Button Variants & States</CardTitle>
            <CardDescription>
              Primary (#138808), Secondary (#0B2A5B), Ghost, with 44px minimum tap
              targets.
            </CardDescription>
          </CardHeader>
          <div className="flex flex-wrap gap-3">
            <Button variant="primary">
              {t('components.buttonPrimary', 'Primary Action')}
            </Button>
            <Button variant="secondary">
              {t('components.buttonSecondary', 'Secondary Action')}
            </Button>
            <Button variant="ghost">{t('components.buttonGhost', 'Ghost Action')}</Button>
            <Button
              variant="primary"
              isLoading={isButtonLoading}
              onClick={() => {
                setIsButtonLoading(true);
                setTimeout(() => setIsButtonLoading(false), 2000);
              }}
            >
              {isButtonLoading ? 'Loading...' : 'Click to Load'}
            </Button>
            <Button variant="primary" disabled>
              Disabled
            </Button>
          </div>
        </Card>

        <Card className="space-y-4 p-6">
          <CardHeader className="px-0 pt-0">
            <CardTitle>TextInput with Label & Error Text</CardTitle>
            <CardDescription>
              Accessible label, helper text, and WCAG AA #B3261E error styling with 3px
              Navy focus ring.
            </CardDescription>
          </CardHeader>
          <TextInput
            label={t('components.inputLabel', 'Household State / Location')}
            required
            value={inputText}
            onChange={(e) => {
              setInputText(e.target.value);
              if (e.target.value.trim().length < 3) {
                setInputError(
                  t('components.inputError', 'Please provide a valid state name')
                );
              } else {
                setInputError('');
              }
            }}
            helperText={t(
              'components.inputHelper',
              'Enter your state of permanent residence'
            )}
            errorText={inputError}
          />
        </Card>
      </div>

      {/* Alerts */}
      <div className="space-y-3">
        <Alert variant="info" title="Official Source Synchronization">
          All criteria data synced with Government of India ministry gazettes up to
          October 2026.
        </Alert>
        <Alert variant="warning" title="Document Verification Warning">
          Applicants must ensure their land registration certificate matches the district
          land registry.
        </Alert>
        <Alert variant="error" title="Disqualification Criteria Detected">
          Annual family income reported exceeds the statutory maximum ceiling for this
          subsidy program.
        </Alert>
        <Alert variant="success" title="Eligibility Confirmed">
          You satisfy all criteria for PM Surya Ghar Muft Bijli Yojana. Estimated annual
          benefit: ₹18,000.
        </Alert>
      </div>

      {/* ChatBubble & Checklist */}
      <div className="grid grid-cols-1 items-start gap-6 md:grid-cols-2">
        <Card className="p-6">
          <CardHeader className="px-0 pt-0">
            <CardTitle>ChatBubble Component</CardTitle>
            <CardDescription>
              Conversational assistant updates with aria-live, avatar, timestamps, and
              typing state.
            </CardDescription>
          </CardHeader>
          <div className="space-y-2 rounded-xl border border-[#D9E0EA] bg-[#F7F9FC] p-4">
            <ChatBubble
              sender="assistant"
              message={t(
                'components.chatBotMessage',
                'Yes, under PM-KUSUM Component B, farmers can get up to 60% subsidy on standalone solar water pumping systems.'
              )}
              timestamp="10:42 AM"
            />
            <ChatBubble
              sender="user"
              message={t(
                'components.chatUserMessage',
                'Can small farmers in Uttar Pradesh receive financial support for solar pumps?'
              )}
              timestamp="10:43 AM"
            />
            <ChatBubble sender="assistant" isLoading />
          </div>
        </Card>

        <Checklist
          title={t('components.checklistTitle', 'Required Documents Checklist')}
          subtitle="Check each document you currently have available:"
          items={checklistItems}
          onToggle={handleToggleChecklist}
        />
      </div>

      {/* Tabs & Card States Demo */}
      <Card className="p-6">
        <CardHeader className="px-0 pt-0">
          <CardTitle>Tabs & Card States (Loading, Error, Empty)</CardTitle>
          <CardDescription>
            Accessible keyboard operable tabs (Arrow keys / Home / End) and dynamic card
            state toggles.
          </CardDescription>
        </CardHeader>

        <div className="mb-4 flex items-center gap-2">
          <span className="text-xs font-semibold text-[#55627A]">
            Simulate Card State:
          </span>
          {['normal', 'loading', 'error', 'empty'].map((state) => (
            <button
              key={state}
              type="button"
              onClick={() => setCardState(state)}
              className={`rounded border px-2.5 py-1 text-xs font-semibold capitalize ${
                cardState === state
                  ? 'border-[#0B2A5B] bg-[#0B2A5B] text-white'
                  : 'border-[#D9E0EA] bg-white text-[#55627A] hover:bg-[#F7F9FC]'
              }`}
            >
              {state}
            </button>
          ))}
        </div>

        <Card
          isLoading={cardState === 'loading'}
          isError={cardState === 'error'}
          isEmpty={cardState === 'empty'}
          errorMessage="Network timeout while contacting eligibility rule engine."
          onRetry={() => setCardState('normal')}
          emptyTitle={t('components.emptyTitle', 'No Schemes Found')}
          emptyDescription={t(
            'components.emptyDesc',
            'No schemes match your current criteria. Try adjusting your filters.'
          )}
          emptyAction={
            <Button variant="primary" size="sm" onClick={() => setCardState('normal')}>
              Reset Filters
            </Button>
          }
        >
          <CardContent className="p-0">
            <Tabs
              tabs={[
                {
                  id: 'overview',
                  label: 'Scheme Overview',
                  content: (
                    <div className="space-y-3 py-2 text-sm text-[#1A2433]">
                      <p>
                        <strong>PM-KUSUM:</strong> Flagship central government initiative
                        empowering farmers to replace diesel pumps with solar energy.
                      </p>
                      <div className="grid grid-cols-1 gap-3 pt-2 sm:grid-cols-2">
                        <div className="rounded-lg border border-[#D9E0EA] bg-[#F7F9FC] p-3">
                          <p className="font-bold text-[#0B2A5B]">Subsidy Percentage</p>
                          <p className="text-sm font-bold text-[#138808]">Up to 60%</p>
                        </div>
                        <div className="rounded-lg border border-[#D9E0EA] bg-[#F7F9FC] p-3">
                          <p className="font-bold text-[#0B2A5B]">Target Beneficiaries</p>
                          <p className="text-sm text-[#55627A]">
                            Individual farmers, water user associations
                          </p>
                        </div>
                      </div>
                    </div>
                  ),
                },
                {
                  id: 'criteria',
                  label: 'Eligibility Criteria',
                  count: 3,
                  content: (
                    <ul className="list-disc space-y-1.5 py-2 pl-5 text-sm text-[#55627A]">
                      <li>
                        Beneficiary must own agricultural land with clear title records.
                      </li>
                      <li>
                        Must not have an existing grid electric pump connection on the
                        same parcel.
                      </li>
                      <li>
                        Pump size up to 7.5 HP is eligible for full capital subsidy.
                      </li>
                    </ul>
                  ),
                },
                {
                  id: 'source',
                  label: 'Official Ministry Source',
                  content: (
                    <div className="space-y-2 py-2 text-sm">
                      <p className="text-[#55627A]">
                        Ministry of New and Renewable Energy (MNRE), Government of India.
                      </p>
                    </div>
                  ),
                },
              ]}
              activeTab={activeTab}
              onChange={setActiveTab}
            />
          </CardContent>
        </Card>
      </Card>

      {/* Accessible Native Modal Dialog */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={t('components.modalTitle', 'Official Verification Guarantee')}
        description={t(
          'components.modalDesc',
          'YojanaSetu is committed to providing factual, unbiased welfare scheme guidance.'
        )}
        footer={
          <>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              {t('common.close', 'Close')}
            </Button>
            <Button variant="primary" onClick={() => setModalOpen(false)}>
              Understood
            </Button>
          </>
        }
      >
        <div className="space-y-4 text-sm text-[#1A2433]">
          <p>
            YojanaSetu operates under a strict transparency standard. Every criterion and
            qualification decision is deterministically matched against publicly published
            gazettes from respective ministries.
          </p>
          <div className="rounded-lg border border-[#A3D9A3] bg-[#EAF5EA] p-3 text-xs text-[#0E6606]">
            🔒 <strong>Zero Data Collection:</strong> We never transmit, store, or ask for
            your identity card numbers. You can use YojanaSetu completely anonymously.
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default DesignSystemPage;
