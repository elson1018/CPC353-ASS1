"""Render a report chart from current exports (optional ReportLab and Poppler)."""

import argparse
import csv
import shutil
import subprocess
from pathlib import Path


def render_chart(output_dir):
    from reportlab.graphics import renderPDF, renderSVG
    from reportlab.graphics.charts.barcharts import HorizontalBarChart
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.lib.colors import HexColor

    with (output_dir / 'switching_distribution.csv').open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    types = ['Intra-sentential', 'Inter-sentential', 'Tag Switching']
    origins = ['Self-Collected (Real)', 'AI-Generated (LLM)']
    data, sizes = [], []
    for origin in origins:
        subset = {r['SwitchingType']: r for r in rows if r['Group'] == origin}
        counts = [int(subset[t]['Count']) for t in types]
        denominators = {int(r['CodeSwitchedReviews']) for r in subset.values()}
        if len(denominators) != 1:
            raise ValueError('Inconsistent review denominator for ' + origin)
        size = denominators.pop()
        if size <= 0 or sum(counts) != size:
            raise ValueError('Chart requires nonempty groups with one recorded type per mixed review')
        sizes.append(size)
        data.append([count / size * 100 for count in counts])

    drawing = Drawing(250, 215)
    drawing.add(String(125, 200, 'Switching types by origin',
                       fontName='Helvetica-Bold', fontSize=11, textAnchor='middle'))
    drawing.add(String(125, 186, 'Code-switched reviews; existing primary labels',
                       fontName='Helvetica', fontSize=8, textAnchor='middle'))
    colors = [HexColor('#244C71'), HexColor('#408279')]
    chart = HorizontalBarChart()
    chart.x, chart.y, chart.width, chart.height = 80, 44, 154, 120
    chart.data = data
    chart.categoryAxis.categoryNames = types
    chart.categoryAxis.labels.fontName = 'Helvetica'
    chart.categoryAxis.labels.fontSize = 8
    chart.categoryAxis.labels.boxAnchor = 'e'
    chart.valueAxis.valueMin, chart.valueAxis.valueMax, chart.valueAxis.valueStep = 0, 100, 20
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontName = 'Helvetica'
    chart.valueAxis.labelTextFormat = '%d%%'
    chart.bars.strokeWidth = 0
    for i, color in enumerate(colors):
        chart.bars[i].fillColor = color
    chart.barWidth = 8
    chart.groupSpacing = 15
    chart.barLabelFormat = '%.1f%%'
    chart.barLabels.fontName = 'Helvetica'
    chart.barLabels.fontSize = 7
    chart.barLabels.boxAnchor = 'w'
    chart.barLabels.nudge = 3
    drawing.add(chart)
    for x, color, label in [(20, colors[0], f'Real-labelled ({sizes[0]})'),
                            (140, colors[1], f'AI ({sizes[1]})')]:
        drawing.add(Rect(x, 173, 9, 7, fillColor=color, strokeColor=None))
        drawing.add(String(x + 14, 173, label, fontName='Helvetica', fontSize=8))
    drawing.add(String(125, 17, 'Percent of each group; AI examples are seed-dependent.',
                       fontName='Helvetica', fontSize=8, textAnchor='middle'))
    base = output_dir / 'switching_by_origin'
    renderPDF.drawToFile(drawing, str(base.with_suffix('.pdf')))
    renderSVG.drawToFile(drawing, str(base.with_suffix('.svg')))
    converter = shutil.which('pdftoppm')
    if converter:
        subprocess.run([converter, '-r', '200', '-singlefile', '-png',
                        str(base.with_suffix('.pdf')), str(base)], check=True, capture_output=True)
    print('Chart saved as PDF/SVG' + ('/PNG.' if converter else '; install Poppler for PNG export.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent / 'outputs')
    args = parser.parse_args()
    render_chart(args.output_dir)
