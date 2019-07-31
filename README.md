## PDF on Submit

Generate a PDF on submit of Quotation, Sales Order, Sales Invoice or Delivery Note.
All can be turned off via `PDF on Submit Settings`.

![](screencast.gif)

### Install

```bash
cd frappe-bench
bench get-app https://github.com/alyf-de/pdf_on_submit.git
bench --site erp.my-company.com install-app pdf_on_submit
```

(Replace `erp.my-company.com` with your site name.)

For some reason, the `on_submit` trigger still runs before submission is complete. That's why there will be **DRAFT** printed on your documents. If you do not want this, got to Print Settings and uncheck `Always add "Draft" Heading for printing draft documents`.

#### License

Copyright (C) 2019  Raffael Meyer <raffael@alyf.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
