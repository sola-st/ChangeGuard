def _init_airflow_core_hooks(self):
    core_dummy_hooks = {
        "generic": "Generic",
        "email": "Email",
    }
    for key, display in core_dummy_hooks.items():
        self._hooks_lazy_dict[key] = HookInfo(
            hook_class_name=None,
            connection_id_attribute_name=None,
            package_name=None,
            hook_name=display,
            connection_type=None,
            connection_testable=False,
        )
    for cls in [FSHook, PackageIndexHook]:
        package_name = cls.__module__
        hook_class_name = f"{cls.__module__}.{cls.__name__}"
        hook_info = self._import_hook(
            connection_type=None,
            provider_info=None,
            hook_class_name=hook_class_name,
            package_name=package_name,
        )
        self._hook_provider_dict[hook_info.connection_type] = HookClassProvider(
            hook_class_name=hook_class_name, package_name=package_name
        )
        self._hooks_lazy_dict[hook_info.connection_type] = hook_info
