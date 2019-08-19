#说明
针对deepdive信息抽取部分过慢的问题，这里采用ltp替换原先deepdive默认的斯坦福NLP提取包

提出两种解决方法，demo_source 是deepdive官方提供的原始流程代码

demo_version_1和demo_version_2是两种优化方法,demo_version_3是多种关系抽取demo

如果是基于python3的话需要改一下源码，可以直接将ddlib目录下的四个文件复制替换安装的ddlib

其中deepdive有打标环节，需要人工定义规则，为此为了减轻工作量，这里采用了自动提取规则，具体可以看Extraction_rules

更多解析：

https://blog.csdn.net/weixin_42001089/article/details/90749577

https://blog.csdn.net/weixin_42001089/article/details/91388707

#监督学习
deepdive是一个半监督的学习框架，关于关系抽取其实也有很多使用深度学习进行的全监督方式：
https://github.com/Mryangkaitong/Chinese_NRE
