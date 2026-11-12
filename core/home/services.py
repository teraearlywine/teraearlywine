"""Public service copy shared by page routes, navigation, and the sitemap."""

SERVICES = {
    'data-platform-modernization': {
        'name': 'Data platform modernization',
        'title': 'Data Platform Modernization Consultant | Tera Earlywine',
        'description': (
            'Modernize the data behind reporting, compliance, and AI. Work with Tera '
            'Earlywine to map critical workflows, define ownership, and plan migration.'
        ),
        'headline': 'Make the warehouse easier to run.',
        'intro': (
            'A report changes when you switch dashboards. The same transformations '
            'run over and over. I help your engineers trace what the business depends '
            'on and decide where a platform change will pay off.'
        ),
        'problem_title': 'The same question returns two numbers.',
        'problem': (
            'Competing definitions, expensive refreshes, and unknown downstream '
            'consumers make even simple changes hard to release. I work with the '
            'people who build and use the data to identify the first useful repair.'
        ),
        'signals': [
            'Teams reconcile competing versions of the same metric.',
            'Warehouse costs are rising faster than the workloads they support.',
            'Quality or access issues are blocking analytics and AI work.',
        ],
        'deliverables': [
            ('Workload assessment', 'A map of critical jobs, consumers, operating costs, and ownership gaps.'),
            ('Data Foundation Blueprint', 'The target architecture, data contracts, access model, and tests.'),
            ('Migration sequence', 'An order of work with decision owners, cutover checks, and a rollback path.'),
        ],
        'approach': (
            'We start with one decision the platform has to support. We follow the '
            'data into the report or application, identify redundant work, and agree '
            'which checks will tell us the change is safe.'
        ),
        'experience': (
            'My work includes enterprise migrations, platform engineering at Block '
            'and Mercari, and infrastructure optimization that contributed to $500K+ '
            'in Snowflake savings.'
        ),
        'starting_point': (
            'For a smaller team, the paid Data Waste & Efficiency Diagnostic reviews '
            'one warehouse and a defined set of workloads. Bring query history, billing '
            'context, and a workload owner. You leave with a baseline, ranked improvements, '
            'explicit assumptions, and a measurement plan.'
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
        'headline': 'Get the next cutover ready.',
        'intro': (
            'When a growing platform has two versions of the truth, the next release '
            'needs more than a date. I trace the failing workflow with your team, '
            'identify what depends on it, and document when to switch over or roll back.'
        ),
        'problem_title': 'The deadline keeps moving.',
        'problem': (
            'Downstream reports disagree and new dependencies appear each time the team '
            'rehearses a cutover. I help your engineers separate release blockers from '
            'follow-up work and give each blocker an owner.'
        ),
        'signals': [
            'Source and target totals diverge.',
            'Consumer dependencies surface late.',
            'The team needs a recovery path while production keeps running.',
        ],
        'deliverables': [
            ('Dependency map', 'The jobs, people, reports, and applications affected by the first cutover.'),
            ('Reconciliation checks', 'Tests for completeness, freshness, and the business rules behind the numbers.'),
            ('Cutover runbook', 'Acceptance criteria, decision owners, rollback triggers, and a rehearsed path back.'),
        ],
        'approach': (
            'We choose one representative discrepancy, reproduce it in both systems, '
            'and test the fix against the downstream result. Then we rehearse the '
            'transition with the people who will own it in production.'
        ),
        'experience': (
            'I’ve worked on migration programs spanning 500+ workflows. That experience '
            'informs how I trace dependencies and verify the reports that need to stay available.'
        ),
        'starting_point': (
            'Bring one unresolved discrepancy, the current cutover plan, and the deadline '
            'driving the work. We can use those to scope a recovery review.'
        ),
    },
    'production-ai-systems': {
        'name': 'Production AI systems',
        'title': 'Production AI Systems Consultant | Tera Earlywine',
        'description': (
            'Move an AI workflow toward production with evaluation, permissions, '
            'recovery, monitoring, and human escalation. Work with Tera Earlywine.'
        ),
        'headline': 'Give the production reviewer evidence.',
        'intro': (
            'When a pilot is ready for review, I work alongside your platform, data, and '
            'risk teams to test one workflow under real operating constraints.'
        ),
        'problem_title': 'The demo works. The operating questions are open.',
        'problem': (
            'A production reviewer needs to know which actions the workflow can take, '
            'where a human intervenes, and how operators recover from a partial failure. '
            'Those answers shape the release.'
        ),
        'signals': [
            'The team has a promising pilot and needs evaluation criteria.',
            'An agent needs controlled access to business systems.',
            'Operators need to explain or recover from a failed run.',
        ],
        'deliverables': [
            ('Scoped workflow', 'Defined inputs, permissions, state, and human escalation points.'),
            ('Evaluation report', 'Results for accuracy, latency, cost, and agreed failure scenarios.'),
            ('Operational handoff', 'Monitoring, a recovery runbook, and explicit responsibilities for operating the workflow.'),
        ],
        'approach': (
            'The Production AI Lighthouse starts with one use case. We establish a '
            'baseline, integrate the workflow, and test it against agreed launch criteria. '
            'Your team gets the evidence to release, revise, or stop.'
        ),
        'experience': (
            'I’m designing a governed multi-agent system for Block’s compliance data '
            'engineering team, with a focus on access, auditability, and operational reliability.'
        ),
        'starting_point': (
            'Bring one workflow, a person who owns its outcome, and an example of a '
            'wrong or incomplete result. We can use those to scope the evaluation.'
        ),
    },
    'fractional-data-leadership': {
        'name': 'Fractional data leadership',
        'title': 'Fractional Data Platform Leadership | Tera Earlywine',
        'description': (
            'Get independent data-platform leadership for architecture decisions, '
            'delivery priorities, governance, and production operations. Consulting by Tera Earlywine.'
        ),
        'headline': 'Put a senior data engineer alongside your team.',
        'intro': (
            'When platform decisions are waiting for an owner, I help your engineering '
            'leadership agree on priorities and work through the technical decisions with your team.'
        ),
        'problem_title': 'The team has more commitments than capacity.',
        'problem': (
            'A migration, recurring incidents, and new AI requests can compete for the '
            'same engineers. I help make the tradeoffs explicit and identify what needs a decision first.'
        ),
        'signals': [
            'Architecture and investment decisions lack a clear owner.',
            'Operational work keeps displacing planned improvements.',
            'The team needs experienced support during a transition.',
        ],
        'deliverables': [
            ('Platform roadmap', 'Priorities tied to business decisions, production risk, and team capacity.'),
            ('Decision record', 'Documented design choices, dependencies, and the evidence behind them.'),
            ('Operating model', 'Owners, review practices, escalation paths, and a handoff your internal team can use.'),
        ],
        'approach': (
            'We map the decisions waiting on your team and agree on a bounded remit, '
            'working cadence, and handoff. I join design reviews and contribute directly '
            'to the platform work that needs senior engineering attention.'
        ),
        'experience': (
            'My background includes staff data engineering at Block, warehouse and data '
            'engineering at Mercari, and independent consulting across data reliability and production AI.'
        ),
        'starting_point': (
            'Bring the decisions that are waiting, your team structure, and the outcomes '
            'you need to protect. We can agree on which responsibilities I can take on.'
        ),
    },
}
