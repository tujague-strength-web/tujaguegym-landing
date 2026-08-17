#!/usr/bin/env python3
"""Genera rutina-4-semanas.pdf, el material descargable de la landing.

Uso:  python3 tools/generar-rutina.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf import PDF, wrap, text_width  # noqa: E402

INK      = (.09, .09, .10)
MUTED    = (.42, .42, .46)
LIME     = (.83, 1.0, .28)
LIME_INK = (.36, .45, .04)
RULE     = (.87, .87, .89)
ZEBRA    = (.972, .972, .975)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'rutina-4-semanas.pdf')


class Doc(PDF):
    """Capa de maquetación: cursor vertical, títulos, párrafos y tablas."""

    def __init__(self):
        self.page_no = 0          # lo usa new_page(), que corre dentro de super()
        super().__init__(margin=54)
        self.content_w = self.w - self.margin * 2

    # --------------------------------------------------------------- bloques

    def h1(self, s):
        self.ensure(64)
        self.y -= 8
        self.text(self.margin, self.y, s, 'bold', 21)
        self.y -= 10
        self.rect(self.margin, self.y, 46, 3.5, LIME)
        self.y -= 22

    def h2(self, s):
        self.ensure(52)
        self.y -= 12
        self.text(self.margin, self.y, s, 'bold', 13)
        self.y -= 16

    def para(self, s, size=10, color=INK, gap=6):
        for ln in wrap(s, 'regular', size, self.content_w):
            self.ensure(size + 4)
            self.y -= size + 3.4
            self.text(self.margin, self.y, ln, 'regular', size, color)
        self.y -= gap

    def bullet(self, s, size=10):
        lines = wrap(s, 'regular', size, self.content_w - 16)
        for i, ln in enumerate(lines):
            self.ensure(size + 4)
            self.y -= size + 3.4
            if i == 0:
                self.rect(self.margin + 1.5, self.y + 3, 4, 4, LIME_INK)
            self.text(self.margin + 16, self.y, ln, 'regular', size, INK)
        self.y -= 3

    def note(self, title, body):
        """Recuadro destacado con barra lima a la izquierda."""
        lines = wrap(body, 'regular', 9.5, self.content_w - 42)
        height = 26 + len(lines) * 13
        self.ensure(height + 12)
        self.y -= height
        top = self.y
        self.rect(self.margin, top, self.content_w, height, (.985, .985, .97))
        self.rect(self.margin, top, 3.5, height, LIME_INK)
        cursor = top + height - 16
        self.text(self.margin + 16, cursor, title, 'bold', 10, INK)
        for ln in lines:
            cursor -= 13
            self.text(self.margin + 16, cursor, ln, 'regular', 9.5, INK)
        self.y -= 14

    def table(self, headers, rows, widths):
        """Tabla con encabezado lima; repite el encabezado si cambia de página."""
        cols = [w / sum(widths) * self.content_w for w in widths]

        def draw_header():
            self.ensure(30)
            self.y -= 21
            self.rect(self.margin, self.y, self.content_w, 21, INK)
            x = self.margin
            for head, cw in zip(headers, cols):
                self.text(x + 8, self.y + 7, head.upper(), 'bold', 8, LIME)
                x += cw

        draw_header()
        for i, row in enumerate(rows):
            wrapped = [wrap(str(cell), 'regular', 9.5, cw - 16) or ['']
                       for cell, cw in zip(row, cols)]
            height = max(18, max(len(w) for w in wrapped) * 12 + 8)
            if self.ensure(height):
                draw_header()
            self.y -= height
            if i % 2 == 1:
                self.rect(self.margin, self.y, self.content_w, height, ZEBRA)
            self.line(self.margin, self.y, self.margin + self.content_w, self.y, RULE)
            x = self.margin
            for j, (cell_lines, cw) in enumerate(zip(wrapped, cols)):
                cursor = self.y + height - 12
                for ln in cell_lines:
                    self.text(x + 8, cursor, ln, 'bold' if j == 0 else 'regular', 9.5,
                              INK if j == 0 else MUTED)
                    cursor -= 12
                x += cw
        self.y -= 12

    # ------------------------------------------------------- páginas y firma

    def new_page(self):
        super().new_page()
        self.page_no += 1
        if self.page_no > 1:
            self.footer()
            self.y = self.h - self.margin - 6

    def footer(self):
        y = self.margin - 22
        self.line(self.margin, y + 14, self.w - self.margin, y + 14, RULE)
        self.text(self.margin, y, 'TujagueGYM — Rutina de 4 semanas',
                  'regular', 8, MUTED)
        self.text_right(self.w - self.margin, y, str(self.page_no - 1),
                        'regular', 8, MUTED)


def cover(d):
    d.rect(0, 0, d.w, d.h, (.043, .043, .047))
    d.rect(d.margin, d.h - 132, 40, 40, LIME)
    d.text(d.margin + 12, d.h - 121, 'T', 'bold', 24, (.04, .04, .05))
    d.text(d.margin + 54, d.h - 121, 'TujagueGYM', 'bold', 20, (.96, .96, .97))

    d.text(d.margin, 500, 'RUTINA DE', 'bold', 46, (.96, .96, .97))
    d.text(d.margin, 448, '4 SEMANAS', 'bold', 46, LIME)
    d.rect(d.margin, 424, 64, 4, LIME)

    for i, ln in enumerate([
        'Plan de musculación progresivo, con series, repeticiones,',
        'descansos e intensidad definidos para cada día.',
        'Incluye versión para principiantes y para intermedios.',
    ]):
        d.text(d.margin, 388 - i * 19, ln, 'regular', 12, (.72, .72, .76))

    for i, ln in enumerate(['Plan A — Principiantes · 3 días por semana',
                            'Plan B — Intermedios · 4 días por semana']):
        d.text(d.margin, 300 - i * 20, ln, 'bold', 11, LIME)

    d.line(d.margin, 150, d.w - d.margin, 150, (.20, .20, .23))
    d.text(d.margin, 128, 'Material gratuito para socios y futuros socios.',
           'regular', 9.5, (.55, .55, .60))
    d.new_page()


def como_usarlo(d):
    d.h1('Cómo usar este plan')
    d.para('Este plan dura 4 semanas y está pensado para que sepas exactamente qué hacer '
           'cada día que entrás al gimnasio. Elegí uno de los dos planes y respetalo las '
           '4 semanas completas: cambiar de rutina cada semana es el error más común y el '
           'que más frena el progreso.')

    d.h2('1. Elegí tu plan')
    d.bullet('Plan A (principiantes): menos de 6 meses entrenando de forma constante. '
             '3 días por semana, cuerpo completo. Ejemplo: lunes, miércoles y viernes.')
    d.bullet('Plan B (intermedios): más de 6 meses entrenando, ya dominás los ejercicios '
             'básicos. 4 días por semana divididos en tren superior e inferior.')

    d.h2('2. Entendé el RIR')
    d.para('RIR significa "repeticiones en reserva": cuántas repeticiones más podrías haber '
           'hecho al terminar la serie. Es la forma de medir el esfuerzo sin depender del peso. '
           'RIR 3 significa que terminás la serie pudiendo hacer 3 repeticiones más. Si la '
           'tabla dice 10 repeticiones con RIR 3, elegí un peso con el que podrías haber '
           'hecho 13.')

    d.h2('3. Progresá todas las semanas')
    d.para('La regla es simple: si completaste todas las series en el rango de repeticiones '
           'indicado y con el RIR correcto, la próxima sesión sumá peso. En ejercicios de '
           'pierna y espalda, 2,5 a 5 kg. En ejercicios de brazos y hombros, 1 a 2,5 kg. Si '
           'no llegaste al rango, repetí el mismo peso hasta lograrlo.')

    d.h2('4. Calentá antes de cada sesión')
    d.bullet('5 a 10 minutos de bicicleta, cinta o elíptico a ritmo suave.')
    d.bullet('En el primer ejercicio del día: 2 series de aproximación con poco peso '
             '(por ejemplo 10 repeticiones con la barra y luego 5 con la mitad del peso '
             'de trabajo). Estas series no cuentan en la tabla.')

    d.h2('5. Respetá los descansos')
    d.para('Los descansos entre series están en la tabla y son parte del entrenamiento: '
           'descansar de menos baja el rendimiento de las series siguientes. Cronometralos '
           'con el celular.')

    d.note('Antes de empezar',
           'Si tenés una lesión, una condición médica o hace mucho que no hacés actividad '
           'física, consultá con un profesional de la salud antes de comenzar. Ningún plan '
           'genérico reemplaza la supervisión presencial: si algo duele (no "arde", duele), '
           'pará y consultanos.')
    d.new_page()


PLAN_A = [
    ('Día 1 — Cuerpo completo', [
        ('Sentadilla con barra (o goblet con mancuerna)', '3', '8-10', '2 min', '3'),
        ('Press de banca con mancuernas', '3', '8-10', '2 min', '3'),
        ('Remo con barra', '3', '10', '90 s', '3'),
        ('Elevaciones laterales', '2', '12-15', '60 s', '2'),
        ('Plancha frontal', '3', '30 s', '45 s', '—'),
    ]),
    ('Día 2 — Cuerpo completo', [
        ('Peso muerto rumano', '3', '8-10', '2 min', '3'),
        ('Press militar con mancuernas', '3', '8-10', '90 s', '3'),
        ('Jalón al pecho (o dominada asistida)', '3', '10', '90 s', '3'),
        ('Prensa de piernas', '3', '12', '90 s', '3'),
        ('Curl de bíceps con barra', '2', '12', '60 s', '2'),
    ]),
    ('Día 3 — Cuerpo completo', [
        ('Sentadilla búlgara', '3', '10 por pierna', '90 s', '3'),
        ('Press inclinado con mancuernas', '3', '10', '90 s', '3'),
        ('Remo en polea baja', '3', '12', '90 s', '3'),
        ('Extensión de tríceps en polea', '2', '12', '60 s', '2'),
        ('Elevación de talones de pie', '3', '15', '45 s', '2'),
    ]),
]

PLAN_B = [
    ('Día 1 — Tren superior (fuerza)', [
        ('Press de banca con barra', '4', '5-6', '3 min', '2'),
        ('Remo con barra', '4', '6-8', '2,5 min', '2'),
        ('Press militar con barra', '3', '6-8', '2 min', '2'),
        ('Dominadas (o jalón al pecho)', '3', '8', '2 min', '2'),
        ('Curl de bíceps con barra', '3', '10', '60 s', '1'),
        ('Extensión de tríceps en polea', '3', '10', '60 s', '1'),
    ]),
    ('Día 2 — Tren inferior (fuerza)', [
        ('Sentadilla con barra', '4', '5-6', '3 min', '2'),
        ('Peso muerto rumano', '3', '8', '2,5 min', '2'),
        ('Prensa de piernas', '3', '10', '2 min', '2'),
        ('Curl femoral acostado', '3', '12', '90 s', '1'),
        ('Elevación de talones de pie', '4', '12', '60 s', '1'),
        ('Plancha frontal', '3', '45 s', '45 s', '—'),
    ]),
    ('Día 3 — Tren superior (hipertrofia)', [
        ('Press inclinado con mancuernas', '4', '8-10', '2 min', '2'),
        ('Remo en polea con agarre neutro', '4', '10-12', '90 s', '2'),
        ('Aperturas en polea', '3', '12-15', '60 s', '1'),
        ('Jalón al pecho agarre supino', '3', '10-12', '90 s', '2'),
        ('Elevaciones laterales', '4', '12-15', '45 s', '1'),
        ('Curl martillo', '3', '12', '60 s', '1'),
    ]),
    ('Día 4 — Tren inferior (hipertrofia)', [
        ('Hip thrust con barra', '4', '10-12', '2 min', '2'),
        ('Sentadilla búlgara', '3', '10-12 por pierna', '90 s', '2'),
        ('Extensión de cuádriceps', '3', '12-15', '60 s', '1'),
        ('Curl femoral sentado', '3', '12-15', '60 s', '1'),
        ('Abducción de cadera en máquina', '3', '15', '45 s', '1'),
        ('Elevación de talones sentado', '4', '15', '45 s', '1'),
    ]),
]

HEADERS = ['Ejercicio', 'Series', 'Reps', 'Descanso', 'RIR']
WIDTHS = [46, 12, 16, 15, 11]


def plan(d, titulo, subtitulo, dias):
    d.h1(titulo)
    d.para(subtitulo, color=MUTED)
    for nombre, ejercicios in dias:
        d.h2(nombre)
        d.table(HEADERS, ejercicios, WIDTHS)
    d.new_page()


def progresion(d):
    d.h1('La progresión semana a semana')
    d.para('Los ejercicios no cambian durante las 4 semanas: lo que cambia es cuánto '
           'esfuerzo exigís. Así se ve el plan completo:')

    d.table(['Semana', 'Objetivo', 'Cómo se siente'], [
        ('Semana 1', 'Aprender los movimientos y registrar tus pesos iniciales. '
                     'Quedate corto antes que pasarte.', 'RIR 3 — exigente pero cómodo'),
        ('Semana 2', 'Sumá 2,5 kg en los básicos o 1 repetición por serie respecto '
                     'de la semana 1.', 'RIR 2 a 3 — cuesta las últimas series'),
        ('Semana 3', 'La semana más dura: sumá una serie al primer ejercicio de cada '
                     'día y volvé a subir el peso.', 'RIR 1 a 2 — cerca del fallo'),
        ('Semana 4', 'Descarga: mismo peso que la semana 3 pero con 2 series menos '
                     'por ejercicio. El cuerpo consolida lo ganado.', 'RIR 4 — liviano a propósito'),
    ], [14, 52, 34])

    d.h2('Qué hacer al terminar las 4 semanas')
    d.para('Volvé a empezar el mismo plan desde la semana 1, pero usando como punto de '
           'partida los pesos que lograste en la semana 3. Vas a poder repetir este ciclo '
           'dos o tres veces antes de necesitar un plan nuevo.')

    d.note('El registro es lo que hace que esto funcione',
           'Anotá el peso y las repeticiones de cada serie, en el cuaderno o en el celular. '
           'Sin registro no sabés si progresaste y la progresión es, literalmente, todo el '
           'plan. Al final de este PDF tenés una planilla para imprimir.')
    d.new_page()


TECNICA = [
    ('Sentadilla', [
        'Barra apoyada sobre los trapecios, no sobre el cuello.',
        'Pies al ancho de los hombros, puntas levemente hacia afuera.',
        'Bajá empujando la cadera hacia atrás y abajo, con las rodillas en la línea de '
        'los pies, hasta que el muslo quede paralelo al piso.',
        'La espalda se mantiene recta: si la zona lumbar se redondea abajo, no bajes tanto.',
    ]),
    ('Press de banca', [
        'Omóplatos juntos y apoyados en el banco durante toda la serie.',
        'Bajá la barra controlado hasta tocar la parte baja del pecho.',
        'Los codos van a unos 45 grados del torso, no abiertos a 90.',
        'Los pies firmes en el piso. Si entrenás pesado, usá seguros o pedí ayuda.',
    ]),
    ('Peso muerto rumano', [
        'Rodillas apenas flexionadas y fijas: el movimiento es de cadera, no de rodilla.',
        'Llevá la cola hacia atrás mientras la barra baja pegada a las piernas.',
        'Bajá hasta sentir tensión en los isquiotibiales, sin redondear la espalda.',
        'Subí apretando los glúteos, sin hiperextender la zona lumbar arriba.',
    ]),
    ('Remo con barra', [
        'Torso inclinado unos 45 grados, espalda recta y mirada al piso.',
        'Traé la barra hacia el ombligo, no hacia el pecho.',
        'Pensá en llevar los codos hacia atrás y juntar los omóplatos.',
        'Sin impulso de cadera: si necesitás rebote, es demasiado peso.',
    ]),
    ('Press militar', [
        'Barra a la altura de las clavículas, manos apenas más abiertas que los hombros.',
        'Apretá glúteos y abdomen para no arquear la espalda.',
        'Empujá hacia arriba y llevá la cabeza levemente adelante al pasar la barra.',
        'Terminá con los brazos extendidos y la barra sobre la línea de los hombros.',
    ]),
]


def tecnica(d):
    d.h1('Técnica de los ejercicios clave')
    d.para('Cinco movimientos concentran la mayor parte de los resultados de este plan. '
           'Aprendelos bien antes de subir el peso.', color=MUTED)
    for nombre, puntos in TECNICA:
        d.h2(nombre)
        for punto in puntos:
            d.bullet(punto, size=9.5)
    d.new_page()


def registro(d):
    d.h1('Planilla de registro')
    d.para('Imprimí esta hoja (una por día de entrenamiento) o copiá las columnas en el '
           'celular. Anotá el peso real que usaste en cada serie.', color=MUTED)

    d.y -= 6
    d.text(d.margin, d.y, 'Día:  ____________________        '
                          'Semana:  ______        Fecha:  ____ / ____ / ______',
           'regular', 10, INK)
    d.y -= 16

    filas = [('', '', '', '', '')] * 14
    d.table(['Ejercicio', 'Peso', 'Series x reps', 'RIR', 'Notas'],
            filas, [34, 12, 20, 8, 26])

    d.para('Cómo me sentí hoy (energía, dolores, descanso):', color=MUTED, size=9.5)
    for _ in range(3):
        d.y -= 20
        d.line(d.margin, d.y, d.w - d.margin, d.y, RULE)
    d.new_page()


def cierre(d):
    d.h1('Ahora te toca a vos')
    d.para('Tenés 4 semanas de entrenamiento planificadas. No necesitás nada más para '
           'empezar: elegí tu plan, agendá los días en el calendario y cumplilos. La '
           'constancia gana por goleada a cualquier rutina perfecta.')

    d.h2('Tres cosas que hacen la diferencia')
    d.bullet('Dormí. Entre 7 y 9 horas: el músculo crece mientras descansás, no en la sala.')
    d.bullet('Comé suficiente proteína. Como referencia general, entre 1,6 y 2,2 gramos '
             'por kilo de peso corporal por día.')
    d.bullet('No faltes dos veces seguidas. Una sesión perdida no es nada; dos seguidas '
             'se vuelven un mes.')

    d.note('¿Querés que ajustemos el plan a vos?',
           'Este PDF es un plan general. En TujagueGYM podemos adaptarlo a tu nivel, a tus '
           'horarios y a los equipos que tenés disponibles, y corregirte la técnica en el '
           'momento. Escribinos o pasá por el gimnasio y lo vemos juntos.')

    d.y -= 10
    d.rect(d.margin, d.y - 54, d.content_w, 54, (.043, .043, .047))
    d.text(d.margin + 20, d.y - 24, 'TujagueGYM', 'bold', 15, LIME)
    d.text(d.margin + 20, d.y - 42, 'Entrenamiento de fuerza y musculación',
           'regular', 10, (.72, .72, .76))
    d.y -= 64


def main():
    d = Doc()
    cover(d)
    como_usarlo(d)
    plan(d, 'Plan A — Principiantes',
         '3 días por semana, cuerpo completo. Dejá al menos un día de descanso entre '
         'sesiones (por ejemplo lunes, miércoles y viernes).', PLAN_A)
    plan(d, 'Plan B — Intermedios',
         '4 días por semana divididos en tren superior y tren inferior. Por ejemplo lunes, '
         'martes, jueves y viernes.', PLAN_B)
    progresion(d)
    tecnica(d)
    registro(d)
    cierre(d)
    d.save(OUT)
    print(f'PDF generado: {OUT} ({os.path.getsize(OUT) / 1024:.1f} KB, '
          f'{len(d.pages)} páginas)')


if __name__ == '__main__':
    main()
