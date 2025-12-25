# das 会话获取相关示例
文档地址： https://next.api.alibabacloud.com/document/DAS/2020-01-16/GetMySQLAllSessionAsync
```
# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys

from typing import List

from alibabacloud_das20200116.client import Client as DAS20200116Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_das20200116 import models as das20200116_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> DAS20200116Client:
        """
        Initialize the Client with the credentials
        @return: Client
        @throws Exception
        """
        # It is recommended to use the default credential. For more credentials, please refer to: https://www.alibabacloud.com/help/en/alibaba-cloud-sdk-262060/latest/configure-credentials-378659.
        credential = CredentialClient()
        config = open_api_models.Config(
            credential=credential
        )
        # See https://api.alibabacloud.com/product/DAS.
        config.endpoint = f'das.cn-shanghai.aliyuncs.com'
        return DAS20200116Client(config)

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        client = Sample.create_client()
        get_my_sqlall_session_async_request = das20200116_models.GetMySQLAllSessionAsyncRequest(
            instance_id='pc-xxx'
            # node_id='pi-xxx' # 只有polardb才需要提供次参数
            # result_id='xxxx' # 这是异步接口，第二次调用传入次参数
        )
        runtime = util_models.RuntimeOptions()
        try:
            # Copy the code to run, please print the return value of the API by yourself.
            await client.get_my_sqlall_session_async_with_options_async(get_my_sqlall_session_async_request, runtime)
        except Exception as error:
            # Only a printing example. Please be careful about exception handling and do not ignore exceptions directly in engineering projects.
            # print error message
            print(error.message)
            # Please click on the link below for diagnosis.
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    Sample.main(sys.argv[1:])
```

