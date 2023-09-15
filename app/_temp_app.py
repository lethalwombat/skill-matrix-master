import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback_context
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache
import datetime
from helpers_dash import (
    heading, input_text, input_email, input_number, 
    input_dropdown, small_button, medium_button, col, card_tab,
    mid_col
    )
from helpers_input import (
    dropdown_options, placeholders, patterns, valid_pattern, 
    default_values
    )
from helpers_params import update_bicep_params, clone_params, tmp_clean_up
from helpers_bicep import (
    bicep_build, params_build
    )
from helpers_doc import generate_doc

# app set-up
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], long_callback_manager=long_callback_manager)
app.title = 'eMAS template builder'
server = app.server

# top heading
top_heading = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Br(),
            heading('exposé MODERN ARCHITECTURE SUITE deployment template builder'),
        ], width=12)
    ])
], fluid=True)

# general inputs
inputs_general = mid_col([
    input_text('Organisation code', id='input_org', minlength=3, maxlength=3, placeholder=placeholders.get('organisation'), pattern=patterns.get('text_org_code')),
    input_text('Project', id='input_project', placeholder=placeholders.get('project')),
    input_dropdown('Zone type', id='input_zone', options=dropdown_options.get('input_zone')),
    html.Div([
        input_text('Zone name', id='input_zone_name', minlength=5, maxlength=10, placeholder=placeholders.get('zone'), pattern=patterns.get('text_alphanumeric')),
        input_dropdown('Environment', id='input_env', options=dropdown_options.get('environment'))        
    ], id='input_env_hide'),
    input_text('Subscription', id='input_subscription', minlength=36, maxlength=36, placeholder=placeholders.get('microsoft_id')),
    html.Div([
        input_dropdown('One sub for all?', id='input_same_dmz_sub', options=dropdown_options.get('generic_yes_no'))
    ], id='input_same_sub_dmz_hide'),
    html.Div([
        input_text('DMZ subscription', id='input_dmz_subscription', minlength=36, maxlength=36, placeholder=placeholders.get('microsoft_id'))
    ], id='input_dmz_sub_hide'),
    input_dropdown('Location', id='input_location', options=dropdown_options.get('input_location')),
    html.Div([
        input_dropdown('Deploy Purview', id='input_gov_enable', options=dropdown_options.get('generic_yes_no'))
    ], id='input_gov_enable_hide'),
    html.Div([
        input_dropdown('Purview public network', id='input_gov_public_net', options=dropdown_options.get('generic_enabled_disabled')),
        input_text('Purview admin tenant id', id='input_gov_admin_tenant_id', minlength=36, maxlength=36, placeholder=placeholders.get('microsoft_id')),
    ], id='inputs_purview_spec'),
    input_text('Released by', id='input_released_by', pattern=None, placeholder=placeholders.get('email')),
    input_text('Version', id='input_version', pattern=None, placeholder=placeholders.get('version')),
], 6)

# resource configuration
inputs_resources = mid_col([
    input_dropdown('Data Factory', id='input_df_enable', options=dropdown_options.get('generic_yes_no')),
    input_dropdown('Databricks', id='input_db_enable', options=dropdown_options.get('generic_yes_no')),
    input_dropdown('Event Hub (Streaming)', id='input_stream_enable', options=dropdown_options.get('generic_yes_no')),
    input_dropdown('Monitoring (Alerts)', id='input_monitor_enable', options=dropdown_options.get('generic_yes_no')),
    input_dropdown('Data Share', id='input_share_enable', options=dropdown_options.get('generic_yes_no')),
], 6)

# network inputs
inputs_network = mid_col([
    input_text('IP range', id='input_ip_range', minlength=7, maxlength=15, pattern=patterns.get('ip_address'), value=default_values.get('network')),
    input_dropdown('Network prefix', id='input_network_prefix', options=dropdown_options.get('input_network_prefix')),
    input_dropdown('Default subnet prefix', id='input_default_subnet', options=dropdown_options.get('input_default_subnet')),
], 6)

# storage inputs
inputs_storage = mid_col([
    input_text('Raw storage account name', id='input_storage_raw', value='raw1', pattern=patterns.get('text_alphanumeric')),
    input_text('Curated storage account name', id='input_storage_cur', value='cur1', pattern=patterns.get('text_alphanumeric')),    
    input_dropdown('Public network access', id='input_storage_public_net', options=dropdown_options.get('generic_enabled_disabled')),
    input_dropdown('Blob public access', id='input_blob_public', options=dropdown_options.get('generic_enabled_disabled')),
    input_dropdown('Storage sku', id='input_storage_sku', options=dropdown_options.get('input_storage_sku')),
    input_dropdown('Storage lock', id='input_storage_lock', options=dropdown_options.get('generic_enabled_disabled')),
    input_number('Storage retention days', id='input_storage_retention')
], 6)

