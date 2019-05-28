import logging
from shutit_module import ShutItModule

from minishift_library import cicd
from minishift_library import staticip
from minishift_library import kopf
from minishift_library import helmflux
from minishift_library import networkpolicy


class shutit_minishift(ShutItModule):

	def build(self, shutit):
		# Assumes Mac, and brew.
		platform = shutit.send_and_get_output('uname')
		if platform == 'Darwin':
			try:
				pw = open('secret').read().strip()
			except IOError:
				shutit.log('''\n================================================================================\nWARNING! IF THIS DOES NOT WORK YOU MAY NEED TO SET UP A 'secret' FILE IN THIS FOLDER!\n================================================================================''',level=logging.CRITICAL)
				pw = 'nopass'
			shutit.send('brew install --force docker-machine-driver-xhyve')
			shutit.login(command='sudo su', password=pw)
			shutit.send('sudo chown root:wheel $(brew --prefix)/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve')
			shutit.send('sudo chmod u+s $(brew --prefix)/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve')
			shutit.logout()
			shutit.send('brew cask install --force minishift || brew cast upgrade --force minishift')
			shutit.send('minishift start --cpus 4 --memory 18GB')
			shutit.send('minishift profile set minishift')
			if shutit.send_and_get_output('''minishift status  | grep ^Minishift | awk {'print $2'}''') == 'Running':
				shutit.pause_point('minishift already running, either CTRL-] to continue with it, or CTRL-Q to quit and run minishift delete to remove before re-running')
		elif platform == 'Linux':
			# See: https://www.novatec-gmbh.de/en/blog/getting-started-minishift-openshift-origin-one-vm/
			# Going to assume it's already there.
			if not shutit.command_available('minishift'):
				shutit.pause_point('Need to install minishift, see: https://www.novatec-gmbh.de/en/blog/getting-started-minishift-openshift-origin-one-vm/')
			shutit.send('minishift start --cpus 4 --memory 12GB --vm-driver virtualbox')
			shutit.send('minishift profile set minishift')
			if shutit.send_and_get_output('''minishift status  | grep ^Minishift | awk {'print $2'}''') == 'Running':
				shutit.pause_point('minishift already running, either CTRL-] to continue with it, or CTRL-Q to quit and run minishift delete to remove before re-running')
		if not shutit.command_available('oc'):
			shutit.send('wget -nv https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-mac.zip')
			shutit.multisend('unzip openshift-origin-client-tools-v3.11.0-0cbc58b-mac.zip',{'replace':'y'})
			wd = shutit.send_and_get_output('pwd')
			shutit.login(command='sudo su', password=pw)
			shutit.send('mv ' + wd + '/oc /usr/local/bin')
			shutit.send('mv ' + wd + '/kubectl /usr/local/bin')
			shutit.send('rm ' + wd + '/openshift-origin-client-tools-v3.11.0-0cbc58b-mac.zip')
			shutit.logout()
			shutit.pause_point('')
		shutit.send('eval $(minishift oc-env)')
		minishift_ip = shutit.send_and_get_output('minishift ip')
		shutit.pause_point('\n\nminishift ip is: ' + minishift_ip + '\n\n... go to: \n\nhttps://' + minishift_ip + ':8443/console\n\nto see the console')
		if shutit.cfg[self.module_id]['do_cicd']:
			cicd.do_cicd(shutit)
		if shutit.cfg[self.module_id]['do_staticip']:
			staticip.do_staticip(shutit)
		if shutit.cfg[self.module_id]['do_kopf']:
			kopf.do_kopf(shutit)
		if shutit.cfg[self.module_id]['do_helmflux']:
			helmflux.do_helmflux(shutit)
		if shutit.cfg[self.module_id]['do_networkpolicy']:
			networkpolicy.do_networkpolicy(shutit)
		return True

	def get_config(self, shutit):
		for do in ('cicd','staticip','kopf','helmflux','networkpolicy',):
			shutit.get_config(self.module_id,'do_' + do,boolean=True,default=False)
		return True

def module():
		return shutit_minishift(
			'shutit-minishift.shutit_minishift.shutit_minishift', 1514628579.0001,
			description='',
			maintainer='',
			delivery_methods=['bash'],
			depends=['shutit.tk.setup']
		)
