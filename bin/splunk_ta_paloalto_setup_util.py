import json
import splunk.clilib.cli_common as scc
import splunk.admin as admin

import splunktalib.common.util as utils
from splunktalib.conf_manager import ta_conf_manager as ta_conf
from splunktalib.conf_manager import conf_manager as conf
import splunk_ta_paloalto_consts as c


'''
Usage Examples:
setup_util = Setup_Util(uri, session_key)
setup_util.get_log_level()
setup_util.get_credential_account("my_account_name")
setup_util.get_customized_setting("my_customized_field_name")
'''

class Setup_Util(object):

    def __init__(self, uri, session_key):
        self.__uri = uri
        self.__session_key = session_key
        self.encrypt_fields_credential = (c.password,)
        self.encrypt_fields_customized = (c.password,)
        self.cred_confs = ((c.myta_credential_settings, c.myta_credential_conf),)

    def _parse_conf(self):
        conf_mgr = conf.ConfManager(self.__uri, self.__session_key)
        conf_mgr.set_appname("Splunk_TA_paloalto")
        conf_mgr.reload_conf(c.myta_conf)
        conf_mgr.reload_conf(c.myta_credential_conf)
        conf_mgr.reload_conf(c.myta_customized_conf)
        # read global and proxy settings
        all_settings = conf_mgr.all_stanzas_as_dicts(c.myta_conf)
        if not all_settings:
            all_settings = {}
        self._setNoneValues(all_settings.get(c.global_settings, {}))
        # read account credential settings
        for cred, cred_conf in self.cred_confs:
            ta_conf_mgr = ta_conf.TAConfManager(
                cred_conf, self.__uri, self.__session_key, "Splunk_TA_paloalto")
            ta_conf_mgr.set_encrypt_keys(self.encrypt_fields_credential)
            creds = ta_conf_mgr.all(return_acl=False)
            self._setNoneValues(creds)
            all_settings.update({cred: creds})
        # read customized settings
        ta_conf_mgr = ta_conf.TAConfManager(
            c.myta_customized_conf, self.__uri, self.__session_key, "Splunk_TA_paloalto")
        ta_conf_mgr.set_encrypt_keys(self.encrypt_fields_customized)
        customized_settings = ta_conf_mgr.all(return_acl=False)
        for stanza_name, stanza_content in customized_settings.iteritems():
            self._setNoneValues(stanza_content)
        all_settings.update({c.myta_customized_settings: customized_settings})
        return all_settings

    @staticmethod
    def _setNoneValues(stanza):
        for k, v in stanza.iteritems():
            if v is None:
                stanza[k] = ""

    def get_log_level(self):
        global_settings = self._parse_conf().get('global_settings', None)
        if not global_settings:
            raise Exception("Log level is not set")
        log_level = global_settings.get('log_level', None)
        if not log_level:
            raise Exception("Log level is not set")
        return log_level


    def get_credential_account(self, key):
        credential_settings = self._parse_conf().get('credential_settings', None)
        if not credential_settings:
            raise Exception("Credential account is not set")
        if not key in credential_settings:
            raise Exception("Credential key can not be found")
        credential_account = credential_settings.get(key, {})
        credential_account = {
            "username": key,
            "password": credential_account.get("password", "")
        }
        return credential_account

    def get_customized_setting(self, key):
        customized_settings = self._parse_conf().get('customized_settings', None)
        if not customized_settings:
            raise Exception("Customized setting is not set")
        if not key in customized_settings:
            raise Exception("Customized key can not be found")
        customized_setting = customized_settings.get(key, {})
        _type = customized_setting.get("type", None)
        if not _type:
            raise Exception("Type of this customized setting is not set")
        if _type == "bool":
            return {'0':False,'1':True}[customized_setting.get("bool", '0')]
        elif _type == "text":
            return customized_setting.get("content", "")
        elif _type == "password":
            return customized_setting.get("password", "")
        else:
            raise Exception("Type of this customized setting is corrupted")