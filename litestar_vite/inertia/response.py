from __future__ import annotations

import itertools
from mimetypes import guess_type
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, Callable, Iterable, Mapping, MutableMapping, cast

from litestar import Litestar, MediaType, Request
from litestar.exceptions import ImproperlyConfiguredException
from litestar.response import Template
from litestar.response.base import ASGIResponse
from litestar.serialization import get_serializer
from litestar.status_codes import HTTP_200_OK
from litestar.utils.deprecation import warn_deprecation
from litestar.utils.helpers import get_enum_string_value

from litestar_vite.inertia._utils import get_headers
from litestar_vite.inertia.types import InertiaHeaderType
from litestar_vite.plugin import VitePlugin

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.background_tasks import BackgroundTask, BackgroundTasks
    from litestar.connection import Request
    from litestar.connection.base import AuthT, StateT, UserT
    from litestar.datastructures.cookie import Cookie
    from litestar.types import ResponseCookies


class InertiaResponse(Template):
    """Inertia Response"""

    def __init__(
        self,
        props: MutableMapping[str, Any] | None = None,
        template_name: str | None = None,
        *,
        template_str: str | None = None,
        background: BackgroundTask | BackgroundTasks | None = None,
        context: dict[str, Any] | None = None,
        cookies: ResponseCookies | None = None,
        encoding: str = "utf-8",
        headers: dict[str, Any] | None = None,
        media_type: MediaType | str | None = None,
        status_code: int = HTTP_200_OK,
    ) -> None:
        """Handle the rendering of a given template into a bytes string.

        Args:
            props: a set of data to render into a response
            template_name: Path-like name for the template to be rendered, e.g. ``index.html``.
            template_str: A string representing the template, e.g. ``tmpl = "Hello <strong>World</strong>"``.
            background: A :class:`BackgroundTask <.background_tasks.BackgroundTask>` instance or
                :class:`BackgroundTasks <.background_tasks.BackgroundTasks>` to execute after the response is finished.
                Defaults to ``None``.
            context: A dictionary of key/value pairs to be passed to the temple engine's render method.
            cookies: A list of :class:`Cookie <.datastructures.Cookie>` instances to be set under the response
                ``Set-Cookie`` header.
            encoding: Content encoding
            headers: A string keyed dictionary of response headers. Header keys are insensitive.
            media_type: A string or member of the :class:`MediaType <.enums.MediaType>` enum. If not set, try to infer
                the media type based on the template name. If this fails, fall back to ``text/plain``.
            status_code: A value for the response HTTP status code.
        """
        super().__init__(
            template_name=template_name,
            template_str=template_str,
            background=background,
            context=context,
            cookies=cookies,
            encoding=encoding,
            headers=headers,
            media_type=media_type,
            status_code=status_code,
        )
        self._props = props
        self.headers.update(
            get_headers(InertiaHeaderType(enabled=True)),
        )

    def to_asgi_response(
        self,
        app: Litestar | None,
        request: Request[UserT, AuthT, StateT],
        *,
        background: BackgroundTask | BackgroundTasks | None = None,
        cookies: Iterable[Cookie] | None = None,
        encoded_headers: Iterable[tuple[bytes, bytes]] | None = None,
        headers: dict[str, str] | None = None,
        is_head_response: bool = False,
        media_type: MediaType | str | None = None,
        status_code: int | None = None,
        type_encoders: Mapping[Any, Callable[[Any], Any]] | None = None,
    ) -> ASGIResponse:
        if app is not None:
            warn_deprecation(
                version="2.1",
                deprecated_name="app",
                kind="parameter",
                removal_in="3.0.0",
                alternative="request.app",
            )
        is_inertia = getattr(request, "is_inertia", False)
        headers = {**headers, **self.headers} if headers is not None else self.headers
        cookies = self.cookies if cookies is None else itertools.chain(self.cookies, cookies)
        type_encoders = (
            {**type_encoders, **(self.response_type_encoders or {})} if type_encoders else self.response_type_encoders
        )
        plugin = request.app.plugins.get(VitePlugin)
        template_engine = plugin.template_config.to_engine()
        if not template_engine:
            msg = "Template engine is not configured"
            raise ImproperlyConfiguredException(msg)
        if is_inertia:
            media_type = get_enum_string_value(self.media_type or media_type or MediaType.JSON)
            body = self.render(self.content, media_type, get_serializer(type_encoders))
        else:
            media_type = self.media_type or media_type
            if not media_type:
                if self.template_name:
                    suffixes = PurePath(self.template_name).suffixes
                    for suffix in suffixes:
                        if _type := guess_type(f"name{suffix}")[0]:
                            media_type = _type
                            break
                    else:
                        media_type = MediaType.TEXT
                else:
                    media_type = MediaType.HTML
            context = self.create_template_context(request)
            if self.template_str is not None:
                body = template_engine.render_string(self.template_str, context).encode(self.encoding)
            else:
                # cast to str b/c we know that either template_name cannot be None if template_str is None
                template = template_engine.get_template(cast("str", self.template_name))
                body = template.render(**context).encode(self.encoding)

        return ASGIResponse(
            background=self.background or background,
            body=body,
            cookies=cookies,
            encoded_headers=encoded_headers,
            encoding=self.encoding,
            headers=headers,
            is_head_response=is_head_response,
            media_type=media_type,
            status_code=self.status_code or status_code,
        )
