"""Generador mínimo de PDF en Python puro (sin dependencias).

Sólo lo necesario para maquetar la rutina de TujagueGYM: texto con las fuentes
estándar Helvetica, rectángulos, líneas y saltos de página automáticos.
Las medidas están en puntos (72 pt = 1 pulgada) y el origen es la esquina
inferior izquierda, como manda el formato PDF.
"""

# Anchos de caracter (unidades/1000 em) de las fuentes estándar Helvetica.
_HELV = {
    ' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667, "'": 191,
    '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333, '.': 278, '/': 278,
    ':': 278, ';': 278, '<': 584, '=': 584, '>': 584, '?': 556, '@': 1015,
    'A': 667, 'B': 667, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778, 'H': 722,
    'I': 278, 'J': 500, 'K': 667, 'L': 556, 'M': 833, 'N': 722, 'O': 778, 'P': 667,
    'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722, 'V': 667, 'W': 944, 'X': 667,
    'Y': 667, 'Z': 611, '[': 278, '\\': 278, ']': 278, '^': 469, '_': 556, '`': 333,
    'a': 556, 'b': 556, 'c': 500, 'd': 556, 'e': 556, 'f': 278, 'g': 556, 'h': 556,
    'i': 222, 'j': 222, 'k': 500, 'l': 222, 'm': 833, 'n': 556, 'o': 556, 'p': 556,
    'q': 556, 'r': 333, 's': 500, 't': 278, 'u': 556, 'v': 500, 'w': 722, 'x': 500,
    'y': 500, 'z': 500, '{': 334, '|': 260, '}': 334, '~': 584,
}

_HELV_BOLD = dict(_HELV, **{
    "'": 238, '"': 474, '!': 333, '?': 611, '(': 333, ')': 333, ':': 333, ';': 333,
    'A': 722, 'B': 722, 'J': 556, 'K': 722, 'L': 611,
    'b': 611, 'c': 556, 'd': 611, 'f': 333, 'g': 611, 'h': 611, 'i': 278, 'j': 278,
    'k': 556, 'l': 278, 'm': 889, 'n': 611, 'o': 611, 'p': 611, 'q': 611, 'r': 389,
    's': 556, 't': 333, 'u': 611, 'v': 556, 'w': 778, 'x': 556, 'y': 556,
})

for _d in (_HELV, _HELV_BOLD):
    for _digit in '0123456789':
        _d[_digit] = 556
    # Acentuadas y signos del español: mismo ancho que su letra base.
    for _acc, _base in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'),
                        ('ü', 'u'), ('ñ', 'n'), ('Á', 'A'), ('É', 'E'), ('Í', 'I'),
                        ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N'), ('¿', '?'), ('¡', '!'),
                        ('°', 'o'), ('–', '-'), ('—', '-'), ('“', '"'), ('”', '"')):
        _d[_acc] = _d[_base]

FONTS = {
    'regular': ('F1', _HELV),
    'bold':    ('F2', _HELV_BOLD),
    'italic':  ('F3', _HELV),
}

A4 = (595.28, 841.89)


def text_width(s, font, size):
    widths = FONTS[font][1]
    return sum(widths.get(ch, 556) for ch in s) * size / 1000.0


def wrap(s, font, size, max_width):
    """Corta el texto en líneas que entren en max_width."""
    lines, current = [], ''
    for word in s.split():
        candidate = f'{current} {word}'.strip()
        if current and text_width(candidate, font, size) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _escape(s):
    return s.replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')


