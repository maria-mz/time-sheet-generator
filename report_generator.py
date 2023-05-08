from pymongo import MongoClient
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.lib import colors

client = MongoClient('mongodb://localhost:27017/')
database = client['employee_data']
employees = database['employees']

PDF_WIDTH, PDF_HEIGHT = A4

def write_text(pdf, font, font_size, text_content, x, y):
	text = pdf.beginText()
	text.setFont(font, font_size)
	text.setTextOrigin(x, y)
	text.textLine(text_content)
	pdf.drawText(text)

def draw_header(pdf):
	pdf.setStrokeColorRGB(0, 0, 0)

	top_rect_width = PDF_WIDTH / 3.5
	top_rect_height = 40

	# calculate x, y coordinate of top-left corner of top rectangle
	top_rect_x = (PDF_WIDTH - top_rect_width) / 2
	top_rect_y = PDF_HEIGHT - inch
        
	bottom_rect_width = top_rect_width * 0.75
	bottom_rect_height = top_rect_height * 0.5

	# calculate x, y coordinate of top-left corner of bottom rectangle
	bottom_rect_x = top_rect_x + (0.125 * top_rect_width)
	bottom_rect_y = top_rect_y - 30

	# Draw the two rectangles
	pdf.setStrokeAlpha(0.5)
	pdf.setLineWidth(0.1)
	pdf.rect(top_rect_x, top_rect_y, top_rect_width, top_rect_height)
	pdf.rect(bottom_rect_x, bottom_rect_y, bottom_rect_width, bottom_rect_height)

	# Add the borders
	pdf.setStrokeAlpha(1)
	pdf.setLineWidth(1)
    
	pdf.line(top_rect_x, top_rect_y, top_rect_x, top_rect_y + top_rect_height)
	pdf.line(top_rect_x, top_rect_y + top_rect_height, top_rect_x + top_rect_width, top_rect_y + top_rect_height)
    
	pdf.line(bottom_rect_x, bottom_rect_y, bottom_rect_x + bottom_rect_width, bottom_rect_y)
	pdf.line(bottom_rect_x + bottom_rect_width, bottom_rect_y, bottom_rect_x + bottom_rect_width, bottom_rect_y + bottom_rect_height)

	# Add the titles
	write_text(pdf, 'Helvetica', 14, "BRIGHT BYTE INC.", top_rect_x + 20, top_rect_y + top_rect_height - 20)
	write_text(pdf, 'Helvetica', 12, "CREW TIMESHEET", bottom_rect_x + 10, bottom_rect_y + bottom_rect_height - 15)


def extract_data(employee_data, table_data):
	total_reg = 0
	total_ot = 0
	week_ending = ""

	for row in employee_data:
		total_reg += row['regular_hours']
		total_ot += row['overtime_hours']
		table_data.append([
			row['day_of_week'][:3],
    		row['work_date'],
			row['time_in'],
			row['time_out'],
			format(row['regular_hours'], '.2f'),
			format(row['overtime_hours'], '.2f')
		])
		if row['day_of_week'] == "Friday":
			week_ending = row['work_date']
	
	return total_reg, total_ot, week_ending


def write_document(pdf):
	table_data = []
	# Add the two headers for the table
	table_data.append(["Day", "Date", "Time", "", "Hours"])		
	table_data.append(["", "", "In", "Out", "Reg.", "OT"])		

	# Loop through all employees
	employee_cursor = employees.find({})
	for employee in employee_cursor:
		name = employee["full_name"]
		job = employee["job_title"]
		data = employee["work_days"]
		
		write_employee_name(pdf, name)
		write_job(pdf, job)

		first_week_data = data[:len(data)//2]
		second_week_data = data[len(data)//2:]

		week_data_list = [(first_week_data, True), (second_week_data, False)]

		# Loop through the week data
		for week_data, is_first in week_data_list:
			total_reg, total_ot, week_ending = extract_data(week_data, table_data)
			table_data.append(["", "", "", "Total:", format(total_reg, '.2f'), format(total_ot, '.2f')])
			write_week_ending(pdf, week_ending, is_first)
			draw_table(pdf, table_data, is_first)
			table_data = table_data[:2]

		# Move to next page
		pdf.showPage()


def write_employee_name(pdf, name):
	y = PDF_HEIGHT - (PDF_HEIGHT / 5)
	write_text(pdf, 'Helvetica', 12, "Employee", inch, y)
	write_text(pdf, 'Helvetica', 12, name, inch * 3, y)


def write_job(pdf, job):
	y = PDF_HEIGHT - (PDF_HEIGHT / 5) - 30
	write_text(pdf, 'Helvetica', 12, "Job Title", inch, y)
	write_text(pdf, 'Helvetica', 12, job, inch * 3, y)


def write_week_ending(pdf, date, is_first):
	y = PDF_HEIGHT - (PDF_HEIGHT / 5) - 60
	write_text(pdf, 'Helvetica-Bold', 12, "Week Ending", inch, y if is_first else y - 250)
	write_text(pdf, 'Helvetica', 12, date, inch * 3, y if is_first else y - 250)
        

def draw_table(pdf, data, is_first):
	table = Table(data)

	# Add style to table cells
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

	# Draw the table on the canvas
	table.wrapOn(pdf, 0, 0)
	table.drawOn(pdf, inch*1.5, 400 if is_first else 150)


def generate_time_sheet():
    pdf = canvas.Canvas("test.pdf", pagesize=A4)
    pdf = canvas.Canvas("test.pdf", pagesize=A4)
    draw_header(pdf)
    write_document(pdf)
    pdf.save()

# generate_time_sheet()
