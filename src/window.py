# window.py
#
# Copyright 2024 newton
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

gi.require_version("WebKit", "6.0")
from gi.repository import GLib, GObject, WebKit

import re as regex

@Gtk.Template(resource_path='/io/github/lo2dev/Zenith/window.ui')
class ZenithWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ZenithWindow'

    split_view = Gtk.Template.Child()

    tabview_frame = Gtk.Template.Child()
    tabview = Gtk.Template.Child()
    tablist = Gtk.Template.Child()

    url_bar = Gtk.Template.Child()
    button_forward = Gtk.Template.Child()
    button_back = Gtk.Template.Child()
    button_reload = Gtk.Template.Child()
    new_tab_button = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings(schema_id="io.github.lo2dev.Zenith")
        self.settings.bind("win-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("win-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)

        self.settings.connect("changed", self.on_update_round_webpages)
        self.on_update_round_webpages(_, _)


        self.tablist.set_model(self.tabview.get_pages())
        print(self.tablist.get_model())
        self.new_tab(_)

        self.new_tab_button.connect("clicked", self.new_tab)
        self.url_bar.connect("activate", self.on_entry_activate)

        self.button_forward.connect("clicked", lambda _: self.get_current_webview().go_forward())
        self.button_back.connect("clicked", lambda _: self.get_current_webview().go_back())
        self.button_reload.connect("clicked", lambda _: self.get_current_webview().reload())

        tablist_model = self.tablist.get_model()
        tablist_model.connect("selection-changed", self.on_tab_selection_change)
        tablist_model.connect("items-changed", self.switch_to_new_tab)




    def new_tab(self, _):
        webview = WebKit.WebView.new()
        webview.load_uri("https://start.duckduckgo.com")

        webview.connect("enter-fullscreen", self.on_enter_fullscreen)
        webview.connect("leave-fullscreen", self.on_leave_fullscreen)
        webview.connect("notify::estimated-load-progress", self.on_estimated_load_progress, webview)
        #webview.connect("load-failed", self.on_load_failed)
        webview.bind_property(
            "uri",
            self.url_bar.get_buffer(),
            "text",
            GObject.BindingFlags.DEFAULT,
        )

        tabview_page = self.tabview.add_page(webview)
        tabview_page.set_title("New Page")
        webview.connect("load-changed", self.on_load_changed, webview, tabview_page)

        self.url_bar.set_text("")


    def switch_to_new_tab(self, _, position, *args):
        self.tablist.get_model().select_item(position, True)


    def get_current_webview(self):
        return self.tabview.get_selected_page().get_child()


    def on_tab_selection_change(self, _position, _n_items, _user_data):
        self.url_bar.set_text( self.get_current_webview().get_uri() )


    def on_entry_activate(self, _entry):
        url = self.url_bar.get_buffer().get_text()
        scheme = GLib.Uri.peek_scheme(url)

        if not scheme:
            if regex.search(".\..", url):
                url= f"https://{url}"
            else:
                url = f"https://duck.com/?q={url}"

        self.get_current_webview().load_uri(url)


    def on_load_changed(self, _, load_event, webview, tabview_page):
        match load_event:
            case WebKit.LoadEvent.STARTED:
                # print("Page loading started")
                pass
            case WebKit.LoadEvent.FINISHED:
                # print("Page loading has finished")
                tabview_page.set_title(webview.get_title())


    def on_load_failed(self, _load_event, fail_url, error):
        # Loading failed as a result of calling stop_loading
        if error.matches(WebKit.NetworkError, WebKit.NetworkError.CANCELLED):
            return

        self.get_current_webview().load_alternate_html(
            self.error_page(fail_url, error.message),
            fail_url,
            None,
        )


    def error_page(self, fail_url, msg):
        error = f"""
            <div style="text-align:center margin:24px">
                <h2>An error occurred while loading {fail_url}</h2>
                <p>{msg}</p>
            </div>
            """
        return error


    def on_timeout(self):
        self.url_bar.set_progress_fraction(0)
        return False


    def on_estimated_load_progress(self, _widget, _load_progress, webview):
        self.url_bar.set_progress_fraction(webview.get_estimated_load_progress())
        if self.url_bar.get_progress_fraction() == 1:
            GLib.timeout_add(500, self.on_timeout)


    def on_enter_fullscreen(self, _):
        self.get_current_webview().get_parent().remove_css_class("webview-container-rounded")
        self.split_view.set_collapsed(True)


    def on_leave_fullscreen(self, _):
        self.get_current_webview().get_parent().add_css_class("webview-container-rounded")
        self.split_view.set_collapsed(False)


    def on_update_round_webpages(self, x, y):
        if self.settings.get_boolean("rounded-webpages"):
            self.tabview_frame.add_css_class("rounded-webpages")
        else:
            self.tabview_frame.remove_css_class("rounded-webpages")

