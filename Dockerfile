FROM public.ecr.aws/lambda/python:3.10

# Copy function code. This copies EVERYTHING inside the app folder to the lambda root.
COPY ./app ${LAMBDA_TASK_ROOT}

WORKDIR ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["main.handler"]