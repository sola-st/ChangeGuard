async def __call__(self, scope, receive, send):
    dependency_exception = None
    async with AsyncExitStack() as stack:
        scope[self.context_name] = stack
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            dependency_exception = e
            raise e
    if dependency_exception:
        raise dependency_exception
