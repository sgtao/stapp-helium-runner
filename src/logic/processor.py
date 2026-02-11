# processor.py
from urllib.parse import urljoin
from logic.models import PageData, LinkItem


class DataProcessingUseCase:
    def execute(self, raw_data: dict) -> PageData:
        # 1. YAML構造の解釈 (F-01)
        body = next(
            item["value"]
            for item in raw_data["hl_runner"]
            if item["key"] == "body"
        )
        link_items = next(
            item["value"]
            for item in raw_data["hl_runner"]
            if item["key"] == "link_items"
        )

        base_url = body.get("url", "")

        # 2. リンクの抽出と正規化 (F-10, F-11)
        processed_links = []
        seen_urls = set()

        for item in link_items.get("html", []):
            original_url = item.get("url", "")
            # アンカー(#)のみのリンクはクロール対象外として処理（任意）
            if original_url.startswith("#"):
                continue

            abs_url = urljoin(base_url, original_url)

            if abs_url not in seen_urls:
                processed_links.append(
                    LinkItem(
                        text=item.get("text", "").strip(),
                        original_url=original_url,
                        absolute_url=abs_url,
                    )
                )
                seen_urls.add(abs_url)

        return PageData(
            title=body.get("title", "No Title"),
            base_url=base_url,
            content=body.get("html", []),
            links=processed_links,
        )
