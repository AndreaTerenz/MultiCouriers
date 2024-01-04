FROM python:3.11

RUN mkdir -p "/mcp"
WORKDIR "/mcp"

ADD Instances/ ./Instances/
ADD MILP/ ./MILP/
ADD Minizinc/ ./Minizinc/
ADD SAT_SMT/*.py ./SAT_SMT/
ADD res/ ./res/
ADD utils/ ./utils/
ADD mainMain.py .
ADD Pipfile .
ADD Pipfile.lock .

RUN pip install pipenv
RUN pipenv install

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get install --no-install-recommends -y minizinc

# Starting command
ENTRYPOINT ["pipenv", "run", "python", "mainMain.py"]
# Default starting arguments
CMD ["-m", "SMT", "-i", " 01"]