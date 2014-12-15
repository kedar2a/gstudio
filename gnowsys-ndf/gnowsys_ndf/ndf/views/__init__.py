"""Views for Gstudio"""
from jsonrpc import jsonrpc_method

@jsonrpc_method('gnowsys_ndf.ndf.sayHello')
def whats_the_time(request, name='Lester'):
  return "Hello %s" % name

@jsonrpc_method('gnowsys_ndf.ndf.gimmeThat', authenticated=True)
def something_special(request, secret_data):
  return {'sauce': ['authenticated', 'sauce']}