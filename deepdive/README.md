针对deepdive信息抽取部分过慢的问题，这里采用ltp替换原先deepdive默认的斯坦福NLP提取包

提出两种解决方法，demo_source 是deepdive官方提供的原始流程代码

demo_version_1和demo_version_2是两种优化方法,demo_version_3是多种关系抽取demo


其中deepdive有打标环节，需要人工定义规则，为此为了减轻工作量，可以先运行脚本text_statistics.py得到一些文本的统计信息，其输入是文本和label，输出是rule_reference.txt

备用下载链接：https://pan.baidu.com/s/1JR7L_pCIXFLLjrbRSOJw9A 提取码：obn7

更多解析：

https://blog.csdn.net/weixin_42001089/article/details/90749577

https://blog.csdn.net/weixin_42001089/article/details/91388707
