"""
PDFTimesheet Class for creating a PDF timesheet report.
"""
from datetime import datetime
from dataclasses import dataclass

from reportlab import platypus
from reportlab.pdfgen import canvas
from reportlab.lib import colors, pagesizes, units
from reportlab.pdfbase import pdfmetrics

import constants
from db.db_data import Employee, Shift


PAGE_WIDTH, PAGE_HEIGHT = pagesizes.A4
FONT = "Helvetica"
DEFAULT_FILENAME = "timesheet.pdf"


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
        self._y -= (1.5 * units.cm)
        self._draw_employees(employees)


    def _draw_text(
        self,
        text: str,
        x: int,
        y: int,
        font: str = FONT,
        font_size: int = 12,
    ) -> None:
        """
        Draws text on the current page.
        """
        text_obj = self._pdf.beginText(x, y)
        text_obj.setFont(font, font_size)
        text_obj.textLine(text)

        self._pdf.drawText(text_obj)


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

        self._draw_text(
            text=page_num,
            x=self._get_x_for_centered_text(page_num, font_size=12),
            y=units.inch * 0.5
        )


    def _draw_header_title(self) -> None:
        """
        Draws the <COMPANY NAME> header box on the page.
        """
        text = constants.COMPANY_NAME
        font_size = 14

        table = platypus.Table([[text]])

        table.setStyle([
            ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (0, 0), font_size),
            ('LEFTPADDING', (0, 0), (0, 0), 16),
            ('RIGHTPADDING', (0, 0), (0, 0), 16),
            ('TOPPADDING', (0, 0), (0, 0), 16),
            ('BOTTOMPADDING', (0, 0), (0, 0), 16),
            ('BOX', (0, 0), (0, 0), 0.1, colors.black), # All borders 0.1 thick
            ('LINEBEFORE', (0, 0), (0, 0), 1, colors.black),  # Left border 1 thick
            ('LINEABOVE', (0, 0), (0, 0), 1, colors.black),  # Top border 1 thick
        ])

        table_width, table_height = table.wrapOn(self._pdf, 0, 0)
        table.drawOn(self._pdf, x=(PAGE_WIDTH - table_width) / 2.0, y=self._y - table_height)

        self._y -= table_height


    def _draw_header_subtitle(self) -> None:
        """
        Draws the CREW TIMESHEET header box on the page.
        """
        text = "CREW TIMESHEET"
        font_size = 12

        table = platypus.Table([[text]])

        table.setStyle([
            ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (0, 0), font_size),
            ('LEFTPADDING', (0, 0), (0, 0), 10),
            ('RIGHTPADDING', (0, 0), (0, 0), 10),
            ('TOPPADDING', (0, 0), (0, 0), 6),
            ('BOTTOMPADDING', (0, 0), (0, 0), 6),
            ('BOX', (0, 0), (0, 0), 0.1, colors.black), # All borders 0.1 thick
            ('LINEAFTER', (0, 0), (0, 0), 1, colors.black),  # Right border 1 thick
            ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),  # Bottom border 1 thick
        ])

        table_width, table_height = table.wrapOn(self._pdf, 0, 0)
        table.drawOn(self._pdf, x=(PAGE_WIDTH - table_width) / 2.0, y=self._y - table_height)

        self._y -= table_height


    def _draw_header(self) -> None:
        """
        Draws the header on the PDF. This should appear only on the first page.
        """
        self._draw_header_title()

        self._y -= (0.3 * units.cm)

        self._draw_header_subtitle()


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
        self._draw_text(
            text=label,
            x=units.inch,
            y=self._y,
            font=font if not bold else f"{font}-Bold",
            font_size=font_size
        )

        self._draw_text(
            text=text,
            x=units.inch + (units.inch * 1.95),
            y=self._y,
            font=font,
            font_size=font_size
        )


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

        self._y -= (1.5 * units.cm)

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
