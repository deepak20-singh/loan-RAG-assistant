TEST_CASES = [
    # ========== POLICY QUESTIONS ==========
    {
        "id": "POLICY_001",
        "description": "Basic credit score requirement",
        "query": "What's the minimum credit score needed for a $40,000 loan?",
        "type": "policy",
        "expected_keywords": ["650", "credit score"],
    },
    {
        "id": "POLICY_002",
        "description": "Credit score for large loan",
        "query": "What credit score do I need for a $300,000 loan?",
        "type": "policy",
        "expected_keywords": ["740", "credit score"],
    },
    {
        "id": "POLICY_003",
        "description": "DTI requirements",
        "query": "What's the maximum debt-to-income ratio you accept?",
        "type": "policy",
        "expected_keywords": ["50", "DTI"],
    },
    {
        "id": "POLICY_004",
        "description": "Documentation requirements",
        "query": "What documents do I need to apply?",
        "type": "policy",
        "expected_keywords": ["tax returns", "bank statements"],
    },
    {
        "id": "POLICY_005",
        "description": "Restricted industries",
        "query": "Can I get a loan for a cannabis business?",
        "type": "policy",
        "expected_keywords": ["cannabis", "prohibited", "no"],
    },
    {
        "id": "POLICY_006",
        "description": "Startup loan availability",
        "query": "I just started my business 6 months ago. Can I still apply?",
        "type": "policy",
        "expected_keywords": ["startup", "25,000", "720"],
    },
    {
        "id": "POLICY_007",
        "description": "Interest rates",
        "query": "What interest rates can I expect with a 720 credit score?",
        "type": "policy",
        "expected_keywords": ["9", "12", "tier 2"],
    },
    {
        "id": "POLICY_008",
        "description": "SBA programs",
        "query": "Tell me about SBA loan programs",
        "type": "policy",
        "expected_keywords": ["SBA", "7(a)", "504"],
    },
    {
        "id": "POLICY_009",
        "description": "Veteran benefits",
        "query": "Are there special programs for veterans?",
        "type": "policy",
        "expected_keywords": ["veteran", "reduced fees", "priority"],
    },
    {
        "id": "POLICY_010",
        "description": "Edge case - not in policies",
        "query": "Can you give me legal advice on my business structure?",
        "type": "policy",
        "expected_keywords": ["unable", "not", "policy"],
        "note": "System should refuse / say it doesn't know"
    },

    # ========== LOAN ASSESSMENTS ==========
    {
        "id": "ASSESS_001",
        "description": "Strong applicant - should approve",
        "query": "Can we approve a $50,000 working capital loan?",
        "applicant_id": "APP001",
        "type": "decision",
        "expected_decision": "approve",
        "note": "John Smith - 720 credit, low DTI, established"
    },
    {
        "id": "ASSESS_002",
        "description": "Weak applicant - should reject",
        "query": "Can we approve a $40,000 loan?",
        "applicant_id": "APP002",
        "type": "decision",
        "expected_decision": ["reject", "needs_review"],
        "note": "Jane Doe - 580 credit (below 650), DTI > 50%"
    },
    {
        "id": "ASSESS_003",
        "description": "Premium applicant - large loan",
        "query": "Can we approve a $500,000 expansion loan?",
        "applicant_id": "APP003",
        "type": "decision",
        "expected_decision": "approve",
        "note": "Robert Wilson - 785 credit, strong business"
    },
    {
        "id": "ASSESS_004",
        "description": "Borderline - should need review",
        "query": "Can we approve a $30,000 loan?",
        "applicant_id": "APP004",
        "type": "decision",
        "expected_decision": ["approve", "needs_review"],
        "note": "Maria Garcia - meets criteria but tight DTI"
    },
    {
        "id": "ASSESS_005",
        "description": "Construction industry consideration",
        "query": "Can we approve a $200,000 equipment loan?",
        "applicant_id": "APP005",
        "type": "decision",
        "expected_decision": "approve",
        "note": "David Chen - meets construction industry requirements"
    },
    {
        "id": "ASSESS_006",
        "description": "Prohibited industry - must reject",
        "query": "Can we approve a $100,000 loan?",
        "applicant_id": "APP006",
        "type": "decision",
        "expected_decision": "reject",
        "note": "Cannabis business - prohibited regardless of financials"
    },
    {
        "id": "ASSESS_007",
        "description": "Veteran applicant",
        "query": "Can we approve a $75,000 loan?",
        "applicant_id": "APP007",
        "type": "decision",
        "expected_decision": ["approve", "needs_review"],
        "note": "Michael Brown - veteran, meets criteria but DTI borderline"
    },
    {
        "id": "ASSESS_008",
        "description": "First-year retail business",
        "query": "Can we approve a $25,000 loan?",
        "applicant_id": "APP008",
        "type": "decision",
        "expected_decision": ["reject", "needs_review"],
        "note": "Emily Rodriguez - business too new, low DSCR"
    },
    {
        "id": "ASSESS_009",
        "description": "Startup with strong credit",
        "query": "Can we approve a $20,000 startup loan?",
        "applicant_id": "APP009",
        "type": "decision",
        "expected_decision": ["approve", "needs_review"],
        "note": "James Anderson - qualifies for startup program"
    },
    {
        "id": "ASSESS_010",
        "description": "Premium minority/women-owned",
        "query": "Can we approve a $400,000 expansion loan?",
        "applicant_id": "APP010",
        "type": "decision",
        "expected_decision": "approve",
        "note": "Lisa Patel - excellent profile, multiple program benefits"
    },

    # ========== EDGE CASES ==========
    {
        "id": "EDGE_001",
        "description": "Cache test - repeat query",
        "query": "What's the minimum credit score needed for a $40,000 loan?",
        "type": "policy",
        "expected_cached": True,
        "note": "Run after POLICY_001 to test exact cache"
    },
    {
        "id": "EDGE_002",
        "description": "Semantic cache test - similar query",
        "query": "What credit score is required for a $40k loan?",
        "type": "policy",
        "expected_cached": True,
        "note": "Should hit semantic cache from POLICY_001"
    },
    {
        "id": "EDGE_003",
        "description": "Invalid applicant ID",
        "query": "Can we approve a loan?",
        "applicant_id": "APP999",
        "type": "decision",
        "expected_error": True,
    },
    {
        "id": "EDGE_004",
        "description": "Empty query",
        "query": "",
        "type": "validation_error",
        "expected_error": True,
    },
    {
        "id": "EDGE_005",
        "description": "Out of scope question",
        "query": "What's the weather today?",
        "type": "policy",
        "note": "System should respond it doesn't know / not in policies"
    },
]