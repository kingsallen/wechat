import sensorsanalytics
from setting import settings
import conf.common as const


# 从神策分析配置页面中获取数据接收的 URL
SA_SERVER_URL = settings['sensors_url']

# 初始化一个 Consumer，用于数据发送
# DefaultConsumer 是同步发送数据，因此不要在任何线上的服务中使用此 Consumer
consumer = sensorsanalytics.AsyncBatchConsumer(SA_SERVER_URL, request_timeout=3000)
# 使用 Consumer 来构造 SensorsAnalytics 对象
sa = sensorsanalytics.SensorsAnalytics(consumer)







