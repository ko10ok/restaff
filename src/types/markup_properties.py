from collections import namedtuple
from typing import NamedTuple, Any

PageProperties = namedtuple('Page', ['width', 'height'])


class StaffProperties(NamedTuple):
    left_offset: Any
    right_offset: Any
    top_offset: Any
    staff_line_offset: Any
    staff_line_count: Any
    staff_offset: Any
    staff_count: Any
    parts_offset: Any

    @property
    def staff_height(self):
        return self.staff_line_offset * (self.staff_line_count - 1)

    @property
    def parts_height(self):
        return self.staff_height * self.staff_count + self.staff_offset * (self.staff_count - 1)

    def parts_count_per_page(self, page: PageProperties):
        return int((page.height - self.top_offset) // (self.parts_height + self.parts_offset))
