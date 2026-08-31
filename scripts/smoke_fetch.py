import logging
from src.utils.config import get_fetcher_config
from src.retrieval.fetch import fetch_page


def main():
  logging.basicConfig(level=logging.WARNING)

  cfg = get_fetcher_config()
  url1 = "https://cloud.tencent.com/developer/article/2587032"
  url2 = "https://www.cnblogs.com/zrq96/p/18966394"
  url3 = "https://thisisnotexistweb/text"  #不可达的url
  print("开始第一次测试（使用可达的url）")
  res1 = fetch_page(url1,timeout=cfg["timeout"],user_agent=cfg["user_agent"])
  if res1 and res1 != "":
    print("第一次测试成功!返回有内容")
  else :
    print("测试失败")
  
  print("开始第二次测试（使用不同的可达url）")
  res2 = fetch_page(url2,timeout=cfg["timeout"],user_agent=cfg["user_agent"])
  if res2 and res2 != "":
    print("第二次测试成功!返回有内容")
  else :
    print("测试失败，返回内容为")

  print("开始第三次测试（使用不可达的url）")
  res3 = fetch_page(url3,timeout=cfg["timeout"],user_agent=cfg["user_agent"])
  if res3 and res3 != "":
    print("第三次测试失败，返回有内容")
  else :
    print("测试成功！无返回内容")

  print("测试完毕")


  return








if __name__=="__main__":
  main()



