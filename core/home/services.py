"""Public service copy shared by page routes, navigation, and the sitemap."""

from core.home.blog_content import OFFERS


WAREHOUSE_DIAGNOSTIC_SLUG = 'warehouse-cost-diagnostic'

SERVICES = {
    'data-platform-modernization': {
        'name': 'Data and reporting',
        'title': 'Data and Reporting Consulting | Tera Earlywine',
        'description': (
            'Improve reporting, resolve conflicting metrics, and build data your team '
            'can rely on. Data consulting with Tera Earlywine.'
        ),
        'headline': 'Data your team can use.',
        'intro': (
            'When numbers disagree or reporting takes too much effort, decisions slow '
            'down. I help clarify what your metrics mean, improve data quality, and '
            'build reporting your team can rely on.'
        ),
        'problem_title': 'The same question returns two numbers.',
        'problem': (
            'Different definitions, manual fixes, and unclear responsibilities make '
            'reporting harder than it needs to be. I work with the people who build '
            'and use the data to agree on what the numbers should mean and where to '
            'make the first useful improvement.'
        ),
        'signals': [
            'Teams reconcile competing versions of the same metric.',
            'Recurring reports depend on manual steps or one person’s knowledge.',
            'Data quality, access, or platform costs are holding back useful work.',
        ],
        'deliverables': [
            ('Shared definitions', 'Metric definitions, business rules, and clear owners agreed with the people using the reports.'),
            ('Reporting improvements', 'Data models, quality checks, and reporting changes tied to the decisions your team needs to make.'),
            ('A practical handoff', 'Documentation and a walkthrough so your team understands the changes and can maintain them.'),
        ],
        'approach': (
            'We start with a business question and trace the data behind it. We agree '
            'on definitions, test a useful change, and work through the approach with '
            'the team carrying it forward. Platform cost reviews and migration '
            'planning are available when the underlying systems need attention.'
        ),
        'experience': (
            'My background spans business intelligence, data engineering, and consulting, '
            'including roles at Mercari and Block. My work has included aligning '
            'stakeholders on shared definitions, building a prototype, and teaching '
            'the approach to the implementation team. Optimization work also identified '
            '$500K+ in projected Snowflake savings.'
        ),
        'starting_point': (
            'Bring a report people question, a recurring manual task, or a decision '
            'your current data cannot support. We can use that example to define the '
            'problem and agree on a useful starting point. For a focused cost review, '
            'the paid Data Waste & Efficiency Diagnostic covers one warehouse and '
            'a defined set of workloads, with a baseline, ranked improvements, '
            'explicit assumptions, and a measurement plan.'
        ),
    },
    'data-migration-rescue': {
        'name': 'Data migration rescue',
        'title': 'Data Migration Rescue Consultant | Tera Earlywine',
        'description': (
            'Get a stalled data migration moving with dependency mapping, '
            'reconciliation, cutover planning, and rollback criteria. '
            'Consulting by Tera Earlywine.'
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
        'name': 'Practical AI and workflow automation',
        'title': 'AI and Workflow Automation Consulting | Tera Earlywine',
        'description': (
            'Find useful AI applications, automate repetitive work, and test workflows '
            'with clear human review and ownership. Consulting with Tera Earlywine.'
        ),
        'headline': 'Turn an AI idea into a useful workflow.',
        'intro': (
            'If your team spends hours gathering information, copying data, or repeating '
            'the same checks, there may be a better way to do the work. I help identify '
            'useful opportunities, build and test a workflow, and decide where a person '
            'should review the result.'
        ),
        'problem_title': 'The task keeps coming back.',
        'problem': (
            'A repeated task may be a good candidate for automation, but the right '
            'approach depends on the work and the people doing it. We look at the '
            'information needed, the mistakes that matter, and where human judgment '
            'belongs before choosing an AI or automation approach.'
        ),
        'signals': [
            'People repeatedly gather, copy, summarize, or check the same information.',
            'Your team has an AI idea but needs a practical way to test its usefulness.',
            'A promising pilot needs clearer review, permissions, or recovery steps.',
        ],
        'deliverables': [
            ('Workflow assessment', 'The current steps, dependencies, and opportunities to simplify or automate the work.'),
            ('A tested workflow', 'A prototype or integration evaluated against agreed examples, costs, and failure scenarios.'),
            ('Guidance for your team', 'Human review points, operating responsibilities, documentation, and a walkthrough for the people using it.'),
        ],
        'approach': (
            'We start with one workflow and the person who owns its outcome. We agree '
            'on what would make a change worthwhile, then build and test an appropriate '
            'solution. For a workflow moving toward production, we also work through '
            'access, evaluation, monitoring, and recovery with the teams responsible '
            'for operating it.'
        ),
        'experience': (
            'For a client, I designed an audit-agent proof of concept that recorded its '
            'steps and decisions for review. The work surfaced gaps in the process and '
            'documented what still needed attention before production. This was a '
            'proof of concept, not a production deployment.'
        ),
        'starting_point': (
            'Bring one repeated task or AI idea, an example of the current inputs and '
            'outputs, and the person who depends on the result. We can use those to '
            'scope a workflow assessment or a focused prototype.'
        ),
    },
    'fractional-data-leadership': {
        'name': 'Data and AI project delivery',
        'title': 'Data and AI Project Delivery Consulting | Tera Earlywine',
        'description': (
            'Get data and AI projects moving with clear requirements, shared priorities, '
            'better handoffs, and practical team support. Consulting with Tera Earlywine.'
        ),
        'headline': 'Get data and AI projects moving.',
        'intro': (
            'A project can stall when people have different definitions of the problem '
            'or no clear owner for the next decision. I help business and technical '
            'teams agree on requirements, choose priorities, and make handoffs easier '
            'to manage.'
        ),
        'problem_title': 'People are working toward different versions of the goal.',
        'problem': (
            'Business needs, technical constraints, and team capacity can pull a '
            'project in different directions. I bring the people involved together '
            'to clarify the outcome, make tradeoffs explicit, and agree on the next '
            'steps and who owns them.'
        ),
        'signals': [
            'Teams disagree on requirements, definitions, or what success looks like.',
            'Work is delayed by unclear priorities, decisions, or responsibilities.',
            'A team needs experienced support to plan delivery or take over a handoff.',
        ],
        'deliverables': [
            ('A shared project scope', 'The business problem, requirements, success criteria, and decisions agreed with the people involved.'),
            ('A delivery plan', 'Priorities, dependencies, responsibilities, and review points that account for team capacity.'),
            ('A team ready to continue', 'Decision records, documentation, and teaching that help the team carry the work forward.'),
        ],
        'approach': (
            'We start with the decisions holding up the work and agree on a bounded '
            'role. I work across business and technical teams to resolve requirements '
            'and support delivery. When senior technical leadership is needed, I can '
            'join architecture reviews and work directly on the data or AI solution.'
        ),
        'experience': (
            'My background spans business intelligence, data engineering, and consulting, '
            'including roles at Mercari and Block. My work has included aligning '
            'stakeholders on shared definitions, teaching implementation approaches, '
            'and helping teams continue the work after handoff.'
        ),
        'starting_point': (
            'Bring a project that is stuck, the decisions waiting to be made, and the '
            'people involved. We can agree on where I can help clarify the work and '
            'support your team through the next step.'
        ),
    },
    WAREHOUSE_DIAGNOSTIC_SLUG: {
        'name': OFFERS['diagnostic']['name'],
        'title': 'Warehouse Cost Diagnostic | Tera Earlywine',
        'description': (
            'A paid review of one data warehouse and a defined set of workloads. '
            'Get a cost baseline, ranked improvements, and a plan to verify savings.'
        ),
        'headline': 'Find out what is driving your warehouse bill.',
        'intro': (
            'A paid review of one warehouse and a defined set of workloads. Get a cost '
            'baseline, ranked recommendations, and a plan to verify the results.'
        ),
        'problem_title': 'Your warehouse bill went up. What would you change first?',
        'problem': (
            'A higher bill can come from more demand, repeated processing, or capacity you '
            'pay for even when it sits idle. I trace costs to the jobs and reports they '
            'support so your team can decide where to spend engineering time.'
        ),
        'signals': [
            'Costs are rising and your team cannot explain which workloads drove the increase.',
            'Recurring queries or refresh jobs look expensive, but their business requirements are unclear.',
            'Finance needs assumptions and a way to verify the benefit before funding a change.',
        ],
        'deliverables': [
            ('Cost baseline', 'The recurring costs we can attribute to the workloads in scope, with the period and assumptions behind them.'),
            ('Ranked recommendations', 'The changes worth testing first, with estimated benefit, engineering effort, and risks to the output.'),
            ('Measurement plan', 'What to compare before and after a change, including warehouse charges, data freshness, and reporting accuracy.'),
        ],
        'approach': (
            'We agree on the workloads and what each one needs to deliver. I review billing '
            'and query history with your team, then walk through which changes are worth '
            'testing and how to measure the results. We scope implementation separately.'
        ),
        'sample': {
            'title': 'Example recommendation',
            'change': 'Test moving a dashboard refresh from every five minutes to every 15 minutes.',
            'details': [
                'Expected benefit. Cut scheduled runs from 288 to 96 per day. Check whether that reduces billed compute for the shared warehouse.',
                'Engineering effort. Review refresh requirements with the report owner, change one schedule, and keep the existing schedule ready to restore.',
                'How to verify it. Compare billed compute and report freshness over comparable weeks, and reconcile the reported totals before keeping the change.',
            ],
        },
        'experience': (
            'My optimization work identified $500K+ in projected Snowflake savings. '
            'I connect technical recommendations to the business case and the evidence '
            'the team needs to measure the result.'
        ),
        'starting_point': (
            'Bring one example of a rising charge or a workload you want to investigate. '
            'Billing history, query history, and someone who knows what the workload '
            'supports can help us agree on the scope of the diagnostic.'
        ),
    },
}
