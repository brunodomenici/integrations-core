# (C) Datadog, Inc. 2019-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import pytest

from . import common

pytestmark = [pytest.mark.e2e, common.python_autodiscovery_only]


def test_e2e_v1_with_apc_ups_profile(dd_agent_check):
    config = common.generate_container_instance_config([])
    instance = config['instances'][0]
    instance.update(
        {
            'snmp_version': 1,
            'community_string': 'apc_ups',
        }
    )
    assert_apc_ups_metrics(dd_agent_check, config)


def test_e2e_core_v3_no_auth_no_priv(dd_agent_check):
    config = common.generate_container_instance_config([])
    instance = config['instances'][0]
    instance.update(
        {
            'user': 'datadogNoAuthNoPriv',
            'snmp_version': 3,
            'context_name': 'apc_ups',
            'community_string': '',
        }
    )
    assert_apc_ups_metrics(dd_agent_check, config)


def test_e2e_core_v3_with_auth_no_priv(dd_agent_check):
    config = common.generate_container_instance_config([])
    instance = config['instances'][0]
    instance.update(
        {
            'user': 'datadogMD5NoPriv',
            'snmp_version': 3,
            'authKey': 'doggiepass',
            'authProtocol': 'MD5',
            'context_name': 'apc_ups',
            'community_string': '',
        }
    )
    assert_apc_ups_metrics(dd_agent_check, config)


def test_e2e_v1_with_apc_ups_profile_batch_size_1(dd_agent_check):
    config = common.generate_container_instance_config([])
    instance = config['instances'][0]
    instance.update(
        {
            'snmp_version': 1,
            'community_string': 'apc_ups',
            'oid_batch_size': 1,
        }
    )
    assert_apc_ups_metrics(dd_agent_check, config)


def assert_apc_ups_metrics(dd_agent_check, config):
    config['init_config']['loader'] = 'core'
    instance = config['instances'][0]
    aggregator = dd_agent_check(config, rate=True)

    profile_tags = [
        'snmp_profile:apc_ups',
        'model:APC Smart-UPS 600',
        'firmware_version:2.0.3-test',
        'serial_num:test_serial',
        'ups_name:testIdentName',
        'device_vendor:apc',
    ]
    tags = profile_tags + ["snmp_device:{}".format(instance['ip_address'])]

    metrics = [
        'upsAdvBatteryNumOfBadBattPacks',
        'upsAdvBatteryReplaceIndicator',
        'upsAdvBatteryRunTimeRemaining',
        'upsAdvBatteryTemperature',
        'upsAdvBatteryCapacity',
        'upsHighPrecInputFrequency',
        'upsHighPrecInputLineVoltage',
        'upsHighPrecOutputCurrent',
        'upsAdvInputLineFailCause',
        'upsAdvOutputLoad',
        'upsBasicBatteryTimeOnBattery',
        'upsAdvTestDiagnosticsResults',
    ]

    common.assert_common_metrics(aggregator, tags, is_e2e=True, loader='core')

    for metric in metrics:
        aggregator.assert_metric('snmp.{}'.format(metric), metric_type=aggregator.GAUGE, tags=tags, count=2)
    aggregator.assert_metric(
        'snmp.upsOutletGroupStatusGroupState',
        metric_type=aggregator.GAUGE,
        tags=['outlet_group_name:test_outlet'] + tags,
    )
    aggregator.assert_metric(
        'snmp.upsBasicStateOutputState.AVRTrimActive', 1, metric_type=aggregator.GAUGE, tags=tags, count=2
    )
    aggregator.assert_metric(
        'snmp.upsBasicStateOutputState.BatteriesDischarged', 1, metric_type=aggregator.GAUGE, tags=tags, count=2
    )
    aggregator.assert_metric(
        'snmp.upsBasicStateOutputState.LowBatteryOnBattery', 1, metric_type=aggregator.GAUGE, tags=tags, count=2
    )
    aggregator.assert_metric(
        'snmp.upsBasicStateOutputState.NoBatteriesAttached', 1, metric_type=aggregator.GAUGE, tags=tags, count=2
    )
    aggregator.assert_metric(
        'snmp.upsBasicStateOutputState.OnLine', 0, metric_type=aggregator.GAUGE, tags=tags, count=2
    )
    aggregator.assert_metric(
        'snmp.upsBasicStateOutputState.ReplaceBattery', 1, metric_type=aggregator.GAUGE, tags=tags, count=2
    )
    aggregator.assert_metric('snmp.upsBasicStateOutputState.On', 1, metric_type=aggregator.GAUGE, tags=tags, count=2)

    aggregator.assert_all_metrics_covered()