# -*- coding: utf-8 -*-

import os
import re
from sphinx_testing import with_app

import unittest

CR = '\r?\n'

nwdiag_fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'
with_png_app = with_app(srcdir='tests/docs/nwdiag',
                        buildername='latex',
                        write_docstring=True,
                        confoverrides={
                            'latex_documents': [('index', 'test.tex', '', 'test', 'manual')],
                        })
with_pdf_app = with_app(srcdir='tests/docs/nwdiag',
                        buildername='latex',
                        write_docstring=True,
                        confoverrides={
                            'latex_documents': [('index', 'test.tex', '', 'test', 'manual')],
                            'nwdiag_latex_image_format': 'PDF',
                            'nwdiag_fontpath': nwdiag_fontpath,
                        })
with_oldpdf_app = with_app(srcdir='tests/docs/nwdiag',
                           buildername='latex',
                           write_docstring=True,
                           confoverrides={
                               'latex_documents': [('index', 'test.tex', '', 'test', 'manual')],
                               'nwdiag_tex_image_format': 'PDF',
                               'nwdiag_fontpath': nwdiag_fontpath,
                           })


class TestSphinxcontribNwdiagLatex(unittest.TestCase):
    @with_png_app
    def test_build_png_image(self, app, status, warning):
        """
        .. nwdiag::

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'\\sphinxincludegraphics{{nwdiag-.*?}.png}')

    @unittest.skipUnless(os.path.exists(nwdiag_fontpath), "TrueType font not found")
    @with_pdf_app
    def test_build_pdf_image1(self, app, status, warning):
        """
        .. nwdiag::

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'\\sphinxincludegraphics{{nwdiag-.*?}.pdf}')

    @unittest.skipUnless(os.path.exists(nwdiag_fontpath), "TrueType font not found")
    @with_oldpdf_app
    def test_build_pdf_image2(self, app, status, warning):
        """
        .. nwdiag::

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'\\includegraphics{{nwdiag-.*?}.pdf}')

    @with_png_app
    def test_width_option(self, app, status, warning):
        """
        .. nwdiag::
           :width: 3cm

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'\\sphinxincludegraphics\[width=3cm\]{{nwdiag-.*?}.png}')

    @with_png_app
    def test_height_option(self, app, status, warning):
        """
        .. nwdiag::
           :height: 4cm

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'\\sphinxincludegraphics\[height=4cm\]{{nwdiag-.*?}.png}')

    @with_png_app
    def test_scale_option(self, app, status, warning):
        """
        .. nwdiag::
           :scale: 50%

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'\\sphinxincludegraphics\[scale=0.5\]{{nwdiag-.*?}.png}')

    @with_png_app
    def test_align_option_left(self, app, status, warning):
        """
        .. nwdiag::
           :align: left

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'{\\sphinxincludegraphics{{nwdiag-.*?}.png}'
                                          r'\\hspace\*{\\fill}}'))

    @with_png_app
    def test_align_option_center(self, app, status, warning):
        """
        .. nwdiag::
           :align: center

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'{\\hspace\*{\\fill}'
                                          r'\\sphinxincludegraphics{{nwdiag-.*?}.png}'
                                          r'\\hspace\*{\\fill}}'))

    @with_png_app
    def test_align_option_right(self, app, status, warning):
        """
        .. nwdiag::
           :align: right

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'{\\hspace\*{\\fill}'
                                          r'\\sphinxincludegraphics{{nwdiag-.*?}.png}'))

    @with_png_app
    def test_caption_option(self, app, status, warning):
        """
        .. nwdiag::
           :caption: hello world

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')

        figure = re.compile((r'\\begin{figure}\[htbp\]' + CR +
                             r'\\centering' + CR +
                             r'\\capstart' + CR + CR +
                             r'\\noindent\\sphinxincludegraphics{{nwdiag-.*?}.png}' + CR +
                             r'\\caption{hello world}\\label{\\detokenize{index:id1}}\\end{figure}'),
                            re.DOTALL)
        self.assertRegexpMatches(source, figure)

    @with_png_app
    def test_caption_option_and_align_option(self, app, status, warning):
        """
        .. nwdiag::
           :align: left
           :caption: hello world

           network { A; B; }
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')

        figure = re.compile((r'\\begin{wrapfigure}{l}{0pt}' + CR +
                             r'\\centering' + CR +
                             r'\\noindent\\sphinxincludegraphics{{nwdiag-.*?}.png}' + CR +
                             r'\\caption{hello world}\\label{\\detokenize{index:id1}}\\end{wrapfigure}'),
                            re.DOTALL)
        self.assertRegexpMatches(source, figure)

    @with_png_app
    def test_href(self, app, status, warning):
        """
        .. nwdiag::

           network { A; B; }
           A [href = ':ref:`target`'];
        """
        app.builder.build_all()
        source = (app.outdir / 'test.tex').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'\\sphinxincludegraphics{{nwdiag-.*?}.png}')
