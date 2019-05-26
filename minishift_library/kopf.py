def do_kopf(s):
	s.send('rm -rf kopf_tmp')
	s.send('mkdir kopf_tmp')
	s.send('cd kopf_tmp')
	s.send('git clone https://github.com/zalando-incubator/kopf')
	s.send('cd kopf')
	s.send_file('crd.yaml',''' apiVersion: apiextensions.k8s.io/v1beta1
 kind: CustomResourceDefinition
 metadata:
   name: ephemeralvolumeclaims.zalando.org
 spec:
   scope: Namespaced
   group: zalando.org
   versions:
     - name: v1
       served: true
       storage: true
   names:
     kind: EphemeralVolumeClaim
     plural: ephemeralvolumeclaims
     singular: ephemeralvolumeclaim
     shortNames:
       - evcs
       - evc''')
	s.send('kubectl apply -f crd.yaml')
	s.pause_point('')
	pass
