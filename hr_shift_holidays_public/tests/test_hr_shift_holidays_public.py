# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, time

import pytz

from odoo import fields
from odoo.tools import mute_logger

from odoo.addons.hr_shift.tests.common import TestHrShiftBase


class TestHrShiftHolidaysPublic(TestHrShiftBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.planning = cls.env["hr.shift.planning"].create(
            {
                "year": 2025,
                "week_number": 3,
                "start_date": "2025-01-13",
                "end_date": "2025-01-19",
            }
        )
        cls.holidays_public = cls.env["hr.holidays.public"].create(
            {
                "year": 2025,
                "line_ids": [(0, 0, {"date": "2025-01-14", "name": "Test line"})],
            }
        )

    # def test_hr_shift_planning_holiday_public(self):
    #     self.planning.generate_shifts()
    #     shift_a = self.planning.shift_ids.filtered(
    #         lambda x: x.employee_id == self.employee_a
    #     )
    #     shift_a_line_0 = shift_a.line_ids.filtered(lambda x: x.day_number == "0")
    #     self.assertEqual(shift_a_line_0.state, "unassigned")
    #     shift_a_line_1 = shift_a.line_ids.filtered(lambda x: x.day_number == "1")
    #     self.assertEqual(shift_a_line_1.state, "holiday")

    @mute_logger("odoo.models.unlink")
    def test_misc(self):
        # holiday_type = self.env["hr.leave.type"].create(
        #     {"name": "Leave Type Test", "exclude_public_holidays": True}
        # )
        # leave = self.env["hr.leave"].create({
        #     "holiday_status_id": holiday_type.id,
        #     "date_from": "2025-01-13",
        #     "date_to": "2025-01-13",
        #     "employee_id": self.employee_a.id,
        #     "state": "draft",
        # })
        # leave.action_confirm()
        self.holidays_public.unlink()
        self.planning.generate_shifts()
        self.planning.shift_ids.template_id = self.template_morning
        shifts = self.planning.shift_ids.filtered(
            lambda x: x.employee_id == self.employee_a
        )
        date = fields.Date.from_string("2025-01-13")
        shifts_line = shifts.line_ids.filtered(lambda x: x.start_date == date)
        shifts_line.start_time = "2025-01-12 23:00:00"
        shifts_line.end_time = "2025-01-13 07:00:00"
        print(
            {
                "shifts_line": shifts_line,
            }
        )
        (self.planning.shift_ids.line_ids - shifts_line).unlink()
        calendar = self.employee_a.resource_calendar_id
        calendar.tz = "Europe/Madrid"
        self.employee_a.resource_id.tz = calendar.tz
        calendar.attendance_ids.filtered(lambda x: x.dayofweek != "1").unlink()
        print(
            {
                "calendar": calendar,
                "calendar.attendance_ids": calendar.attendance_ids,
                "calendar.attendance_ids.dayofweek": calendar.attendance_ids.mapped(
                    "dayofweek"
                ),
            }
        )
        tz = self.employee_a.resource_id.calendar_id.tz
        date = fields.Date.from_string("2025-01-13")
        date_from = datetime.combine(date, time.min, tzinfo=pytz.timezone(tz))
        date_to = datetime.combine(date, time.max, tzinfo=pytz.timezone(tz))
        # print('ANTES-_get_resources_day_total')
        # day_total = calendar.with_context(exclude_public_holidays=True)._get_resources_day_total(date_from, date_to, self.employee_a.resource_id)
        # # day_total = calendar._get_resources_day_total(date_from, date_to, self.employee_a.resource_id)
        # print('DESPUES-_get_resources_day_total')
        # print({
        #     'day_total': day_total,
        # })
        # # extra
        report = self.env["hr.attendance.theoretical.time.report"]
        print("ANTES-_theoretical_hours")
        res = report._theoretical_hours(self.employee_a, date)
        print("DESPUES-_theoretical_hours")
        print(
            {
                "res": res,
            }
        )
