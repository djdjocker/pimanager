# -*- coding: utf-8 -*-
import manager
import os
import re

from bottle import request
from lxml import etree

def escape(s):
    """Replace special characters "&", "<", ">" and (") to HTML-safe sequences.
    There is a special handling for `None` which escapes to an empty string.
    .. versionchanged:: 0.9
       `quote` is now implicitly on.
    :param s: the string to escape.
    :param quote: ignored.
    """
    if s is None:
        return ''
    
    s = s.replace('&', '&amp;').replace('<', '&lt;') \
        .replace('>', '&gt;').replace('"', "&quot;")
        
    return s


def unescape(s):
    """The reverse function of `escape`.  This unescapes all the HTML
    entities, not only the XML entities inserted by `escape`.
    :param s: the string to unescape.
    """
    def handle_match(m):
        name = m.group(1)
        if name in HTMLBuilder._entities:
            return unichr(HTMLBuilder._entities[name])
        try:
            if name[:2] in ('#x', '#X'):
                return unichr(int(name[2:], 16))
            elif name.startswith('#'):
                return unichr(int(name[1:]))
        except ValueError:
            pass
        return u''
    return _entity_re.sub(handle_match, s)

class Template(object):
    _default_css = [("", "lib/bootstrap/css/bootstrap.css"),
                    ("", "src/css/base.css"),
                    ("", "src/css/glyphicons.css"),
                    ]#[ ("", "src/css/main.css")]
    
    _default_js = [("", "lib/jquery/jquery-3.1.1.js"),
                   ("", "lib/jquery/jquery.cookie.js"),
                   ("", "lib/bootstrap/js/bootstrap.js")
                   ]
    _void_elements = frozenset([
        u'area', u'base', u'br', u'col', u'embed', u'hr', u'img', u'input',
        u'keygen', u'link', u'menuitem', u'meta', u'param', u'source',
        u'track', u'wbr'])
    
    _format_regex = re.compile(
        '(?:'
            # ruby-style pattern
            '#\{(.+?)\}'
        ')|(?:'
            # jinja-style pattern
            '\{\{(.+?)\}\}'
        ')')

    def __init__(self, template=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'base.tpl'), content="", css=[], js=[], title="PiManager", template_content=False, extra=[]):
        if template:
            try:
                with open(template) as tfile:
                    content = tfile.read()
                    self._template = etree.HTML(content)
            except :
                self._template = etree.HTML("""
                <html>
                    <head />
                    <body>
                        <content>
                    </body>
                </html>""")
                
        self._content = content
        self._css = self._default_css + css
        self._js = self._default_js + js
        self._title = title
        self._template_content = template_content
        self._extras = extra
    
    def __repr__(self):
        return self.render()
        
    def __str__(self):
        return self.render()
        
    def __iter__(self):
        return self.render()
        
    def render(self, element=None, generated_attributes=''):
        if element is None:
            element = self._template
            
        result = ""
        
        if hasattr(element, 'docinfo'):
            for info in 'doctype', 'externalDTD' :
                i = getattr(element.docinfo, info)
                if i:
                    result += """%s
""" % i
            element = element.getroot()
        
        if isinstance(result, unicode):
            result = result.encode('utf-8')
        
        if 't-if' in element.attrib:
            if not bool(eval(element.attrib['t-if'].encode("utf8"))):
                return element.tail and self.render_tail(element.tail, element) or ''
            del element.attrib['t-if']
                
        t_render = None
        template_attributes = {}
        
        for (attribute_name, attribute_value) in element.attrib.iteritems():
            attribute_name = unicode(attribute_name)
            attribute_value = attribute_value.encode("utf8")

            if attribute_name.startswith("t-"):
                if attribute_name[2:].startswith('att'):
                    generated_attributes += self.render_attribute(element, attribute_name[6:], eval(attribute_value))
                        
                else:
                    if hasattr(self, "render_tag_%s" % attribute_name[2:]):
                        t_render = getattr(self, "render_tag_%s" % attribute_name[2:])
                    template_attributes[attribute_name[2:]] = attribute_value
            else:
                generated_attributes += self.render_attribute(element, attribute_name, attribute_value)

        if t_render:
            result += t_render(self, element, template_attributes, generated_attributes)
        else:
            result += self.render_element(element, template_attributes, generated_attributes)

        if element.tail:
            result += self.render_tail(element.tail, element)

        if isinstance(result, unicode):
            return result.encode('utf-8')
        
        return result
        
    def render_element(self, element, template_attributes, generated_attributes, inner=None):
        # element: element
        # template_attributes: t-* attributes
        # generated_attributes: generated attributes
        # inner: optional innerXml
        name = unicode(element.tag)

        if inner:
            g_inner = inner.encode('utf-8') if isinstance(inner, unicode) else inner
        else:
            g_inner = [] if element.text is None else [self.render_text(element.text, element)]
            for current_node in element.iterchildren(tag=etree.Element):
                g_inner.append(self.render(current_node, generated_attributes= name == "t" and generated_attributes or ''))
                    
        inner = "".join(g_inner)
        trim = template_attributes.get("trim", 0)
        
        if trim == 0:
            pass
        elif trim == 'left':
            inner = inner.lstrip()
        elif trim == 'right':
            inner = inner.rstrip()
        elif trim == 'both':
            inner = inner.strip()
        
        if name == "t":
            return inner
        
        elif name == 'title':
            return """<title>%s</title>
""" % self._title

        elif name == "css":
            result = ""
            for css in self._css:
                if isinstance(css, (str, unicode)):
                    path = css
                else:
                    module, css = css
                    path = "/static/" + (module and "%s"%module or "") + css
                result += """<link rel="stylesheet" type="text/css" href="%s" />
""" % path
            return result

        elif name == "js":
            result = ""
            for js in self._js:
                if isinstance(js, (str, unicode)):
                    path = js
                else:
                    module, js = js
                    path = "/static/" + (module and "%s"%module or "") + js
                result += """<script src="%s" ></script>
""" % path
            return result

        elif name == "content":
            if self._template_content:
                return Template(template=self._template_content, content=self._content).render()
            else:
                return self._content
                
        elif name == "extras":
            result = ""
            if self._extras:
                for extra in self._extras:
                    result += Template(template=extra[0], content=extra[1]).render()

            return result
        else:
            if len(inner) or name not in self._void_elements:
                result = "<%s%s>%s</%s>" % tuple(
                    v if isinstance(v, str) else v.encode('utf-8')
                    for v in (name, generated_attributes, inner, name)
                )
            else:
                result = "<%s%s/>" % (name.encode("utf-8"), generated_attributes)
                
            return result
            
    def render_text(self, text, element):
        return text.encode('utf-8')

    def render_tail(self, tail, element):
        return tail.encode('utf-8')

    def render_attribute(self, element, name, value):
        return self._build_attribute(name, value)

    def _build_attribute(self, name, value):
        value = escape(value)
        if isinstance(name, unicode): name = name.encode('utf-8')
        if isinstance(value, unicode): value = value.encode('utf-8')
        return ' %s="%s"' % (name, value)
