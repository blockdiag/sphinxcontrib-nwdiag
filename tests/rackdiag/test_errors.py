# -*- coding: utf-8 -*-

from mock import patch
from sphinx_testing import with_app

import sys
import unittest


class TestSphinxcontribRackdiagErrors(unittest.TestCase):
    @with_app(srcdir='tests/docs/rackdiag', write_docstring=True)
    def test_parse_error(self, app, status, warning):
        """
        .. rackdiag::

           {
             * A
             * B
        """
        app.builder.build_all()
        self.assertIn('got unexpected token:', warning.getvalue())

    @with_app(srcdir='tests/docs/rackdiag', confoverrides=dict(rackdiag_html_image_format='JPG'))
    def test_unknown_format_error(self, app, status, warning):
        app.builder.build_all()
        self.assertIn('unknown format: JPG', warning.getvalue())

    @with_app(srcdir='tests/docs/rackdiag', confoverrides=dict(rackdiag_html_image_format='PDF'))
    def test_reportlab_not_found_error(self, app, status, warning):
        try:
            # unload reportlab and make loading it impossible
            sys.modules.pop('reportlab', None)
            path = sys.path
            sys.path = []

            app.builder.build_all()
            self.assertIn('Could not output PDF format. Install reportlab.',
                          warning.getvalue())
        finally:
            sys.path = path

    @with_app(srcdir='tests/docs/rackdiag')
    @patch("rackdiag.utils.rst.nodes.rackdiag.processor.drawer.DiagramDraw")
    def test_rendering_error(self, app, status, warning, DiagramDraw):
        DiagramDraw.side_effect = RuntimeError("UNKNOWN ERROR!")
        app.builder.build_all()
        self.assertIn('UNKNOWN ERROR!', warning.getvalue())

    @with_app(srcdir='tests/docs/rackdiag')
    @patch("sphinxcontrib.rackdiag.rackdiag.drawer.DiagramDraw.draw")
    def test_font_settings_error(self, app, status, warning, draw):
        draw.side_effect = UnicodeEncodeError("", "", 0, 0, "")
        app.builder.build_all()
        self.assertIn('UnicodeEncodeError caught (check your font settings)',
                      warning.getvalue())
