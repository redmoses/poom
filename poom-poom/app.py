#!/usr/bin/env python

import ConfigParser
import sys
import os
from dropbox.client import DropboxOAuth2FlowNoRedirect, DropboxClient
from dropbox import rest as dbrest


def load_config(root_dir):
    global config
    config = ConfigParser.ConfigParser()
    config.read(root_dir + '/settings.ini')


def save_token():
    try:
        config_file = open('settings.ini', 'w')
        config.set("Auth", "access_token", access_token)
        config.write(config_file)
        config_file.close()
    except IOError, e:
        print "Error: %s" % e


def try_again():
    answer = raw_input("Do you want to try again? (y/n): ").strip()
    if answer == 'y':
        connect()
    else:
        quit(0)


def connect():
    global access_token, user_id
    app_key = config.get("Auth", "app_key")
    app_secret = config.get("Auth", "app_secret")
    access_token = config.get("Auth", "access_token")

    if access_token == '':
        auth_flow = DropboxOAuth2FlowNoRedirect(app_key, app_secret)

        authorize_url = auth_flow.start()
        print "1. Go to: " + authorize_url
        print "2. Click \"Allow\" (you might have to log in first)."
        print "3. Copy the authorization code."
        auth_code = raw_input("Enter the authorization code here: ").strip()
        try:
            access_token, user_id = auth_flow.finish(auth_code)
        except dbrest.ErrorResponse, e:
            print("Error: %s" % (e,))
            try_again()
        finally:
            save_token()
    else:
        try:
            dc = DropboxClient(access_token).account_info()
        except dbrest.ErrorResponse, e:
            print("Error: %s" % (e,))
            access_token = ''
            save_token()
            try_again()


def upload_file(file_path):
    dc = DropboxClient(access_token)
    try:
        f = open(file_path, 'rb')
        file_name = os.path.basename(file_path)
        dc.put_file(file_name, f)
        f.close()
    except IOError:
        print "Error: can\'t find file or read data"
    except dbrest.ErrorResponse, e:
        print ("Error: %s" % (e,))


def open_file_in_ms_office(file_path):
    office_url = config.get("General", "office_url")
    upload_file(file_path)
    url = office_url + os.path.basename(file_path)
    url_open_cmd = 'xdg-open \"%s\" > /dev/null 2>&1 &' % (url)
    os.system(url_open_cmd)


if __name__ == '__main__':
    load_config(os.path.dirname(sys.argv[0]))
    connect()
    file = sys.argv[1]
    if file != '':
        open_file_in_ms_office(file)