# ingestion inputs
inputs_ingest = mid_col([
    input_dropdown('Public network access', id='input_ingest_public_net', options=dropdown_options.get('generic_enabled_disabled')),
    input_dropdown('Backup storage redundancy', id='input_ingest_backup', options=dropdown_options.get('input_backup')),
    input_text('SQL admin login', id='input_sql_login', pattern=None, placeholder=placeholders.get('email')),
    input_text('SQL admin sid', id='input_sql_sid', minlength=36, maxlength=36, placeholder=placeholders.get('microsoft_id')),
    input_text('SQL admin tenant id', id='input_sql_tenant', minlength=36, maxlength=36, placeholder=placeholders.get('microsoft_id')),
], 6)

# warehouse inputs
inputs_warehouse = mid_col([
    input_dropdown('Public network access', id='input_warehouse_public_net', options=dropdown_options.get('generic_enabled_disabled')),
    input_text('SQL admin login', id='input_sql_warehouse_login', pattern=patterns.get('text_alphanumeric'), placeholder=placeholders.get('login')),
    input_text('SQL admin password', id='input_sql_warehouse_password', pattern=None, value=placeholders.get('password')),
], 6)

# monitoring inputs
inputs_monitor = mid_col([
    input_text('Action group', id='input_alerts_action_group', value='AlertsGroup'),
    input_text('Email', id='input_alerts_email', pattern=None, placeholder=placeholders.get('email')),
], 6)

# output containers
output = html.Div([], id='container_output')

# controls
download_controls_left = html.Div([
    dbc.Stack([
        input_dropdown('Do you need documentation?', id='input_doc_enabled', options=dropdown_options.get('generic_yes_no')),
        html.Div([
            input_text('Client', id='doc_client', placeholder=placeholders.get('organisation_name'), pattern=None),
            input_text('Author', id='doc_author', placeholder=placeholders.get('doc_author'), pattern=None),
        ], id='doc_inputs_hide')
    ], gap=0)
])

download_controls_right = html.Div([
    dbc.Stack([
        dbc.Button("Deployment template", color="primary", className="me-1", id='download_template'),
        dbc.Button("Deployment parameters", color="primary", className="me-1", id='download_params'),
        dbc.Button("Documentation", color="primary", className="me-1", id='download_doc'),
        dcc.Download(id='download_template_trigger'),
        dcc.Download(id='download_params_trigger'), 
        output,
        html.Div([
            html.Progress(className='d-grid gap-1 col-6 mx-auto')], style={'display' : 'none'}, id='download_progress_bar')
    ], gap=1)
])

download_controls = dbc.Container([
    dbc.Row([
        dbc.Col([
            download_controls_left
        ], width={'size' : 4, 'offset' : 0}),
        dbc.Col([
            download_controls_right
        ], width={'size' : 4, 'offset' : 0})
    ], justify='evenly')
], fluid=True)

# application layout
app.layout = dbc.Container([
    top_heading,
    dbc.Tabs(
        [
            card_tab(label='Platform', content=inputs_general, id='inputs_general'),
            card_tab(label='Resources', content=inputs_resources, id='inputs_resources'),
            card_tab(label='Network', content=inputs_network, id='inputs_network'),
            card_tab(label='Storage', content=inputs_storage, id='inputs_storage'),
            card_tab(label='Ingestion', content=inputs_ingest, id='inputs_ingest'),
            card_tab(label='Warehouse', content=inputs_warehouse, id='inputs_warehouse'),
            card_tab(label='Monitoring', content=inputs_monitor, id='inputs_monitor'),
            card_tab(label='BUILD', content=download_controls, id='download_controls'),
        ])
], fluid=True)

# hide one sub for all if DMZ is selected
@app.callback(
    Output('input_same_sub_dmz_hide', 'style'),
    Input('input_zone', 'value')
)
def toggle_same_sub(input_zone_value):
    if input_zone_value == '1':
        return {'display': 'none'}
    return {'display': 'block'}

