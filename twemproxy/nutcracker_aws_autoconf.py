#!/usr/bin/python

import boto3
import botocore.exceptions
import sys
import yaml

from pprint import pprint

# configuration
CLUSTER_TAG_KEY = "PhhhotoTwemproxyMember"
CLUSTER_TAG_VALUE = "true"

# This depends on some things in the environment. It will use credentials
# in ~/.aws/config (useful in development). It can also just use AWS_DEFAULT_REGION
# and whatever permissions the container / EC2 instance has via IAM.
#
# for example:
# export AWS_DEFAULT_REGION=us-east-1

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

def get_session_region_client():
  """
  Magic Alert! Tries to make an elasticache session. If it fails
  because no AWS region is set in the environment, it hits
  http://169.254.169.254/latest/meta-data/placement/availability-zone
  to try to get the current one. If it can't, we crash.
  """
  session = boto3.session.Session()
  try:
    client = session.client('elasticache')
  except botocore.exceptions.NoRegionError, e:
    # no region, so ask this mysterious AWS URL
    print "no AWS region; get one from http://169.254.169.254/latest/meta-data/placement/availability-zone..."
    import requests
    import os
    resp = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone')
    region = resp.text[:-1] # trim the last char (us-east-1b -> us-east-1)
    print "found region %s" % region
    os.environ['AWS_DEFAULT_REGION'] = region

    # try it again, if this doesn't work, just crash
    client = session.client('elasticache')

  region = session.region_name

  print "got", session, region, client
  return session, region, client

def get_engine_addresses():
  """
  Hits the AWS API and returns a structure like:
  {'memcached': ['cac-me-1tvncei2gal0r.ihepav.0001.use1.cache.amazonaws.com:11211:1'],
   'redis': []}
  """
  session, region, client = get_session_region_client()

  engine_addresses = {
    'redis': [],
    'memcached': []
  }

  try:
    clusters = get_clusters(client)
  except botocore.exceptions.NoCredentialsError, e:
    print "No AWS credentials found. this is expected to happen during `docker build`."
    print "We'll skip the AWS API part and use the input config file as is."
    return None

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

def update_twemproxy_config(addresses, input_filename, output_filename):
  # load config
  f = open(input_filename, 'r')
  config = yaml.load(f)
  f.close()

  # update config
  if addresses is not None:
    # addresses can be None when the AWS API is not reachable; just write input to output
    for engine in ['memcached', 'redis']:
      config[engine]['servers'] = addresses[engine]
  new_config = yaml.dump(config)

  # write new config
  f = open(output_filename, 'w')
  f.write(new_config)
  f.close()

  print "wrote the following to %s:" % output_filename
  print new_config


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Usage: python nutcracker_aws_autoconf.py inputfilename outputfilename"
    raise SystemExit

  input_filename = sys.argv[1]
  output_filename = sys.argv[2]

  print "Reading %s, writing %s" % (input_filename, output_filename)

  addresses = get_engine_addresses()
  update_twemproxy_config(addresses, input_filename, output_filename)
