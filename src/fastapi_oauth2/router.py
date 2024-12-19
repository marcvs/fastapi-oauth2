from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from starlette.requests import Request

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth2")


@router.get("/{provider}/authorize")
def authorize(request: Request, provider: str):
    if request.auth.ssr:
        return request.auth.clients[provider].authorization_redirect(request)
    return dict(url=request.auth.clients[provider].authorization_url(request))


@router.get("/{provider}/token")
async def token(request: Request, provider: str):
    logger.info(F"being called for provider {provider}")
    logger.info(F"going to call  request.auth.clients[provider]._state: [{request.auth.clients[provider]._state}]")
    logger.info(F" some info about: request.auth.clients[provider]: [{request.auth.clients[provider]}]")
    if request.auth.ssr:
        return await request.auth.clients[provider].token_redirect(request)
    return await request.auth.clients[provider].token_data(request)


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(request.base_url)
    response.delete_cookie("Authorization")
    return response
