#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'

import argparse
import os
import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak, Image, ListFlowable, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.units import inch
from reportlab.lib.enums import *
from reportlab.lib import colors

from pjc.tournament import Tournament, TeamPlanning

default_table_style = [
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 12),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ('TOPPADDING', (0, 0), (-1, -1), 0.15 * inch),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0.15 * inch),
]

cell_bkgnd_color = colors.Color(0.9, 0.9, 0.9)

tables_spacer = Spacer(0, 0.2 * inch)

SCRIPT_HOME = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(SCRIPT_HOME, 'assets')

logo_left = Image(os.path.join(ASSETS_DIR, 'logo_left.png'), width=0.84 * inch, height=0.79 * inch)
logo_right = Image(os.path.join(ASSETS_DIR, 'logo_right.png'), width=0.95 * inch, height=0.79 * inch)

cell_body = ParagraphStyle(
    'cell_header',
    fontName='Helvetica',
    fontSize=12
)

cell_header = ParagraphStyle(
    'cell_header',
    parent=cell_body,
    fontName='Helvetica-Bold'
)
match_title = ParagraphStyle(
    'match_title',
    parent=cell_header,
    alignment=TA_CENTER,
    spaceAfter=10
)

match_comment = ParagraphStyle(
    'match_comment',
    parent=cell_body,
    fontName='Helvetica-Oblique',
    fontSize=10
)


class PageHeader(object):
    LOGO_WIDTH = 1.15 * inch
    MARGIN = 0.5 * inch

    def __init__(self, title=None, page_size=portrait(A4)):
        self.title = title or ''
        self.text_width = page_size[0] - 2 * self.MARGIN

    def get_story(self):
        return [
            Table(
                [
                    [logo_left, 'POBOT Junior Cup 2015', logo_right],
                    ['', self.title, '']
                ],
                colWidths=[self.LOGO_WIDTH, self.text_width - 2 * self.LOGO_WIDTH, self.LOGO_WIDTH],
                rowHeights=[0.5 * inch, 0.5 * inch],
                style=[
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 24),
                    ('FONTSIZE', (0, 1), (2, 1), 18),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('VALIGN', (1, 0), (1, -1), 'TOP'),
                    ('SPAN', (0, 0), (0, 1)),
                    ('SPAN', (2, 0), (2, 1)),
                ]
            ),
            Spacer(0, 0.5 * inch)
        ]


class TeamHeader(object):
    team_name_style = ParagraphStyle(
        'team_name',
        fontName='Helvetica-Bold',
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=0.2 * inch
    )

    team_school_style = ParagraphStyle(
        'team_school',
        fontName='Helvetica',
        fontSize=14,
        alignment=TA_CENTER
    )

    def __init__(self, team):
        self.team = team

    def get_story(self):
        return [
            Paragraph("%s - %s" % (self.team.num, self.team.name), self.team_name_style),
            Paragraph(
                "%s - %s" % (self.team.school or '<i>équipe open</i>', self.team.level.orig),
                self.team_school_style
            ),
            Spacer(0, 0.5 * inch)
        ]


def generate_individual_sheet(title, tournament, body_generator):
    page_header_story = PageHeader(title).get_story()
    story = []

    for team in tournament.registered_teams:
        story.extend(page_header_story)
        story.extend(TeamHeader(team).get_story())
        body_generator(story, team)
        story.append(PageBreak())

    return story


