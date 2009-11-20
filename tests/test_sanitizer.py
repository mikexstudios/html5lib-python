import os,sys,unittest
from support import simplejson, html5lib_test_files

from html5lib import html5parser, sanitizer, constants, treebuilders, treewalkers, serializer

class SanitizeTest(unittest.TestCase):
  def addTest(cls, name, expected, input, strip=False):
    def test(self, expected=expected, input=input):
        expected = simplejson.loads(simplejson.dumps(expected))
        self.assertEqual(expected, self.sanitize_html(input, strip=strip))
    setattr(cls, name, test)
  addTest = classmethod(addTest)

  def sanitize_html2(self,stream):
    return ''.join([token.toxml() for token in
       html5parser.HTMLParser(tokenizer=sanitizer.HTMLSanitizer).
           parseFragment(stream).childNodes])

  def sanitize_html(self, data, encoding=None, strip=False):
    
    def sanitizer_factory(*args, **kwargs):
      san = sanitizer.HTMLSanitizer(*args, **kwargs)
      san.strip_tokens = strip
      return san

    parser = html5parser.HTMLParser(tree=treebuilders.getTreeBuilder("dom"),
        tokenizer=sanitizer_factory)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(parser.parseFragment(data, encoding=encoding))
    slzr = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False,
        quote_attr_values=True, 
        use_trailing_solidus=True, space_before_trailing_solidus=False)
    return slzr.render(stream, encoding)

  def test_should_handle_astral_plane_characters(self):
    self.assertEqual(u"<p>\U0001d4b5 \U0001d538</p>",
      self.sanitize_html("<p>&#x1d4b5; &#x1d538;</p>"))
    self.assertEqual(u"<p>\U0001d4b5 \U0001d538</p>",
      self.sanitize_html("<p>&#x1d4b5; &#x1d538;</p>", strip=True))

for tag_name in sanitizer.HTMLSanitizer.allowed_elements:
    if tag_name in ['caption', 'col', 'colgroup', 'optgroup', 'option', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr']: continue ### TODO
    if tag_name != tag_name.lower(): continue ### TODO
    if tag_name == 'image':
        SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
          "<img title=\"1\"/>foo &lt;bad&gt;bar&lt;/bad&gt; baz",
          "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name))
        SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
          "<img title=\"1\"/>foo bar baz",
          "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name), 
          strip=True)
    elif tag_name == 'br':
        SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
          "<br title=\"1\"/>foo &lt;bad&gt;bar&lt;/bad&gt; baz<br/>",
          "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name))
        SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
          "<br title=\"1\"/>foo bar baz<br/>",
          "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name),
          strip=True)
    elif tag_name in constants.voidElements:
        SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
          "<%s title=\"1\"/>foo &lt;bad&gt;bar&lt;/bad&gt; baz" % tag_name,
          "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name))
        SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
          "<%s title=\"1\"/>foo bar baz" % tag_name,
          "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name),
          strip=True)
    else:
        SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
          "<%s title=\"1\">foo &lt;bad&gt;bar&lt;/bad&gt; baz</%s>" % (tag_name,tag_name),
          "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name))
        # textarea and title are treated differently
        if tag_name in ["textarea", "title"]:
          SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
            "<%s title=\"1\">foo &lt;bad&gt;bar&lt;/bad&gt; baz</%s>" % (tag_name,tag_name),
            "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name),
            strip=True)
        else:
          SanitizeTest.addTest("test_should_allow_%s_tag" % tag_name,
            "<%s title=\"1\">foo bar baz</%s>" % (tag_name,tag_name),
            "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name),
            strip=True)

for tag_name in sanitizer.HTMLSanitizer.allowed_elements:
    tag_name = tag_name.upper()
    SanitizeTest.addTest("test_should_forbid_%s_tag" % tag_name,
      "&lt;%s title=\"1\"&gt;foo &lt;bad&gt;bar&lt;/bad&gt; baz&lt;/%s&gt;" % (tag_name,tag_name),
      "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name))
    SanitizeTest.addTest("test_should_forbid_%s_tag" % tag_name, "foo bar baz", 
      "<%s title='1'>foo <bad>bar</bad> baz</%s>" % (tag_name,tag_name), strip=True)

for attribute_name in sanitizer.HTMLSanitizer.allowed_attributes:
    if attribute_name != attribute_name.lower(): continue ### TODO
    if attribute_name == 'style': continue
    SanitizeTest.addTest("test_should_allow_%s_attribute" % attribute_name,
      "<p %s=\"foo\">foo &lt;bad&gt;bar&lt;/bad&gt; baz</p>" % attribute_name,
      "<p %s='foo'>foo <bad>bar</bad> baz</p>" % attribute_name)
    SanitizeTest.addTest("test_should_allow_%s_attribute" % attribute_name,
      "<p %s=\"foo\">foo bar baz</p>" % attribute_name,
      "<p %s='foo'>foo <bad>bar</bad> baz</p>" % attribute_name, strip=True)

for attribute_name in sanitizer.HTMLSanitizer.allowed_attributes:
    attribute_name = attribute_name.upper()
    SanitizeTest.addTest("test_should_forbid_%s_attribute" % attribute_name,
      "<p>foo &lt;bad&gt;bar&lt;/bad&gt; baz</p>",
      "<p %s='display: none;'>foo <bad>bar</bad> baz</p>" % attribute_name)
    SanitizeTest.addTest("test_should_forbid_%s_attribute" % attribute_name,
      "<p>foo bar baz</p>",
      "<p %s='display: none;'>foo <bad>bar</bad> baz</p>" % attribute_name,
      strip=True)

for protocol in sanitizer.HTMLSanitizer.allowed_protocols:
    SanitizeTest.addTest("test_should_allow_%s_uris" % protocol,
      "<a href=\"%s\">foo</a>" % protocol,
      """<a href="%s">foo</a>""" % protocol)
    SanitizeTest.addTest("test_should_allow_%s_uris" % protocol,
      "<a href=\"%s\">foo</a>" % protocol,
      """<a href="%s">foo</a>""" % protocol, strip=True)

for protocol in sanitizer.HTMLSanitizer.allowed_protocols:
    SanitizeTest.addTest("test_should_allow_uppercase_%s_uris" % protocol,
      "<a href=\"%s\">foo</a>" % protocol,
      """<a href="%s">foo</a>""" % protocol)
    SanitizeTest.addTest("test_should_allow_uppercase_%s_uris" % protocol,
      "<a href=\"%s\">foo</a>" % protocol,
      """<a href="%s">foo</a>""" % protocol, strip=True)

def buildTestSuite():
    for filename in html5lib_test_files("sanitizer"):
        for test in simplejson.load(file(filename)):
          SanitizeTest.addTest('test_' + test['name'], test['output'], test['input'])
        for test in simplejson.load(file(filename)):
          SanitizeTest.addTest('test_strip_' + test['name'], test['stripped'],
            test['input'], strip=True)

    return unittest.TestLoader().loadTestsFromTestCase(SanitizeTest)

def main():
    buildTestSuite()
    unittest.main()

if __name__ == "__main__":
    main()
