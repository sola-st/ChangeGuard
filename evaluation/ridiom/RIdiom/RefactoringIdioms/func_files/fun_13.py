def load_providers_configuration(self):
    log.debug("Loading providers configuration")
    from airflow.providers_manager import ProvidersManager
    self.restore_core_default_configuration()
    for provider, config in ProvidersManager().already_initialized_provider_configs:
        for provider_section, provider_section_content in config.items():
            provider_options = provider_section_content["options"]
            section_in_current_config = self.configuration_description.get(provider_section)
            if not section_in_current_config:
                self.configuration_description[provider_section] = deepcopy(provider_section_content)
                section_in_current_config = self.configuration_description.get(provider_section)
                section_in_current_config["source"] = f"default-{provider}"
                for option in provider_options:
                    section_in_current_config["options"][option]["source"] = f"default-{provider}"
            else:
                section_source = section_in_current_config.get("source", "Airflow's core package").split(
                    "default-"
                )[-1]
                raise AirflowConfigException(
                    f"The provider {provider} is attempting to contribute "
                    f"configuration section {provider_section} that "
                    f"has already been added before. The source of it: {section_source}. "
                    "This is forbidden. A provider can only add new sections. It "
                    "cannot contribute options to existing sections or override other "
                    "provider's configuration.",
                    UserWarning,
                )
    self._default_values = create_default_config_parser(self.configuration_description)
    try:
        del self.sensitive_config_values
    except AttributeError:
        pass
    self._providers_configuration_loaded = True