def generate_match_sheets(tournament, **kwArgs):
    match_comments = [
        """
            Le match se termine dès que <b>3 tours complets</b> sont effectués ou bien au bout de 2"30.
            <br/>
            Pour un sans-faute le nombre de quadrants valides sera de 12.
        """,
        """
            Le match est arrêté au bout de 2"30 ou bien <b>dès que le passager est perdu</b>.
            <br/>
            La comptabilisation est sinon identique à celle de l'épreuve 1.
        """,
        """
            Le match est arrêté au bout de 2"30 ou bien <b>dès que le robot perd la ligne</b>.
            <br/>
            Le quai d'embarquement n'est regarni que s'il a été complètement vidé de ses passagers. Les
            passagers déplacés seront remis sur l'emplacement le plus proche.
            <br/>
            Un passager n'est comptabilisé que s'il est <b>entièrement contenu</b> dans la zone de dépose,
            c'est à dire si rien de dépasse de la bordure externe du trait de délimitation.
        """
    ]

    def generate_body(story, team):
        for match_num, match_name in enumerate(('vitesse', 'confort'), start=1):
            story.append(Table(
                [
                    [
                        [
                            Paragraph("Epreuve %d : %s" % (match_num, match_name), style=match_title),
                            Paragraph(match_comments[match_num - 1], style=match_comment)
                        ]
                    ],
                    ["Arbitre", ''],
                    ["Temps total", '', "Quadrants valides", '']
                ],
                colWidths=[1.67 * inch] * 4,
                style=default_table_style + [
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('SPAN', (0, 0), (3, 0)),
                    ('SPAN', (0, 1), (1, 1)),
                    ('SPAN', (2, 1), (3, 1)),
                    ('BACKGROUND', (0, 0), (3, 0), cell_bkgnd_color),
                    ('BACKGROUND', (0, 1), (1, 1), cell_bkgnd_color),
                    ('BACKGROUND', (0, 2), (0, 2), cell_bkgnd_color),
                    ('BACKGROUND', (2, 2), (2, 2), cell_bkgnd_color),
                ]
            ))
            story.append(tables_spacer)

        story.append(Table(
            [
                [
                    [
                        Paragraph("Epreuve 3 : transport de passagers", style=match_title),
                        Paragraph(match_comments[2], style=match_comment)
                    ]
                ],
                ["Arbitre", ''],
                ["Total passagers", '', '', '']
            ],
            colWidths=[1.67 * inch] * 4,
            style=default_table_style + [
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('SPAN', (0, 0), (3, 0)),
                ('SPAN', (0, 1), (1, 1)),
                ('SPAN', (2, 1), (3, 1)),
                ('SPAN', (2, 2), (3, 2)),
                ('BACKGROUND', (0, 0), (3, 0), cell_bkgnd_color),
                ('BACKGROUND', (0, 1), (1, 1), cell_bkgnd_color),
                ('BACKGROUND', (0, 2), (0, 2), cell_bkgnd_color),
                ('BACKGROUND', (2, 2), (3, 2), cell_bkgnd_color),
            ]
        ))

    return generate_individual_sheet('Feuille de match', tournament, generate_body)


def generate_jury_sheets(tournament, **kwArgs):
    def generate_body(story, team):
        story.append(Table(
            [
                ['Numéro du jury', '']
            ],
            colWidths=[(6.7 - 2.38) * inch, 2.38 * inch],
            style=default_table_style + [
                ('BACKGROUND', (0, 0), (0, 0), cell_bkgnd_color),
                ('ALIGN', (0, 0), (0, 0), 'RIGHT')
            ]
        ))
        story.append(tables_spacer)

        story.append(Table(
            [
                ['Points évalués', '', Paragraph('<para align=center><b>Note</b> (sur 20)', style=cell_body)],
                ['1', [
                    Paragraph('Pertinence du sujet choisi', style=cell_header),
                    Paragraph(
                        'Qualifie la manière dont le sujet traité correspond avec '
                        'les attentes exprimées dans le descriptif du concours',
                        style=cell_body
                    )
                ]],
                ['2', [
                    Paragraph('Qualité de la recherche', style=cell_header)
                ]],
                ['3', [
                    Paragraph("Qualité de l'exposé", style=cell_header)
                ]],
                ['4', [
                    Paragraph("Qualité du poster", style=cell_header),
                    Paragraph('Complétude, soin de réalisation, respect des consignes.', style=cell_body),
                    Paragraph('Doivent y figurer les éléments suivants :', style=cell_body),
                    ListFlowable([
                        Paragraph("description de l'équipe", style=cell_body),
                        Paragraph("quelques mots sur le robot et les stratégies choisies", style=cell_body),
                        Paragraph("description du thème de recherche", style=cell_body),
                        Paragraph("quelques mots sur la place de la robotique dans l'établissement", style=cell_body),
                    ], bulletType='bullet', start='-')
                ]],
                [Paragraph("<para align=right><b>Total des points</b> (sur 80)", style=cell_body), '']
            ],
            colWidths=[0.34 * inch, 3.97 * inch, 2.38 * inch],
            style=default_table_style + [
                ('SPAN', (0, 0), (1, 0)),
                ('SPAN', (0, -1), (1, -1)),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, 0), cell_bkgnd_color),
                ('BACKGROUND', (0, 0), (0, -1), cell_bkgnd_color),
                ('BACKGROUND', (0, -1), (1, -1), cell_bkgnd_color),
            ]
        ))

    return generate_individual_sheet('Dossier de recherche', tournament, generate_body)


