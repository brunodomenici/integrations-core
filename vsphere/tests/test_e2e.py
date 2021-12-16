import pytest

from datadog_checks.base import AgentCheck


@pytest.mark.e2e
def test_e2e(dd_agent_check, aggregator, realtime_instance):
    with pytest.raises(Exception):
        dd_agent_check(realtime_instance)
    aggregator.assert_service_check("vsphere.can_connect", AgentCheck.CRITICAL)
