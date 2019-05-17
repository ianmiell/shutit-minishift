def do_cicd(s):
	# Create Projects
	s.send('oc new-project dev --display-name="Tasks - Dev"')
	s.send('oc new-project stage --display-name="Tasks - Stage"')
	s.send('oc new-project cicd --display-name="CI/CD"')
	# Grant Jenkins Access to Projects
	s.send('oc policy add-role-to-group edit system:serviceaccounts:cicd -n dev')
	s.send('oc policy add-role-to-group edit system:serviceaccounts:cicd -n stage')
	s.send('rm -rf minishift_cicd_tmp')
	s.send('mkdir minishift_cicd_tmp')
	s.send('cd minishift_cicd_tmp')
	s.send('git clone https://github.com/siamaksade/openshift-cd-demo')
	s.send('cd openshift-cd-demo')
	s.send('oc new-app -n cicd -f cicd-template.yaml --param DEV_PROJECT=dev --param STAGE_PROJECT=stage')
	# Sometimes errors are seen in some pods but that's ok (?)
	s.send_until('oc get pods | grep -v Running | grep -v ^NAME | grep -v Completed | grep -v Error | wc -l','0',debug_command='oc get pods',cadence=5.0)
	s.pause_point('in cicd, look at template\n\nGet routes with oc get routes, then hit jenkins endpoint.\n\nLog in as developer/developer')
