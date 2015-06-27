# -*- coding: utf-8 -*-
"""
    packetdiag.sphinx_ext
    ~~~~~~~~~~~~~~~~~~~~~

    Allow packetdiag-formatted diagrams to be included in Sphinx-generated
    documents inline.

    :copyright: Copyright 2010 by Takeshi Komiya.
    :license: BSDL.
"""

from __future__ import absolute_import

import os
import re
import posixpath
import traceback
import pkg_resources
from collections import namedtuple
from docutils import nodes
from sphinx import addnodes
from sphinx.util.osutil import ensuredir

import packetdiag.utils.rst.nodes
import packetdiag.utils.rst.directives
from blockdiag.utils.bootstrap import detectfont, Application
from blockdiag.utils.compat import u, string_types
from blockdiag.utils.fontmap import FontMap
from blockdiag.utils.rst.directives import with_blockdiag

# fontconfig; it will be initialized on `builder-inited` event.
fontmap = None


class packetdiag_node(packetdiag.utils.rst.nodes.packetdiag):
    def to_drawer(self, image_format, builder, **kwargs):
        if 'filename' in kwargs:
            filename = kwargs.pop('filename')
        else:
            filename = self.get_abspath(image_format, builder)

        antialias = builder.config.packetdiag_antialias
        transparency = builder.config.packetdiag_transparency
        image = super(packetdiag_node, self).to_drawer(image_format, filename, fontmap,
                                                       antialias=antialias, transparency=transparency,
                                                       **kwargs)
        for node in image.diagram.traverse_nodes():
            node.href = resolve_reference(builder, node.href)

        return image

    def get_relpath(self, image_format, builder):
        options = dict(antialias=builder.config.packetdiag_antialias,
                       fontpath=builder.config.packetdiag_fontpath,
                       fontmap=builder.config.packetdiag_fontmap,
                       format=image_format,
                       transparency=builder.config.packetdiag_transparency)
        if hasattr(builder, 'imgpath'):  # Sphinx (<= 1.2.x) or HTML writer
            outputdir = builder.imgpath
        else:
            outputdir = ''
        return posixpath.join(outputdir, self.get_path(**options))

    def get_abspath(self, image_format, builder):
        options = dict(antialias=builder.config.packetdiag_antialias,
                       fontpath=builder.config.packetdiag_fontpath,
                       fontmap=builder.config.packetdiag_fontmap,
                       format=image_format,
                       transparency=builder.config.packetdiag_transparency)

        if hasattr(builder, 'imagedir'):  # Sphinx (>= 1.3.x)
            outputdir = os.path.join(builder.outdir, builder.imagedir)
        elif hasattr(builder, 'imgpath'):  # Sphinx (<= 1.2.x) and HTML writer
            outputdir = os.path.join(builder.outdir, '_images')
        else:
            outputdir = builder.outdir
        path = os.path.join(outputdir, self.get_path(**options))
        ensuredir(os.path.dirname(path))

        return path


class Packetdiag(packetdiag.utils.rst.directives.PacketdiagDirective):
    node_class = packetdiag_node

    def node2image(self, node, diagram):
        return node


def resolve_reference(builder, href):
    if href is None:
        return None

    pattern = re.compile(u("^:ref:`(.+?)`"), re.UNICODE)
    matched = pattern.search(href)
    if matched is None:
        return href
    elif not hasattr(builder, 'current_docname'):  # ex. latex builder
        return matched.group(1)
    else:
        refid = matched.group(1)
        domain = builder.env.domains['std']
        node = addnodes.pending_xref(refexplicit=False)
        xref = domain.resolve_xref(builder.env, builder.current_docname, builder,
                                   'ref', refid, node, node)
        if xref:
            if 'refid' in xref:
                return "#" + xref['refid']
            else:
                return xref['refuri']
        else:
            builder.warn('undefined label: %s' % refid)
            return None


def html_render_svg(self, node):
    image = node.to_drawer('SVG', self.builder, filename=None, nodoctype=True)
    image.draw()

    if 'align' in node['options']:
        align = node['options']['align']
        self.body.append('<div align="%s" class="align-%s">' % (align, align))
        self.context.append('</div>\n')
    else:
        self.body.append('<div>')
        self.context.append('</div>\n')

    # reftarget
    for node_id in node['ids']:
        self.body.append('<span id="%s"></span>' % node_id)

    # resize image
    size = image.pagesize().resize(**node['options'])
    self.body.append(image.save(size))
    self.context.append('')


def html_render_clickablemap(self, image, width_ratio, height_ratio):
    href_nodes = [node for node in image.nodes if node.href]
    if not href_nodes:
        return

    self.body.append('<map name="map_%d">' % id(image))
    for node in href_nodes:
        x1, y1, x2, y2 = image.metrics.cell(node)

        x1 *= width_ratio
        x2 *= width_ratio
        y1 *= height_ratio
        y2 *= height_ratio
        areatag = '<area shape="rect" coords="%s,%s,%s,%s" href="%s">' % (x1, y1, x2, y2, node.href)
        self.body.append(areatag)

    self.body.append('</map>')


