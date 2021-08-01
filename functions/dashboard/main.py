import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    request_method = req.method
    resources = req.route_params.get("resources")
    resource_id = req.route_params.get("id")
    return func.HttpResponse(f"{request_method}, {resources}, {resource_id}", status_code=200)