def generate_approval_sheets(tournament, **kwArgs):
    def generate_body(story, team):
        story.append(Table(
            [
                ['Arbitre', '']
            ],
            colWidths=[6.7 / 2 * inch] * 2,
            style=default_table_style + [
                ('BACKGROUND', (0, 0), (0, 0), cell_bkgnd_color),
                ('ALIGN', (0, 0), (0, 0), 'RIGHT')
            ]
        ))
        story.append(tables_spacer)

        story.append(Table(
            [
                ["Le robot ne comporte qu'une seule brique programmable"],
                [Paragraph(
                    "Aucun moyen de solidification du robot n'est utilisé dans la construction<br/>"
                    "<i>(vis, colle, autocollants, adhésif,...)</i>",
                    style=cell_body), ''
                ],
                [Paragraph(
                    "Le robot est entièrement autonome, y compris en matière d'énergie",
                    style=cell_body
                ), ''],
                [Paragraph(
                    "Si RCX, la tourelle de téléchargement est réglée en faible puissance",
                    style=cell_body
                ), ''],
                [Paragraph(
                    "L'équipe est capable de démontrer qu'elle a parfaitement compris l'utilisation et le principe "
                    "de fonctionnement des éventuelles extensions électroniques ou électro-mécaniques utilisées",
                    style=cell_body
                ), ''],
                [Paragraph(
                    "L'équipe a préparé un dossier de recherche sur la thématique de la compétition "
                    "et a remis son poster aux organisateurs",
                    style=cell_body
                ), ''],
                [Paragraph(
                    "L'équipe est informé que seuls 2 équipiers sont autorisés à être autour de la table de jeu "
                    "pendant les matchs",
                    style=cell_body
                ), ''],
                [Paragraph(
                    "L'équipe a bien compris les règles du jeu ainsi que la procédure de départ",
                    style=cell_body
                ), ''],
            ],
            colWidths=[6 * inch, 0.7 * inch],
            style=default_table_style + [
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ]
        ))

    return generate_individual_sheet("Fiche d'homologation", tournament, generate_body)


def generate_time_tables(tournament, **kwArgs):
    def generate_body(story, team):
        story.append(Table(
            [
                [
                    'Epreuve %d' % (i + 1),
                    match.time.strftime('%H:%M'),
                    'Table',
                    match.table
                ] for i, match in enumerate(team.planning.matches)
            ],
            colWidths=[6.7 / 4 * inch] * 4,
            style=default_table_style + [
                ('BACKGROUND', (0, 0), (0, -1), cell_bkgnd_color),
                ('BACKGROUND', (2, 0), (2, -1), cell_bkgnd_color),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ]
        ))

        story.append(tables_spacer)

        story.append(Table(
            [
                [
                    'Exposé',
                    team.planning.presentation.time.strftime('%H:%M'),
                    'Jury',
                    team.planning.presentation.jury
                ]
            ],
            colWidths=[6.7 / 4 * inch] * 4,
            style=default_table_style + [
                ('BACKGROUND', (0, 0), (0, -1), cell_bkgnd_color),
                ('BACKGROUND', (2, 0), (2, -1), cell_bkgnd_color),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ]
        ))

    return generate_individual_sheet("Heures de passage", tournament, generate_body)


def generate_stand_labels(tournament, **kwArgs):
    story = []

    team_num_style = ParagraphStyle(
        'label_team_num',
        fontSize=48,
        autoLeading='min',
        alignment=TA_CENTER,
    )

    team_name_style = ParagraphStyle(
        'label_team_name',
        parent=team_num_style,
        fontName="Helvetica-Oblique",
        fontSize=40,
        wordWrap=False,
        spaceBefore=0.3 * inch
    )

    team_detail_style = ParagraphStyle(
        'label_team_detail',
        parent=team_name_style,
        fontSize=24,
        autoLeading='min',
    )

    page_header_story = PageHeader().get_story()
    for team in tournament.registered_teams:
        story.extend(page_header_story)
        story.extend([
            Spacer(0, 1 * inch),
            Paragraph("Equipe %d" % team.num, team_num_style),
            Paragraph(team.name, team_name_style),
            Spacer(0, 1.5 * inch),
            Paragraph(team.school or '<i>Equipe open</i>', team_detail_style),
            Paragraph(team.level.orig, team_detail_style),
            Spacer(0, 0.3 * inch),
            Paragraph("%s (%02d)" % (team.city, int(team.department)), team_detail_style),
            PageBreak()
        ])

    return story


