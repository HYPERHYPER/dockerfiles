#!/usr/bin/python

import boto3
import yaml
from pprint import pprint

# configuration
CLUSTER_TAG_KEY = "PhhhotoTwemproxyMember"
CLUSTER_TAG_VALUE = "true"

TWEMPROXY_CONFIG_INPUT_FILE = 'nutcracker.cfg'
TWEMPROXY_CONFIG_OUTPUT_FILE = 'nutcracker.out.cfg'

# "static memory"
_AWS_ACCT_ID = None

def get_account_id():
  """Gets the AWS Account ID (uses whatever auth is available in env)"""
  global _AWS_ACCT_ID
  if _AWS_ACCT_ID is None:
    _AWS_ACCT_ID = boto3.client('sts').get_caller_identity().get('Account')
  return _AWS_ACCT_ID

def get_elasticache_arn(region, cache_cluster_id):
  """Generates an AWS ARN from a CacheClusterId"""
  return "arn:aws:elasticache:%s:%s:cluster:%s" % (region, get_account_id(), cache_cluster_id)

def is_twemproxy_member(client, region, cache_cluster_id):
  arn = get_elasticache_arn(region, cache_cluster_id)
  response = client.list_tags_for_resource(ResourceName=arn)
  for tag in response['TagList']:
    if tag['Key'] == CLUSTER_TAG_KEY and tag['Value'] == CLUSTER_TAG_VALUE:
      return True
  return False

def get_clusters(client):
  """Get a list of CacheClusters"""
  response = client.describe_cache_clusters(ShowCacheNodeInfo=True)
  clusters = response['CacheClusters']
  return clusters

def get_twemproxy_address(node):
  """Get a twemproxy-formatted address string (uses weight '1')"""
  return "%s:%s:1" % (node['Endpoint']['Address'], node['Endpoint']['Port'])

def get_engine_addresses():
  """Hits the AWS API and returns a structure like:
  {'memcached': ['cac-me-1tvncei2gal0r.ihepav.0001.use1.cache.amazonaws.com:11211:1'],
   'redis': []}
  """
  session = boto3.session.Session()
  region = session.region_name
  client = session.client('elasticache')

  engine_addresses = {
    'redis': [],
    'memcached': []
  }

  clusters = get_clusters(client)
  print "Found %d ElastiCache clusters..." % len(clusters)

  for i, cluster in enumerate(clusters):
    cluster_desc = "Cluster %d %s (%s)" % (i+1, cluster['CacheClusterId'], cluster['Engine'])

    if cluster['CacheClusterStatus'] != 'available':
      print "%s is not available (status is %s), skipping" % (cluster_desc, cluster['CacheClusterStatus'])
      continue
    
    if not is_twemproxy_member(client, region, cluster['CacheClusterId']):
      print "%s is not tagged %s=%s, skipping" % (cluster_desc, CLUSTER_TAG_KEY, CLUSTER_TAG_VALUE)
      continue

    print "%s is a Twemproxy candidate; investigate its %d nodes..." % (cluster_desc, len(cluster['CacheNodes']))
    for node in cluster['CacheNodes']:
      if node['CacheNodeStatus'] != 'available':
        print "%s node %s is not available (status is %s), skipping" % (cluster_desc, node['CacheNodeId'], node['CacheNodeStatus'])
        continue

      # success!
      address = get_twemproxy_address(node)
      print "%s node id %s added: %s" % (cluster_desc, node['CacheNodeId'], address)
      engine_addresses[cluster['Engine']].append(address)

  pprint(engine_addresses)
  return engine_addresses

def update_twemproxy_config(addresses):
  global TWEMPROXY_CONFIG_INPUT_FILE, TWEMPROXY_CONFIG_OUTPUT_FILE

  # load config
  f = open(TWEMPROXY_CONFIG_INPUT_FILE, 'r')
  config = yaml.load(f)
  f.close()

  for engine in ['memcached', 'redis']:
    config[engine]['servers'] = addresses[engine]

  f = open(TWEMPROXY_CONFIG_OUTPUT_FILE, 'w')
  f.write(yaml.dump(config))
  f.close()

  print "wrote %s" % TWEMPROXY_CONFIG_OUTPUT_FILE

if __name__ == '__main__':
  addresses = get_engine_addresses()
  update_twemproxy_config(addresses)
