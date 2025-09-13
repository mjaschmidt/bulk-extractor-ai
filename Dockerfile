# This is a comment. Docker ignores these lines.

# --- STAGE 1: THE FOUNDATION ---
# Every Dockerfile must start with a `FROM` instruction. It specifies the "base image"
# we are building on top of. Think of it as choosing the type of kitchen to start with.
# We are choosing an image from Docker Hub (a public library of images) called 'python'.
# - '3.11' specifies the exact Python version, ensuring consistency.
# - '-slim' is a variant of the Python image that is much smaller because it excludes
#   unnecessary components. This makes our final image more lightweight and efficient.
FROM python:3.11-slim

# --- STAGE 2: SETTING UP THE WORKSPACE ---
# The `WORKDIR` instruction sets the working directory for any subsequent `RUN`, `CMD`,
# `COPY`, etc., commands. It's like running `cd /app` inside the container's terminal.
# If the directory doesn't exist, Docker creates it for us. This is a best practice
# that keeps our project files organized in one place inside the container.
WORKDIR /app

# --- STAGE 3: INSTALLING DEPENDENCIES (THE SMART WAY) ---
# The `COPY` instruction copies files from your local machine (the "build context")
# into the container's filesystem.
# Here, we copy ONLY the requirements.txt file first.
# WHY? Docker builds images in layers. Each instruction creates a new layer. Docker is
# smart and will cache these layers. If a file hasn't changed, Docker will reuse the
# cached layer from a previous build instead of re-running the instruction.
# Since `requirements.txt` changes much less often than our source code, we copy it
# first. This means the time-consuming dependency installation step will be skipped
# in future builds unless we actually change our dependencies. This is a key optimization.
COPY requirements.txt .

# The `RUN` instruction executes a command inside the container's shell.
# We are chaining two commands with `&& \`. This ensures they run in a single layer,
# which is slightly more efficient.
# 1. `pip install uv`: We install our preferred package manager, `uv`.
# 2. `uv pip install --no-cache-dir -r requirements.txt`: We use `uv` to install all
#    the packages listed in requirements.txt. The `--no-cache-dir` flag tells pip
#    not to store the downloaded packages in a cache, which helps keep the final
#    image size smaller.
RUN pip install uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

# --- STAGE 4: ADDING YOUR APPLICATION CODE ---
# Now that the dependencies are installed, we copy the rest of our application files.
# If we change our Python code, Docker will only have to re-run this step and the
# ones after it, reusing the cached layer from the dependency installation.
# `COPY ./src ./src` copies our entire `src` directory into the `/app/src` directory
# inside the container.
COPY ./src ./src
COPY prompt.txt .
COPY meta_prompt.txt .

# --- STAGE 5: NETWORK CONFIGURATION ---
# The `EXPOSE` instruction is a form of documentation. It informs Docker that the
# container listens on the specified network port at runtime. It does NOT actually
# publish the port. It's a signal to the person running the container about which
# port they should map.
EXPOSE 8000

# --- STAGE 6: THE STARTUP COMMAND ---
# The `CMD` instruction provides the default command to execute when a container is
# started from this image. There can only be one `CMD` in a Dockerfile.
# We are using the "exec form" (`["executable", "param1", "param2"]`). This is the
# recommended best practice over the "shell form" (`CMD uvicorn src.api:app...`).
# WHY? The exec form makes our Uvicorn server the main process (PID 1) inside the
# container. This means it will correctly receive signals from Docker, like a stop
# signal, allowing for a graceful shutdown.
# - "uvicorn": The program to run.
# - "src.api:app": The path to our FastAPI app instance.
# - "--host", "0.0.0.0": This tells Uvicorn to listen on all available network interfaces
#   inside the container, not just localhost. This is essential for it to be reachable
#   from outside the container.
# - "--port", "8000": The port to listen on inside the container.
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]