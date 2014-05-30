# -*- coding: utf-8 -*-
"""
    nwdiag.sphinx_ext
    ~~~~~~~~~~~~~~~~~~~~

    Allow nwdiag-formatted diagrams to be included in Sphinx-generated
    documents inline.

    :copyright: Copyright 2010 by Takeshi Komiya.
    :license: BSDL.
"""

import io
import os
import posixpath
import traceback
from collections import namedtuple
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

from docutils import nodes
from sphinx.errors import SphinxError
from sphinx.util.osutil import ensuredir

import nwdiag_sphinxhelper as nwdiag


class NwdiagError(SphinxError):
    category = 'Nwdiag error'


class Nwdiag(nwdiag.utils.rst.directives.NwdiagDirective):
    def run(self):
        try:
            return super(Nwdiag, self).run()
        except nwdiag.core.parser.ParseException as e:
            if self.content:
                msg = '[%s] ParseError: %s\n%s' % (self.name, e, "\n".join(self.content))
            else:
                msg = '[%s] ParseError: %s\n%r' % (self.name, e, self.arguments[0])

            reporter = self.state.document.reporter
            return [reporter.warning(msg, line=self.lineno)]

    def node2image(self, node, diagram):
        return node


def get_image_filename(self, code, format, options, prefix='nwdiag'):
    """
    Get path of output file.
    """
    if format.upper() not in ('PNG', 'PDF', 'SVG'):
        raise NwdiagError('nwdiag error:\nunknown format: %s\n' % format)

    if format.upper() == 'PDF':
        try:
            import reportlab
        except ImportError:
            msg = 'nwdiag error:\n' + \
                  'colud not output PDF format; Install reportlab\n'
            raise NwdiagError(msg)

    hashkey = (code + str(options)).encode('utf-8')
    fname = '%s-%s.%s' % (prefix, sha(hashkey).hexdigest(), format.lower())
    if hasattr(self.builder, 'imgpath'):
        # HTML
        relfn = posixpath.join(self.builder.imgpath, fname)
        outfn = os.path.join(self.builder.outdir, '_images', fname)
    else:
        # LaTeX
        relfn = fname
        outfn = os.path.join(self.builder.outdir, fname)

    if os.path.isfile(outfn):
        return relfn, outfn

    ensuredir(os.path.dirname(outfn))

    return relfn, outfn


def get_fontmap(self):
    FontMap = nwdiag.utils.fontmap.FontMap

    try:
        fontmappath = self.builder.config.nwdiag_fontmap
        fontmap = FontMap(fontmappath)
    except:
        attrname = '_nwdiag_fontmap_warned'
        if not hasattr(self.builder, attrname):
            msg = ('nwdiag cannot load "%s" as fontmap file, '
                   'check the nwdiag_fontmap setting' % fontmappath)
            self.builder.warn(msg)
            setattr(self.builder, attrname, True)

        fontmap = FontMap(None)

    try:
        fontpath = self.builder.config.nwdiag_fontpath
        if isinstance(fontpath, nwdiag.utils.compat.string_types):
            fontpath = [fontpath]

        if fontpath:
            config = namedtuple('Config', 'font')(fontpath)
            _fontpath = nwdiag.utils.bootstrap.detectfont(config)
            fontmap.set_default_font(_fontpath)
    except:
        attrname = '_nwdiag_fontpath_warned'
        if not hasattr(self.builder, attrname):
            msg = ('nwdiag cannot load "%s" as truetype font, '
                   'check the nwdiag_fontpath setting' % fontpath)
            self.builder.warn(msg)
            setattr(self.builder, attrname, True)

    return fontmap


def create_nwdiag(self, code, format, filename, options, prefix='nwdiag'):
    """
    Render nwdiag code into a PNG output file.
    """
    draw = None
    fontmap = get_fontmap(self)
    try:
        tree = nwdiag.core.parser.parse_string(code)
        diagram = nwdiag.core.builder.ScreenNodeBuilder.build(tree)

        antialias = self.builder.config.nwdiag_antialias
        draw = nwdiag.core.drawer.DiagramDraw(format, diagram, filename,
                                              fontmap=fontmap, antialias=antialias)
    except Exception as e:
        if self.builder.config.nwdiag_debug:
            traceback.print_exc()

        raise NwdiagError('nwdiag error:\n%s\n' % e)

    return draw


def make_svgtag(self, image, relfn, trelfn, outfn,
                alt, thumb_size, image_size):
    svgtag_format = """<svg xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    alt="%s" width="%s" height="%s">%s
    </svg>"""

    code = io.open(outfn, 'r', encoding='utf-8-sig').read()

    return (svgtag_format %
            (alt, image_size[0], image_size[1], code))


