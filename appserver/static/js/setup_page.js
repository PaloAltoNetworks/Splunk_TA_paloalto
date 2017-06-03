function return_page() {
    return '<div class="entityEditForm"><div class="formWrapper">' +
                '<div class="fieldsetWrapper" id="credSettingId">' +
                    '<fieldset>' +
                        '<legend>PAN Device Credentials</legend>' +
                        '<p>These are the credentials that will be used to communicate with your Palo Alto Networks Firewall or Panorama.</p>' +
                        '<div>' +
                            '<a class="color-gray mgr-16 credBtn btn" id="passwordBtnAdd">Add Account</a>' +
                        '</div>' +
                        '<br>' +
                        '<br>' +
                        '<div>' +
                            '<table id="passwordCredTable" class="table mg-10" style="display: table;">' +
                                '<thead class="tableHead">' +
                                    '<tr>' +
                                    '</tr>' +
                                '</thead>' +
                                '<tbody class="tableBody">' +
                                '</tbody>' +
                            '</table>' +
                        '</div>' +
                    '</fieldset>' +
                '</div>' +
                '<div class="fieldsetWrapper" id="wildfire_SettingId">' +
                    '<fieldset>' +
                        '<legend>WildFire Cloud API Key</legend>' +
                        '<p class="helpText"> Used to retrieve reports from the WildFire Cloud.  An API Key is available from the WildFire Portal (<a href="https://wildfire.paloaltonetworks.com" target="_blank">https://wildfire.paloaltonetworks.com</a>).</p>' +
                        '<div class="widget" style="display: block;">' +
                            '<label>WildFire API Key</label>' +
                            '<div>' +
                                '<input class="index_input" type="password" id="wildfire_api_key_id" autocomplete="off" />' +
                            '</div>' +
                            '<div class="widgeterror" style="display: none;">' +
                            '</div>' +
                        '</div>' +
                    '</fieldset>' +
                '</div>' +
                '<div class="fieldsetWrapper" id="AF_SettingId">' +
                    '<fieldset>' +
                        '<legend>AutoFocus API Key</legend>' +
                        '<p class="helpText"> Used to retrieve reports from the AutoFocus Cloud. (<a href="https://www.paloaltonetworks.com/documentation/autofocus/autofocus/autofocus_api/get-started-with-the-autofocus-api/get-your-api-key#36712" target="_blank">Get Your API Key</a>).</p>' +
                        '<div class="widget" style="display: block;">' +
                            '<label>AutoFocus API Key</label>' +
                            '<div>' +
                                '<input class="index_input" type="password" id="autofocus_api_key_id" autocomplete="off" />' +
                            '</div>' +
                            '<div class="widgeterror" style="display: none;">' +
                            '</div>' +
                        '</div>' +
                    '</fieldset>' +
                '</div>' +
                '<div class="shadow">' +
                '</div>' +
            '</div> <!-- end of form_wrapper-->' +
            '<div class="dialog passwordCredDialog">' +
                '<div id="passwordCredDialog" class="dialog-header color-gray pd-16">' +
                    'Add Account' +
                '</div>' +
                '<div class="dialog-content pd-16">' +
                    '<form autocomplete="off" id="passwordCredForm" class="credform">' +
                    '</form>' +
                '</div>' +
            '</div>' +
            '<div class="jmFormActions" style="">' +
                    '<button class="my-btn-secondary" type="button"><span>Cancel</span></button>' +
                    '<button type="submit" class="my-btn-primary"><span>Save</span></button>' +
            '</div>' +
        '</div></div>';
}

function return_cred_form() {
        return '<div class="dialog">' +
            '<div class="dialog-header pd-16">' +
                'Add New Credentials' +
            '</div>' +
            '<div class="dialog-content pd-16">' +
                '<form autocomplete="off" id="form">' +
                '</form>' +
            '</div>' +
        '</div>';
}
