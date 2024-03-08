from typing import Dict

from adaptive_padding.padding.adaptive_padding.level100 import Level100
from adaptive_padding.padding.adaptive_padding.level500 import Level500
from adaptive_padding.padding.adaptive_padding.level700 import Level700
from adaptive_padding.padding.adaptive_padding.level900 import Level900
from adaptive_padding.padding.nearest.external_integration import JuliaExternalIntegration
from adaptive_padding.padding.nearest.nearest_padding import NearestPadding
from adaptive_padding.padding.existing.exponential_padding import ExponentialPadding
from adaptive_padding.padding.existing.linear import LinearPadding
from adaptive_padding.padding.existing.mouse_elephant import MouseElephant
from adaptive_padding.padding.existing.mtu import Mtu
from adaptive_padding.padding.existing.random import RandomPadding
from adaptive_padding.padding.existing.random_255 import Random255
from adaptive_padding.padding.padding_strategy import PaddingStrategy

from os.path import join


def create_existing_strategies_mapping() -> Dict[str, PaddingStrategy]:
    return {
        "exponential": ExponentialPadding(),
        "linear": LinearPadding(),
        "mouse_elephant": MouseElephant(),
        "mtu": Mtu(),
        "random": RandomPadding(),
        "random255": Random255()}


def create_proposal_strategies_mapping() -> Dict[str, PaddingStrategy]:
    return {
        "level100": Level100(),
        "level500": Level500(),
        "level700": Level700(),
        "level900": Level900()
    }


def create_nearest_strategies_mapping() -> Dict[str, PaddingStrategy]:
    julia_command = ["julia", join("adaptive_padding", "padding", "nearest" "OptimalPadding.jl")]
    julia_external_integration = JuliaExternalIntegration(julia_command)
    return {
        "near": NearestPadding(julia_external_integration)
    }