class PlanningFlowable(Flowable):
    CHART_X0 = 1.5 * inch
    CHART_Y0 = -0.3 * inch
    DX = 0.25 * inch
    DY = -0.2 * inch

    def __init__(self, tournament):
        Flowable.__init__(self)
        self.tournament = tournament

    @staticmethod
    def _total_minutes(t):
        return t.hour * 60 + t.minute

    def draw(self):
        canvas = self.canv

        base_font = ('Helvetica', 10)
        bars_font = ('Helvetica', 8)

        y = self.CHART_Y0 + 0.4 * inch

        today = datetime.datetime.today()
        start_time, end_time = (datetime.datetime.combine(today, t) for t in self.tournament.get_planning_time_span())
        t0_min = self._total_minutes(start_time)
        dt = TeamPlanning.Match.SLOT_DURATION

        def _time_to_x(t):
            return (self._total_minutes(t) - t0_min) / 10 * self.DX + self.CHART_X0 - 0.05 * inch

        time = start_time

        all_teams = self.tournament.registered_teams
        teams_count = len(all_teams)

        y_max = self.CHART_Y0 + (teams_count - 1) * self.DY

        label_x_offset = 0.04 * inch
        bar_label_x_offset = 0.06 * inch
        bar_label_y_offset = 0.02 * inch

        canvas.setFont(*base_font)
        while time <= end_time:
            x = _time_to_x(time)

            canvas.saveState()
            canvas.rotate(90)
            canvas.drawCentredString(y, -x - label_x_offset, time.strftime('%H:%M'))
            canvas.restoreState()

            canvas.setStrokeColor(colors.silver)
            canvas.setDash(1, 2)

            canvas.line(x, self.CHART_Y0 - self.DY, x, y_max)

            time += dt

        x_max = x

        x = self.CHART_X0 - 0.1 * inch
        y = self.CHART_Y0

        match_colors = [
            colors.lightpink,
            colors.lightgreen,
            colors.lightblue
        ]
        presentation_color = colors.lightsalmon
        bar_width = -self.DY * 0.6

        for team in self.tournament.registered_teams:
            planning = team.planning

            canvas.setFillColor(colors.black)
            canvas.setFont(*base_font)
            canvas.drawRightString(x, y, "%d - %s" % (team.num, team.name))

            canvas.setStrokeColor(colors.silver)
            canvas.setDash(1, 2)
            y_line = y + bar_width / 2
            canvas.line(self.CHART_X0, y_line, x_max, y_line)

            canvas.setFont(*bars_font)
            for i, match in enumerate(planning.matches):
                bar_x = _time_to_x(match.time)
                canvas.setFillColor(match_colors[i])
                canvas.rect(bar_x, y, self.DX, bar_width, stroke=0, fill=1)
                canvas.setFillColor(colors.black)
                canvas.drawString(bar_x + bar_label_x_offset, y + bar_label_y_offset, "T%d" % match.table)

            bar_x = _time_to_x(planning.presentation.time)
            canvas.setFillColor(presentation_color)
            canvas.rect(bar_x, y, self.DX * 3, bar_width, stroke=0, fill=1)
            canvas.setFillColor(colors.black)
            canvas.drawString(bar_x + bar_label_x_offset, y + bar_label_y_offset, "J%d" % planning.presentation.jury)

            y += self.DY

        # draw the legend

        legend_x = self.CHART_X0 + 0.5 * inch
        legend_y = y + self.DY
        x_step = 2 * inch

        canvas.setFont(*base_font)

        x = legend_x
        sample_colors = match_colors + [presentation_color]
        labels = ["épreuve %d" % i for i in range(1, len(match_colors) + 1)] + ['présentation']

        for color, label in zip(sample_colors, labels):
            canvas.setFillColor(color)
            canvas.rect(x - self.DX - 0.1 * inch, legend_y - 0.02 * inch, self.DX, bar_width, stroke=0, fill=1)
            canvas.setFillColor(colors.black)
            canvas.drawString(x, legend_y, label)

            x += x_step

        canvas.drawString(
            legend_x, legend_y + 1.5 * self.DY,
            "(Tn/Jn : n = numéro de table ou de jury)"
        )


