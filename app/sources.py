from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceConfig:
    slug: str
    name: str
    source_type: str
    url: str
    description: str = ""


SOURCE_LIST = [
    SourceConfig("kamchatinfo", "kamchatinfo.com", "website", "https://kamchatinfo.com", "Камчатка сегодня"),
    SourceConfig("kam24", "kam24.ru", "website", "https://kam24.ru", "Кам24"),
    SourceConfig("kamtoday", "kamtoday.ru", "website", "https://kamtoday.ru", "Камчатка сегодня"),
    SourceConfig("kam_kray", "kam-kray.ru", "website", "https://kam-kray.ru", "Камчатский край"),
    SourceConfig("ria_kamchatka", "RIA Новости", "website", "https://ria.ru/location_Kamchatskijj_krajj/", "РИА Новости"),
    SourceConfig("poluostrov_kamchatka", "Полуостров Камчатка", "website", "https://www.poluostrov-kamchatka.ru", "Полуостров Камчатка"),
    SourceConfig("bezformata_elizovo", "Bezformata", "website", "https://elizovo.bezformata.com/?amp=1", "Елизово без формата"),
    SourceConfig("lenta_elizovo", "Lenta.ru", "website", "https://lenta.ru/tags/geo/elizovo/", "Лента.ру"),
    SourceConfig("kaminform", "Kaminform", "website", "https://kaminform.online/news/segodnja-v-kamchatskom-krae/novosti-elizovo", "КамИнформ"),
    SourceConfig("gosuslugi_elizovo", "Госуслуги Елизово", "website", "https://elizovo.gosuslugi.ru/dlya-zhiteley/novosti-i-reportazhi/?cur_cc=45&filter%5B45%5D%5BCategory%5D=13", "Госуслуги Елизово"),
    SourceConfig("chpkamchatka", "ЧП Камчатка", "telegram", "https://t.me/chpkamchatka", "Telegram channel"),
    SourceConfig("bezfiltra_41", "Без фильтра 41", "telegram", "https://t.me/bezfiltra_41", "Telegram channel"),
    SourceConfig("massmediakam", "Массмедиа Кам", "telegram", "https://t.me/massmediakam", "Telegram channel"),
    SourceConfig("kamchatka_smi", "Камчатка СМИ", "telegram", "https://t.me/kamchatka_smi", "Telegram channel"),
    SourceConfig("new_elizovo", "Новый Елизово", "telegram", "https://t.me/new_elizovo", "Telegram channel"),
    SourceConfig("kamgov41", "Камчатский Gov", "telegram", "https://t.me/kamgov41", "Telegram channel"),
    SourceConfig("kamchatskaya_zhizn", "Камчатская жизнь", "telegram", "https://t.me/kamchatskaya_zhizn", "Telegram channel"),
    SourceConfig("kamreporter", "Камчатский репортер", "telegram", "https://t.me/kamreporter", "Telegram channel"),
    SourceConfig("max_kam24ru", "MAX: kam24ru", "max", "https://max.ru/kam24ru", "MAX"),
    SourceConfig("max_kamchatka_now", "MAX: kamchatka_now", "max", "https://max.ru/kamchatka_now", "MAX"),
    SourceConfig("max_kamreporter", "MAX: kamreporter", "max", "https://max.ru/kamreporter", "MAX"),
    SourceConfig("vk_overhear_elizovo", "VK: overhear_elizovo", "vk", "https://vk.ru/overhear_elizovo", "VK group"),
    SourceConfig("vk_elizovo_group_41", "VK: elizovo_group_41", "vk", "https://vk.ru/elizovo_group_41", "VK group"),
    SourceConfig("vk_razeb41", "VK: razeb41", "vk", "https://vk.ru/razeb41", "VK group"),
    SourceConfig("vk_infokamch", "VK: infokamch", "vk", "https://vk.ru/infokamch", "VK group"),
    SourceConfig("vk_kamgov41", "VK: kamgov41", "vk", "https://vk.ru/kamgov41", "VK group"),
    SourceConfig("vk_kamchatrip", "VK: kamchatrip", "vk", "https://vk.ru/kamchatrip", "VK group"),
    SourceConfig("vk_kamotzovik", "VK: kamotzovik", "vk", "https://vk.ru/kamotzovik", "VK group"),
]


def get_sources() -> list[SourceConfig]:
    return list(SOURCE_LIST)


def get_sources_by_type(source_type: str) -> list[SourceConfig]:
    return [source for source in SOURCE_LIST if source.source_type == source_type]
