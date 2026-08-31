import logging
import httpx
import trafilatura
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def fetch_page(url:str,timeout:float = 10.0,user_agent:str = "") -> str:
  """抓取网页正文，三级降级"""
  headers = {"User-Agent":user_agent} if user_agent else {}

  #请求网页
  try:
    res = httpx.get(url,headers=headers,timeout=timeout,follow_redirects=True)
  except httpx.HTTPError as e:
    logger.warning("请求失败%s:%s，降级返回空串",url,e)  #采用惰性格式化，只有在真正输出时才拼接字符串
    return ""
  
  if res.status_code != 200:
    logger.warning("状态码%s，降级返回空串",res.status_code)
    return ""
  
  html = res.text

  #trafilatura提取
  try:
    content = trafilatura.extract(html,url=url)
  except Exception as e:
    content = None
    logger.warning("trafilatura提取失败%s:%s",url,e)
  
  if content and len(content) > 100:
    return content
  
  #降级为BeautifulSoup手工提取
  soup = BeautifulSoup(html,"html.parser")
  title = soup.title.string.strip() if soup.title and soup.title.string else ""
  paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
  text = title + "\n" + "\n".join(paragraphs)
  if text and len(text) > 100:
    return text
  
  #降级，返回空串
  logger.warning("%s提取正文失败（内容过短），返回空串",url)
  return ""



