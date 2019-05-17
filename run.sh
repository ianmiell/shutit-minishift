#!/bin/bash
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
if [[ ! -a "$SHUTIT" ]]
then
	echo "Must have shutit on path, eg export PATH=$PATH:/path/to/shutit_dir"
	exit 1
fi
function usage() {
	cat > /dev/stdout << END
$0 BUILD

Where BUILD is one of:

- cicd                     - Run CI/CD demo

END
}
BUILD=$1
shift
if [[ ${BUILD} = 'cicd' ]]
then
	git submodule init
	git submodule update
	$SHUTIT build --echo -d bash \
	    -s techniques.shutit_minikube.shutit_minikube do_cicd yes \
		"$@"
else
	usage
	exit 1
fi
if [[ $? != 0 ]]
then
	exit 1
fi
