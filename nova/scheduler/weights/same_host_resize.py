from oslo.config import cfg

from nova.scheduler import weights

same_host_resize_weight_opts = [
    cfg.FloatOpt('weight_of_same_host_resize',
                 default=10000000.0,
                 help='The final weight value to be returned if '
                      'the host is the same as the source.'),
]

CONF = cfg.CONF
CONF.import_opt('allow_resize_to_same_host', 'nova.compute.api')
CONF.register_opts(same_host_resize_weight_opts)


class SameHostResizeWeigher(weights.BaseHostWeigher):
    """Same Host Resize Weigher.

    This weigher can compute a weight allowing the destination machine
    to match source during resize operation.

    This weigher requires the allow_resize_to_same_host config to be enabled.
    It might also not work properly if scheduler_host_subset_size is not 1.
    """

    def _enabled(self):
        return CONF.allow_resize_to_same_host

    def _weigh_object(self, host_state, weight_properties):
        value = 0.0

        if self._enabled():
            spec = weight_properties.get('request_spec', {})
            props = spec.get('instance_properties', {})
            if props.get('task_state') == 'resize_prep':
                current_host = props.get('host')
                if host_state.host == current_host:
                    value = CONF.weight_of_same_host_resize

        return value
