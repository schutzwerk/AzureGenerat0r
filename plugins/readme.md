# How to develop plugins? <br />
A plugin is handled as an independent python module.
There are a few conventions for plugin development.
* Each plugin needs a init() method, that initializes variables and saves them to a storage.
* Use a storage file to save variables. 
  Thus values can be reused if a plugin is started multiple times (what should be the case in most instances).
* The storage file has to end with `storage.yml`.
* Pipe a generated value to stdout with print().

An example for a plugin can be found in `hostnameGenerator.py`. 
A plugin can be activated by using `PLUGIN/<pluginName>` in the specification.