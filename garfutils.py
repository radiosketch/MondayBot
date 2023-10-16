from PIL import Image, ImageDraw, ImageFont

'''
TextWrapper, by Ihor Pomaranskyy
Sourced from StackOverflow at:
https://stackoverflow.com/a/49719319

Modified by rad1osketxh:
- Replaced `draw.textsize()` with `draw.textlength()`
  This avoids a deprecation warning in newer versions of python
'''

class TextWrapper(object):
    """ Helper class to wrap text in lines, based on given text, font
        and max allowed line width.
    """

    def __init__(self, text, font, max_width):
        self.text = text
        self.text_lines = [
            ' '.join([w.strip() for w in l.split(' ') if w])
            for l in text.split('\n')
            if l
        ]
        self.font = font
        self.max_width = max_width

        self.draw = ImageDraw.Draw(
            Image.new(
                mode='RGB',
                size=(100, 100)
            )
        )

        self.space_width = self.draw.textlength(
            text=' ',
            font=self.font
        )

    def get_text_width(self, text):
        return self.draw.textlength(
            text=text,
            font=self.font
        )

    def wrapped_text(self):
        wrapped_lines = []
        buf = []
        buf_width = 0

        for line in self.text_lines:
            for word in line.split(' '):
                word_width = self.get_text_width(word)

                expected_width = word_width if not buf else \
                    buf_width + self.space_width + word_width

                if expected_width <= self.max_width:
                    # word fits in line
                    buf_width = expected_width
                    buf.append(word)
                else:
                    # word doesn't fit in line
                    wrapped_lines.append(' '.join(buf))
                    buf = [word]
                    buf_width = word_width

            if buf:
                wrapped_lines.append(' '.join(buf))
                buf = []
                buf_width = 0

        return '\n'.join(wrapped_lines)

FONT = ImageFont.truetype('mitr.bold.ttf', 52)
POS = (40, 545)
    
def garf_text(text, hate=False, align='center'):
    image = Image.open(f"monday{'hate' if hate else ''}.jpg")
    draw = ImageDraw.Draw(image)
    wrapped_text = TextWrapper(text, FONT, 610).wrapped_text()
    text_bbox = draw.textbbox(POS, wrapped_text, FONT)
    width = text_bbox[2] - text_bbox[0]
    size = image.size
    if text_bbox[3] > size[1] - 15:
        new_image = Image.new('RGB', (size[0], text_bbox[3] + 15), (71, 197, 235))
        Image.Image.paste(new_image, image, (0, 0))
        draw = ImageDraw.Draw(new_image)
        image = new_image
    draw.text(((size[0] - width)/2,POS[1]), wrapped_text, font=FONT, align=align, spacing=2, fill=(235, 211, 25), stroke_width=2, stroke_fill=(124, 114, 0))
    return image

def save_garf(text, hate=False, align='center'):
    image = garf_text(text, hate=hate, align=align)
    image.save('output.jpg')