# processor.py
from urllib.parse import urljoin
from logic.models import PageData, LinkItem


class DataProcessingUseCase:
    def execute(self, raw_data) -> PageData:
        # case 1: hl_runner が存在（従来挙動）
        if isinstance(raw_data, dict) and "hl_runner" in raw_data:
            return self._from_hl_runner(raw_data["hl_runner"])

        # case 2: raw_data が list（link_items 想定）
        if isinstance(raw_data, list):
            return PageData(
                title="Select dict type",
                base_url="",
                content=[],
                links=[],
            )

        # case 3: それ以外（何も取れない）
        return self._from_link_items(raw_data)

    # ----------------------------
    # 内部処理
    # ----------------------------
    def _from_hl_runner(self, hl_runner: list) -> PageData:
        body = self._find_value(hl_runner, "body", {})
        link_items = self._find_value(hl_runner, "link_items", {})

        base_url = body.get("url", "")
        links = self._extract_links(
            link_items.get("html", []),
            base_url,
        )

        return PageData(
            title=body.get("title", "No Title"),
            base_url=base_url,
            content=body.get("html", []),
            links=links,
        )

    def _from_link_items(self, raw_data: dict) -> PageData:
        # body がない前提なので最低限だけ
        base_url = raw_data.get("url", "")
        links = self._extract_links(
            raw_data.get("html", []),
            base_url,
        )

        return PageData(
            title=raw_data.get("title", "No Title"),
            base_url=base_url,
            content=raw_data.get("html", []),
            links=links,
        )

    def _extract_links(
        self, html_items: list, base_url: str
    ) -> list[LinkItem]:
        processed_links = []
        seen_urls = set()

        for item in html_items:
            if not isinstance(item, dict):
                continue

            original_url = item.get("url", "")
            if not original_url or original_url.startswith("#"):
                continue

            abs_url = urljoin(base_url, original_url)

            if abs_url in seen_urls:
                continue

            processed_links.append(
                LinkItem(
                    text=item.get("text", "").strip(),
                    original_url=original_url,
                    absolute_url=abs_url,
                )
            )
            seen_urls.add(abs_url)

        return processed_links

    def _find_value(self, items: list, key: str, default):
        for item in items:
            if item.get("key") == key:
                return item.get("value", default)
        return default
