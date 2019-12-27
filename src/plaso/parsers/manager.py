# -*- coding: utf-8 -*-
"""The parsers and plugins manager."""

from __future__ import unicode_literals



class ParsersManager(object):
  """The parsers and plugins manager."""

  _parser_classes = {}

  @classmethod
  def DeregisterParser(cls, parser_class):
    """Deregisters a parser class.

    The parser classes are identified based on their lower case name.

    Args:
      parser_class (type): parser class (subclass of BaseParser).

    Raises:
      KeyError: if parser class is not set for the corresponding name.
    """
    parser_name = parser_class.NAME.lower()
    if parser_name not in cls._parser_classes:
      raise KeyError('Parser class not set for name: {0:s}.'.format(
          parser_class.NAME))

    del cls._parser_classes[parser_name]

  @classmethod
  def GetNamesOfParsersWithPlugins(cls):
    """Retrieves the names of all parsers with plugins.

    Returns:
      list[str]: names of all parsers with plugins.
    """
    parser_names = []

    for parser_name, parser_class in cls.GetParsers():
      if parser_class.SupportsPlugins():
        parser_names.append(parser_name)

    return sorted(parser_names)

  @classmethod
  def GetParserAndPluginNames(cls, parser_filter_expression=None):
    """Retrieves the parser and parser plugin names.

    Args:
      parser_filter_expression (Optional[str]): parser filter expression,
          where None represents all parsers and plugins.

    Returns:
      list[str]: parser and parser plugin names.
    """
    parser_and_plugin_names = []
    for parser_name, parser_class in cls.GetParsers(
        parser_filter_expression=parser_filter_expression):
      parser_and_plugin_names.append(parser_name)

      if parser_class.SupportsPlugins():
        for plugin_name, _ in parser_class.GetPlugins():
          parser_and_plugin_names.append(
              '{0:s}/{1:s}'.format(parser_name, plugin_name))

    return parser_and_plugin_names

  @classmethod
  def GetParserPluginsInformation(cls, parser_filter_expression=None):
    """Retrieves the parser plugins information.

    Args:
      parser_filter_expression (Optional[str]): parser filter expression,
          where None represents all parsers and plugins.

    Returns:
      list[tuple[str, str]]: pairs of parser plugin names and descriptions.
    """
    parser_plugins_information = []
    for _, parser_class in cls.GetParsers(
        parser_filter_expression=parser_filter_expression):
      if parser_class.SupportsPlugins():
        for plugin_name, plugin_class in parser_class.GetPlugins():
          description = getattr(plugin_class, 'DESCRIPTION', '')
          parser_plugins_information.append((plugin_name, description))

    return parser_plugins_information

  # Note this method is used by l2tpreg.
  @classmethod
  def GetParserObjectByName(cls, parser_name):
    """Retrieves a specific parser object by its name.

    Args:
      parser_name (str): name of the parser.

    Returns:
      BaseParser: parser object or None.
    """
    parser_class = cls._parser_classes.get(parser_name, None)
    if parser_class:
      return parser_class()
    return None

  @classmethod
  def GetParserObjects(cls, parser_filter_expression=None):
    """Retrieves the parser objects.

    Args:
      parser_filter_expression (Optional[str]): parser filter expression,
          where None represents all parsers and plugins.

    Returns:
      dict[str, BaseParser]: parsers per name.
    """
    includes, excludes = cls._GetParserFilters(parser_filter_expression)

    parser_objects = {}
    for parser_name, parser_class in iter(cls._parser_classes.items()):
      # If there are no includes all parsers are included by default.
      if not includes and parser_name in excludes:
        continue

      if includes and parser_name not in includes:
        continue

      parser_object = parser_class()
      if parser_class.SupportsPlugins():
        plugin_includes = None
        if parser_name in includes:
          plugin_includes = includes[parser_name]

        parser_object.EnablePlugins(plugin_includes)

      parser_objects[parser_name] = parser_object

    return parser_objects

  @classmethod
  def GetParsers(cls, parser_filter_expression=None):
    """Retrieves the registered parsers and plugins.

    Retrieves a dictionary of all registered parsers and associated plugins
    from a parser filter string. The filter string can contain direct names of
    parsers, presets or plugins. The filter string can also negate selection
    if prepended with an exclamation point, e.g.: "foo,!foo/bar" would include
    parser foo but not include plugin bar. A list of specific included and
    excluded plugins is also passed to each parser's class.

    The three types of entries in the filter string:
     * name of a parser: this would be the exact name of a single parser to
       include (or exclude), e.g. foo;
     * name of a preset, e.g. win7: the presets are defined in
       plaso/parsers/presets.py;
     * name of a plugin: if a plugin name is included the parent parser will be
       included in the list of registered parsers;

    Args:
      parser_filter_expression (Optional[str]): parser filter expression,
          where None represents all parsers and plugins.

    Yields:
      tuple: containing:

      * str: name of the parser:
      * type: parser class (subclass of BaseParser).
    """
    includes, excludes = cls._GetParserFilters(parser_filter_expression)

    for parser_name, parser_class in iter(cls._parser_classes.items()):
      # If there are no includes all parsers are included by default.
      if not includes and parser_name in excludes:
        continue

      if includes and parser_name not in includes:
        continue

      yield parser_name, parser_class

  @classmethod
  def GetParsersInformation(cls):
    """Retrieves the parsers information.

    Returns:
      list[tuple[str, str]]: parser names and descriptions.
    """
    parsers_information = []
    for _, parser_class in cls.GetParsers():
      description = getattr(parser_class, 'DESCRIPTION', '')
      parsers_information.append((parser_class.NAME, description))

    return parsers_information

  @classmethod
  def GetPresets(cls):
    """Retrieves the preset definitions.

    Returns:
      generator[PresetDefinition]: preset definition generator in alphabetical
          order by name.
    """
    return cls._presets.GetPresets()

  @classmethod
  def ReadPresetsFromFile(cls, path):
    """Reads parser and parser plugin presets from a file.

    Args:
      path (str): path of file that contains the the parser and parser plugin
          presets configuration.
    """
    cls._presets.ReadFromFile(path)

  @classmethod
  def RegisterParser(cls, parser_class):
    """Registers a parser class.

    The parser classes are identified based on their lower case name.

    Args:
      parser_class (type): parser class (subclass of BaseParser).

    Raises:
      KeyError: if parser class is already set for the corresponding name.
    """
    parser_name = parser_class.NAME.lower()
    if parser_name in cls._parser_classes:
      raise KeyError('Parser class already set for name: {0:s}.'.format(
          parser_class.NAME))

    cls._parser_classes[parser_name] = parser_class

  @classmethod
  def RegisterParsers(cls, parser_classes):
    """Registers parser classes.

    The parser classes are identified based on their lower case name.

    Args:
      parser_classes (list[type]): parsers classes (subclasses of BaseParser).

    Raises:
      KeyError: if parser class is already set for the corresponding name.
    """
    for parser_class in parser_classes:
      cls.RegisterParser(parser_class)
