"""
Copyright (C) 2005 - 2010 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the
configuration page.

    handleList method: lists configurable parameters in the configuration page
    corresponds to handleractions = list in restmap.conf

    handleEdit method: controls the parameters and saves the values
    corresponds to handleractions = edit in restmap.conf
"""

import json
import splunk.clilib.cli_common as scc
import splunk.admin as admin


import splunktalib.common.util as utils
import splunktalib.common.log as log
from splunktalib.conf_manager import ta_conf_manager as ta_conf
from splunktalib.conf_manager import conf_manager as conf
import splunk_ta_paloalto_consts as c

logger = log.Logs().get_logger("setup")


class ConfigApp(admin.MConfigHandler):
    valid_args = ("all_settings",)

    stanza_map = {
        c.global_settings: False,
        c.myta_credential_settings: True,
        c.myta_customized_settings: True,
    }

    cred_fields = (c.password,)
    encrypt_fields_credential = (c.password,)
    encrypt_fields_customized = (c.password,)
    cred_confs = ((c.myta_credential_settings, c.myta_credential_conf),)

    def setup(self):
        """
        Set up supported arguments
        """
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in self.valid_args:
                self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        logger.info("start list")
        conf_mgr = conf.ConfManager(scc.getMgmtUri(), self.getSessionKey())
        conf_mgr.reload_conf(c.myta_conf)
        conf_mgr.reload_conf(c.myta_credential_conf)
        conf_mgr.reload_conf(c.myta_customized_conf)
        # read globala and proxy settings
        all_settings = conf_mgr.all_stanzas_as_dicts(c.myta_conf)
        if not all_settings:
            all_settings = {}
        self._setNoneValues(all_settings.get(c.global_settings, {}))
        # read account credential settings
        for cred, cred_conf in self.cred_confs:
            ta_conf_mgr = ta_conf.TAConfManager(
                cred_conf, scc.getMgmtUri(), self.getSessionKey())
            ta_conf_mgr.set_encrypt_keys(self.encrypt_fields_credential)
            creds = ta_conf_mgr.all(return_acl=False)
            if creds:
                self._setNoneValues(creds)
                all_settings.update({cred: creds})
        # read customized settings
        ta_conf_mgr = ta_conf.TAConfManager(
            c.myta_customized_conf, scc.getMgmtUri(), self.getSessionKey())
        ta_conf_mgr.set_encrypt_keys(self.encrypt_fields_customized)
        customized_settings = ta_conf_mgr.all(return_acl=False)
        all_settings.update({c.myta_customized_settings: customized_settings})
        self._clearPasswords(all_settings, self.cred_fields)
        all_settings = json.dumps(all_settings)
        all_settings = utils.escape_json_control_chars(all_settings)
        confInfo[c.myta_settings].append(c.all_settings, all_settings)
        logger.info("end list")

    def handleEdit(self, confInfo):
        logger.info("start edit")
        conf_mgr = conf.ConfManager(scc.getMgmtUri(), self.getSessionKey(),
                                    app_name=self.appName)
        conf_mgr.reload_conf(c.myta_conf)
        conf_mgr.reload_conf(c.myta_credential_conf)
        conf_mgr.reload_conf(c.myta_customized_conf)
        all_origin_settings = conf_mgr.all_stanzas_as_dicts(c.myta_conf)
        all_settings = utils.escape_json_control_chars(
            self.callerArgs.data[c.all_settings][0])
        all_settings = json.loads(all_settings)
        # write globala and proxy settings
        self._updateGlobalSettings(c.global_settings, all_settings,
                                   all_origin_settings, conf_mgr)
        # write account credential settings
        for cred, conf_file in self.cred_confs:
            creds = all_settings.get(cred, {})
            if creds == c.ignore_backend_req:
                logger.info("Ignore backend rest request")
                continue
            ta_conf_mgr = ta_conf.TAConfManager(
                conf_file, scc.getMgmtUri(), self.getSessionKey(),
                appname=self.appName)

            ta_conf_mgr.set_encrypt_keys(self.encrypt_fields_credential)
            self._updateCredentials(creds, ta_conf_mgr)

        # write customized settings
        customized_settings = all_settings.get(c.myta_customized_settings, {})
        ta_conf_mgr = ta_conf.TAConfManager(
            c.myta_customized_conf, scc.getMgmtUri(), self.getSessionKey(),
            appname=self.appName)

        ta_conf_mgr.set_encrypt_keys(self.encrypt_fields_customized)
        self._updateCredentials(customized_settings, ta_conf_mgr)
        conf_mgr.reload_conf(c.myta_conf)
        conf_mgr.reload_conf(c.myta_credential_conf)
        conf_mgr.reload_conf(c.myta_customized_conf)
        logger.info("end edit")

    def _updateGlobalSettings(self, stanza, all_settings,
                              all_origin_settings, conf_mgr):
        if not self.stanza_map[stanza]:
            return
        global_settings = all_settings.get(stanza, {})
        if self._configChanges(global_settings, all_origin_settings[stanza]):
            logger.info("%s stanza changed", stanza)
            conf_mgr.update_properties(c.myta_conf, stanza, global_settings)

    def _updateCredentials(self, all_creds, ta_conf_mgr):
        all_origin_creds = ta_conf_mgr.all(return_acl=False)
        if all_origin_creds is None:
            all_origin_creds = {}
        for name, settings in all_creds.iteritems():
            settings[c.name] = name
            if name not in all_origin_creds:
                logger.info("new %s stanza", name)
                ta_conf_mgr.create(settings)
            else:
                settings[c.removed] = 0
                if not self._configChanges(settings, all_origin_creds[name]):
                    logger.debug("%s stanza is not changed", name)
                    continue
                logger.info("%s stanza changes", name)
                ta_conf_mgr.update(settings)
        stanzas = [k for k, v in all_origin_creds.iteritems()
                   if k not in all_creds and utils.is_false(v.get(c.removed))]
        for stanza in stanzas:
            logger.info("Remove %s", stanza)
            ta_conf_mgr.update({c.name: stanza, c.removed: "1"})

    @staticmethod
    def _clearPasswords(settings, cred_fields):
        for k, val in settings.iteritems():
            if isinstance(val, dict):
                return ConfigApp._clearPasswords(val, cred_fields)
            elif isinstance(val, (str, unicode)):
                if k in cred_fields:
                    settings[k] = ""

    @staticmethod
    def _setNoneValues(stanza):
        for k, v in stanza.iteritems():
            if v is None:
                stanza[k] = ""

    @staticmethod
    def _configChanges(new_config, origin_config):
        for k, v in new_config.iteritems():
            if k in ConfigApp.cred_fields and v == "":
                continue
            if v != origin_config.get(k):
                return True
        return False


admin.init(ConfigApp, admin.CONTEXT_APP_ONLY)