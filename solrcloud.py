import requests
import sys
import pprint
import time
from datetime import datetime
import simplejson as json
from checks import AgentCheck

class SolrcloudCheck(AgentCheck):
    cores = {}

    def check(self, instance):
        url = instance.get('url', 'http://127.0.0.1:8983')
        statpath1 = '/solr/admin/cores?action=STATUS&wt=json'
        #statpath2 = '/solr/$corename/admin/mbeans?stats=true&wt=json'
        tagpath1 = '/solr/admin/info/system?wt=json'
        tagpath2 = '/solr/admin/collections?action=CLUSTERSTATUS&wt=json'

        rstat = requests.get(url + statpath1)
        jstat1 = json.loads(rstat.text)
        for c in jstat1["status"]:
            self.cores[c] = {}
            self.cores[c]["stat"] = {}
            self.cores[c]["tag"] = {}
            self.cores[c]["stat"]["solrcloud.numdocs"] = jstat1["status"][c]["index"]["numDocs"]
            #need to determine correct datatype for this
            #self.cores[c]["stat"]["solrcloud.current"] = jstat1["status"][c]["index"]["current"]

            if "lastModified" in jstat1["status"][c]["index"]:
                lm_ds = datetime.strptime(jstat1["status"][c]["index"]["lastModified"], "%Y-%m-%dT%H:%M:%S.%fZ")
                lm_stamp = time.mktime(lm_ds.timetuple())
                self.cores[c]["stat"]["solrcloud.lastModified"] = time.time() - lm_stamp

            self.cores[c]["stat"]["solrcloud.sizeInBytes"] = jstat1["status"][c]["index"]["sizeInBytes"]

            self.cores[c]["tag"]["name"] = jstat1["status"][c]["name"]
            if "cloud" in jstat1["status"][c]:
                self.cores[c]["tag"]["collection"] = jstat1["status"][c]["cloud"]["collection"]
                #self.cores[c]["tag"]["shard"] = jstat1["status"][c]["cloud"]["shard"]
                #self.cores[c]["tag"]["replica"] = jstat1["status"][c]["cloud"]["replica"]

        rtag1 = requests.get(url + tagpath1)
        jtag1 = json.loads(rtag1.text)

        for c in self.cores:
            #self.cores[c]["tag"]["solrmode"] = jtag1["mode"]
            self.cores[c]["tag"]["solrversion"] = jtag1["lucene"]["solr-spec-version"]

        rtag2 = requests.get(url + tagpath2)
        jtag2 = json.loads(rtag2.text)

        for c in self.cores:
            for col in jtag2["cluster"]["collections"]:
                if col == self.cores[c]["tag"]["collection"]:
                    if "aliases" in jtag2["cluster"]["collections"][col]:
                        for a in jtag2["cluster"]["collections"][col]["aliases"]:
                            self.cores[c]["tag"]["alias:"+a] = None
                for sh in jtag2["cluster"]["collections"][col]["shards"]:
                    for repl in jtag2["cluster"]["collections"][col]["shards"][sh]["replicas"]:
                        for core in self.cores.items():
                            if jtag2["cluster"]["collections"][col]["shards"][sh]["replicas"][repl]["core"] == core[1]["tag"]["name"]:
                                if jtag2["cluster"]["collections"][col]["shards"][sh]["replicas"][repl]["state"] == "active":
                                    self.cores[c]["stat"]["solrcloud.cloudstatus"] = 1
                                else:
                                    self.cores[c]["stat"]["solrcloud.cloudstatus"] = 0

        #pprint.pprint(self.cores)
        #format data and send it
        for c in self.cores:
            for s in self.cores[c]["stat"]:
                t = []
                v = int(self.cores[c]["stat"][s])
                for i in self.cores[c]["tag"]:
                    if self.cores[c]["tag"][i] == None:
                        t.append(i)
                    else:
                        t.append(i + ":" + str(self.cores[c]["tag"][i]))
                self.gauge(s, v, tags=t)
                #print(s + "," + str(v))
