from prefect import flow, task

@task
def extract():
    ...

@task
def transform(data):
    ...

@task
def load(data):
    ...

@flow
def real_estate_flow():
    raw_data = extract()
    clean_data = transform(raw_data)
    load(clean_data)
