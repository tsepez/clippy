#!/bin/bash -eu

set -o pipefail

DIRNAME="$(dirname "${BASH_SOURCE[0]}")"
BASENAME="$(basename "${BASH_SOURCE[0]}")"
VENV="${DIRNAME}/venv"

if [[ ! -d "${VENV}" ]]; then
  echo "Virtualenv not found. Creating virtualenv"
  python3 -m venv "${VENV}"
  source "${VENV}/bin/activate"
  echo "Installing dependencies into virtualenv"
  ${VENV}/bin/python -m pip install -r "${DIRNAME}/requirements.txt"
fi

exec "${VENV}/bin/python3" "${DIRNAME}/${BASENAME}.py" "$@"