# callback to enable and disable input fields drive by requested zone type
@app.callback(
    Output('input_env_hide', 'style'),
    Output('input_gov_enable_hide', 'style'),
    Output('inputs_purview_spec', 'style'),
    Output('input_dmz_sub_hide', 'style'),
    Output('inputs_storage', 'disabled'),
    Output('inputs_ingest', 'disabled'),
    Output('inputs_warehouse', 'disabled'),
    Output('inputs_monitor', 'disabled'),
    Input('input_zone', 'value'), # zone type
    Input('input_gov_enable', 'value'), # deploy purview
    Input('input_same_dmz_sub', 'value'), # one sub for all
)
def input_fields_state(input_zone_value, input_gov_enable_value, input_same_dmz_sub_value):
    vis = {
        True : {'display' : 'none'},
        False : {'display' : 'block'}
    }
    governance_inputs = [
        vis[False], vis[True], vis[True], vis[True]
    ]
    # governance specific inputs
    if all([
        input_zone_value == '1', input_gov_enable_value == '1'
    ]):
        governance_inputs = [
            vis[True], vis[False], vis[False], vis[True]
    ]
    elif all([
        input_zone_value == '1', input_gov_enable_value == '2'
    ]):
        governance_inputs = [
            vis[True], vis[False], vis[True], vis[True]
        ]
    # same sub for all
    if all([
        input_same_dmz_sub_value == '2',
        input_zone_value == '2'
    ]):
        governance_inputs[-1] = vis[False]
    
    # how many other input are affected by the zone type?
    n_outputs_affected = 4
    # input states
    input_states = {
        '1' : [True for i in range(n_outputs_affected)],
        '2' : [False for i in range(n_outputs_affected)]
    }
    return governance_inputs + input_states.get(input_zone_value)

# input validation
all_inputs = [
    'input_org', 'input_project', 'input_subscription', 'input_dmz_subscription',
    'input_gov_admin_tenant_id', 'input_released_by', 'input_version', 'input_ip_range', 'input_storage_raw',
    'input_storage_cur', 'input_sql_sid', 'input_sql_tenant', 'input_sql_warehouse_login',
    'input_sql_warehouse_password', 'input_alerts_action_group', 'input_alerts_email', 'input_zone_name'
]
all_inputs_values = [
    Input(input, 'value') for input in all_inputs
]
all_inputs_patterns = [
    Input(input, 'pattern') for input in all_inputs
]
@app.callback(
    Output('download_controls', 'disabled'),
    Input('input_zone', 'value'),
    Input('input_gov_enable', 'value'),
    *all_inputs_values,
    *all_inputs_patterns
)
def enable_buttons(*args):
    # input state of the entire form
    form_input_state = [
        args[0], args[1]
    ]
    # valid input states to accept
    # TODO need to replace with pattern matching instead of hardcoding form states
    form_required_inputs_always = [
        0, 1, 2, 3, 4, 7, 8, 9
    ]
    form_required_inputs_dlz = [
        i for i in range(10, 19)
    ]
    form_required_inputs = {
        '12' : [
            *form_required_inputs_always # dmz without purview
        ],
        '11' : [
            *form_required_inputs_always, 6 # dmz with purview
        ],
        '21' : [
            *form_required_inputs_always, *form_required_inputs_dlz # dlz
        ],
        '22' : [
            *form_required_inputs_always, *form_required_inputs_dlz # dlz when switched back from dmz
        ]
    }
    inputs_and_patterns_to_check = args[2:] # ignore the dropdowns
    _midpoint = int(len(inputs_and_patterns_to_check) / 2)
    inputs = inputs_and_patterns_to_check[0:_midpoint]
    patterns = inputs_and_patterns_to_check[_midpoint:]
    # check each input against the pattern
    for pattern, input in zip(patterns, inputs):
        if not valid_pattern(pattern, input):
            form_input_state.append('0')
            continue
        form_input_state.append('1')

    # check if the form is still invalid
    for pos in form_required_inputs.get(''.join(form_input_state[0:2])):
        if form_input_state[pos] == '0':
            # return ''.join(form_input_state)
            return True # change back to True when done with development
    return False

