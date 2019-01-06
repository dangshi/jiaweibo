### 项目架构
data后端数据层与web前端之间采用restful接口，即利用json数据进行交互。
* data目录存放后端代码
* web 目录存放前端代码
* doc 目录保存前后端交互接口
### 接口基本格式
```python
{
  "status": "OK",  # "OK" or "FAILED", 代表操作状态
  "msg":"",  #返回操作状态的详细信息, 例如操作成功，或者出错信息
  "result":{},  # 返回具体操作返回的数据，格式可以为dict,list
}
```
