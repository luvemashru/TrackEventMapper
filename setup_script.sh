echo Creating Virtual Env and installing dependencies.....
python3 -m venv venv
source ./venv/bin/activate
echo Virtual Env creation successful
pip install poetry
poetry install
echo Dependencies Installed successfully
