import logging
from shutit_module import ShutItModule

from minishift_library import cicd


class shutit_minishift(ShutItModule):

	def build(self, shutit):
		# Assumes Mac, and brew.
		if shutit.send_and_get_output('uname') != 'Darwin':
			shutit.exit('not darwin')
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
		if not shutit.command_available('oc'):
			shutit.send('wget -nv https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-mac.zip')
			shutit.send('unzip openshift-origin-client-tools-v3.11.0-0cbc58b-mac.zip')
			wd = shutit.send_and_get_output('pwd')
			shutit.login(command='sudo su', password=pw)
			shutit.send('mv ' + wd + '/oc /usr/local/bin')
			shutit.send('mv ' + wd + '/kubectl /usr/local/bin')
			shutit.send('rm ' + wd + '/openshift-origin-client-tools-v3.11.0-0cbc58b-mac.zip')
			shutit.logout()
			shutit.pause_point('')
		shutit.send('brew cask install --force minishift')
		shutit.send('minishift profile set minishift')
		if shutit.send_and_get_output('''minishift status  | grep ^Minishift | awk {'print $2'}''') == 'Running':
			shutit.pause_point('minishift already running, either CTRL-] to continue with it, or CTRL-Q to quit and run minishift delete to remove before re-running')
		shutit.send('minishift start')
		shutit.send('eval $(minishift oc-env)')
		minishift_ip = shutit.send_and_get_output('minishift ip')
		shutit.log('\n\nminishift ip is: ' + minishift_ip + '\n\n... go to: \n\nhttps://' + minishift_ip + ':8443/console\n\nto see the console',logging.CRITICAL)
		shutit.pause_point('\n\nminishift ip is: ' + minishift_ip + '\n\n... go to: \n\nhttps://' + minishift_ip + ':8443/console\n\nto see the console')

		return True

	def get_config(self, shutit):
		for do in ('cicd',):
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
