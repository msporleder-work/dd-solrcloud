this is a solr monitoring agent for datadog, using python and dogstatsd

it functions using the solr web api, so no jmx is needed

Features:
  * discover all cores, collections, and aliases
    * cache these (auto invalidate if a timestamp is available somewhere)
  * tag items appropriately
    * collection
    * alias
    * DIH?
    * leader?
  * gather useful stats
    * core size on disk
    * num documents in core
    * DIH stats
    * tlog count (validate via lsof optional)
    * cache stats
    * request timings and numbers
  * things to monitor outside of scope
    * java process ulimit
    * general java stats (old gen size, gc times)
    * general jetty stats?
