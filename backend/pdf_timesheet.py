"""
PDFTimesheet Class for creating a PDF timesheet report.
"""
from datetime import datetime
from dataclasses import dataclass

from reportlab import platypus
from reportlab.pdfgen import canvas, textobject
from reportlab.lib import colors, pagesizes, units
from reportlab.pdfbase import pdfmetrics

import constants
from db.db_data import Employee, Shift


PAGE_WIDTH, PAGE_HEIGHT = pagesizes.A4
FONT = "Helvetica"
DEFAULT_FILENAME = "timesheet.pdf"


@dataclass
class PDFText:
    """
    Wrapper for ReportLab's PDF text object that holds extra details.

    :param content: The text content.
    :param x: The initial x-coordinate for the text.
    :param y: The initial y-coordinate for the text.
    :param font_size: The font size.
    :param pdf_obj: ReportLab's PDF text object.
    """
    content: str
    x: int
    y: int
    font_size: int
    pdf_obj: textobject.PDFTextObject


@dataclass
class PDFBorderedText:
    """
    Represents a text object with a surrounding border.

    :param text: The PDF text object.
    :param x: The x-coordinate for the border.
    :param y: The y-coordinate for the border.
    :param width: The width of the border.
    :param height: The height of the border.
    """
    text: PDFText
    x: int
    y: int
    width: int
    height: int


@dataclass
class PDFTimesheetTable:
    """
    Represents a (weekly) timesheet table.

    :param week_ending: The ending date of the week.
    :param rows: The rows of the table.
    """
    week_ending: datetime.date
    rows: list[str]


