echo 'PYTHON 3.11'
cd ./docker && docker build -f PythonDockerFile -t python3.11:v1.0.0 ./ && cd ../

echo 'Backend image'
cd ./docker && docker build -f BackendDockerFile -t manufacturing-back:v1.0.0 ./ && cd ../