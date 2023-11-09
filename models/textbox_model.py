class TextBoxModel:
    def __init__(self, text_lines, pos, color, back_color, horz_center=False):
        self.text_lines = text_lines
        self.pos = pos
        self.color = color
        self.back_color = back_color
        self.horz_centered = horz_center
        self.width = 0
