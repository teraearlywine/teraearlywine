"""Generate the printable, ungated production-readiness worksheet."""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'core/home/assets/downloads/data-ai-production-readiness-scorecard.pdf'
C = canvas.Canvas(str(OUT), pagesize=(612, 792))
C.setTitle('Data & AI Production Readiness Scorecard')
C.setAuthor('Tera Earlywine Consulting')
navy = HexColor('#142c71'); orange = HexColor('#e05b2d'); ink = HexColor('#202735'); muted = HexColor('#536071')

def text(x, y, s, size=10, font='Helvetica', color=ink):
    C.setFillColor(color); C.setFont(font, size); C.drawString(x, y, s)

def wrap(s, x, y, width=510, size=10, leading=14, font='Helvetica', color=ink):
    for line in simpleSplit(s, font, size, width):
        text(x, y, line, size, font, color); y -= leading
    return y

def header(label, page):
    text(48, 752, 'TERA EARLYWINE CONSULTING', 9, 'Helvetica-Bold', navy)
    text(48, 733, label.upper(), 8, 'Helvetica-Bold', orange)
    C.setStrokeColor(navy); C.setLineWidth(1); C.line(48, 721, 564, 721)
    C.setStrokeColor(HexColor('#cbd1db')); C.line(48, 43, 564, 43)
    text(48, 27, 'teraearlywine.com  |  Data & AI Production Readiness Scorecard', 8, color=muted)
    text(552, 27, str(page), 8, color=muted)

def title(s, y=689):
    text(48, y, s, 22, 'Helvetica-Bold', navy)

def line(label, y):
    text(48, y, label, 10, 'Helvetica-Bold'); C.setStrokeColor(HexColor('#aab3c1')); C.line(180, y-2, 564, y-2)

def question(s, y):
    y = wrap(s, 48, y, width=510, size=10, leading=13, font='Helvetica-Bold')
    text(48, y-2, '[ ] Ready     [ ] Needs work     [ ] Unknown     [ ] Not applicable', 9, color=muted)
    return y-29

def section(name, questions, y):
    text(48, y, name.upper(), 11, 'Helvetica-Bold', orange); y -= 22
    for q in questions: y = question(q, y)
    return y-5

header('A practical worksheet', 1)
title('Is this workflow ready', 683); title('for production?', 655)
y=wrap('Use this scorecard to review one data or AI workflow before a release, a production review, or an operating handoff. The goal is to expose gaps and decide who will address them.', 48, 620, size=11, leading=16)
text(48, 557, 'START WITH ONE WORKFLOW', 11, 'Helvetica-Bold', orange)
line('Workflow or output', 532); line('Business owner', 503); line('Technical owner', 474); line('Review date / stage', 445)
text(48, 405, 'HOW TO USE IT', 11, 'Helvetica-Bold', orange)
y=wrap('1. Bring the business owner and the people who build and operate the workflow together.', 48, 381, size=10, leading=15)
y=wrap('2. Mark each statement Ready, Needs work, Unknown, or Not applicable. Note evidence, not just intent.', 48, y-8, size=10, leading=15)
y=wrap('3. Use the final page to assign an owner, next action, and review date for the most consequential gaps.', 48, y-8, size=10, leading=15)
y=wrap('A Ready answer means the control exists and has evidence appropriate to the workflow. Unknown is a prompt to investigate. Mark Not applicable only when the team can explain why.', 48, y-13, size=10, leading=15)
wrap('This is a discussion aid, not a certification, compliance determination, or guarantee of production readiness. The right controls depend on the workflow and its consequences.', 48, 169, size=9, leading=13, color=muted)
C.showPage()
header('Review the workflow', 2); title('The foundation')
y=section('01 / Consequence & ownership', [
'The purpose, users, and decisions that depend on this output are documented.',
'The business and technical owners are named, and release decisions have an accountable approver.',
'The team understands what happens if the output is wrong, late, unavailable, or misused.'], 650)
y=section('02 / Data & dependencies', [
'Sources, downstream consumers, and critical upstream dependencies are identified.',
'Quality and freshness requirements are agreed, with checks for missing, late, or incorrect data.',
'The team can trace a representative output back to its inputs and key transformations.'], y)
y=section('03 / Access & sensitive data', [
'Access is limited to authorized people and services, and permissions have an owner.',
'Sensitive data handling, retention, and sharing are defined for inputs, outputs, logs, and third-party services.',
'The workflow has a documented way to review and revoke access.'], y)
C.showPage()
header('Review the workflow', 3); title('Running it in the real world')
y=section('04 / Testing & evaluation', [
'Representative cases and known failure conditions have been tested against agreed acceptance criteria.',
'For AI outputs, evaluations cover relevant errors, harmful or unsupported outputs, and changes over time; otherwise mark not applicable.',
'A person with authority has reviewed the evidence and accepted unresolved risks.'], 650)
y=section('05 / Monitoring & recovery', [
'The team can detect consequential failures, quality issues, and unexpected behavior.',
'Alerts have an owner and a clear escalation path, including human review when needed.',
'A runbook describes how to pause, recover, roll back, and communicate during an incident; recovery has been exercised.'], y)
y=section('06 / Cost & operating responsibility', [
'The expected cost, capacity limits, and material cost drivers are understood and monitored.',
'An operating owner has time and authority to maintain the workflow, dependencies, and documentation.',
'There is a review cadence for incidents, changes, quality, access, and cost.'], y)
C.showPage()
header('Turn findings into action', 4); title('What happens next?')
y=wrap('Prioritize by consequence and uncertainty. A single unresolved issue can matter more than a long list of ready items; do not add up answers to make a release decision.', 48, 657, size=10, leading=15)
for idx,(name,desc) in enumerate([
('ADDRESS NOW','A consequential gap needs a decision or action before release or continued operation.'),
('INVESTIGATE','The team lacks evidence or needs to understand the impact before deciding.'),
('ACCEPT FOR THIS STAGE','The responsible owner understands the limitation, records the rationale, and sets a review date.')]):
    yy=594-idx*122
    text(48, yy, name, 10, 'Helvetica-Bold', orange)
    wrap(desc, 48, yy-17, size=9, leading=12)
    line('Gap / decision', yy-46); line('Owner / next action', yy-69); line('Due / review date', yy-92)
text(48, 191, 'NEED A SECOND SET OF EYES?', 11, 'Helvetica-Bold', navy)
wrap('Bring your questions to a 20-30 minute fit call. We can identify the most useful starting point for your workflow.', 48, 171, size=10, leading=14)
C.setFillColor(navy); C.roundRect(48, 91, 190, 35, 2, fill=1, stroke=0)
text(61, 104, 'DISCUSS YOUR WORKFLOW  >', 10, 'Helvetica-Bold', white)
C.linkURL('https://www.teraearlywine.com/#contact', (48,91,238,126), relative=0)
C.save()
print(OUT)
