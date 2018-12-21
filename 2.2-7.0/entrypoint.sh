#!/bin/sh

set -e

if [ "${1}" == "unit" ] || [ "${1}" == "static" ] || [ "${1}" == "validate_m2_package" ] || [ "${1}" == "eqp" ]; then
	set -- python3 /m2test.py "$@"
fi

exec "$@"