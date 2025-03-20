docker run -d --gpus=all -v /mnt:/mnt -p 11434:11434 --name ollama ollama/ollama
sleep 30
docker exec -it ollama ollama run llama3.1


set CMAKE_ARGS="-DLLAMA_CUBLAS=on" && set FORCE_CMAKE=1 && pip install --no-cache-dir llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124