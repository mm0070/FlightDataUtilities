import os
import sys

from webbrowser import BackgroundBrowser, UnixBrowser, register, _iscommand

__all__ = ['register_additional_browsers']

class Chrome(UnixBrowser):
    '''
    Launcher class for Google Chrome browser.
    '''
    remote_args = ['%action', '%s']
    remote_action = ''
    remote_action_newwin = '--new-window'
    remote_action_newtab = ''
    background = True
    

Chromium = Chrome

def _register_xdg_open():
    '''
    Opens a URL or file in the user's preferred browser or application
    '''
    if _iscommand('xdg-open'):
        register('xdg-open', None, BackgroundBrowser('xdg-open'))

def _register_gvfs_open():
    '''
    GVFS is the virtual file system for the GNOME desktop
    gvfs-open opens a file in the using the appropriate applicatioin when
    the user is using the GNOME desktop
    '''
    if 'GNOME_DESKTOP_SESSION_ID' in os.environ and _iscommand('gvfs-open'):
        register('gvfs-open', None, BackgroundBrowser('gvfs-open'))
        
def _register_google_chrome():
    '''
    '''
    for browser in ('google-chrome', 'chrome', 'chromium', 'chromium-browser'):
        if _iscommand(browser):
            register(browser, None, Chrome(browser))

def register_additional_browsers():
    '''
    '''
    if os.environ.get('DISPLAY') and sys.version_info[0:3] < (3, 3):
        _register_xdg_open()
        _register_gvfs_open()
        _register_google_chrome()
     
    