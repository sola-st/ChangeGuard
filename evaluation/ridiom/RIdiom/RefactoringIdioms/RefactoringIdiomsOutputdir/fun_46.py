def get_graphql_response(
    *,
    settings,
    query,
    after = None,
    category_id = None,
):
    headers , variables  = {'Authorization': f'token {settings.input_token.get_secret_value()}'}, {'after': after, 'category_id': category_id}
    response = httpx.post(
        github_graphql_url,
        headers=headers,
        timeout=settings.httpx_timeout,
        json={"query": query, "variables": variables, "operationName": "Q"},
    )
    if response.status_code != 200:
        logging.error(
            f"Response was not 200, after: {after}, category_id: {category_id}"
        )
        logging.error(response.text)
        raise RuntimeError(response.text)
    data = response.json()
    if "errors" in data:
        logging.error(f"Errors in response, after: {after}, category_id: {category_id}")
        logging.error(response.text)
        raise RuntimeError(response.text)
    return data
