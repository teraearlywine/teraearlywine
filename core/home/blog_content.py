"""Original essays and notes for Tera Earlywine's blog.

The collection discusses design principles and working practices in Tera's
first-person voice, without invented client anecdotes or outcome claims.
"""


def _article(identifier, slug, title, category, dek, sections):
    word_count = sum(
        len(paragraph.split())
        for section in sections
        for paragraph in section['paragraphs']
    )
    return {
        'id': identifier,
        'slug': slug,
        'title': title,
        'category': category,
        'dek': dek,
        'read_minutes': max(1, round(word_count / 200)),
        'sections': sections,
    }


def _section(title, *paragraphs):
    return {'title': title, 'paragraphs': list(paragraphs)}


ARTICLES = [
    _article(
        1, 'small-systems-clear-ownership', 'Small systems. Clear ownership.',
        'Systems', 'The best starting point is often a smaller system with a clearer promise.',
        [
            _section(
                'Make the promise small enough to keep',
                'When I think about a useful system, I start with its promise. What should someone be able to count on? A current number before a meeting. An exception arriving with the person who can resolve it. A task that is either finished or clearly waiting for a decision. The promise gives the design a boundary.',
                'A smaller boundary makes responsibility easier to describe. It also makes failure easier to notice. If I cannot explain what a system owns in a few sentences, I want to examine whether I have combined several jobs before understanding any one of them. Complexity sometimes belongs in the problem. It should still earn its place in the solution.',
            ),
            _section(
                'Ownership is part of the design',
                'I would give each important transition an owner: who can approve an input, who handles an exception, and who decides that the result is ready to use. A document saying that a team owns everything is less useful than a clear answer at the moment something needs attention.',
                'That answer needs an operating rhythm. Someone should be able to see what changed, what is unresolved, and what happens next without reconstructing the whole history. A short review with reliable evidence can be more valuable than a dashboard full of activity.',
            ),
            _section(
                'Grow from a working unit',
                'I would rather expand a system after its smallest useful version has demonstrated a complete cycle. That means following an input through a decision to an observable result, including the awkward cases. Once that path is understandable, adding another source or another workflow becomes a deliberate extension. The goal is a foundation that people can explain, trust, and improve together.',
            ),
        ],
    ),
    _article(
        2, 'the-work-after-the-demo', 'The work after the demo.',
        'AI & work', 'A compelling first result is the beginning of an operating model.',
        [
            _section(
                'A new set of questions',
                'A good demo makes a possibility tangible. I can see a workflow taking shape and imagine how it might help. The next step, though, changes the questions. What happens with incomplete information? Who notices when an external service stops responding? How does someone correct a result without starting again?',
                'These questions are design material. They reveal what the system must explain to its users and what the people operating it need to see. I want to answer them while the workflow is still small enough to change easily, before a polished interface makes uncertain behavior feel settled.',
            ),
            _section(
                'Define a complete attempt',
                'For an AI-assisted workflow, I would write down what counts as one attempt. It needs a beginning, an allowed set of actions, a stopping point, and a result that can be checked. If it stops halfway through, the next attempt should know what already happened. Repeating a request should not silently repeat an external action.',
                'I also want an explicit path for uncertainty. A system that asks for a decision at the right time can be much more useful than one that confidently fills every gap. The request should include the evidence, the unresolved issue, and the smallest choice needed to move forward.',
            ),
            _section(
                'Observe the outcome',
                'My final question is simple: how will I know that the intended result actually happened? A successful internal step might mean a draft was created. The useful outcome might require someone to receive it, review it, or act on it. I would keep those states distinct. That makes the workflow easier to operate and gives the next improvement a concrete place to begin. The work after the demo turns possibility into something someone can depend on.',
            ),
        ],
    ),
    _article(
        3, 'designing-for-the-long-run', 'Designing for the long run.',
        'Perspectives', 'Build for the person who will inherit the next decision.',
        [
            _section(
                'Leave a useful trail',
                'I think of a durable system as one that remains understandable after the original conversation is forgotten. The people who inherit it should be able to find its purpose, its boundaries, and the reason behind its important choices. That does not require recording every discussion. It requires keeping the decisions that change how the system should be used.',
                'A short decision record can do a surprising amount of work. I would include the problem, the chosen approach, the tradeoff, and the condition that would make me revisit it. The last part matters because a sensible decision can become an obstacle when its assumptions change.',
            ),
            _section(
                'Make change an ordinary operation',
                'Long-lived systems need room for revision. I would look for places where a business rule is hidden inside a technical workaround, where a person carries an undocumented exception, or where a small change requires understanding every component. Those are useful signals for where to create a clearer boundary.',
                'I would also make routine care visible. What needs review each week? Which dependencies can drift? How can someone tell that the information is becoming stale? Maintenance becomes easier to prioritize when it connects directly to the promise the system makes to the people using it.',
            ),
            _section(
                'Optimize for the next thoughtful change',
                'The long run is difficult to predict, so I would avoid designing every possible future at once. Instead, I would make the next change easier to evaluate and safer to reverse. Clear ownership, readable evidence, and small releases help with that. A durable design does not eliminate the need for judgment. It gives the next person enough context to exercise judgment well, even when the conditions are different from the ones I started with.',
            ),
        ],
    ),
    _article(
        4, 'a-dashboard-needs-a-decision', 'A dashboard needs a decision.',
        'Systems', 'Start with what someone needs to decide, then choose what to show.',
        [_section('Design backward from action',
            'Before I sketch a dashboard, I want to name the decision it supports. Is someone choosing where to investigate, whether to release a change, or which work to prioritize? Each question asks for different evidence. A large collection of available metrics can obscure that purpose.',
            'I would pair each important signal with its definition, its freshness, and the action it can inform. If the reader cannot tell what a number means or what changed, another chart is unlikely to help. A useful dashboard should shorten the path from observation to a considered decision.')],
    ),
    _article(
        5, 'the-shape-of-a-handoff', 'The shape of a handoff.',
        'Perspectives', 'Give the next person context, evidence, and a clear next move.',
        [_section('Transfer understanding',
            'I think a handoff is complete when the next person can act without reconstructing the previous person’s thought process. A status label helps, but it cannot carry the whole exchange. I would include what was requested, what has happened, and what still needs a decision.',
            'The most useful detail is often the boundary of uncertainty. If a check was skipped, I want to say so. If a result depends on an assumption, I want to make it visible. Good handoffs preserve momentum by making the next step understandable rather than merely assigning it.')],
    ),
    _article(
        6, 'an-agent-needs-an-edge', 'An agent needs an edge.',
        'AI & work', 'Useful autonomy begins with a boundary someone can understand.',
        [_section('Define where judgment returns',
            'When designing an agent workflow, I would start by drawing its boundary. What can it read? What can it change? Which decisions require a person? A broad instruction to help is a useful conversation starter, but an operating workflow needs more precise permissions.',
            'I also want a clear stopping condition. The agent should know when the intended outcome is achieved, when it needs input, and when another attempt would repeat the same failure. Those edges make autonomy easier to trust because the people using the system can anticipate how it will behave.')],
    ),
    _article(
        7, 'make-the-exception-visible', 'Make the exception visible.',
        'Systems', 'An unresolved item should have a place to wait and a path forward.',
        [_section('Give uncertainty somewhere to go',
            'I would design an exception path at the same time as the expected path. Missing information, conflicting values, and unavailable dependencies are ordinary parts of a workflow. If there is no place for them, they tend to become hidden work for the person maintaining the system.',
            'An exception should show why it is waiting, who can resolve it, and what evidence is available. I want the original input to remain accessible so the decision can be revisited. A visible queue turns uncertainty into manageable work and makes recurring problems easier to recognize over time.')],
    ),
    _article(
        8, 'a-smaller-first-release', 'A smaller first release.',
        'Perspectives', 'Choose one complete path that makes the next decision easier.',
        [_section('Keep the learning intact',
            'I would scope a first release around one complete user outcome. That may mean fewer inputs, a narrower audience, or a manual review at an important transition. The useful constraint is that the path still reaches something someone can use and evaluate.',
            'A small release should answer a question about the design. Can people understand the result? Does the handoff work? Is the difficult part actually difficult in practice? I want the next scope decision to come from those observations. That keeps a reduced first version meaningful while leaving room to change the larger plan.')],
    ),
    _article(
        9, 'data-with-a-definition', 'Data with a definition.',
        'Systems', 'A shared number needs a shared meaning.',
        [_section('Bring the definition along',
            'When two reports disagree, I would check their definitions before comparing their arithmetic. A date may represent when an event happened, when it arrived, or when someone approved it. Each can be valid and still answer a different question.',
            'I want important measures to travel with a plain-language explanation of what is included, what is excluded, and how timing works. A short example can make the boundary much easier to understand. Definitions are part of the product people use, especially when a number moves between teams with different responsibilities and expectations.')],
    ),
    _article(
        10, 'show-the-work-that-matters', 'Show the work that matters.',
        'AI & work', 'Evidence should help a person assess the result.',
        [_section('Make a result reviewable',
            'For an AI-assisted result, I want evidence that helps someone judge whether it is usable. That could mean the source material, the assumptions applied, and the checks performed. A long activity log can be available without becoming the main explanation.',
            'I would organize the review around the user’s decision. What changed? Why does the system believe the result is ready? What remains uncertain? This makes review a practical part of the workflow. The goal is to give the person enough context to accept, correct, or reject the result with confidence.')],
    ),
    _article(
        11, 'the-cost-of-a-hidden-rule', 'The cost of a hidden rule.',
        'Systems', 'A workaround deserves a name when people begin to depend on it.',
        [_section('Name the business choice',
            'A special case can begin as a reasonable shortcut and gradually become a business rule. I would look closely when someone says a value must always be changed by hand or that a particular record should be ignored. The explanation often matters more than the code that implements it.',
            'I want the rule to have a name, a reason, and an owner who can revisit it. That makes future changes easier to discuss. It also helps distinguish a lasting policy from a temporary accommodation whose original conditions may no longer apply.')],
    ),
    _article(
        12, 'a-note-to-my-future-self', 'A note to my future self.',
        'Perspectives', 'Capture the reason while the decision is still fresh.',
        [_section('Save the useful context',
            'When I finish a piece of work, I want to leave a small note for the next person who opens it. Often that person will be me. I would write what the change intended to accomplish, how I checked it, and the one thing that might be surprising later.',
            'This kind of note does not need to be exhaustive. Its value comes from preserving context that the finished artifact cannot express on its own. A few clear sentences written while the decision is fresh can make the next investigation much less expensive.')],
    ),
    _article(
        13, 'a-retry-is-a-design-choice', 'A retry is a design choice.',
        'AI & work', 'Before repeating an action, understand what the first attempt changed.',
        [_section('Give repetition a meaning',
            'When a request times out, I would avoid assuming that nothing happened. The receiving system might have completed the action before the response was lost. That possibility matters when the action sends a message, creates a record, or changes another person’s work.',
            'I want each attempt to carry a stable identity and leave evidence of its outcome where possible. The recovery path should check that evidence before repeating the action. A retry then becomes a deliberate way to finish incomplete work, with clear handling for the cases where the outcome remains uncertain.')],
    ),
    _article(
        14, 'freshness-is-part-of-quality', 'Freshness is part of quality.',
        'Systems', 'Correct information can still arrive too late to be useful.',
        [_section('Connect timing to use',
            'I would define freshness from the decision backward. A planning report might tolerate a day of delay. An operational queue may need a much shorter window. The same dataset can serve both, but the expectations should be visible to the people relying on it.',
            'A timestamp alone does not explain whether information is current enough. I want to distinguish when the source changed, when processing completed, and what period the result covers. When the expected window is missed, the interface should make that state clear so someone can choose how to proceed.')],
    ),
    _article(
        15, 'designing-a-calm-workflow', 'Designing a calm workflow.',
        'Perspectives', 'Reserve attention for the moments that need a person.',
        [_section('Make interruptions earn their place',
            'I would treat attention as a limited part of the system. Every notification asks someone to stop what they are doing and interpret a new signal. That interruption should come with a useful reason, especially when a workflow runs repeatedly throughout the day.',
            'A calm workflow can keep routine progress available while surfacing meaningful changes. I want a notification to explain what happened, why it matters now, and whether action is needed. Combining related information and avoiding repeated alerts for an unchanged condition makes it easier to notice the moments that deserve judgment.')],
    ),
    _article(
        16, 'the-human-review-step', 'The human review step.',
        'AI & work', 'Give reviewers a decision they can actually make.',
        [_section('Design the review itself',
            'A review step needs more design than an approve button. I would first name the decision the reviewer is responsible for and the evidence they need. The person should know whether they are checking accuracy, exercising judgment, or authorizing an external action.',
            'I also want a useful way to send work back. A correction should preserve the reviewer’s explanation and give the workflow a clear next step. When review is vague, it can become a ritual. When the decision is concrete, it becomes a meaningful part of how the system earns trust.')],
    ),
    _article(
        17, 'migration-as-a-sequence', 'Migration as a sequence.',
        'Systems', 'Make each transition understandable before widening the change.',
        [_section('Create checkpoints that mean something',
            'I would break a migration into transitions with clear entry and exit conditions. A useful checkpoint answers whether the new path can serve a defined need, how its results compare, and what would trigger a return to the previous path.',
            'That structure makes progress easier to assess than a single percentage complete. Moving code, moving data, validating behavior, and changing who depends on the result are different kinds of work. I want each to have visible evidence. The sequence can then expand deliberately as confidence grows in the parts already moved.')],
    ),
    _article(
        18, 'leave-room-for-a-question', 'Leave room for a question.',
        'Perspectives', 'A thoughtful pause can improve the shape of the work.',
        [_section('Use questions to reduce uncertainty',
            'I value a question that changes the work in a useful way. Before building, I would ask what outcome matters and what would make the result unusable. During the work, I would revisit assumptions when new evidence makes the original answer less certain.',
            'The timing matters. Some questions can wait until there is something concrete to react to. Others determine whether the next action is appropriate at all. I want to make that distinction explicit so a conversation can preserve momentum while giving consequential decisions the attention they need.')],
    ),
    _article(
        19, 'a-source-is-a-relationship', 'A source is a relationship.',
        'Systems', 'Understand who creates the information and what they need it to mean.',
        [_section('Look beyond the connection',
            'Connecting to a source is only one part of understanding it. I would also ask who creates the records, what events cause them to change, and which corrections can happen later. Those details explain behavior that a schema alone cannot show.',
            'The relationship needs a way to communicate change. If a definition shifts or a field becomes optional, someone downstream should know before a report quietly changes meaning. I want source ownership and expectations to be visible alongside the technical connection. That gives maintenance a human path as well as a technical one.')],
    ),
    _article(
        20, 'useful-automation-has-a-receipt', 'Useful automation has a receipt.',
        'AI & work', 'Record the outcome in the place where it can be verified.',
        [_section('Follow the action to its destination',
            'When a workflow performs an action elsewhere, I want a receipt from the destination when one is available. An internal success message can tell me the request was sent. A record identifier or a readback can help establish what actually exists after the action.',
            'I would connect that evidence to the original request so another person can follow the result without searching through logs. If confirmation is unavailable, the workflow should say what is known and what remains uncertain. The receipt makes follow-up practical and gives recovery a more reliable starting point.')],
    ),
    _article(
        21, 'the-value-of-a-quiet-default', 'The value of a quiet default.',
        'Perspectives', 'Let the main task remain the most obvious thing on the page.',
        [_section('Choose the first experience carefully',
            'Defaults shape how a tool feels before anyone changes a setting. I would begin with the information and controls needed for the most common task, then make deeper detail easy to reach. This asks the design to have a point of view about what deserves attention first.',
            'A quiet default should still make important state visible. An unresolved decision, stale input, or failed action needs a clear place. I want the interface to feel composed because its priorities are understandable, with enough room for someone to explore when they need more context.')],
    ),
    _article(
        22, 'testing-the-uncomfortable-path', 'Testing the uncomfortable path.',
        'Systems', 'Practice the moments that are hardest to improvise.',
        [_section('Follow the failure through',
            'I would choose tests based on what could make the workflow hard to recover. A missing response, a partial write, or an expired credential can reveal more about the operating design than another example of the expected path. The useful question is what the person running the system will see next.',
            'I want to check that the failure is visible, the earlier work remains understandable, and recovery does not repeat an action unexpectedly. Testing these paths also improves documentation because it replaces an imagined recovery procedure with a sequence someone has actually exercised.')],
    ),
    _article(
        23, 'context-is-a-working-material', 'Context is a working material.',
        'AI & work', 'Select the information that helps with the current decision.',
        [_section('Curate what the workflow needs',
            'When giving an AI workflow context, I would start with the task and the decision it needs to make. More information can introduce contradictions or make an old assumption look current. The useful context explains the objective, relevant evidence, and boundaries for action.',
            'I also want to distinguish a fact from a suggestion and a current instruction from historical background. Clear labels make the input easier to interpret and easier for a person to review. Treating context as maintained working material helps the workflow adapt when the project’s direction changes.')],
    ),
    _article(
        24, 'build-a-place-to-return', 'Build a place to return.',
        'Perspectives', 'A good workspace helps people resume with less reconstruction.',
        [_section('Support the next session',
            'I would design a project workspace around returning to the work. The opening view should help someone see the current objective, the latest meaningful result, and the next decision. A chronological stream can remain available, but the current state needs its own clear expression.',
            'This matters when work spans several short sessions or moves between people. I want the workspace to preserve the thread of the effort without requiring everyone to remember it. A small amount of deliberate organization can make the next session feel like a continuation instead of another investigation.')],
    ),
    _article(
        25, 'measure-the-whole-path', 'Measure the whole path.',
        'Systems', 'A fast component can still belong to a slow experience.',
        [_section('Include the waiting',
            'When evaluating a workflow, I would measure the time from the initial need to the usable outcome. Processing speed is one part of that path. Waiting for an input, clarifying an exception, and handing the result to another person may account for much more of the experience.',
            'I want to see where work waits and why. That can change the improvement plan from optimizing a fast step to simplifying a confusing transition. Measuring the whole path keeps the focus on what someone experiences and helps the team choose a change with a meaningful effect.')],
    ),
    _article(
        26, 'a-useful-stopping-point', 'A useful stopping point.',
        'AI & work', 'Completion needs a definition the workflow can recognize.',
        [_section('Describe what done looks like',
            'Before starting an automated task, I would define the observable condition that means it is complete. A finished draft, a verified update, and a delivered message are different outcomes. The stopping point should match the request so the workflow can report its result accurately.',
            'I would also define how the task stops when it cannot continue. It should preserve useful progress, explain the obstacle, and identify the smallest input needed next. Clear stopping points make a system easier to operate because activity no longer has to stand in for evidence of completion.')],
    ),
    _article(
        27, 'one-more-point-of-view', 'One more point of view.',
        'Perspectives', 'A collection grows through the connections between its ideas.',
        [_section('Leave the collection open',
            'I like the idea of a collection that changes shape as new thoughts arrive. Each note can stand on its own while giving the surrounding ideas another connection. A question about ownership may lead to a thought about interfaces, which may lead back to how a workflow earns trust.',
            'I would leave room for those connections to develop without deciding the entire structure in advance. The important part is making each contribution clear enough to explore. Over time, the collection can reveal patterns that were difficult to see from any single starting point.')],
    ),
]

ARTICLES_BY_SLUG = {article['slug']: article for article in ARTICLES}