def make_imgtag(self, image, relfn, trelfn, outfn,
                alt, thumb_size, image_size):
    result = ""
    imgtag_format = '<img src="%s" alt="%s" width="%s" height="%s" />\n'

    if trelfn:
        result += ('<a href="%s">' % relfn)
        result += (imgtag_format %
                   (trelfn, alt, thumb_size[0], thumb_size[1]))
        result += ('</a>')
    else:
        result += (imgtag_format %
                   (relfn, alt, image_size[0], image_size[1]))

    return result


def render_dot_html(self, node, code, options, prefix='nwdiag',
                    imgcls=None, alt=None):
    trelfn = None
    thumb_size = None
    try:
        format = self.builder.config.nwdiag_html_image_format
        relfn, outfn = get_image_filename(self, code, format, options, prefix)

        image = create_nwdiag(self, code, format, outfn, options, prefix)
        if not os.path.isfile(outfn):
            image.draw()
            image.save()

        # generate thumbnails
        image_size = image.pagesize()
        if 'maxwidth' in options and options['maxwidth'] < image_size[0]:
            thumb_prefix = prefix + '_thumb'
            trelfn, toutfn = get_image_filename(self, code, format,
                                                options, thumb_prefix)

            ratio = float(options['maxwidth']) / image_size[0]
            thumb_size = (options['maxwidth'], image_size[1] * ratio)
            if not os.path.isfile(toutfn):
                image.filename = toutfn
                image.save(thumb_size)

    except UnicodeEncodeError:
        msg = ("nwdiag error: UnicodeEncodeError caught "
               "(check your font settings)")
        self.builder.warn(msg)
        raise nodes.SkipNode
    except NwdiagError as exc:
        self.builder.warn('dot code %r: ' % code + str(exc))
        raise nodes.SkipNode

    self.body.append(self.starttag(node, 'p', CLASS='nwdiag'))
    if relfn is None:
        self.body.append(self.encode(code))
    else:
        if alt is None:
            alt = node.get('alt', self.encode(code).strip())

        if format.upper() == 'SVG':
            tagfunc = make_svgtag
        else:
            tagfunc = make_imgtag

        self.body.append(tagfunc(self, image, relfn, trelfn, outfn, alt,
                                 thumb_size, image_size))

    self.body.append('</p>\n')
    raise nodes.SkipNode


def html_visit_nwdiag(self, node):
    render_dot_html(self, node, node['code'], node['options'])


def render_dot_latex(self, node, code, options, prefix='nwdiag'):
    try:
        format = self.builder.config.nwdiag_tex_image_format
        fname, outfn = get_image_filename(self, code, format, options, prefix)

        image = create_nwdiag(self, code, format, outfn, options, prefix)
        if not os.path.isfile(outfn):
            image.draw()
            image.save()

    except NwdiagError as exc:
        self.builder.warn('dot code %r: ' % code + str(exc))
        raise nodes.SkipNode

    if fname is not None:
        self.body.append('\\par\\includegraphics{%s}\\par' % fname)
    raise nodes.SkipNode


def latex_visit_nwdiag(self, node):
    render_dot_latex(self, node, node['code'], node['options'])


def on_doctree_resolved(self, doctree, docname):
    if self.builder.format in ('html', 'latex'):
        return

    for node in doctree.traverse(nwdiag.utils.rst.nodes.nwdiag):
        code = node['code']
        prefix = 'nwdiag'
        format = 'PNG'
        options = node['options']
        relfn, outfn = get_image_filename(self, code, format, options, prefix)

        image = create_nwdiag(self, code, format, outfn, options, prefix)
        if not os.path.isfile(outfn):
            image.draw()
            image.save()

        candidates = {'image/png': relfn}
        image = nodes.image(uri=outfn, candidates=candidates)
        node.parent.replace(node, image)


def setup(app):
    app.add_node(nwdiag.utils.rst.nodes.nwdiag,
                 html=(html_visit_nwdiag, None),
                 latex=(latex_visit_nwdiag, None))
    app.add_directive('nwdiag', Nwdiag)
    app.add_config_value('nwdiag_fontpath', None, 'html')
    app.add_config_value('nwdiag_fontmap', None, 'html')
    app.add_config_value('nwdiag_antialias', False, 'html')
    app.add_config_value('nwdiag_debug', False, 'html')
    app.add_config_value('nwdiag_html_image_format', 'PNG', 'html')
    app.add_config_value('nwdiag_tex_image_format', 'PNG', 'html')
    app.connect("doctree-resolved", on_doctree_resolved)
