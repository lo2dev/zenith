# window.py
#
# Copyright 2024 Lo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gi
from gi.repository import Adw, Gtk, Gio

@Gtk.Template(resource_path='/io/github/lo2dev/Zenith/preferences.ui')
class ZenithPreferencesDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'ZenithPreferencesDialog'

    # split_view = Gtk.Template.Child()
    rounded_webpages_row = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        settings = Gio.Settings(schema_id="io.github.lo2dev.Zenith")
        settings.bind("rounded-webpages", self.rounded_webpages_row, "active", Gio.SettingsBindFlags.DEFAULT)


