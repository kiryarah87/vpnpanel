import base64
from urllib.parse import quote

from app.models.credential import ClientCredential
from app.models.enum import ProtocolType
from app.schemas.inbound import InboundRead


class LinkGenerator:
    """Генератор ссылок для импорта в VPN клиенты"""

    def generate(
        self,
        inbounds: list[InboundRead],
        credential: ClientCredential,
        server_host: str,
    ) -> str:
        links = []

        for inbound in inbounds:
            if not inbound.is_active:
                continue

            if inbound.protocol == ProtocolType.VLESS_TCP_REALITY:
                link = self._vless_reality_link(
                    inbound, credential.xray_uuid, server_host, "tcp"
                )
                if link:
                    links.append(link)

            elif inbound.protocol == ProtocolType.VLESS_XHTTP_REALITY:
                link = self._vless_reality_link(
                    inbound, credential.xray_uuid, server_host, "xhttp"
                )
                if link:
                    links.append(link)

            elif inbound.protocol == ProtocolType.HYSTERIA2:
                link = self._hysteria2_link(
                    inbound, credential.hysteria2_password, server_host
                )
                if link:
                    links.append(link)

            elif inbound.protocol == ProtocolType.NAIVEPROXY:
                link = self._naiveproxy_link(inbound, credential, server_host)
                if link:
                    links.append(link)

        content = "\n".join(links)
        return base64.b64encode(content.encode()).decode()

    def _vless_reality_link(
        self, inbound, uuid: str, host: str, network: str
    ) -> str | None:
        if not inbound.reality_public_key:
            return None

        flow = "xtls-rprx-vision" if network == "tcp" else ""
        params = {
            "type": network,
            "security": "reality",
            "pbk": inbound.reality_public_key or "",
            "sid": inbound.reality_short_id or "",
            "sni": inbound.sni or "",
            "fp": "chrome",
        }
        if flow:
            params["flow"] = flow

        query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        tag = quote(str(inbound.tag or ""))
        return f"vless://{uuid}@{host}:{inbound.port}?{query}#{tag}"

    def _hysteria2_link(self, inbound, password: str, host: str) -> str | None:
        tag = quote(str(inbound.tag or ""))
        sni = inbound.sni or host
        return (
            f"hysteria2://{password}@{host}:{inbound.port}?sni={sni}&insecure=1#{tag}"
        )

    def _naiveproxy_link(self, inbound, credential, host: str) -> str | None:
        if not credential.naiveproxy_username or not credential.naiveproxy_password:
            return

        tag = quote(str(inbound.tag or ""))
        username = quote(credential.naiveproxy_username)
        password = quote(credential.naiveproxy_password)
        return f"naive+https://{username}:{password}@{host}:{inbound.port}#{tag}"
