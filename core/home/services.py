"""Public service copy shared by page routes, navigation, and the sitemap."""

SERVICES = {
    'data-platform-modernization': {
        'name': 'Data platform modernization',
        'title': 'Data Platform Modernization Consultant | Tera Earlywine',
        'description': (
            'Modernize enterprise data platforms with clear architecture, ownership, '
            'quality controls, and a practical migration plan. Work with Tera '
            'Earlywine.'
        ),
        'headline': 'Build a foundation your team can trust.',
        'intro': (
            'I help enterprise data leaders modernize the systems their reporting, '
            'compliance, and AI depend on. The work starts with the decisions your '
            'platform needs to support and the production constraints it has to '
            'respect.'
        ),
        'problem_title': 'When the platform becomes the constraint.',
        'problem': (
            'A growing stack can leave your team with inconsistent business '
            'definitions, fragile dependencies, rising costs, and unclear ownership. '
            'Replacing tools alone does not resolve those problems. I work through the'
            ' architecture and operating model together, so a new platform has a clear'
            ' purpose and a team that can run it.'
        ),
        'signals': [
            'Teams reconcile competing versions of the same metric.',
            'New analytics or AI work stalls on data quality and access.',
            'Platform cost and maintenance grow faster than business value.',
        ],
        'deliverables': [
            (
                'Current-state assessment',
                (
                    'A map of critical workflows, consumers, dependencies, and the '
                    'risks that constrain delivery.'
                ),
            ),
            (
                'Data Foundation Blueprint',
                (
                    'Target architecture, data contracts, quality checks, access '
                    'controls, and explicit ownership.'
                ),
            ),
            (
                'Sequenced migration plan',
                (
                    'A practical order of work with validation, cutover, rollback, and'
                    ' operating responsibilities.'
                ),
            ),
        ],
        'approach': (
            'I begin with a bounded assessment of the workloads that matter most. '
            'Together, we identify what should stay, what needs to change, and what '
            'evidence will justify each step. A blueprint then connects technical '
            'decisions to business priorities and gives the delivery team a sequence '
            'it can execute.'
        ),
        'experience': (
            'My experience spans enterprise migration programs, data-platform '
            'leadership at Block and Mercari, and hands-on work with SQL, Python, dbt,'
            ' Airflow, Snowflake, BigQuery, and GCP. I bring that operating context to'
            ' architecture decisions, including the handoff and maintenance work that '
            'follows a launch.'
        ),
        'starting_point': (
            'Bring the business priorities, the current platform constraints, and one '
            'workflow that illustrates the problem. A fit call helps us decide whether'
            ' a diagnostic or a Data Foundation Blueprint is the right starting point.'
        ),
    },
    'data-migration-rescue': {
        'name': 'Data migration rescue',
        'title': 'Data Migration Rescue Consultant | Tera Earlywine',
        'description': (
            'Get a stalled data migration moving with dependency mapping, '
            'reconciliation, cutover planning, and rollback criteria. Independent '
            'consulting by Tera Earlywine.'
        ),
        'headline': 'Give a stalled migration a credible path forward.',
        'intro': (
            'I help teams recover data migrations when the deadline is approaching, '
            'the results do not reconcile, or production continuity is at risk. The '
            'first task is to make the failure modes visible and agree on what a safe '
            'next step looks like.'
        ),
        'problem_title': 'When moving the data is only part of the problem.',
        'problem': (
            'A migration can look nearly complete while downstream reports still '
            'disagree, undocumented dependencies keep appearing, and no one owns the '
            'cutover decision. I trace the gap between the old and new systems, '
            'separate blockers from follow-up work, and help your team establish a '
            'realistic release boundary.'
        ),
        'signals': [
            'Validation results disagree and the cause is unclear.',
            'Cutover dates move because dependencies keep surfacing.',
            'The team needs a recovery plan while keeping production running.',
        ],
        'deliverables': [
            (
                'Migration risk review',
                (
                    'A dependency map, blocker inventory, and prioritized recovery '
                    'plan tied to affected business workflows.'
                ),
            ),
            (
                'Reconciliation strategy',
                (
                    'Source-to-target checks for business logic, completeness, '
                    'freshness, and the exceptions that require review.'
                ),
            ),
            (
                'Cutover and recovery plan',
                (
                    'Readiness criteria, named decision owners, rollback triggers, and'
                    ' a runbook for the transition.'
                ),
            ),
        ],
        'approach': (
            'I start with a representative failing workflow and follow it through the '
            'source, transformation, and consuming system. That gives us a concrete '
            'basis for diagnosis. We then agree on acceptance criteria, sequence the '
            'fixes, and rehearse the transition with the people who will own it in '
            'production.'
        ),
        'experience': (
            'My work has included enterprise migration programs spanning 500+ '
            'workflows. That experience informs how I approach dependencies, business-'
            'logic validation, and production continuity. I combine hands-on data '
            'engineering with the coordination needed to make release decisions '
            'understandable to both engineering and business owners.'
        ),
        'starting_point': (
            'Bring the current migration plan, the most important unresolved '
            'discrepancy, and the deadline or operational constraint driving urgency. '
            'We can use the fit call to identify the smallest useful diagnostic scope.'
        ),
    },
    'production-ai-systems': {
        'name': 'Production AI systems',
        'title': 'Production AI Systems Consultant | Tera Earlywine',
        'description': (
            'Move an AI workflow toward production with evaluation, permissions, '
            'recovery, monitoring, and human escalation. Work with independent '
            'consultant Tera Earlywine.'
        ),
        'headline': 'Make an AI workflow ready for real operations.',
        'intro': (
            'I help enterprise teams turn a promising AI workflow into a system they '
            'can evaluate, control, and operate. The focus is a bounded business use '
            'case with clear ownership and evidence for a production-readiness '
            'decision.'
        ),
        'problem_title': 'When a successful demo still leaves unanswered questions.',
        'problem': (
            'An AI pilot may work in a demonstration while leaving accuracy, '
            'permissions, failure recovery, and ongoing cost unresolved. In regulated '
            'and critical operations, those questions shape the system. I work through'
            ' the data foundation and operational controls alongside the workflow '
            'itself.'
        ),
        'signals': [
            'A pilot has value, but no agreed evaluation or release criteria.',
            'An agent needs access to business systems with clear limits.',
            'The team needs to recover from failures and explain what happened.',
        ],
        'deliverables': [
            (
                'Scoped workflow and controls',
                (
                    'An integrated workflow with defined inputs, state, permissions, '
                    'and human escalation points.'
                ),
            ),
            (
                'Evaluation report',
                (
                    'An assessment of accuracy, latency, cost, and failure cases '
                    'against agreed acceptance criteria.'
                ),
            ),
            (
                'Operational handoff',
                (
                    'Monitoring, recovery procedures, a runbook, and explicit '
                    'responsibilities for ongoing operation.'
                ),
            ),
        ],
        'approach': (
            'The Production AI Lighthouse starts with one use case and the evidence '
            'needed to judge it. I establish a baseline, build the smallest useful '
            'workflow, and test its behavior under realistic failure conditions. We '
            'use the results to decide whether to release, revise, or stop before '
            'expanding the scope.'
        ),
        'experience': (
            'I bring enterprise data engineering experience across fintech, '
            'marketplaces, and regulated operations. I am designing a governed multi-'
            'agent system for compliance data engineering, with attention to '
            'auditability, security, and reliability. That ongoing work informs my '
            'approach to state, permissions, recovery, and operational ownership.'
        ),
        'starting_point': (
            'Bring one workflow, the decision it supports, and the consequences of an '
            'incorrect or incomplete result. The fit call helps establish whether the '
            'data foundation is ready and whether a scoped lighthouse engagement makes'
            ' sense.'
        ),
    },
    'fractional-data-leadership': {
        'name': 'Fractional data leadership',
        'title': 'Fractional Data Platform Leadership | Tera Earlywine',
        'description': (
            'Get independent data-platform leadership for architecture decisions, '
            'delivery priorities, governance, and production operations. Consulting by'
            ' Tera Earlywine.'
        ),
        'headline': 'Give critical data work clear direction.',
        'intro': (
            'I work with enterprise leaders who need experienced data-platform '
            'judgment and hands-on delivery support. Fractional leadership connects '
            'business priorities, technical decisions, and the operating '
            'responsibilities that keep a platform reliable.'
        ),
        'problem_title': 'When the team needs decisions as much as delivery.',
        'problem': (
            'A capable team can still be pulled between urgent incidents, a migration '
            'backlog, cost pressure, and new AI requests. Without an agreed direction,'
            ' every decision becomes a separate negotiation. I help establish '
            'priorities, clarify ownership, and make the tradeoffs visible enough to '
            'act on.'
        ),
        'signals': [
            'Architecture and investment decisions lack a clear owner.',
            'Operational work repeatedly displaces strategic priorities.',
            'The team needs senior guidance during a transition or delivery push.',
        ],
        'deliverables': [
            (
                'Prioritized platform roadmap',
                (
                    'A sequence of decisions and delivery milestones grounded in '
                    'business value, production risk, and team capacity.'
                ),
            ),
            (
                'Architecture and delivery guidance',
                (
                    'Decision records, design reviews, and hands-on support for the '
                    'highest-priority platform work.'
                ),
            ),
            (
                'Operating model',
                (
                    'Clear ownership, review practices, escalation paths, and a '
                    'handoff plan that supports the internal team.'
                ),
            ),
        ],
        'approach': (
            'I begin by understanding the team, the commitments already in flight, and'
            ' the decisions that are blocked. We agree on a bounded remit and a '
            'working cadence, then connect architecture review and delivery support to'
            ' that remit. The aim is to strengthen the team’s ability to make and '
            'carry out decisions.'
        ),
        'experience': (
            'My background includes staff-level data engineering at Block, data '
            'engineering at Mercari, and independent consulting. I have worked across '
            'platform modernization, reliability, governance, and business-facing data'
            ' products. That mix helps me connect detailed implementation questions to'
            ' the wider delivery and operating context.'
        ),
        'starting_point': (
            'Bring the decisions that are waiting, the team structure, and the '
            'outcomes you need to protect. We can use a fit call to determine the '
            'leadership scope, where hands-on support would help, and how ownership '
            'should transition over time.'
        ),
    },
}