# download deployment template
get_state = lambda x : State(x, 'value')
@app.long_callback(
    output=[
        Output('container_output', 'children'), # uncomment for testing
        Output('download_params_trigger', 'data'),
    ],
    inputs=[
        Input('download_template', 'n_clicks'),
        Input('download_params', 'n_clicks'),
        Input('download_doc', 'n_clicks'),  
        get_state('input_zone'), get_state('input_zone_name'), get_state('input_env'),
        get_state('input_org'), get_state('input_project'), get_state('input_location'),
        get_state('input_subscription'), get_state('input_gov_public_net'), get_state('input_gov_admin_tenant_id'),
        get_state('input_gov_enable'), get_state('input_df_enable'), get_state('input_db_enable'),
        get_state('input_stream_enable'), get_state('input_monitor_enable'), get_state('input_share_enable'),
        get_state('input_ip_range'), get_state('input_network_prefix'), get_state('input_default_subnet'),
        get_state('input_released_by'), get_state('input_version'),
        get_state('input_storage_raw'), get_state('input_storage_cur'), get_state('input_storage_public_net'), get_state('input_blob_public'), get_state('input_storage_sku'),
        get_state('input_storage_lock'), get_state('input_storage_retention'),
        get_state('input_ingest_public_net'), get_state('input_ingest_backup'), get_state('input_sql_login'), get_state('input_sql_sid'), get_state('input_sql_tenant'),
        get_state('input_warehouse_public_net'), get_state('input_sql_warehouse_login'), get_state('input_sql_warehouse_password'),
        get_state('input_alerts_action_group'), get_state('input_alerts_email'),
        get_state('input_same_dmz_sub'), get_state('input_dmz_subscription'),
        get_state('doc_client'), get_state('doc_author')
    ],
    running=[
        (Output('download_params', 'disabled'), True, False),
        (Output('download_template', 'disabled'), True, False),
        (Output('download_doc', 'disabled'), True, False),
        (Output('input_doc_enabled', 'disabled'), True, False),
        (Output('doc_client', 'disabled'), True, False),
        (Output('doc_author', 'disabled'), True, False),
        (Output('download_progress_bar', 'style'), {'display' : 'block'}, {'display' : 'none'}),
    ],
    prevent_initial_call=True
)
def download_template(
    n_clicks_template, n_clicks_params, n_clicks_doc,
    input_zone_value, input_zone_name_value, input_env_value,
    input_org_value, input_project_value, input_location_value,
    input_subscription_value, input_gov_public_net_value, input_gov_admin_tenant_id_value,
    input_gov_enable_value, input_df_enable_value, input_db_enable_value,
    input_stream_enable_value, input_monitor_enable_value, input_share_enable_value,
    input_ip_range_value, input_network_prefix_value, input_default_subnet_value,
    input_released_by_value, input_version_value,
    input_storage_raw_value, input_storage_cur_value, input_storage_public_net_value, input_blob_public_value, input_storage_sku_value, 
    input_storage_lock_value, input_storage_retention_value,
    input_ingest_public_net_value, input_ingest_backup_value, input_sql_login_value, input_sql_sid_value, input_sql_tenant_value,
    input_warehouse_public_net_value, input_sql_warehouse_login_value, input_sql_warehouse_password_value,
    input_alerts_action_group_value, input_alerts_email_value,
    input_same_dmz_sub_value, input_dmz_subscription_value,
    doc_client_value, doc_author_value
    ):
    # clean up tmp
    tmp_clean_up()

    # temporary folder where results will be output
    tmp_key = clone_params()

    # params for all zones
    true_false_mapping = {'1' : True, '2' : False}
    zone_mapping = {'1' : 'dmz', '2' : 'dlz'}
    param_file_to_inputs = {
        'organisation' : {'value' : input_org_value.lower()},
        'project' : {'value' : input_project_value},
        'location' : {'value' : input_location_value},
        'targetSubscriptionId' : {'value' : input_subscription_value},
        'networkParams' : {
            'value' : {
                'ipRange' : input_ip_range_value,
                'vnetSuffix' : input_network_prefix_value,
                'subnetSuffix' : input_default_subnet_value,
            }
        },
        'governanceParams' : {
            'value' : {
                'publicNetworkAccess' : input_gov_public_net_value,
                'adminTenantId' : placeholders.get('microsoft_id'),
            }
        },
        'platformParams' : {
            'value' : {
                'isGovernanceEnabled' : true_false_mapping.get(input_gov_enable_value),
                'isDataFactoryEnabled' : true_false_mapping.get(input_df_enable_value),
                'isDataBricksEnabled' : true_false_mapping.get(input_db_enable_value),
                'isStreamingEnabled' : true_false_mapping.get(input_stream_enable_value),
                'isDataShareEnabled' : true_false_mapping.get(input_monitor_enable_value),
                'isMonitoringEnabled' : true_false_mapping.get(input_share_enable_value),
                'zoneType' : zone_mapping.get(input_zone_value).upper()
            }
        },
        'releaseParams' : {
            'value' : {
                'ReleasedBy': input_released_by_value,
                'Version': input_version_value
            }
        }
    }
    for zone_type in ['dmz', 'dlz']:
        for k, v in param_file_to_inputs.items():
            update_bicep_params(zone_type, tmp_key, k, v)
    # dmz specific params
    if all([
        input_zone_value == '1',
        true_false_mapping.get(input_gov_enable_value),
        len(input_gov_admin_tenant_id_value) > 0
        ]):
            update_bicep_params('dmz', tmp_key, 'governanceParams', {
                'value' : {
                    'publicNetworkAccess' : input_gov_public_net_value,
                    'adminTenantId' : input_gov_admin_tenant_id_value,
                    }
                }
            )
    # dlz specific params
    elif input_zone_value == '2': # dlz
        param_file_to_inputs_dlz = {
            'zone' : {
                'value' : input_zone_name_value
            },
            'environment' : {
                'value' : input_env_value
            },
            'dmzSubscriptionId' : {
                'value' : input_subscription_value
            },
            'storageParams' : {
                'value' : {
                    'dataLakeNames' : [input_storage_raw_value, input_storage_cur_value],
                    'publicNetworkAccess' : input_storage_public_net_value,
                    'allowBlobPublicAccess': {'Enabled' : True, 'Disabled' : False}.get(input_blob_public_value),
                    'sku': input_storage_sku_value,
                    'storageLock' : {'Enabled' : True, 'Disabled' : False}.get(input_storage_lock_value),
                    'storageRetentionDays' : input_storage_retention_value
                }
            },
            'ingestParams' : {
                'value' : {
                    'publicNetworkAccess' : input_ingest_public_net_value,
                    'requestedBackupStorageRedundancy': input_ingest_backup_value,
                    'adminLogin' : input_sql_login_value,
                    'adminSid' : input_sql_sid_value,
                    'adminTenantId' : input_sql_tenant_value
                }
            },
            'warehouseParams' : {
                'value' : {
                    'publicNetworkAccess' : input_warehouse_public_net_value,
                    'sqlAdministratorLogin' : input_sql_warehouse_login_value,
                    'sqlAdministratorLoginPassword' : input_sql_warehouse_password_value
                }
            },
            'monitoringParams' : {
            'value' : {
                'actionGroupName' : input_alerts_action_group_value,
                'emailAddress' : input_alerts_email_value
            }
            },            
        }
        for k, v in param_file_to_inputs_dlz.items():
            update_bicep_params('dlz', tmp_key, k, v)
        # dmz is in a different sub
        if all([input_same_dmz_sub_value == '2', len(input_dmz_subscription_value) > 0]):
            update_bicep_params('dlz', tmp_key, 'dmzSubscriptionId', {'value' : input_dmz_subscription_value})

    # copy output files into the tmp folder
    trigger = callback_context.triggered[0]['prop_id'].split('.')[0] # which button has been clicked?
    if trigger == 'download_params':
        return '', dcc.send_file(
            params_build(zone_mapping.get(input_zone_value), tmp_key)
        )
    elif trigger == 'download_template':
        return '', dcc.send_file(
            bicep_build(zone_mapping.get(input_zone_value), tmp_key)
        )
    elif trigger == 'download_doc':
        return '', dcc.send_file(
            generate_doc(zone_mapping.get(input_zone_value), tmp_key, context={
                'doc_client' : doc_client_value,
                'doc_author' : doc_author_value,
                'doc_date' : datetime.datetime.today().strftime('%m/%d/%Y'),
                'input_org_value' : input_org_value.lower(),
                'input_project_value' : input_project_value,
                'input_project_3' : ''.join([i[0] for i in input_project_value.split(' ') if len(i) > 0]).upper(),
                'input_location_value' : input_location_value,
                'input_network_ip_range_value' : input_ip_range_value,
                'input_network_prefix_value' : input_network_prefix_value,
                'input_default_subnet_value' : input_default_subnet_value,
                'zone_name_value' : input_zone_name_value.lower(),
                'input_zone_name_value' : input_zone_name_value.title(),
                'input_storage_raw_value' : input_storage_raw_value,
                'input_storage_cur_value' : input_storage_cur_value,                
            })
        )

# hide documentation inputs if they are not required
@app.callback(
    Output('download_doc', 'style'),
    Output('doc_inputs_hide', 'style'),
    Input('input_doc_enabled', 'value')
)
def toggle_doc_inputs(input_doc_enabled_value):
    if input_doc_enabled_value == '1':
        return {'display' : 'block'}, {'display' : 'block'}
    return {'display' : 'none'}, {'display' : 'none'}

# uncomment below for development and debugging
if __name__ == '__main__':
    app.run_server(port='8051', host='0.0.0.0', debug=True)
