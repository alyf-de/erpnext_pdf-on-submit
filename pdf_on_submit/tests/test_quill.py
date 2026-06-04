import unittest

from bs4 import BeautifulSoup

from pdf_on_submit.quill import split_quill


class TestSplitQuill(unittest.TestCase):
	def test_split_quill_splits_top_level_blocks(self):
		html = '<div class="ql-editor"><p>One</p><p>Two</p></div>'

		self.assertEqual(
			split_quill(html),
			[
				'<div class="ql-editor"><p>One</p></div>',
				'<div class="ql-editor"><p>Two</p></div>',
			],
		)

	def test_split_quill_splits_list_items(self):
		html = """<div class="ql-editor read-mode">
<ol>
<li data-list="bullet"><span class="ql-ui" contenteditable="false"></span>a</li>
<li data-list="bullet"><span class="ql-ui" contenteditable="false"></span>b</li>
</ol>
</div>"""

		self.assertEqual(
			split_quill(html),
			[
				'<div class="ql-editor read-mode"><ol><li data-list="bullet"><span class="ql-ui" contenteditable="false"></span>a</li></ol></div>',
				'<div class="ql-editor read-mode"><ol><li data-list="bullet"><span class="ql-ui" contenteditable="false"></span>b</li></ol></div>',
			],
		)

	def test_split_quill_preserves_ordered_list_numbers(self):
		html = """<div class="ql-editor">
<ol>
<li data-list="ordered"><span class="ql-ui" contenteditable="false"></span>one</li>
<li data-list="ordered"><span class="ql-ui" contenteditable="false"></span>two</li>
</ol>
</div>"""

		fragments = split_quill(html)
		second_list = BeautifulSoup(fragments[1], "html.parser").find("ol")

		self.assertEqual(second_list.get("start"), "2")
		self.assertEqual(second_list.get("style"), "counter-reset: list-0 1;")

	def test_split_quill_resets_nested_ordered_list_numbers(self):
		html = """<div class="ql-editor">
<ol>
<li data-list="ordered"><span class="ql-ui" contenteditable="false"></span>one</li>
<li class="ql-indent-1" data-list="ordered"><span class="ql-ui" contenteditable="false"></span>one-a</li>
<li class="ql-indent-1" data-list="ordered"><span class="ql-ui" contenteditable="false"></span>one-b</li>
<li data-list="ordered"><span class="ql-ui" contenteditable="false"></span>two</li>
<li class="ql-indent-1" data-list="ordered"><span class="ql-ui" contenteditable="false"></span>two-a</li>
</ol>
</div>"""

		fragments = split_quill(html)
		first_nested_list = BeautifulSoup(fragments[1], "html.parser").find("ol")
		second_nested_list = BeautifulSoup(fragments[2], "html.parser").find("ol")
		reset_nested_list = BeautifulSoup(fragments[4], "html.parser").find("ol")

		self.assertEqual(first_nested_list.get("style"), "counter-reset: list-1 0;")
		self.assertEqual(second_nested_list.get("style"), "counter-reset: list-1 1;")
		self.assertEqual(reset_nested_list.get("style"), "counter-reset: list-1 0;")
