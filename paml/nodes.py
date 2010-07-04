            
import cgi

class Base(object):
    
    def __init__(self):
        self.children = []
    
    def render_start(self, engine):
        return None
    
    def render_content(self, engine):
        return []
    
    def render_end(self, engine):
        return None
    
    def __repr__(self):
        return '<%s at 0x%x>' % (self.__class__.__name__, id(self))


class Document(Base):
    
    def render_start(self, engine):
        return engine.start_document()


class Content(Base):
    
    def __init__(self, content):
        super(Content, self).__init__()
        self.content = content
    
    def render_start(self, engine):
        return self.content
    
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.content)


class Expression(Content):
    
    def render_start(self, engine):
        return '${%s}' % self.content.strip()


class Tag(Base):
    
    self_closing = set('''
        br
        img
        input
    '''.strip().split())
    
    def __init__(self, name, id, class_, kwargs_expr=None):
        super(Tag, self).__init__()
        
        self.name = (name or 'div').lower()
        self.id = id
        self.class_ = (class_ or '').replace('.', ' ').strip()
        self.kwargs_expr = kwargs_expr
    
    def render_start(self, engine):
        
        const_attrs = {}
        if self.id:
            const_attrs['id'] = self.id
        if self.class_:
            const_attrs['class'] = self.class_
        
        if not self.kwargs_expr:
            attr_str = ''.join(' %s="%s"' % (k, cgi.escape(v)) for k, v in const_attrs.items())
        elif not const_attrs:
            attr_str = '<%% __M_writer(__H_attrs(%s)) %%>' % self.kwargs_expr
        else:
            attr_str = '<%% __M_writer(__H_attrs(%r, %s)) %%>' % (const_attrs, self.kwargs_expr)
            
        if self.name in self.self_closing:
            return '<%s%s />' % (self.name, attr_str)
        else:
            return '<%s%s>' % (self.name, attr_str)
    
    def render_end(self, engine):
        if self.name not in self.self_closing:
            return '</%s>' % self.name
    
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
            ', '.join('%s=%r' % (k, getattr(self, k)) for k in ('name', 'id', 'class_', 'kwargs_expr') if getattr(self, k))
        )


class Comment(Base):
    
    def render_start(self, engine):
        return '<!--'
    
    def render_end(self, engine):
        return '-->'
    
    def __repr__(self):
        return '%s()' % self.__class__.__name__


class Control(Base):
    
    def __init__(self, type, test):
        super(Control, self).__init__()
        self.type = type
        self.test = test
    
    def render_start(self, engine):
        return '%% %s %s: ' % (self.type, self.test)
    
    def render_end(self, engine):
        return '%% end%s' % self.type
    
    def __repr__(self):
        return '%s(type=%r, test=%r)' % (
            self.__class__.__name__,
            self.type,
            self.test
        )
    
