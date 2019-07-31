def do_networkpolicy(s):
	# See: https://blog.openshift.com/networkpolicies-and-microsegmentation/

	# Example network policy - needs access to default namespace for router connections
	s.send_file('''np.yaml''','''kind: NetworkPolicy
apiVersion: extensions/v1beta1
metadata:
  name: allow-same-and-default-namespace
spec:
  ingress:
  - from:
    - podSelector: {}
  - from:
    - namespaceSelector:
        matchLabels:
          name: default''')

# TODO: project creation template?
# TODO: ^^ apply to tenant namespace TODO: create tenant nses
# TODO: get admin

	# Must also label default namespace:
	s.send('oc label namespace default name=default')

# TODO: Microsegmentation controller? metacontroller?
	pass
