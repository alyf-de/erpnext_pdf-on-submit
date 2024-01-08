# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "pdf_on_submit"
app_title = "PDF on Submit"
app_publisher = "Raffael Meyer"
app_description = "Generatation, Sales Order, Sales Invoice and Delivery Note"
app_icon = "octicon octicon-file-pdf"
app_color = "#DB2B39"
app_email = "raffael@alyf.de"
app_license = "GPLv3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pdf_on_submit/css/pdf_on_submit.css"
# app_include_js = "/assets/pdf_on_submit/js/pdf_on_submit.js"

# include js, css files in header of web template
# web_include_css = "/assets/pdf_on_submit/css/pdf_on_submit.css"
# web_include_js = "/assets/pdf_on_submit/js/pdf_on_submit.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "pdf_on_submit.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pdf_on_submit.install.before_install"
# after_install = "pdf_on_submit.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pdf_on_submit.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {"on_submit": "pdf_on_submit.attach_pdf.attach_pdf"}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pdf_on_submit.tasks.all"
# 	],
# 	"daily": [
# 		"pdf_on_submit.tasks.daily"
# 	],
# 	"hourly": [
# 		"pdf_on_submit.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pdf_on_submit.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pdf_on_submit.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "pdf_on_submit.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pdf_on_submit.event.get_events"
# }
