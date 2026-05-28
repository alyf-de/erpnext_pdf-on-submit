import copy

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


LIST_TAGS = {"ol", "ul"}


def split_quill(html: str) -> list[str]:
	"""Split a Text Editor HTML string into printable HTML fragments.

	Top-level Quill blocks are returned separately so print formats can render them
	as individual table rows. Lists are split further by item because wkhtmltopdf
	handles page breaks between table rows more reliably than page breaks inside
	long table cells."""
	soup = BeautifulSoup(html, "html.parser")
	nested_divs = soup.find_all("div", recursive=False)

	if len(nested_divs) != 1:
		# If the content is not wrapped in a single div, return the original HTML
		return [html]

	div = nested_divs[0]
	fragments = _split_children(div)

	if _is_quill_editor(div):
		return [_wrap_in_editor(div, fragment) for fragment in fragments]

	return fragments


def _split_children(parent: Tag) -> list[str]:
	fragments = []

	for child in parent.children:
		if _is_blank_text(child):
			continue

		if isinstance(child, Tag) and child.name in LIST_TAGS:
			fragments.extend(_split_list(child))
		else:
			fragments.append(str(child))

	return fragments


def _split_list(list_tag: Tag) -> list[str]:
	list_items = [child for child in list_tag.children if isinstance(child, Tag) and child.name == "li"]
	if not list_items:
		return [str(list_tag)]

	fragments = []
	ordered_counters = [0] * 10

	for item in list_items:
		fragment = _new_tag_like(list_tag)

		if _is_ordered_list_item(list_tag, item):
			indent = _get_quill_indent(item)
			ordered_counters[indent] += 1
			ordered_counters[indent + 1 :] = [0] * (len(ordered_counters) - indent - 1)
			_set_ordered_list_start(fragment, indent, ordered_counters[indent])

		fragment.append(BeautifulSoup(str(item), "html.parser").find("li"))
		fragments.append(str(fragment))

	return fragments


def _is_quill_editor(tag: Tag) -> bool:
	return "ql-editor" in tag.get("class", [])


def _is_blank_text(element: Tag | NavigableString) -> bool:
	return isinstance(element, NavigableString) and not element.strip()


def _new_tag_like(tag: Tag) -> Tag:
	soup = BeautifulSoup("", "html.parser")
	new_tag = soup.new_tag(tag.name)
	new_tag.attrs = copy.deepcopy(tag.attrs)
	return new_tag


def _wrap_in_editor(editor_tag: Tag, fragment: str) -> str:
	soup = BeautifulSoup("", "html.parser")
	editor = soup.new_tag("div")
	editor.attrs = copy.deepcopy(editor_tag.attrs)
	fragment_soup = BeautifulSoup(fragment, "html.parser")

	for child in list(fragment_soup.contents):
		editor.append(child)

	return str(editor)


def _is_ordered_list_item(list_tag: Tag, item: Tag) -> bool:
	data_list = item.get("data-list")
	if data_list:
		return data_list == "ordered"

	return list_tag.name == "ol"


def _get_quill_indent(item: Tag) -> int:
	for class_name in item.get("class", []):
		if class_name.startswith("ql-indent-"):
			return int(class_name.removeprefix("ql-indent-"))

	return 0


def _set_ordered_list_start(list_tag: Tag, indent: int, number: int) -> None:
	if indent == 0 and list_tag.name == "ol":
		list_tag["start"] = str(number)

	style = list_tag.get("style", "").rstrip()
	counter_reset = f"counter-reset: list-{indent} {number - 1};"
	list_tag["style"] = f"{style.rstrip(';')}; {counter_reset}" if style else counter_reset
