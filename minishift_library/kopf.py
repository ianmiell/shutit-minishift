def do_kopf(s):
	# Prep - log in as admin
	s.send('oc login -u system:admin')
	# Prep - install kopf and kubernetes
	s.send('pip install kopf')
	s.send('pip install kubernetes')
	s.send('rm -rf kopf_tmp')
	s.send('mkdir kopf_tmp')
	s.send('cd kopf_tmp')
	s.send('git clone https://github.com/zalando-incubator/kopf')
	s.send('cd kopf')
	# Follow walkthrough as per: https://kopf.readthedocs.io/en/stable/walkthrough/creation/
	s.send('mkdir walkthrough && cd walkthrough')
	# Create the CRD for the evc (ephemeralvolumeclaim)
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

	# Create an evc object
	s.send_file('obj.yaml',''' apiVersion: zalando.org/v1
 kind: EphemeralVolumeClaim
 metadata:
   name: my-claim''')
	s.send('kubectl apply -f obj.yaml')
	s.send('kubectl get EphemeralVolumeClaim')
	s.send('kubectl get ephemeralvolumeclaims')
	s.send('kubectl get evcs')
	s.send('kubectl get evc')
	# Now create supid-simple operator.
	s.send_file('ephemeral.py','''import kopf

 @kopf.on.create('zalando.org', 'v1', 'ephemeralvolumeclaims')
 def create_fn(body, **kwargs):
     print(f"A handler is called with body: {body}")''')
	s.pause_point('now run: kopf run ephemeral.py --verbose &, then in another terminal oc delete evc and watch it handle.')
	# Create a new claim
	s.send_file('evc.yaml',''' apiVersion: zalando.org/v1
 kind: EphemeralVolumeClaim
 metadata:
   name: my-claim
 spec:
   size: 10G''')
	# Create templated pvc yaml file
	s.send_file('pvc.yaml',''' apiVersion: v1
 kind: PersistentVolumeClaim
 metadata:
   name: "{name}"
   annotations:
     volume.beta.kubernetes.io/storage-class: standard
 spec:
   accessModes:
     - ReadWriteOnce
   resources:
     requests:
       storage: "{size}"''')

	# Create new handler
	s.send_file('ephemeral.py','''import kopf
import kubernetes
import yaml

@kopf.on.create('zalando.org', 'v1', 'ephemeralvolumeclaims')
def create_fn(meta, spec, namespace, logger, **kwargs):
    name = meta.get('name')
    size = spec.get('size')
    if not size:
        raise kopf.HandlerFatalError(f"Size must be set. Got {size!r}.")

    path = os.path.join(os.path.dirname(__file__), 'pvc.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=name, size=size)
    data = yaml.load(text)

    api = kubernetes.client.CoreV1Api()
    obj = api.create_namespaced_persistent_volume_claim(
        namespace=namespace,
        body=data,
    )

    logger.info(f"PVC child is created: %s", obj)''')
	s.send('kubectl apply -f evc.yaml')
	s.send('sleep 5 && kubectl get pvc')
	s.pause_point('')
