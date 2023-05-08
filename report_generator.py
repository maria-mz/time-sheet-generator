from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
database = client['employee_data']
employees = database['employees']

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.units import inch

PDF_WIDTH, PDF_HEIGHT = A4

def draw_grid(pdf):
    pdf.setStrokeAlpha(0.25)

    # draw horizontal center line
    pdf.line(0, PDF_HEIGHT/2, PDF_WIDTH, PDF_HEIGHT/2)

    # draw vertical center line
    pdf.line(PDF_WIDTH/2, 0, PDF_WIDTH/2, PDF_HEIGHT)

    # draw grid lines
    pdf.setStrokeColorRGB(0, 0, 1) 
    pdf.setLineWidth(0.25)

    # draw horizontal grid lines
    for y in range(int(PDF_HEIGHT/2), int(PDF_HEIGHT), int(10*mm)):
        pdf.line(0, y, PDF_WIDTH, y)
        pdf.line(0, PDF_HEIGHT-y, PDF_WIDTH, PDF_HEIGHT-y)

    # draw vertical grid lines
    for x in range(int(PDF_WIDTH/2), int(PDF_WIDTH), int(10*mm)):
        pdf.line(x, 0, x, PDF_HEIGHT)
        pdf.line(PDF_WIDTH-x, 0, PDF_WIDTH-x, PDF_HEIGHT)


def write_text(font_size, text_content, x, y):
	text = pdf.beginText()
	text.setFont('Helvetica', font_size)
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
	write_text(14, "BRIGHT BYTE INC.", top_rect_x + 20, top_rect_y + top_rect_height - 20)
	write_text(12, "CREW TIMESHEET", bottom_rect_x + 10, bottom_rect_y + bottom_rect_height - 15)
        
    
pdf = canvas.Canvas("test.pdf", pagesize=A4)
draw_grid(pdf)
draw_header(pdf)
pdf.save()
