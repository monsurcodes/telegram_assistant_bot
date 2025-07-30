import importlib
import pkgutil
from bot.core.base_plugin import BasePlugin

def discover_plugins(plugins_package):
    """
    Discover all plugin classes (subclasses of BasePlugin) in the given plugins package.
    Returns a list of plugin classes.
    """
    plugin_classes = []

    # Iterate over all modules in the plugins package
    for finder, name, ispkg in pkgutil.iter_modules(plugins_package.__path__):
        full_module_name = f"{plugins_package.__name__}.{name}"
        module = importlib.import_module(full_module_name)

        # Find all classes that are subclass of BasePlugin, but not BasePlugin itself
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (
                isinstance(attribute, type)
                and issubclass(attribute, BasePlugin)
                and attribute is not BasePlugin
            ):
                plugin_classes.append(attribute)
    return plugin_classes
