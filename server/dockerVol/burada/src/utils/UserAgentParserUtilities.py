from ua_parser import Result as UaResult ,parse as ua_parse
from typing import Optional

class Result(UaResult):
    """Custom Result class to add additional fields."""
    def __init__(self, is_mobile: bool=False, is_bot: bool=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_mobile = is_mobile
        self.is_bot = is_bot

    def __repr__(self) -> str:
        """Custom representation to include is_mobile and is_bot."""
        return f"Result(ua_string={self.user_agent}, os={self.os}, device={self.device}, is_mobile={self.is_mobile}, is_bot={self.is_bot})"

def _check_is_mobile(user_agent: str) -> bool:
    """Check if the user agent is mobile."""
    ua = user_agent.lower()
    return any(m in ua for m in ['mobile', 'android', 'iphone', 'ipad', 'xiaomi', 'huawei', 'heytap', 'oppo', 'realme', 'samsung', 'vivo', 'silk', 'samsungbrowser', 'windows phone', 'windows mobile', 'blackberry', 'iemobile', 'opera mini', 'ucweb', 'j2me', 'midp', 'wap'])

def _check_is_bot(user_agent: str) -> bool:
    """Check if the user agent is a bot."""
    ua = user_agent.lower()
    return any(b in ua for b in ['bot', 'spider', 'crawl'])

def parse(user_agent: str) -> Result:
    """Parse the user agent string and enrich with is_mobile and is_bot."""
    parsed = ua_parse(user_agent)
    result = Result(user_agent=parsed.user_agent, os=parsed.os,  device=parsed.device, string=parsed.string, is_mobile=_check_is_mobile(user_agent), is_bot=_check_is_bot(user_agent))
    return result
