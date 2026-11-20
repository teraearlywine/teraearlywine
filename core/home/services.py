"""Public service copy shared by page routes, navigation, and the sitemap."""

from core.home.blog_content import OFFERS


WAREHOUSE_DIAGNOSTIC_SLUG = 'warehouse-cost-diagnostic'

SERVICES = {
    'data-platform-modernization': {
        'name': 'Data and reporting',
        'title': 'Data and Reporting Consulting | Tera Earlywine',
        'description': (
            'Resolve conflicting metrics and improve recurring reports with shared '
            'definitions, data quality checks, and a handoff your team can maintain.'
        ),
        'headline': 'The same question returns two numbers.',
        'intro': (
            'I help the people who build and use your reports agree on what the '
            'numbers mean and fix the data behind them.'
        ),
        'deliverables': [
            ('Shared definitions', 'Agreed metric definitions, business rules, and owners.'),
            ('Reporting fixes', 'Data models and quality checks for the reports your team uses to make decisions.'),
            ('A handoff', 'Documentation and a walkthrough so your team can maintain the changes.'),
        ],
        'approach': (
            'We trace one disputed number or recurring manual fix to its source. '
            'Then we test the change with the people who use the report.'
        ),
        'experience': (
            'I aligned stakeholders on shared data definitions, built a prototype, '
            'and taught the approach to the implementation team.'
        ),
        'starting_point': (
            'Bring one report people question or one manual step your team repeats. '
            'We’ll use it to decide what to fix first.'
        ),
    },
    'data-migration-rescue': {
        'name': 'Migration rescue',
        'title': 'Data Migration Rescue Consulting | Tera Earlywine',
        'description': (
            'Get a stalled data migration ready for cutover with a dependency map, '
            'reconciliation checks, and clear criteria for switching over or rolling back.'
        ),
        'headline': 'Know when it’s safe to switch over.',
        'intro': (
            'If the old and new systems disagree or another dependency turns up '
            'late, I help your team decide what needs fixing before the cutover.'
        ),
        'deliverables': [
            ('Dependency map', 'The jobs, reports, applications, and teams affected by the cutover.'),
            ('Reconciliation checks', 'Tests for completeness, freshness, and the business rules behind the numbers.'),
            ('Cutover runbook', 'Who makes the call, what must pass, and when and how to roll back.'),
        ],
        'approach': (
            'We trace one discrepancy through both systems, check the fix against '
            'the downstream report, and rehearse the cutover with the team that will run it.'
        ),
        'experience': (
            'I’ve worked on migration programs spanning 500+ workflows, where '
            'dependencies and reporting continuity matter at every cutover.'
        ),
        'starting_point': (
            'Bring one mismatch, the current cutover plan, and the deadline. '
            'We’ll use them to identify what’s blocking the next release.'
        ),
    },
    'production-ai-systems': {
        'name': 'AI and workflow automation',
        'title': 'AI and Workflow Automation Consulting | Tera Earlywine',
        'description': (
            'Automate one recurring task or strengthen an AI pilot with a tested '
            'workflow, clear human review, and a plan for safe handoff.'
        ),
        'headline': 'Take one recurring task off your team’s plate.',
        'intro': (
            'If people keep gathering, copying, or checking the same information, '
            'I help your team decide what to automate, test it, and define where '
            'a person should step in.'
        ),
        'deliverables': [
            ('A map of the work', 'Which steps to simplify, which to automate, and who owns the result.'),
            ('A tested workflow', 'A prototype or integration checked against real examples, costs, and failure scenarios.'),
            ('A plan to run it', 'What people review, who handles exceptions, and how to recover when something goes wrong.'),
        ],
        'approach': (
            'We agree on what would make the change worthwhile before building it. '
            'If you already have a pilot, we check its permissions, review steps, '
            'and recovery before it goes live.'
        ),
        'experience': (
            'I designed an audit-agent proof of concept that recorded its steps '
            'and decisions for reviewers and surfaced gaps to address before production.'
        ),
        'starting_point': (
            'Bring one repeated task or an existing pilot and an example of the '
            'result someone needs. We’ll work out what to test first.'
        ),
    },
    'fractional-data-leadership': {
        'name': 'Data and AI project delivery',
        'title': 'Data and AI Project Delivery Consulting | Tera Earlywine',
        'description': (
            'Resolve the decisions holding up a data or AI project and give both '
            'teams a shared scope, a delivery plan, and clear owners.'
        ),
        'headline': 'Make the decision holding up your project.',
        'intro': (
            'When business and technical teams are working toward different goals, '
            'I bring them together to agree on what to deliver, who owns it, and '
            'what to do next.'
        ),
        'deliverables': [
            ('Shared scope', 'The outcome, what’s in scope, and how both teams will judge success.'),
            ('Delivery plan', 'Priorities, dependencies, named owners, and review points.'),
            ('A handoff', 'Decision records, documentation, and a walkthrough for the people carrying the work forward.'),
        ],
        'approach': (
            'We start with the decision that’s blocking progress. I lead the work '
            'of getting both teams to agreement and can help review the design or '
            'build the solution when that’s part of the scope.'
        ),
        'experience': (
            'My work has included translating business rules into data definitions '
            'and teaching the team responsible for implementation how to apply them.'
        ),
        'starting_point': (
            'Bring one stalled decision and tell me who needs to make it. '
            'We’ll work out where I can help move the project forward.'
        ),
    },
    WAREHOUSE_DIAGNOSTIC_SLUG: {
        'name': OFFERS['diagnostic']['name'],
        'title': 'Warehouse Cost Diagnostic | Tera Earlywine',
        'description': (
            'A paid review of one data warehouse and a defined set of workloads. '
            'Get a cost baseline, ranked changes, and a plan to measure the results.'
        ),
        'headline': 'Your warehouse bill went up. What should you change first?',
        'intro': (
            'I review one warehouse and a defined set of workloads to find what’s '
            'driving the bill and which changes are worth testing. This is a paid diagnostic.'
        ),
        'deliverables': [
            ('Cost baseline', 'Recurring costs attributable to the workloads in scope and the assumptions behind them.'),
            ('Ranked changes', 'What to test first, with estimated benefit, effort, and risk to reporting.'),
            ('Measurement plan', 'What to compare before and after, including billed compute, data freshness, and report accuracy.'),
        ],
        'approach': (
            'I review billing and query history to trace costs to the jobs and '
            'reports they support. We review the recommendations together and '
            'scope implementation separately.'
        ),
        'sample': {
            'title': 'Example recommendation',
            'change': 'Test moving a dashboard refresh from every five minutes to every 15 minutes.',
            'details': [
                'Scheduled runs fall from 288 to 96 per day. Check whether billed compute falls as well.',
                'Confirm the refresh requirement with the report owner and keep the old schedule ready to restore.',
                'Compare billed compute and freshness over similar weeks and reconcile the report totals before keeping the change.',
            ],
        },
        'experience': (
            'My optimization work identified $500K+ in projected Snowflake savings.'
        ),
        'starting_point': (
            'Bring one unexpected charge or one workload you want to understand. '
            'We’ll use it to scope the review.'
        ),
    },
}
