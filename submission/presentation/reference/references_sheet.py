"""
Generate a standalone References Sheet PDF to bring to CSEF.
Print this and keep it on the table next to the lab notebook.

Contains all 11 references used across the poster and the lab notebook,
including the 3 extras beyond the 8 on the poster ([9] Murdock,
[10] Soula, [11] Meta AI TRIBE V2) that came up during the April 8
TRIBE V2 integration work.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT = ROOT / "CSEF_presentation" / "reference" / "References_Sheet.pdf"

REFS = [
    ("[1]", "Iaccarino, H. F. et al. (2016). Gamma frequency entrainment attenuates amyloid load and modifies microglia. <i>Nature</i>, 540(7632), 230-235."),
    ("[2]", "Martorell, A. J. et al. (2019). Multi-sensory gamma stimulation ameliorates Alzheimer's-associated pathology and improves cognition. <i>Cell</i>, 177(2), 256-271."),
    ("[3]", "Tort, A. B. L. et al. (2010). Measuring phase-amplitude coupling between neuronal oscillations of different frequencies. <i>Journal of Neurophysiology</i>, 104(2), 1195-1210."),
    ("[4]", "Lawhern, V. J. et al. (2018). EEGNet: A compact convolutional neural network for EEG-based brain-computer interfaces. <i>Journal of Neural Engineering</i>, 15(5), 056013."),
    ("[5]", "Lahijanian, M. et al. (2024). Auditory gamma-band entrainment enhances default mode network connectivity in dementia patients. <i>Scientific Reports</i>, 14, 13153."),
    ("[6]", "Thompson, R. F. &amp; Spencer, W. A. (1966). Habituation: A model phenomenon for the study of neuronal substrates of behavior. <i>Psychological Review</i>, 73(1), 16-43."),
    ("[7]", "Chan, D. et al. (2025). Long-term safety and tolerability of gamma sensory stimulation for Alzheimer's disease. <i>Alzheimer's &amp; Dementia</i>, 21(10), e70792."),
    ("[8]", "Fortunato et al. (2023). Non-responder rates in auditory gamma entrainment studies. <i>Frontiers in Integrative Neuroscience</i>, 17."),
    ("[9]", "Murdock, M. H. et al. (2024). Multisensory gamma stimulation promotes glymphatic clearance of amyloid. <i>Nature</i>, 627, 149-156."),
    ("[10]", "Soula, M. et al. (2023). Forty-hertz light stimulation does not entrain native gamma oscillations in Alzheimer's disease model mice. <i>Nature Neuroscience</i>, 26, 570-578."),
    ("[11]", "Meta AI. (2026). TRIBE V2: A Predictive Foundation Model for Brain Encoding. HuggingFace model card: facebook/tribev2."),
    ("[12]", "Wilson, H. R. &amp; Cowan, J. D. (1972). Excitatory and inhibitory interactions in localized populations of model neurons. <i>Biophysical Journal</i>, 12(1), 1-24."),
]


def main():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=20,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        name="SubtitleStyle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=11,
        spaceAfter=14,
        alignment=TA_CENTER,
        textColor=HexColor("#555555"),
    )
    header_style = ParagraphStyle(
        name="HeaderStyle",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6,
        textColor=HexColor("#1a1a1a"),
    )
    ref_style = ParagraphStyle(
        name="RefStyle",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=11.5,
        leading=14.5,
        spaceAfter=5,
        leftIndent=24,
        firstLineIndent=-24,
    )
    ack_style = ParagraphStyle(
        name="AckStyle",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=11.5,
        leading=14.5,
        spaceAfter=0,
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
    )

    story = []

    story.append(Paragraph("References", title_style))
    story.append(Paragraph(
        "Personalized Deep Learning Model for Closed-Loop 40 Hz Entrainment to Optimize Theta-Gamma Coupling in Alzheimer's Disease",
        subtitle_style,
    ))
    story.append(Paragraph(
        "Amaar M. Chughtai &nbsp;&nbsp;|&nbsp;&nbsp; California Science &amp; Engineering Fair 2026",
        subtitle_style,
    ))

    for tag, ref in REFS:
        story.append(Paragraph(f"<b>{tag}</b> &nbsp; {ref}", ref_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Acknowledgements", header_style))
    story.append(Paragraph(
        "AP Statistics teacher consulted on statistical test selection (Wilcoxon signed-rank vs paired t-test). "
        "All other work conducted independently. Computing: personal MacBook + RTX 3080. "
        "No institutional lab or mentor. Dataset: OpenNeuro ds005048, open access license. "
        "All diagrams by the author. All experimental design, analysis, interpretation, and conclusions are the student's own work.",
        ack_style,
    ))

    doc.build(story)
    print(f"Generated: {OUTPUT}")


if __name__ == "__main__":
    main()
