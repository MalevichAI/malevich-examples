ARG mode=python
ARG branch

FROM pogrebnoijak/julius_export_${mode}:0.1
# FROM julius_export_python

ENV GIT_BRANCH ${branch}

RUN apt-get install -y build-essential curl
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements.txt requirements.txt
RUN if test -e requirements.txt; then pip install --no-cache-dir -r requirements.txt; fi

COPY apps ./apps