## 返回数据结构
```
{
  "Message": "Successful",
  "RequestId": "8AABDD91-9D41-5BC3-B596-92E4BEB6DE0E",
  "Data": {
    "State": "SUCCESS",
    "Complete": true,
    "SessionData": {
      "UserStats": [
        {
          "TotalCount": 70,
          "ActiveCount": 0,
          "ThreadIdList": [
            300303599,
            300303952,
            300303671,
            300303387
            ...
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "user_idn_pro_listing_legal"
        },
        {
          "TotalCount": 1,
          "ActiveCount": 0,
          "ThreadIdList": [
            12695824
          ],
          "UserList": [
            "dba_rds"
          ],
          "Key": "dba_rds"
        }
      ],
      "TotalSessionCount": 71,
      "ClientStats": [
        {
          "TotalCount": 10,
          "ActiveCount": 0,
          "ThreadIdList": [
            300303599,
            300303952,
            568745819,
            568745531,
            300303726,
            568745203,
            300303641,
            300304005,
            568745513,
            568745772
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "10.200.2.44"
        },
        {
          "TotalCount": 10,
          "ActiveCount": 0,
          "ThreadIdList": [
            300303671,
            300303387,
            568745751,
            568745742,
            300303702,
            568745269,
            300303619,
            568744147,
            300303519,
            300303248
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "10.200.2.33"
        },
        {
          "TotalCount": 10,
          "ActiveCount": 0,
          "ThreadIdList": [
            300304063,
            568745611,
            568745392,
            568745663,
            568745836,
            300303407,
            300303550,
            300303967,
            300303743,
            300303395
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "10.200.1.9"
        },
        {
          "TotalCount": 10,
          "ActiveCount": 0,
          "ThreadIdList": [
            568744430,
            568747168,
            568745556,
            300303010,
            568746181,
            568746389,
            568745322,
            568746646,
            568743866,
            300304019
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "10.200.1.32"
        },
        {
          "TotalCount": 10,
          "ActiveCount": 0,
          "ThreadIdList": [
            300303780,
            300304232,
            300303737,
            568745943,
            300303842,
            300303994,
            300303675,
            568745546,
            300304200,
            300304357
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "10.200.1.42"
        },
        {
          "TotalCount": 10,
          "ActiveCount": 0,
          "ThreadIdList": [
            568746028,
            568745962,
            300304179,
            568746401,
            568746081,
            300304138,
            300304234,
            300304547,
            568745744,
            568746137
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "10.200.2.47"
        },
        {
          "TotalCount": 10,
          "ActiveCount": 0,
          "ThreadIdList": [
            300303656,
            568745688,
            300303999,
            568745967,
            568745594,
            300303771,
            300303649,
            300303739,
            300303546,
            568745541
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "10.200.1.46"
        },
        {
          "TotalCount": 1,
          "ActiveCount": 0,
          "ThreadIdList": [
            12695824
          ],
          "UserList": [
            "dba_rds"
          ],
          "Key": "10.1.90.30"
        }
      ],
      "MaxActiveTime": 0,
      "ActiveSessionCount": 0,
      "SessionList": [
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 3,
          "Client": "10.200.2.44",
          "SessionId": 300303599
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.44",
          "SessionId": 300303952
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.33",
          "SessionId": 300303671
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.33",
          "SessionId": 300303387
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.2.47",
          "SessionId": 568746028
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 6,
          "Client": "10.200.1.46",
          "SessionId": 300303656
        },
        {
          "User": "dba_rds",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "",
          "Time": 6,
          "Client": "10.1.90.30",
          "SessionId": 12695824
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.9",
          "SessionId": 300304063
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 1503,
          "Client": "10.200.1.32",
          "SessionId": 568744430
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.9",
          "SessionId": 568745611
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.44",
          "SessionId": 568745819
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 220,
          "Client": "10.200.1.32",
          "SessionId": 568747168
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 5,
          "Client": "10.200.1.46",
          "SessionId": 568745688
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 973,
          "Client": "10.200.1.32",
          "SessionId": 568745556
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 1287,
          "Client": "10.200.1.32",
          "SessionId": 300303010
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.42",
          "SessionId": 300303780
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.1.46",
          "SessionId": 300303999
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.33",
          "SessionId": 568745751
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 783,
          "Client": "10.200.1.46",
          "SessionId": 568745967
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.1.42",
          "SessionId": 300304232
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 2,
          "Client": "10.200.2.47",
          "SessionId": 568745962
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 683,
          "Client": "10.200.1.32",
          "SessionId": 568746181
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.1.9",
          "SessionId": 568745392
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 588,
          "Client": "10.200.1.32",
          "SessionId": 568746389
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.42",
          "SessionId": 300303737
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.9",
          "SessionId": 568745663
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 1081,
          "Client": "10.200.1.32",
          "SessionId": 568745322
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.46",
          "SessionId": 568745594
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.33",
          "SessionId": 568745742
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.9",
          "SessionId": 568745836
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.1.42",
          "SessionId": 568745943
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 2,
          "Client": "10.200.1.9",
          "SessionId": 300303407
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.33",
          "SessionId": 300303702
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 467,
          "Client": "10.200.1.32",
          "SessionId": 568746646
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.1.42",
          "SessionId": 300303842
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.9",
          "SessionId": 300303550
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.46",
          "SessionId": 300303771
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.2.47",
          "SessionId": 300304179
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 1,
          "Client": "10.200.1.46",
          "SessionId": 300303649
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.44",
          "SessionId": 568745531
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.2.47",
          "SessionId": 568746401
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.44",
          "SessionId": 300303726
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 0,
          "Client": "10.200.2.44",
          "SessionId": 568745203
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 5,
          "Client": "10.200.2.33",
          "SessionId": 568745269
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.44",
          "SessionId": 300303641
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.33",
          "SessionId": 300303619
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.47",
          "SessionId": 568746081
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 2,
          "Client": "10.200.2.47",
          "SessionId": 300304138
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 0,
          "Client": "10.200.2.33",
          "SessionId": 568744147
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.2.47",
          "SessionId": 300304234
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.33",
          "SessionId": 300303519
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.46",
          "SessionId": 300303739
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.44",
          "SessionId": 300304005
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 1,
          "Client": "10.200.1.46",
          "SessionId": 300303546
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.1.42",
          "SessionId": 300303994
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 14,
          "Client": "10.200.1.32",
          "SessionId": 568743866
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 5,
          "Client": "10.200.2.47",
          "SessionId": 300304547
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 2,
          "Client": "10.200.2.47",
          "SessionId": 568745744
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.47",
          "SessionId": 568746137
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 0,
          "Client": "10.200.1.42",
          "SessionId": 300303675
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 0,
          "Client": "10.200.1.42",
          "SessionId": 568745546
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 0,
          "Client": "10.200.2.33",
          "SessionId": 300303248
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.42",
          "SessionId": 300304200
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.9",
          "SessionId": 300303967
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 4,
          "Client": "10.200.1.9",
          "SessionId": 300303743
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.2.44",
          "SessionId": 568745513
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 5,
          "Client": "10.200.1.46",
          "SessionId": 568745541
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 7,
          "Client": "10.200.1.42",
          "SessionId": 300304357
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 5,
          "Client": "10.200.2.44",
          "SessionId": 568745772
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 2,
          "Client": "10.200.1.9",
          "SessionId": 300303395
        },
        {
          "User": "user_idn_pro_listing_legal",
          "Command": "Sleep",
          "State": "",
          "SqlText": "",
          "DbName": "idn_adakami_listing_legal",
          "Time": 817,
          "Client": "10.200.1.32",
          "SessionId": 300304019
        }
      ],
      "DbStats": [
        {
          "TotalCount": 70,
          "ActiveCount": 0,
          "ThreadIdList": [
            300303599,
            300303952,
            300303671,
            300303387,
            ...
          ],
          "UserList": [
            "user_idn_pro_listing_legal"
          ],
          "Key": "idn_adakami_listing_legal"
        },
        {
          "TotalCount": 1,
          "ActiveCount": 0,
          "ThreadIdList": [
            12695824
          ],
          "UserList": [
            "dba_rds"
          ],
          "Key": ""
        }
      ],
      "TimeStamp": 1766632214347
    },
    "IsFinish": true,
    "Timestamp": 1766632213991,
    "ResultId": "async_c62f1a0f46127b9827154b1fefbb195e",
    "Fail": false
  },
  "Code": 200,
  "Success": true
}
```
