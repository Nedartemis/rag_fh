echo "SETUP 'PYTHONPATH'"
export PYTHONPATH="${PYTHONPATH}:${PWD}"
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

echo "SETUP KEYS"
source ./keys.sh

echo "SETUP virtual env"
source .venv/bin/activate