def html_render_png(self, node):
    image = node.to_drawer('PNG', self.builder)
    if not os.path.isfile(image.filename):
        image.draw()
        image.save()

    # align
    if 'align' in node['options']:
        align = node['options']['align']
        self.body.append('<div align="%s" class="align-%s">' % (align, align))
        self.context.append('</div>\n')
    else:
        self.body.append('<div>')
        self.context.append('</div>')

    # link to original image
    relpath = node.get_relpath('PNG', self.builder)
    if 'width' in node['options'] or 'height' in node['options'] or 'scale' in node['options']:
        self.body.append('<a class="reference internal image-reference" href="%s">' % relpath)
        self.context.append('</a>')
    else:
        self.context.append('')

    # <img> tag
    original_size = image.pagesize()
    resized = original_size.resize(**node['options'])
    img_attr = dict(src=relpath,
                    width=resized.width,
                    height=resized.height)

    if any(node.href for node in image.nodes):
        img_attr['usemap'] = "#map_%d" % id(image)

        width_ratio = float(resized.width) / original_size.width
        height_ratio = float(resized.height) / original_size.height
        html_render_clickablemap(self, image, width_ratio, height_ratio)

    if 'alt' in node['options']:
        img_attr['alt'] = node['options']['alt']

    self.body.append(self.starttag(node, 'img', '', empty=True, **img_attr))


@with_blockdiag
def html_visit_packetdiag(self, node):
    try:
        image_format = get_image_format_for(self.builder)
        if image_format.upper() == 'SVG':
            html_render_svg(self, node)
        else:
            html_render_png(self, node)
    except UnicodeEncodeError:
        if self.builder.config.packetdiag_debug:
            traceback.print_exc()

        msg = ("packetdiag error: UnicodeEncodeError caught "
               "(check your font settings)")
        self.builder.warn(msg)
        raise nodes.SkipNode
    except Exception as exc:
        if self.builder.config.packetdiag_debug:
            traceback.print_exc()

        self.builder.warn('dot code %r: %s' % (node['code'], str(exc)))
        raise nodes.SkipNode


def html_depart_packetdiag(self, node):
    self.body.append(self.context.pop())
    self.body.append(self.context.pop())


def get_image_format_for(builder):
    if builder.format in ('html', 'slides'):
        image_format = builder.config.packetdiag_html_image_format.upper()
    elif builder.format == 'latex':
        if builder.config.packetdiag_tex_image_format:
            image_format = builder.config.packetdiag_tex_image_format.upper()
        else:
            image_format = builder.config.packetdiag_latex_image_format.upper()
    else:
        image_format = 'PNG'

    if image_format.upper() not in ('PNG', 'PDF', 'SVG'):
        raise ValueError('unknown format: %s' % image_format)

    if image_format.upper() == 'PDF':
        try:
            import reportlab  # NOQA: importing test
        except ImportError:
            raise ImportError('Could not output PDF format. Install reportlab.')

    return image_format


def on_builder_inited(self):
    # show deprecated message
    if self.builder.config.packetdiag_tex_image_format:
        self.builder.warn('packetdiag_tex_image_format is deprecated. Use packetdiag_latex_image_format.')

    # initialize fontmap
    global fontmap

    try:
        fontmappath = self.builder.config.packetdiag_fontmap
        fontmap = FontMap(fontmappath)
    except:
        fontmap = FontMap(None)

    try:
        fontpath = self.builder.config.packetdiag_fontpath
        if isinstance(fontpath, string_types):
            fontpath = [fontpath]

        if fontpath:
            config = namedtuple('Config', 'font')(fontpath)
            fontpath = detectfont(config)
            fontmap.set_default_font(fontpath)
    except:
        pass


def on_doctree_resolved(self, doctree, docname):
    if self.builder.format in ('html', 'slides'):
        return

    try:
        image_format = get_image_format_for(self.builder)
    except Exception as exc:
        if self.builder.config.packetdiag_debug:
            traceback.print_exc()

        self.builder.warn('packetdiag error: %s' % exc)
        for node in doctree.traverse(packetdiag_node):
            node.parent.remove(node)

        return

    for node in doctree.traverse(packetdiag_node):
        try:
            with Application():
                relfn = node.get_relpath(image_format, self.builder)
                image = node.to_drawer(image_format, self.builder)
                if not os.path.isfile(image.filename):
                    image.draw()
                    image.save()

                image = nodes.image(uri=relfn, candidates={'*': relfn}, **node['options'])
                node.parent.replace(node, image)
        except Exception as exc:
            if self.builder.config.packetdiag_debug:
                traceback.print_exc()

            self.builder.warn('dot code %r: %s' % (node['code'], str(exc)))
            node.parent.remove(node)


def setup(app):
    app.add_node(packetdiag_node,
                 html=(html_visit_packetdiag, html_depart_packetdiag))
    app.add_directive('packetdiag', Packetdiag)
    app.add_config_value('packetdiag_fontpath', None, 'html')
    app.add_config_value('packetdiag_fontmap', None, 'html')
    app.add_config_value('packetdiag_antialias', False, 'html')
    app.add_config_value('packetdiag_transparency', True, 'html')
    app.add_config_value('packetdiag_debug', False, 'html')
    app.add_config_value('packetdiag_html_image_format', 'PNG', 'html')
    app.add_config_value('packetdiag_tex_image_format', None, 'html')  # backward compatibility for 0.6.1
    app.add_config_value('packetdiag_latex_image_format', 'PNG', 'html')
    app.connect("builder-inited", on_builder_inited)
    app.connect("doctree-resolved", on_doctree_resolved)

    return {
        'version': pkg_resources.require('nwdiag')[0].version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
