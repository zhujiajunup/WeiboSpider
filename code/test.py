import pytesseract
from PIL import Image
image = Image.open('D:\\graduate\\WeiboSpider3\\pin.png')
pytesseract.pytesseract.tesseract_cmd = 'c:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
print(pytesseract.image_to_string(image))