def generate_planning(tournament, doc=None):
    story = PageHeader(title="Planning des passages", page_size=doc.pagesize).get_story() + [PlanningFlowable(tournament)]

    return story


_generators = {
    'm': (generate_match_sheets, 'match sheets', 'match_sheets', portrait(A4)),
    'j': (generate_jury_sheets, 'jury sheets', 'jury_sheets', portrait(A4)),
    'a': (generate_approval_sheets, 'approval sheets', 'approval_sheets', portrait(A4)),
    't': (generate_time_tables, 'time tables', 'time_tables', portrait(A4)),
    's': (generate_stand_labels, 'stand labels', 'stand_labels', portrait(A4)),
    'p': (generate_planning, 'planning', 'planning', landscape(A4)),
}


class FormsDocTemplate(SimpleDocTemplate):
    # declare these attributes for Lint not to complain
    timestamp = text_x = text_y = pagesize = rightMargin = bottomMargin = None

    def handle_documentBegin(self):
        SimpleDocTemplate.handle_documentBegin(self)

        self.timestamp = datetime.datetime.now().strftime("Généré le %d/%m/%Y à %H:%M:%S")
        self.text_x = self.pagesize[0] - self.rightMargin / 2
        self.text_y = self.bottomMargin / 2

    def handle_pageEnd(self):
        canvas = self.canv
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(self.text_x, self.text_y, self.timestamp)

        SimpleDocTemplate.handle_pageEnd(self)


if __name__ == '__main__':
    from textwrap import dedent

    all_types = ''.join(_generators.keys())

    def doc_types(value):
        if value == '*':
            return all_types

        value = value.lower()
        if any(c not in all_types for c in value):
            raise argparse.ArgumentTypeError("invalid code used in document types list")
        return value

    def output_dir(value):
        path = os.path.abspath(os.path.join(SCRIPT_HOME, value))
        if os.path.exists(path) and not os.path.isdir(path):
            raise argparse.ArgumentTypeError('path exists and is not a directory (%s)' % path)
        return path

    parser = argparse.ArgumentParser(
        description=dedent("""
            Event forms and documents generator.

            Produces the PDF files for the various forms and documents personalized
            with the team information.

            Which documents are generated can be customized with the -g/--generate options.
            Its value is either '*' meaning 'all' or a case insensitive string of
            one letter codes representing the document types.

            Available documents are (document code given in parenthesis):
                - (m) individual match sheets for score accounting
                - (j) individual jury sheets for the presentation evaluations
                - (a) individual approval sheets
                - (t) individual time tables
        """),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-d', '--data',
                        help='teams data file\n(default: "%(default)s")',
                        type=file,
                        default='teams.csv')
    parser.add_argument('-o', '--output_dir',
                        help='output directory, created if not found\n(default: "%(default)s")',
                        type=output_dir,
                        default='./output')
    parser.add_argument('-g', '--generate',
                        dest='doctypes',
                        help='specify which documents are to be generated\n(default: "%(default)s")',
                        type=doc_types,
                        default=all_types)
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    print('using data from : %s' % os.path.abspath(args.data.name))

    _tournament = Tournament()
    _tournament.initialize_with_teams_data(team_fp=args.data)

    print('generating documents in : %s' % args.output_dir)
    for code in _generators.keys():
        if code in args.doctypes:
            func, label, pdf_name, page_size = _generators[code]

            pdf_file_name = pdf_name + '.pdf'
            pdf_doc = FormsDocTemplate(
                filename=os.path.join(args.output_dir, pdf_file_name),
                pagesize=page_size,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch
            )
            print('- %s : %s' % (label, pdf_file_name))
            doc_story = func(_tournament, doc=pdf_doc)
            pdf_doc.build(doc_story)
