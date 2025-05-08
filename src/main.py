from dishka import make_container

from core.config.settings import AppSettings, load_app_settings
from core.engine.scenario_manager import ScenarioManager
from core.interfaces import Scenario
from ioc import (
    AppProvider,
    DatabaseProvider,
    IntegrationsProvider,
    ScenarioProvider,
)
from scenarios.astrocatcoin.scenario import AstroCatCoinScenario


def run_scenario(scenario_name: str, scenario_cls: type[Scenario]):
    settings = load_app_settings()
    container = make_container(
        AppProvider(),
        DatabaseProvider(),
        IntegrationsProvider(),
        ScenarioProvider(
            scenario_name=scenario_name,
            scenario_cls=scenario_cls,
        ),
        context={AppSettings: settings},
    )
    settings = container.get(AppSettings)
    with container() as c_req:
        sc_manager = c_req.get(ScenarioManager)
        sc_manager.run_generation_cycle()
    print(settings)
    container.close()


def run_poll_cycle():
    settings = load_app_settings()
    container = make_container(
        context={AppSettings: settings},
    )
    
    container.close()


if __name__ == "__main__":
    run_scenario("astrocatcoin", AstroCatCoinScenario)
