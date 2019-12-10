# -*- coding: utf-8 -*-

from sphinx_testing import with_app

import unittest

with_png_app = with_app(srcdir='tests/docs/rackdiag',
                        buildername='html',
                        write_docstring=True)
with_svg_app = with_app(srcdir='tests/docs/rackdiag',
                        buildername='html',
                        write_docstring=True,
                        confoverrides={
                            'rackdiag_html_image_format': 'SVG',
                        })


class TestSphinxcontribRackdiagHTML(unittest.TestCase):
    @with_png_app
    def test_build_png_image(self, app, status, warning):
        """
        .. rackdiag::

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><img .*? src="_images/.*?.png" .*?/></div>')

    @with_app(srcdir='tests/docs/rackdiag-subdir', buildername='html', write_docstring=True)
    def test_build_png_image_in_subdir(self, app, status, warning):
        """
        .. rackdiag::

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'subdir' / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><img .*? src="\.\./_images/.*?.png" .*?/></div>')

    @with_png_app
    def test_width_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :width: 128

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<img height="880.0" src="\1" width="128.0" /></a></div>'))

    @with_png_app
    def test_height_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :height: 880

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<img height="880.0" src="\1" width="128.0" /></a></div>'))

    @with_png_app
    def test_width_option_and_height_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :width: 100
           :height: 200

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<img height="200.0" src="\1" width="100.0" /></a></div>'))

    @with_png_app
    def test_scale_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :scale: 25%

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<img height="440.0" src="\1" width="64.0" /></a></div>'))

    @with_png_app
    def test_width_option_and_scale_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :width: 128
           :scale: 25%

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<img height="220.0" src="\1" width="32.0" /></a></div>'))

    @with_png_app
    def test_align_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :align: center

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div align="center" class="align-center"><img .*? /></div>')

    @with_png_app
    def test_align_option_and_width_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :align: center
           :width: 128

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div align="center" class="align-center">'
                                          r'<a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<img height="880.0" src="\1" width="128.0" /></a></div>'))

    @with_png_app
    def test_name_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :name: target

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><img .*? id="target" src=".*?" .*? /></div>')

    @with_png_app
    def test_name_option_and_width_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :name: target
           :width: 128

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<img height="880.0" id="target" src="\1" width="128.0" /></a></div>'))

    @with_png_app
    def test_href_and_scale_option_on_png(self, app, status, warning):
        """
        .. rackdiag::
           :scale: 50%

           * A [href = 'http://blockdiag.com/'];
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><a class="reference internal image-reference" href="(.*?.png)">'
                                          r'<map name="(map_\d+)">'
                                          r'<area shape="rect" coords="32.0,840.0,96.0,860.0" '
                                          r'href="http://blockdiag.com/"></map>'
                                          r'<img .*? src="\1" usemap="#\2" .*?/></a></div>'))

    @with_png_app
    def test_reftarget_in_href_on_png1(self, app, status, warning):
        """
        .. _target:

        heading2
        ---------

        .. rackdiag::

           * A [href = ':ref:`target`'];
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><map name="(map_\d+)">'
                                          r'<area shape="rect" coords="64.0,1680.0,192.0,1720.0" href="#target">'
                                          r'</map><img .*? src=".*?.png" usemap="#\1" .*?/></div>'))

    @with_png_app
    def test_reftarget_in_href_on_png2(self, app, status, warning):
        """
        .. _hello world:

        heading2
        ---------

        .. rackdiag::

           * A [href = ':ref:`hello world`'];
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<div><map name="(map_\d+)">'
                                          r'<area shape="rect" coords="64.0,1680.0,192.0,1720.0" href="#hello-world">'
                                          r'</map><img .*? src=".*?.png" usemap="#\1" .*?/></div>'))

    @with_png_app
    def test_missing_reftarget_in_href_on_png(self, app, status, warning):
        """
        .. rackdiag::

           * A [href = ':ref:`unknown_target`'];
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><img .*? src=".*?.png" .*?/></div>')
        self.assertIn('undefined label: unknown_target', warning.getvalue())

    @with_svg_app
    def test_build_svg_image(self, app, status, warning):
        """
        .. rackdiag::

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><svg .*?>')

    @with_svg_app
    def test_width_option_on_svg(self, app, status, warning):
        """
        .. rackdiag::
           :width: 128

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><svg height="880.0" viewBox="0 0 256 1760" width="128.0" .*?>')

    @with_svg_app
    def test_height_option_on_svg(self, app, status, warning):
        """
        .. rackdiag::
           :height: 880

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><svg height="880.0" viewBox="0 0 256 1760" width="128.0" .*?>')

    @with_svg_app
    def test_width_option_and_height_option_on_svg(self, app, status, warning):
        """
        .. rackdiag::
           :width: 100
           :height: 200

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><svg height="200.0" viewBox="0 0 256 1760" width="100.0" .*?>')

    @with_svg_app
    def test_scale_option_on_svg(self, app, status, warning):
        """
        .. rackdiag::
           :scale: 25%

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><svg height="440.0" viewBox="0 0 256 1760" width="64.0" .*?>')

    @with_svg_app
    def test_width_option_and_scale_option_on_svg(self, app, status, warning):
        """
        .. rackdiag::
           :width: 128
           :scale: 25%

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><svg height="220.0" viewBox="0 0 256 1760" width="32.0" .*?>')

    @with_svg_app
    def test_align_option_on_svg(self, app, status, warning):
        """
        .. rackdiag::
           :align: center

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div align="center" class="align-center"><svg .*?>')

    @with_svg_app
    def test_name_option_on_svg(self, app, status, warning):
        """
        .. rackdiag::
           :name: target

           * A
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, r'<div><span id="target"></span><svg .*?>')

    @with_svg_app
    def test_reftarget_in_href_on_svg1(self, app, status, warning):
        """
        .. _target:

        heading2
        ---------

        .. rackdiag::

           * A [href = ':ref:`target`'];
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<a xlink:href="#target">\n\s*<rect .*?>\n'
                                          r'\s*<text .*?>A</text>\n\s*</a>'))

    @with_svg_app
    def test_reftarget_in_href_on_svg2(self, app, status, warning):
        """
        .. _hello world:

        heading2
        ---------

        .. rackdiag::

           * A [href = ':ref:`hello world`'];
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertRegexpMatches(source, (r'<a xlink:href="#hello-world">\n\s*<rect .*?>\n'
                                          r'\s*<text .*?>A</text>\n\s*</a>'))

    @with_svg_app
    def test_missing_reftarget_in_href_on_svg(self, app, status, warning):
        """
        .. rackdiag::

           * A [href = ':ref:`unknown_target`'];
           * B
        """
        app.builder.build_all()
        source = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.assertNotRegex(source, r'<a xlink:href="#hello-world">\n\s*<rect .*?>\n\s*</a>')
        self.assertIn('undefined label: unknown_target', warning.getvalue())

    @with_svg_app
    def test_attribute_plugin_should_not_effect_to_other_diagram(self, app, status, warning):
        """
        This testcase checks that attribute plugin is unloaded correctly (and it does not effect to other diagram).

        .. rackdiag::

           plugin attributes [property];
           * A_foo [property = foo]

        .. rackdiag::

           * A_foo [property = foo]
        """
        app.builder.build_all()
        self.assertIn('Unknown attribute: RackItem.property', warning.getvalue())