class PDFTimesheet:
    """
    Creates a PDF timesheet report for a list of employees.
    """

    def __init__(
        self,
        employees: list[Employee],
        filename: str = DEFAULT_FILENAME
    ) -> None:
        """
        Creates the PDF.

        :param employees: The employees to include in the PDF.
        :param filename: The name of the PDF.
        :raises ValueError: If any employee has fewer than constants.PAY_PERIOD shifts.
        """
        self._pdf = canvas.Canvas(filename, pagesize=pagesizes.A4)
        self._pdf.setStrokeColorRGB(0, 0, 0)
        self._y = PAGE_HEIGHT - units.inch

        self._draw_header()
        self._y -= (2 * units.cm)
        self._draw_employees(employees)


    def _create_pdf_text(
        self,
        content: str,
        x: int,
        y: int,
        font: str = FONT,
        font_size: int = 12,
    ) -> PDFText:
        """
        Creates a PDFText object.
        """
        pdf_obj = self._pdf.beginText(x, y)
        pdf_obj.setFont(font, font_size)
        pdf_obj.textLine(content)

        return PDFText(
            content=content,
            x=x,
            y=y,
            font_size=font_size,
            pdf_obj=pdf_obj
        )


    def _draw_text(self, text: PDFText) -> None:
        """
        Draws text on the current page.
        """
        self._pdf.drawText(text.pdf_obj)


    def _get_x_for_centered_text(self, text: str, font_size: int) -> int:
        """
        Calculates the x-coordinate that would center the text in the PDF.
        """
        text_width = pdfmetrics.stringWidth(text, FONT, font_size)
        x = (PAGE_WIDTH - text_width) / 2.0

        return x


    def _add_page_number(self):
        """
        Adds the current page number to the PDF.
        """
        page_num = str(self._pdf.getPageNumber())

        pdf_text = self._create_pdf_text(
            content=page_num,
            x=self._get_x_for_centered_text(page_num, font_size=12),
            y=units.inch * 0.5
        )

        self._draw_text(pdf_text)


    def _create_bordered_text(
        self,
        text: PDFText,
        padding_horizontal: int,
        padding_vertical: int
    ) -> PDFBorderedText:
        """
        Creates a bordered text object.
        """
        text_width = pdfmetrics.stringWidth(text.content, FONT, text.font_size)

        border_width = text_width + (padding_horizontal * 2)
        border_height = (text.y - text.pdf_obj.getY()) + (padding_vertical * 2)

        border_x = text.pdf_obj.getX() - padding_horizontal
        # y is not perfectly centered... TODO: ?
        border_y = text.y - padding_vertical  - (padding_vertical / 2.0)

        return PDFBorderedText(
            text=text,
            x=border_x,
            y=border_y,
            width=border_width,
            height=border_height
        )


    def _draw_bordered_text(self, bordered_text: PDFBorderedText) -> None:
        """
        Draws a bordered text object (includes text and border) on the current page.
        """
        self._pdf.setStrokeAlpha(1)
        self._pdf.setLineWidth(1)

        self._draw_text(bordered_text.text)

        self._pdf.setStrokeAlpha(0.5)
        self._pdf.setLineWidth(0.1)

        self._pdf.rect(
            bordered_text.x,
            bordered_text.y,
            bordered_text.width,
            bordered_text.height
        )


    def _sink_border(self, border: PDFBorderedText) -> None:
        """
        Sinks the border to create a shadow effect.
        """
        self._pdf.setStrokeAlpha(1)
        self._pdf.setLineWidth(1)

        self._pdf.line(
            border.x,
            border.y,
            border.x,
            border.y + border.height
        )

        self._pdf.line(
            border.x,
            border.y + border.height,
            border.x + border.width,
            border.y + border.height
        )


    def _raise_border(self, border: PDFBorderedText) -> None:
        """
        Raises the border to create a highlighted effect.
        """
        self._pdf.setStrokeAlpha(1)
        self._pdf.setLineWidth(1)

        self._pdf.line(
            border.x,
            border.y,
            border.x + border.width,
            border.y
        )
        self._pdf.line(
            border.x + border.width,
            border.y,
            border.x + border.width,
            border.y + border.height
        )


    def _create_header_title_box(self) -> PDFBorderedText:
        """
        Creates the 'company name' box in the header:
            +----------------------------+
            |        COMPANY NAME        |
            +----------------------------+
        """
        text = constants.COMPANY_NAME
        font_size = 14
        x = self._get_x_for_centered_text(text, font_size)

        pdf_text = self._create_pdf_text(
            content=text,
            font_size=font_size,
            x=x,
            y=self._y
        )

        return self._create_bordered_text(pdf_text, 20, 12)


    def _create_header_subtitle_box(self) -> PDFBorderedText:
        """
        Creates the 'crew timesheet' box in the header:
            +--------------------+
            |   CREW TIMESHEET   |
            +--------------------+
        """
        text = "CREW TIMESHEET"
        font_size = 12
        x = self._get_x_for_centered_text(text, font_size)

        timesheet_text = self._create_pdf_text(
            content=text,
            font_size=font_size,
            x=x,
            y=self._y
        )

        return self._create_bordered_text(timesheet_text, 10, 6)


    def _draw_header(self) -> None:
        """
        Draws the header on the PDF. This should appear only on the first page.
        """
        title = self._create_header_title_box()

        self._y = title.y - (units.cm * 1.05)

        subtitle = self._create_header_subtitle_box()

        self._draw_bordered_text(title)
        self._draw_bordered_text(subtitle)

        self._sink_border(title)
        self._raise_border(subtitle)

        self._y = subtitle.y


    def _draw_labelled_text(
        self,
        label: str,
        text: str,
        font: str = FONT,
        font_size: int = 12,
        bold: bool = False
    ) -> None:
        """
        Draws a labelled text pair, for example:
            Employee            John Smith
        """
        pdf_label = self._create_pdf_text(
            content=label,
            x=units.inch,
            y=self._y,
            font=font if not bold else f"{font}-Bold",
            font_size=font_size
        )

        pdf_text = self._create_pdf_text(
            content=text,
            x=pdf_label.pdf_obj.getX() + (units.inch * 1.95),
            y=self._y,
            font=font,
            font_size=font_size
        )

        self._draw_text(pdf_label)
        self._draw_text(pdf_text)


    def _draw_employees(self, employees: list[Employee]):
        """
        Draws each employee's timesheet in the order they appear in the list.
        There will be one employee per page.
        """
        for employee in employees:
            self._draw_employee(employee)

            self._add_page_number()
            self._pdf.showPage() # Move to next page
            
            self._y = PAGE_HEIGHT - units.inch


    def _draw_employee(self, employee: Employee) -> None:
        """
        Draws an employee's details and timesheet tables on the current page.
        """
        if len(employee.shifts) != constants.PAY_PERIOD_DAYS:
            raise ValueError(
                f"expected {constants.PAY_PERIOD_DAYS} shifts but " \
                f"got {len(employee.shifts)}"
            )

        self._draw_labelled_text("Employee", f"{employee.first_name} {employee.last_name}")

        self._y -= units.cm

        self._draw_labelled_text("Job Title", employee.position)

        self._y -= units.cm

        self._draw_labelled_text("Contract", employee.contract)

        self._y -= units.cm

        self._draw_timesheet(employee.shifts[0:7])

        self._y -= units.cm

        self._draw_timesheet(employee.shifts[7:14])


    def _create_pdf_timesheet_table(self, shifts: list[Shift]) -> PDFTimesheetTable:
        """
        Creates a PDFTimesheetTable from a list of shifts.
        """
        week_ending = shifts[-1].date.strftime(constants.DATE_FORMAT)

        rows = []

        rows.append(["Day", "Date", "Time", "", "Hours"])
        rows.append(["", "", "In", "Out", "Reg.", "OT"])

        total_hours_reg = 0
        total_hours_ot = 0

        def shift_to_row(shift: Shift) -> list[str]:
            day = shift.date.strftime('%A')[:3]
            date = shift.date.strftime(constants.DATE_FORMAT)
            time_in = shift.time_in.strftime("%I:%M %p") if shift.time_in else "--"
            time_out = shift.time_out.strftime("%I:%M %p") if shift.time_out else "--"
            hours_reg = shift.hours_reg
            hours_ot = shift.hours_ot

            return [day, date, time_in, time_out, hours_reg, hours_ot]

        for shift in shifts:
            rows.append(shift_to_row(shift))

            total_hours_reg += float(shift.hours_reg)
            total_hours_ot += float(shift.hours_ot)

        totals_row = ["", "", "", "Total:", "{:.2f}".format(total_hours_reg), "{:.2f}".format(total_hours_ot)]

        rows.append(totals_row)

        return PDFTimesheetTable(week_ending, rows)


    def _draw_timesheet(self, shifts: list[Shift]) -> None:
        """
        Draws an employee's timesheet on the current page.
        """
        pdf_table = self._create_pdf_timesheet_table(shifts)

        self._draw_labelled_text("Week Ending", pdf_table.week_ending, bold=True)

        self._y -= units.cm

        table = platypus.Table(pdf_table.rows)

        table.setStyle([
            ('SPAN', (2, 0), (3, 0)),		# "Time" spans two columns
            ('SPAN', (4, 0), (5, 0)),		# "Hours" spans two columns
            ('GRID', (0, 0), (-1, 0), 1, colors.black),
            ('GRID', (2, 1), (-1, 1), 1, colors.black),
            ('GRID', (3, 9), (-1, -1), 1, colors.black),
            ('GRID', (0, 2), (-1, -2), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (1, 1), 24),
            ('RIGHTPADDING', (0, 0), (1, 1), 24),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (2, 2), (-1, -1), 12),
            ('RIGHTPADDING', (2, 2), (-1,- 1), 12),
            ('BOX', (0, 1), (1, 2), 1, colors.black),
        ])

        _, table_height = table.wrapOn(self._pdf, 0, 0)
        table.drawOn(self._pdf, units.inch * 1.5, self._y - table_height)

        self._y -= table_height


    def get_pdf(self) -> canvas.Canvas:
        """
        Get the PDF.
        """
        return self._pdf
