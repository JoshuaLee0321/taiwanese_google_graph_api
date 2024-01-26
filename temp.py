from scripts.services import *
from threading import Thread


if __name__ == "__main__":
  result = dict()
  drv = init_driver()
  args = (drv, "1", 'tai', result,)
  print(args)
  thread_tai = Thread(target=get_queryVideo, args=args)
  
  
            # result_tai = get_queryVideo(this.taidrv, queryDict['tai'])
            # result_en = get_queryVideo(this.endrv, queryDict['en'])
            # result_zh = get_queryVideo(this.zhdrv, queryDict["zh"])
  thread_tai.start()

  thread_tai.join()

  print(result)