class PDF:
    def __init__(self, size=A4, margin=52):
        self.w, self.h = size
        self.margin = margin
        self.pages = []
        self.buf = []
        self.y = 0
        self.new_page()

    # ---------------------------------------------------------------- páginas

    def new_page(self):
        if self.buf:
            self.pages.append(''.join(self.buf))
        self.buf = []
        self.y = self.h - self.margin

    def ensure(self, space):
        """Salta de página si no entran `space` puntos de contenido."""
        if self.y - space < self.margin:
            self.new_page()
            return True
        return False

    # ---------------------------------------------------------------- dibujo

    def rect(self, x, y, w, h, color, stroke=None, lw=0.7):
        r, g, b = color
        self.buf.append(f'{r:.3f} {g:.3f} {b:.3f} rg\n')
        if stroke:
            sr, sg, sb = stroke
            self.buf.append(f'{sr:.3f} {sg:.3f} {sb:.3f} RG\n{lw} w\n')
            self.buf.append(f'{x:.2f} {y:.2f} {w:.2f} {h:.2f} re B\n')
        else:
            self.buf.append(f'{x:.2f} {y:.2f} {w:.2f} {h:.2f} re f\n')

    def line(self, x1, y1, x2, y2, color=(.85, .85, .87), lw=0.7):
        r, g, b = color
        self.buf.append(
            f'{r:.3f} {g:.3f} {b:.3f} RG\n{lw} w\n'
            f'{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S\n'
        )

    def text(self, x, y, s, font='regular', size=10, color=(.09, .09, .1)):
        code = FONTS[font][0]
        r, g, b = color
        self.buf.append(
            f'BT\n/{code} {size} Tf\n{r:.3f} {g:.3f} {b:.3f} rg\n'
            f'1 0 0 1 {x:.2f} {y:.2f} Tm\n({_escape(s)}) Tj\nET\n'
        )

    def text_right(self, x_right, y, s, font='regular', size=10, color=(.09, .09, .1)):
        self.text(x_right - text_width(s, font, size), y, s, font, size, color)

    def text_center(self, x_center, y, s, font='regular', size=10, color=(.09, .09, .1)):
        self.text(x_center - text_width(s, font, size) / 2, y, s, font, size, color)

    # ------------------------------------------------------------ serializado

    def save(self, path):
        self.pages.append(''.join(self.buf))
        self.buf = []

        objects = []          # cuerpos de los objetos, 1-indexados al escribir
        n_pages = len(self.pages)
        font_ids = {'F1': 'Helvetica', 'F2': 'Helvetica-Bold', 'F3': 'Helvetica-Oblique'}

        # 1: catálogo, 2: árbol de páginas, 3..: fuentes, luego páginas y streams.
        first_font = 3
        first_page = first_font + len(font_ids)
        kids = ' '.join(f'{first_page + i * 2} 0 R' for i in range(n_pages))

        objects.append('<< /Type /Catalog /Pages 2 0 R >>')
        objects.append(f'<< /Type /Pages /Count {n_pages} /Kids [{kids}] >>')
        for code, name in font_ids.items():
            objects.append(
                f'<< /Type /Font /Subtype /Type1 /BaseFont /{name} '
                f'/Encoding /WinAnsiEncoding >>'
            )

        res_fonts = ' '.join(
            f'/{code} {first_font + i} 0 R' for i, code in enumerate(font_ids)
        )
        for i, content in enumerate(self.pages):
            objects.append(
                f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.w:.2f} {self.h:.2f}] '
                f'/Resources << /Font << {res_fonts} >> >> '
                f'/Contents {first_page + i * 2 + 1} 0 R >>'
            )
            objects.append(content)   # marcador: se serializa como stream

        out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offsets = [0]
        for i, body in enumerate(objects, start=1):
            offsets.append(len(out))
            is_stream = i >= first_page and (i - first_page) % 2 == 1
            if is_stream:
                data = body.encode('cp1252', errors='replace')
                out += f'{i} 0 obj\n<< /Length {len(data)} >>\nstream\n'.encode('latin-1')
                out += data + b'\nendstream\nendobj\n'
            else:
                out += f'{i} 0 obj\n{body}\nendobj\n'.encode('cp1252', errors='replace')

        xref_pos = len(out)
        out += f'xref\n0 {len(objects) + 1}\n'.encode('latin-1')
        out += b'0000000000 65535 f \n'
        for off in offsets[1:]:
            out += f'{off:010d} 00000 n \n'.encode('latin-1')
        out += (
            f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'
            f'startxref\n{xref_pos}\n%%EOF\n'
        ).encode('latin-1')

        with open(path, 'wb') as fh:
            fh.write(bytes(out))
