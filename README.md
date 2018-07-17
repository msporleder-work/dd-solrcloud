this is a solr monitoring agent for datadog, using python and dogstatsd

it functions using the solr web api, so no jmx is needed

Install:
  This is just a custom check, not a full integration.  Just drop the .py into
    /etc/datadog-agent/checks.d/ (for agent 6.x) and yaml in conf.d
    The default is to check localhost:8983

Features:
  * discover all cores, collections, and aliases
  * tag items appropriately
    * collection
    * alias
  * gather useful stats
    * core size on disk
    * num documents in core

  * TODO
    * DIH stats
    * timings and handling of custom handlers (/select and /custom-select)
    * cache stats
