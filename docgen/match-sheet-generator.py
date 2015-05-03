#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'

import argparse
import csv

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak, Image, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import *


default_table_style = [
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 12),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ('TOPPADDING', (0, 0), (-1, -1), 0.15 * inch),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0.15 * inch),
]

cell_bkgnd_color = colors.Color(0.9, 0.9, 0.9)

tables_spacer = Spacer(0, 0.2 * inch)

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

logo_left = Image('logo_left.png', width=0.84 * inch, height=0.79 * inch)
logo_right = Image('logo_right.png', width=0.95 * inch, height=0.79 * inch)


def make_header(title):
    return [
        Table(
            [
                [logo_left, 'POBOT Junior Cup 2015', logo_right],
                ['', title, '']
            ],
            colWidths=[1.15 * inch, 4.41 * inch, 1.15 * inch],
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


def make_team_header(number, name, school):
    return [
        Paragraph("%s - %s" % (number, name), team_name_style),
        Paragraph(school, team_school_style),
        Spacer(0, 0.5 * inch)
    ]


def generate_match_sheets(data_fp):
    doc = SimpleDocTemplate(
        filename='match_sheets.pdf'
    )
    page_header = make_header('Feuille de match')
    story = []

    data_fp.seek(0)
    rdr = csv.DictReader(data_fp)
    for record in rdr:
        story.extend(page_header)
        story.extend(make_team_header(record["Number"], record["Name"], record["School"]))

        for i, match_name in enumerate(('vitesse', 'confort')):
            story.append(Table(
                [
                    ["Epreuve %d : %s" % (i + 1, match_name)],
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
                ["Epreuve 3 : transport de passagers"],
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

        story.append(PageBreak())

    doc.build(story)


def generate_jury_sheets(data_fp):
    doc = SimpleDocTemplate(
        filename='jury_sheets.pdf'
    )
    page_header = make_header('Dossier de recherche')
    story = []

    cell_header = ParagraphStyle(
        'cell_header',
        fontName='Helvetica-Bold',
        fontSize=12
    )
    cell_body = ParagraphStyle(
        'cell_header',
        fontName='Helvetica',
        fontSize=12
    )

    data_fp.seek(0)
    rdr = csv.DictReader(data_fp)
    for record in rdr:
        story.extend(page_header)
        story.extend(make_team_header(record["Number"], record["Name"], record["School"]))

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
                ['Points évalués', '', Paragraph('<para align=center><b>Note</b> (sur 20)</para>', style=cell_body)],
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
                [Paragraph("<para align=right><b>Total des points</b> (sur 80)</para>", style=cell_body), '']
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

        story.append(PageBreak())

    doc.build(story)


def generate_approval_sheets(data_fp):
    doc = SimpleDocTemplate(
        filename='approval_sheets.pdf'
    )
    page_header = make_header("Fiche d'homologation")
    story = []

    cell_header = ParagraphStyle(
        'cell_header',
        fontName='Helvetica-Bold',
        fontSize=12
    )
    cell_body = ParagraphStyle(
        'cell_header',
        fontName='Helvetica',
        fontSize=12
    )

    data_fp.seek(0)
    rdr = csv.DictReader(data_fp)
    for record in rdr:
        story.extend(page_header)
        story.extend(make_team_header(record["Number"], record["Name"], record["School"]))

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
                    "<para>Aucun moyen de solidification du robot n'est utilisé dans la construction<br/>"
                    "<i>(vis, colle, autocollants, adhésif,...)</i></para>",
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

        story.append(PageBreak())

    doc.build(story)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Match sheets generator")

    parser.add_argument('-d', '--data',
                        help='teams data file',
                        type=file,
                        default='teams.csv')
    args = parser.parse_args()

    print('generating match sheets...')
    generate_match_sheets(args.data)

    print('generating jury sheets...')
    generate_jury_sheets(args.data)

    print('generating approval sheets...')
    generate_approval_sheets(args.data)