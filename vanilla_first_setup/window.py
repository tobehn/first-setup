# window.py
#
# Copyright 2022 mirkobrombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundationat version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
from gi.repository import Gtk, Gio, GLib, Adw

from vanilla_first_setup.models.preset import Preset
from vanilla_first_setup.models.config import Config
from vanilla_first_setup.utils.processor import Processor
from vanilla_first_setup.utils.run_async import RunAsync
from vanilla_first_setup.utils.welcome_langs import welcome


@Gtk.Template(resource_path='/pm/mirko/FirstSetup/gtk/window.ui')
class FirstSetupWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'FirstSetupWindow'

    carousel = Gtk.Template.Child()
    btn_start = Gtk.Template.Child()
    btn_save = Gtk.Template.Child()
    btn_close = Gtk.Template.Child()
    switch_snap = Gtk.Template.Child()
    switch_flatpak = Gtk.Template.Child()
    switch_apport = Gtk.Template.Child()
    switch_distrobox = Gtk.Template.Child()
    spinner = Gtk.Template.Child()
    status_welcome = Gtk.Template.Child()
    page_welcome = -1
    page_configuration = 0
    page_progress = 1
    page_done = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__config = Config(
            snap=Preset.snap,
            flatpak=Preset.flatpak,
            apport=Preset.apport,
            distrobox=Preset.distrobox
        )
        self.__buiild_ui()
        self.__connect_signals()
        self.__start_welcome_animation()

    def __buiild_ui(self):
        self.switch_snap.set_active(Preset.snap)
        self.switch_flatpak.set_active(Preset.flatpak)
        self.switch_apport.set_active(Preset.apport)
        self.switch_distrobox.set_active(Preset.distrobox)

    def __connect_signals(self):
        self.btn_start.connect('clicked', self.__on_btn_start_clicked)
        self.btn_save.connect('clicked', self.on_btn_save_clicked)
        self.btn_close.connect('clicked', self.on_btn_close_clicked)
        self.switch_snap.connect('state-set', self.__on_switch_snap_state_set)
        self.switch_flatpak.connect(
            'state-set', self.__on_switch_flatpak_state_set)
        self.switch_apport.connect(
            'state-set', self.__on_switch_apport_state_set)
        self.switch_distrobox.connect(
            'state-set', self.__on_switch_distrobox_state_set)

    def __show_page(self, page: int):
        _page = self.carousel.get_nth_page(page + 1)
        self.carousel.scroll_to(_page, True)

    def __on_btn_start_clicked(self, widget):
        self.__show_page(self.page_configuration)

    def on_btn_save_clicked(self, widget):
        def on_done(result, error=None):
            self.spinner.stop()
            self.__show_page(self.page_done)

        self.__show_page(self.page_progress)
        self.spinner.start()

        RunAsync(Processor(self.__config).run, on_done)

    def __on_switch_snap_state_set(self, widget, state):
        self.__config.snap = state

    def __on_switch_flatpak_state_set(self, widget, state):
        self.__config.flatpak = state

    def __on_switch_apport_state_set(self, widget, state):
        self.__config.apport = state

    def __on_switch_distrobox_state_set(self, widget, state):
        self.__config.distrobox = state

    def on_btn_close_clicked(self, widget):
        self.get_application().quit()

    def __start_welcome_animation(self):
        def change_langs():
            for lang in welcome:
                GLib.idle_add(self.status_welcome.set_title, lang )
                time.sleep(1.5)

        RunAsync(change_langs, None)