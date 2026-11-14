"""Rebuild the two newsletter PDFs with ReportLab and the site's bundled fonts."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

ASSETS = Path(__file__).resolve().parents[1] / "core/home/assets"
OUT = ASSETS / "downloads"
INK = colors.HexColor("#131625")
BLUE = colors.HexColor("#263CF2")
ORANGE = colors.HexColor("#FF6B3D")
MUTED = colors.HexColor("#495161")
RULE = colors.HexColor("#B9C1D0")
WASH = colors.HexColor("#F3F5FA")
REGULAR = "Inter"
BOLD = "Inter Bold"
LEFT, RIGHT = 46, 566
TEAMS = "Choose Your Next AI Workflow"
PROFESSIONALS = "From Technical Work to Business Impact"


class Guide:
    def __init__(self, slug, title, audience):
        self.title = title
        self.audience = audience
        self.pdf = Canvas(str(OUT / f"{slug}.pdf"), pagesize=letter,
                          invariant=1, pageCompression=1, lang="en-US")
        self.pdf.setAuthor("Tera Earlywine")
        self.pdf.setTitle(title)
        self.pdf.setSubject(f"The Business of Technology | {audience}")
        self.pdf.setCreator("Tera Earlywine")
        self.pdf.showOutline()

    def text(self, x, y, words, size=11, font=REGULAR, color=INK):
        self.pdf.setFont(font, size)
        self.pdf.setFillColor(color)
        self.pdf.drawString(x, y, words)

    def paragraph(self, words, x, y, width, size=11.5, leading=17, font=REGULAR, color=INK):
        for line in simpleSplit(words, font, size, width):
            self.text(x, y, line, size, font, color)
            y -= leading
        return y

    def rule(self, x1, y, x2, color=RULE):
        self.pdf.setStrokeColor(color)
        self.pdf.setLineWidth(0.7)
        self.pdf.line(x1, y, x2, y)

    def link(self, x, y, title, url, size=9):
        self.text(x, y, title, size, BOLD, BLUE)
        width = pdfmetrics.stringWidth(title, BOLD, size)
        self.rule(x, y - 2.5, x + width, BLUE)
        self.pdf.linkURL(url, (x, y - 4, x + width, y + size + 3), relative=0)

    def page(self, page_number, section, title_lines, intro):
        self.pdf.bookmarkPage(f"page-{page_number}")
        self.pdf.addOutlineEntry(section, f"page-{page_number}", level=0)
        self.text(LEFT, 750, "Tera Earlywine", 16, BOLD)
        self.pdf.setFillColor(BLUE)
        self.pdf.rect(LEFT, 733, 28, 3.5, stroke=0, fill=1)
        self.pdf.setFillColor(ORANGE)
        self.pdf.rect(LEFT + 28, 733, 5, 3.5, stroke=0, fill=1)
        self.text(360, 752, "THE BUSINESS OF TECHNOLOGY", 9, BOLD, BLUE)
        self.rule(LEFT, 721, RIGHT)
        self.text(LEFT, 698, f"{self.audience.upper()}   /   {section.upper()}", 8.6, BOLD, BLUE)
        y = 650
        for line in title_lines:
            self.text(LEFT, y, line, 36, BOLD)
            y -= 40
        y = self.paragraph(intro, LEFT, y + 7, RIGHT - LEFT - 5, size=12, leading=18)
        self.rule(LEFT, 44, RIGHT)
        self.text(LEFT, 27, self.title, 8.3, REGULAR, MUTED)
        self.pdf.setFont(BOLD, 8.3)
        self.pdf.drawRightString(RIGHT, 27, f"{page_number} / 3")
        return y - 18

    def heading(self, words, y):
        self.text(LEFT, y, words, 16, BOLD)
        return y - 23

    def row(self, label, body, y, label_width=125):
        self.rule(LEFT, y + 10, RIGHT)
        label_end = self.paragraph(label, LEFT, y - 7, label_width - 10, 11.1, 15, BOLD)
        body_end = self.paragraph(body, LEFT + label_width, y - 7,
                                  RIGHT - LEFT - label_width - 3, 11.1, 15)
        return min(label_end, body_end) - 13

    def callout(self, title, body, y):
        lines = simpleSplit(body, REGULAR, 11.2, RIGHT - LEFT - 35)
        height = 39 + len(lines) * 15.5
        self.pdf.setFillColor(WASH)
        self.pdf.rect(LEFT, y - height, RIGHT - LEFT, height, stroke=0, fill=1)
        self.text(LEFT + 15, y - 20, title, 11.5, BOLD, BLUE)
        self.paragraph(body, LEFT + 15, y - 39, RIGHT - LEFT - 35, 11.2, 15.5)
        return y - height - 24

    def field(self, name, label, prompt, top, height=35, max_length=240):
        self.text(LEFT, top, label, 11, BOLD)
        self.text(LEFT, top - 14, prompt, 9.5, REGULAR, MUTED)
        bottom = top - 20 - height
        self.pdf.acroForm.textfield(
            name=name, tooltip=f"{label}. {prompt}", x=LEFT, y=bottom,
            width=RIGHT - LEFT, height=height, fontName="Helvetica", fontSize=10,
            textColor=INK, borderColor=RULE, fillColor=colors.white, borderWidth=0.7,
            forceBorder=True, fieldFlags="multiline", maxlen=max_length,
        )
        return bottom - 18

    def next_page(self):
        self.pdf.showPage()

    def save(self):
        self.pdf.save()


def make_teams():
    g = Guide("choose-your-next-ai-workflow", TEAMS, "For teams")
    y = g.page(1, "Choose a candidate", ["Choose Your Next", "AI Workflow"],
               "Bring the person who does the work and one recent example. By the end, "
               "you should have one task to test, a way to judge the result, and someone "
               "who can stop the trial.")
    y = g.heading("Follow one piece of work.", y)
    y = g.paragraph("Pick a recent ticket, invoice, or report. Ask its owner to show you "
                    "what arrived, what they looked up, what they produced, and who checked it. "
                    "Count the minutes spent on exceptions and corrections, too.",
                    LEFT, y, RIGHT - LEFT) - 16
    y = g.heading("Which of these deserves a trial?", y)
    y = g.paragraph("Illustrative choices for a customer operations team", LEFT, y,
                    RIGHT - LEFT, 10, 15, REGULAR, MUTED) - 10
    y = g.row("Route a ticket", "The selected form category already specifies the owner. "
              "Try a routing rule first. Check how often tickets land in the wrong queue.", y)
    y = g.row("Draft a reply", "Requests arrive in free text and the policy is available "
              "to the agent. Test a draft with a link to its source. The agent checks and sends it.", y)
    y = g.row("Release a refund", "Money moves and mistaken refunds are difficult to recover. "
              "Keep the approval with its owner. Try summarizing the request for that person.", y)
    g.callout("Take one candidate forward.", "Can someone inspect the input and correct a "
              "bad output before it affects a customer? If you cannot name the reviewer or "
              "obtain representative examples, resolve that before starting the trial.", y)
    g.next_page()

    y = g.page(2, "Worked example", ["Price the whole task."],
               "Illustrative pilot for a support team. All figures are assumptions to test. "
               "The proposed tool drafts replies. A support agent remains responsible for every send.")
    y = g.heading("Start with one ordinary week.", y)
    y = g.row("Current work", "100 eligible tickets × 8 minutes each = 800 minutes.", y)
    y = g.row("Proposed work", "100 tickets × 4 minutes to review, correct, and send = "
              "400 minutes. Count full rewrites and any follow-up in this average.", y)
    y = g.row("Potential value", "400 minutes released ÷ 60 × $36 per staff hour = $240 "
              "in weekly capacity. Subtract $25 per week for the tool and upkeep.", y)
    y = g.row("Setup cost", "$860 of one-time setup ÷ $215 in weekly net value = 4 weeks "
              "to recover setup, if the team can use all the released time.", y)
    y = g.callout("What could change the answer?", "At 6 minutes of review per ticket, "
                  "weekly capacity is worth $120. After $25 in costs, $95 remains. Setup "
                  "takes just over 9 weeks to recover. Cash savings depend on a real change in spending.", y)
    y = g.heading("Agree on a test before writing the first draft.", y)
    y = g.paragraph("Have the support lead run 100 eligible historical requests, including "
                    "exceptions, through a draft-only trial using the approved inputs. Time the "
                    "full review. For this trial, aim for 4 minutes or less on average and "
                    "zero drafts that disclose another customer’s data or invent policy.",
                    LEFT, y, RIGHT - LEFT) - 8
    g.paragraph("Stop and investigate any critical error. If the gates hold, the lead can "
                "authorize a small live trial with human review and check time and error rates again.",
                LEFT, y, RIGHT - LEFT)
    g.next_page()

    y = g.page(3, "Pilot worksheet", ["Plan one small trial."],
               "Type in the boxes or print this sheet. Fill it out with the person who will "
               "review the output. Save a copy before you run the test.")
    y = g.field("workflow", "What will the tool do?", "Name the trigger, one input, the output, and the person who uses it.", y)
    y = g.field("alternative", "Which simpler option could also work?", "Describe the current process or a rule you can compare against.", y)
    y = g.field("baseline", "How much work happens today?", "Write the weekly volume, minutes per item, and the source of both figures.", y)
    y = g.field("economics", "What would the trial have to earn?", "Include review time, recurring costs, setup effort, and where released capacity would go.", y)
    y = g.field("guardrail", "What mistake would stop the trial?", "Name a failure, the person who can catch it, and how they will pause or reverse the work.", y)
    y = g.field("decision", "Who decides what happens next?", "Name the owner, sample, success threshold, review date, and next action.", y)
    g.link(LEFT, 65, "Explore consulting for teams at teraearlywine.com/for-teams/",
           "https://www.teraearlywine.com/for-teams/")
    g.save()


def make_professionals():
    g = Guide("from-technical-work-to-business-impact", PROFESSIONALS, "For technical professionals")
    y = g.page(1, "Find the decision", ["From Technical Work", "to Business Impact"],
               "Take one change you want someone to fund, adopt, or prioritize. By the end, "
               "you’ll have a three-sentence recommendation a colleague can act on and a "
               "measure you can check together.")
    y = g.heading("Who will do what differently?", y)
    y = g.paragraph("A query going from twelve minutes to two is a technical result. "
                    "Its business value depends on who was waiting and what they could do "
                    "once the result arrived. Ask the person at the other end of the work.",
                    LEFT, y, RIGHT - LEFT) - 18
    y = g.row("Find the moment", "“Walk me through the last time the report was late. "
              "Who was waiting? What choice did they make in the meantime?”", y)
    y = g.row("Trace the change", "Connect a technical change to an observable action. "
              "For example, moving a refresh earlier gives inventory planners time to "
              "review exceptions before a supplier’s order cutoff.", y)
    y = g.row("Test the link", "Would that earlier refresh include the latest transactions? "
              "Could someone act on it? A faster result from incomplete data can create more work.", y)
    g.callout("Try this before the meeting.", "Ask the person who owns the decision to finish "
              "the sentence “If I had this by ___, I could ___.” Their answer gives you the time, "
              "user, and action to put in your recommendation.", y)
    g.next_page()

    y = g.page(2, "Worked example", ["Make a case for a test."],
               "Illustrative inventory team. The engineering request reads “Move the "
               "refresh earlier.” The planning lead needs to know whether that would "
               "help staff release orders before the morning cutoff.")
    y = g.row("Observed baseline", "The report was ready by 8:45 a.m. on 14 of 20 workdays. "
              "On the six late mornings, two planners each spent 20 minutes gathering figures "
              "by hand. That is 6 × 2 × 20 minutes = 4 staff hours.", y)
    y = g.row("Options and cost", "Keep the current schedule and manual fallback, or test "
              "one earlier refresh. Estimate one engineer-day to set up the trial and $45 "
              "of additional compute per 20 workdays. Record actual spend.", y)
    y = g.row("What to measure", "Count mornings the complete report arrives by 8:45, "
              "reconcile its totals against the existing report, and have planners log "
              "manual minutes. Use the same 20-workday window for both options.", y)
    y = g.heading("The note I’d bring to the planning lead", y - 1)
    y = g.paragraph("Our two planners need complete inventory totals by 8:45 to release "
                    "morning orders, and they logged four hours of manual checks over the last "
                    "20 workdays. I recommend one engineer-day and an estimated $45 in extra "
                    "compute to test an earlier refresh alongside the current report for 20 "
                    "workdays. At the review, I’d keep the change if both reports reconcile "
                    "on all 20 days, the earlier one is ready on at least 19 mornings, and "
                    "manual checks fall to one staff hour or less.", LEFT, y, RIGHT - LEFT, 12, 18) - 7
    g.callout("Give the reader a real choice.", "The four hours are an observed baseline in "
              "this example. Three hours recovered is the target. Ask the planning lead whether "
              "that time is worth the cost and what work those hours would make possible.", y)
    g.next_page()

    y = g.page(3, "Decision worksheet", ["Write your own note."],
               "Type in the boxes or print this page. Choose one reader with authority "
               "to make the decision. Ask them to check the assumptions in the finished note.")
    y = g.field("reader", "Who needs to decide, and by when?", "Name the person, the decision, and the event or deadline that makes it matter.", y)
    y = g.field("evidence", "What happened last time?", "Record the baseline, units, time window, and source. Mark anything you still need to estimate.", y)
    y = g.field("option", "What change are you proposing?", "Include the alternative, setup cost, running cost, and who would own the change.", y)
    y = g.field("measure", "What result would justify keeping it?", "Choose a business measure, quality check, review date, and action if the trial falls short.", y)
    y = g.field("note", "Your three-sentence recommendation", "We need to decide ___. I recommend ___ because ___. We’ll know it helped when ___.", y, height=75, max_length=600)
    g.link(LEFT, y, "Try the interactive net-sales example at teraearlywine.com/#sample",
           "https://www.teraearlywine.com/#sample")
    g.save()


if __name__ == "__main__":
    pdfmetrics.registerFont(TTFont(REGULAR, str(ASSETS / "fonts/inter-regular.ttf")))
    pdfmetrics.registerFont(TTFont(BOLD, str(ASSETS / "fonts/inter-bold.ttf")))
    make_teams()
    make_professionals()
